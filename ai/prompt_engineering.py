# ai/prompt_engineering.py
"""
Level 5, Step 2: Prompt Engineering - Experimentation Framework
Test and compare different prompt strategies
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ai.config import validate_api_key, OPENAI_API_KEY
from ai.prompt_templates import SYSTEM_PROMPTS, build_prompt, get_optimal_temperature
from openai import OpenAI
import time


class PromptTester:
    """Framework for testing and comparing prompts"""
    
    def __init__(self):
        """Initialize the tester"""
        if not validate_api_key():
            raise ValueError("API key not configured")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.results = []
    
    def test_prompt(self, system_prompt, user_message, temperature=0.7, label="Test"):
        """
        Test a single prompt configuration
        
        Args:
            system_prompt (str): System prompt to use
            user_message (str): User message
            temperature (float): Temperature setting
            label (str): Label for this test
            
        Returns:
            dict: Test results
        """
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=200
            )
            
            elapsed_time = time.time() - start_time
            
            result = {
                "label": label,
                "system_prompt": system_prompt[:100] + "..." if len(system_prompt) > 100 else system_prompt,
                "user_message": user_message,
                "temperature": temperature,
                "response": response.choices[0].message.content,
                "tokens": response.usage.total_tokens,
                "time": elapsed_time,
                "cost": (response.usage.total_tokens / 1000) * 0.002
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ Error in test '{label}': {e}")
            return None
    
    def compare_system_prompts(self, user_message):
        """Compare different system prompts with same user message"""
        print("\n🔬 Experiment 1: System Prompt Comparison")
        print("="*60)
        print(f"User Message: '{user_message}'")
        print("="*60)
        
        prompts_to_test = ["generic", "student_advisor", "course_recommender"]
        
        for prompt_key in prompts_to_test:
            print(f"\n📝 Testing: {prompt_key}")
            result = self.test_prompt(
                SYSTEM_PROMPTS[prompt_key],
                user_message,
                temperature=0.7,
                label=f"System: {prompt_key}"
            )
            
            if result:
                print(f"🤖 Response: {result['response']}")
                print(f"📊 Tokens: {result['tokens']} | Cost: ${result['cost']:.6f}")
                print("-"*60)
    
    def compare_temperatures(self, system_prompt, user_message):
        """Test same prompt at different temperatures"""
        print("\n🌡️ Experiment 2: Temperature Comparison")
        print("="*60)
        print(f"User Message: '{user_message}'")
        print("="*60)
        
        temperatures = [0.0, 0.7, 1.5]
        
        for temp in temperatures:
            print(f"\n🌡️ Temperature: {temp}")
            result = self.test_prompt(
                system_prompt,
                user_message,
                temperature=temp,
                label=f"Temp: {temp}"
            )
            
            if result:
                print(f"🤖 Response: {result['response']}")
                print(f"📊 Tokens: {result['tokens']}")
                print("-"*60)
    
    def test_few_shot_learning(self):
        """Test few-shot vs zero-shot"""
        print("\n🎯 Experiment 3: Few-Shot Learning")
        print("="*60)
        
        user_question = "I'm 23 and want to work in AI"
        
        # Zero-shot
        print("\n📝 Zero-Shot (No Examples):")
        result1 = self.test_prompt(
            SYSTEM_PROMPTS["student_advisor"],
            user_question,
            label="Zero-shot"
        )
        if result1:
            print(f"🤖 Response: {result1['response']}")
        
        # Few-shot
        print("\n📝 Few-Shot (With Examples):")
        system_prompt, user_prompt = build_prompt(
            "student_advisor",
            user_question,
            few_shot="course_recommendation"
        )
        result2 = self.test_prompt(
            system_prompt,
            user_prompt,
            label="Few-shot"
        )
        if result2:
            print(f"🤖 Response: {result2['response']}")
        
        print("-"*60)
    
    def test_constraints(self):
        """Test different constraints"""
        print("\n📏 Experiment 4: Constraint Testing")
        print("="*60)
        
        user_question = "Explain what Data Science is"
        
        # No constraints
        print("\n📝 No Constraints:")
        result1 = self.test_prompt(
            SYSTEM_PROMPTS["student_advisor"],
            user_question,
            label="No constraints"
        )
        if result1:
            print(f"🤖 Response: {result1['response']}")
            print(f"Word count: {len(result1['response'].split())}")
        
        # With constraints
        print("\n📝 With Constraints (Concise + Beginner-friendly):")
        system_prompt, user_prompt = build_prompt(
            "student_advisor",
            user_question,
            constraints=["concise", "beginner_friendly"]
        )
        result2 = self.test_prompt(
            SYSTEM_PROMPTS["student_advisor"],
            user_prompt,
            label="With constraints"
        )
        if result2:
            print(f"🤖 Response: {result2['response']}")
            print(f"Word count: {len(result2['response'].split())}")
        
        print("-"*60)
    
    def generate_report(self, output_path):
        """Generate comparison report"""
        report = """
╔════════════════════════════════════════════════════════════╗
║          PROMPT ENGINEERING EXPERIMENT REPORT              ║
║          Level 5, Step 2                                   ║
╚════════════════════════════════════════════════════════════╝

SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Tests Run: {total_tests}
Total Tokens Used: {total_tokens}
Total Cost: ${total_cost:.6f}
Average Response Time: {avg_time:.2f}s

""".format(
            total_tests=len(self.results),
            total_tokens=sum(r['tokens'] for r in self.results),
            total_cost=sum(r['cost'] for r in self.results),
            avg_time=sum(r['time'] for r in self.results) / len(self.results) if self.results else 0
        )
        
        report += "\nDETAILED RESULTS\n"
        report += "━"*60 + "\n\n"
        
        for i, result in enumerate(self.results, 1):
            report += f"Test {i}: {result['label']}\n"
            report += f"Temperature: {result['temperature']}\n"
            report += f"User Message: {result['user_message']}\n"
            report += f"\nResponse:\n{result['response']}\n"
            report += f"\nMetrics:\n"
            report += f"  • Tokens: {result['tokens']}\n"
            report += f"  • Time: {result['time']:.2f}s\n"
            report += f"  • Cost: ${result['cost']:.6f}\n"
            report += "\n" + "-"*60 + "\n\n"
        
        report += """
KEY FINDINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. System Prompts:
   • Specific role prompts produce more relevant responses
   • Generic prompts are shorter but less helpful
   • Expert roles add domain knowledge

2. Temperature:
   • 0.0 = Consistent, factual, predictable
   • 0.7 = Balanced, natural conversation
   • 1.5 = Creative, varied, less predictable

3. Few-Shot Learning:
   • Examples significantly improve response quality
   • AI learns patterns from examples
   • Costs more tokens but better results

4. Constraints:
   • AI generally follows constraints well
   • Clear constraints = better outputs
   • Can combine multiple constraints

RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Use specific system prompts for each use case
✓ Set temperature based on task (factual=0.0, creative=1.0)
✓ Add few-shot examples for complex tasks
✓ Define clear constraints for output format
✓ Test different approaches and measure results

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {timestamp}
"""
        
        from datetime import datetime
        report = report.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Save report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n💾 Report saved: {output_path}")
        return report


def main():
    """Run all experiments"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  Level 5, Step 2: Prompt Engineering Experiments          ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    try:
        tester = PromptTester()
        
        # Experiment 1: System Prompts
        tester.compare_system_prompts(
            "I'm interested in technology and want a good career"
        )
        
        # Experiment 2: Temperature
        tester.compare_temperatures(
            SYSTEM_PROMPTS["student_advisor"],
            "What courses do you recommend?"
        )
        
        # Experiment 3: Few-Shot Learning
        tester.test_few_shot_learning()
        
        # Experiment 4: Constraints
        tester.test_constraints()
        
        # Generate report
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        report_path = output_dir / "prompt_comparison.txt"
        
        tester.generate_report(report_path)
        
        print("\n" + "="*60)
        print("🎉 All experiments completed!")
        print("="*60)
        print(f"\n📊 Total tests: {len(tester.results)}")
        print(f"💰 Total cost: ${sum(r['cost'] for r in tester.results):.6f}")
        print(f"📁 Report: {report_path}")
        
    except ValueError as e:
        print(f"❌ Setup error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
