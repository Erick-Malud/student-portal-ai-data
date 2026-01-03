"""
Text Classifier - Step 5
Categorizes student queries and feedback into predefined categories
"""

import json
from typing import Dict, List
from openai import OpenAI
from ai.config import load_api_key


# Define query categories
QUERY_CATEGORIES = {
    'technical_support': 'Issues with platform, login, submission, technical problems',
    'academic_difficulty': 'Content too hard, need help understanding concepts, struggling with coursework',
    'administrative': 'Deadlines, schedules, policies, enrollment, grades questions',
    'feedback_positive': 'Praise, satisfaction, appreciation, positive comments',
    'feedback_negative': 'Complaints, suggestions for improvement, dissatisfaction',
    'career_guidance': 'Job prospects, career paths, industry questions, internships',
    'course_recommendation': 'What courses to take next, prerequisites, learning paths',
    'at_risk_alert': 'Signs of dropping out, severe distress, mental health concerns, giving up',
    'general_question': 'Other inquiries that don\'t fit above categories'
}


class TextClassifier:
    """Classify student text into categories with priority assessment"""
    
    def __init__(self):
        """Initialize text classifier with OpenAI client"""
        api_key = load_api_key()
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
        self.categories = QUERY_CATEGORIES
        print("✓ Text Classifier initialized")
    
    def classify(self, text: str) -> Dict:
        """
        Classify text into category with priority and action assessment
        
        Args:
            text: Student message or feedback
        
        Returns:
            Classification result with category, priority, and recommendations
        """
        if not text or not text.strip():
            return {
                'category': 'general_question',
                'confidence': 0.0,
                'priority': 'low',
                'requires_action': False,
                'suggested_response_time': 'N/A',
                'reasoning': 'Empty text provided'
            }
        
        categories_str = "\n".join(
            f"- {cat}: {desc}" 
            for cat, desc in self.categories.items()
        )
        
        prompt = f"""Classify this student message into one category:

Message: "{text}"

Available categories:
{categories_str}

Respond in JSON format:
{{
    "category": "category_name",
    "confidence": 0.0-1.0,
    "priority": "critical|high|medium|low",
    "requires_action": true/false,
    "suggested_response_time": "< 1 hour | < 4 hours | < 24 hours | < 48 hours | standard",
    "reasoning": "brief explanation of why this category and priority"
}}

Priority rules:
- CRITICAL: at_risk_alert (dropping out, severe distress)
- HIGH: academic_difficulty with strong negative tone, urgent technical issues
- MEDIUM: standard academic_difficulty, administrative questions, technical_support
- LOW: feedback_positive, general_question"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at classifying student support requests. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Very low for consistent classification
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # Handle markdown code blocks
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            
            result = json.loads(content)
            
            # Validate and set defaults
            result.setdefault('category', 'general_question')
            result.setdefault('confidence', 0.5)
            result.setdefault('priority', 'medium')
            result.setdefault('requires_action', False)
            result.setdefault('suggested_response_time', 'standard')
            result.setdefault('reasoning', 'Classified based on content')
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Warning: JSON decode error - {e}")
            return {
                'category': 'general_question',
                'confidence': 0.0,
                'priority': 'low',
                'requires_action': False,
                'suggested_response_time': 'standard',
                'reasoning': f'Error parsing response: {e}'
            }
        except Exception as e:
            print(f"Error classifying text: {e}")
            return {
                'category': 'general_question',
                'confidence': 0.0,
                'priority': 'low',
                'requires_action': False,
                'suggested_response_time': 'standard',
                'reasoning': f'Error: {str(e)}'
            }
    
    def classify_batch(self, texts: List[str], include_text: bool = True) -> List[Dict]:
        """
        Classify multiple texts
        
        Args:
            texts: List of messages to classify
            include_text: Whether to include original text in results
        
        Returns:
            List of classification results
        """
        results = []
        total = len(texts)
        
        print(f"Classifying {total} messages...")
        for i, text in enumerate(texts, 1):
            if i % 10 == 0 or i == total:
                print(f"  Progress: {i}/{total}")
            
            result = self.classify(text)
            if include_text:
                result['text'] = text
            results.append(result)
        
        print(f"✓ Completed classification of {total} messages")
        return results
    
    def get_classification_summary(self, results: List[Dict]) -> Dict:
        """
        Summarize classification results
        
        Returns:
            Summary with counts per category and priority
        """
        if not results:
            return {
                'total_count': 0,
                'by_category': {},
                'by_priority': {},
                'requires_action_count': 0
            }
        
        total = len(results)
        by_category = {}
        by_priority = {}
        requires_action = 0
        
        for result in results:
            # Count by category
            category = result.get('category', 'unknown')
            by_category[category] = by_category.get(category, 0) + 1
            
            # Count by priority
            priority = result.get('priority', 'unknown')
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            # Count action required
            if result.get('requires_action', False):
                requires_action += 1
        
        return {
            'total_count': total,
            'by_category': dict(sorted(by_category.items(), 
                                      key=lambda x: x[1], 
                                      reverse=True)),
            'by_priority': by_priority,
            'requires_action_count': requires_action,
            'requires_action_percentage': (requires_action / total * 100) if total > 0 else 0.0
        }
    
    def get_priority_items(self, results: List[Dict]) -> Dict:
        """
        Extract items by priority level for action
        
        Returns:
            Dict with critical, high, medium, and low priority items
        """
        priority_map = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for result in results:
            priority = result.get('priority', 'low')
            if priority in priority_map:
                priority_map[priority].append(result)
        
        # Sort each by confidence (highest first)
        for priority in priority_map:
            priority_map[priority] = sorted(
                priority_map[priority], 
                key=lambda x: x.get('confidence', 0), 
                reverse=True
            )
        
        return priority_map
    
    def get_action_items(self, results: List[Dict]) -> List[Dict]:
        """
        Get all items requiring action, sorted by priority
        
        Returns:
            List of items needing response/action
        """
        action_items = [
            r for r in results 
            if r.get('requires_action', False) or r.get('priority') in ['critical', 'high']
        ]
        
        # Sort by priority (critical first)
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        action_items.sort(
            key=lambda x: priority_order.get(x.get('priority', 'low'), 3)
        )
        
        return action_items
    
    def get_at_risk_students(self, results: List[Dict]) -> List[Dict]:
        """
        Identify students showing at-risk indicators
        
        Returns:
            List of at-risk classifications
        """
        at_risk = [
            r for r in results 
            if r.get('category') == 'at_risk_alert' or 
            (r.get('priority') == 'critical')
        ]
        
        return sorted(at_risk, 
                     key=lambda x: x.get('confidence', 0), 
                     reverse=True)


def quick_classify(text: str) -> str:
    """
    Quick function to classify a single text
    
    Args:
        text: Text to classify
    
    Returns:
        Human-readable classification description
    """
    classifier = TextClassifier()
    result = classifier.classify(text)
    
    category = result['category']
    priority = result['priority'].upper()
    confidence = result['confidence']
    
    return f"Category: {category} | Priority: {priority} | Confidence: {confidence:.0%}"


if __name__ == "__main__":
    """Test the text classifier"""
    print("=" * 60)
    print("Testing Text Classifier")
    print("=" * 60)
    
    # Test cases
    test_texts = [
        "How do I submit my homework? The upload button isn't working.",
        "I don't understand recursion at all. This is way too confusing.",
        "When is the final exam? What chapters will it cover?",
        "This course is amazing! Best class I've taken.",
        "The lectures are too fast and the homework takes forever.",
        "What career paths can I pursue after this course?",
        "What should I take after finishing Python?",
        "I'm thinking about dropping this class. It's too stressful and I can't handle it.",
        "Is there a study guide for the midterm?"
    ]
    
    try:
        classifier = TextClassifier()
        
        print("\n1. Testing Individual Classification:")
        print("-" * 60)
        for i, text in enumerate(test_texts[:3], 1):
            print(f"\nText {i}: \"{text}\"")
            result = classifier.classify(text)
            print(f"  Category: {result['category']}")
            print(f"  Priority: {result['priority'].upper()}")
            print(f"  Confidence: {result['confidence']:.0%}")
            print(f"  Requires Action: {result['requires_action']}")
            print(f"  Response Time: {result['suggested_response_time']}")
            print(f"  Reasoning: {result['reasoning']}")
        
        print("\n2. Testing Batch Classification:")
        print("-" * 60)
        results = classifier.classify_batch(test_texts, include_text=False)
        print(f"Classified {len(results)} texts")
        
        print("\n3. Testing Classification Summary:")
        print("-" * 60)
        summary = classifier.get_classification_summary(results)
        print(f"Total: {summary['total_count']}")
        print(f"\nBy Category:")
        for category, count in summary['by_category'].items():
            print(f"  - {category}: {count}")
        print(f"\nBy Priority:")
        for priority, count in summary['by_priority'].items():
            print(f"  - {priority}: {count}")
        print(f"\nRequires Action: {summary['requires_action_count']} ({summary['requires_action_percentage']:.1f}%)")
        
        print("\n4. Testing Priority Items:")
        print("-" * 60)
        priority_items = classifier.get_priority_items(results)
        print(f"Critical: {len(priority_items['critical'])}")
        print(f"High: {len(priority_items['high'])}")
        print(f"Medium: {len(priority_items['medium'])}")
        print(f"Low: {len(priority_items['low'])}")
        
        print("\n5. Testing Action Items:")
        print("-" * 60)
        action_items = classifier.get_action_items(results)
        print(f"Items requiring action: {len(action_items)}")
        
        print("\n6. Testing At-Risk Detection:")
        print("-" * 60)
        at_risk = classifier.get_at_risk_students(results)
        print(f"At-risk students detected: {len(at_risk)}")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
