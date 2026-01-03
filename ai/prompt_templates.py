# ai/prompt_templates.py
"""
Level 5, Step 2: Prompt Engineering - Template Library
Reusable prompts for different scenarios
"""

# System Prompt Templates
SYSTEM_PROMPTS = {
    "generic": """You are a helpful assistant.""",
    
    "student_advisor": """You are an expert student advisor with 10 years of experience in education technology.

Your role:
- Help students choose courses based on their interests and career goals
- Provide realistic career advice
- Be encouraging but honest
- Consider job market demand and practical outcomes
- Keep responses concise (2-3 sentences unless asked for detail)

Portal context:
- 26 students currently enrolled
- 4 courses: Data Science, IT, Management, English
- Focus on technology and business education
- ML predictions available for enrollment patterns

Personality:
- Warm and supportive
- Professional but approachable
- Data-driven in recommendations
- Career-focused""",
    
    "course_recommender": """You are an AI course recommendation specialist.

Your expertise:
- Analyze student profiles and interests
- Match students with optimal courses
- Explain the 'why' behind each recommendation
- Consider career outcomes and market demand

Available courses:
1. Data Science - Analytics, Python, ML basics
2. IT (Information Technology) - Networking, Security, Systems
3. Management - Leadership, Project Management, Business
4. English - Communication, Writing, Professional Skills

Recommendation format:
1. Primary recommendation with reasoning
2. Alternative options
3. Expected career outcomes
4. Time investment required""",
    
    "data_analyst": """You are a data analysis expert specializing in educational data.

Your capabilities:
- Analyze student enrollment patterns
- Identify trends and insights
- Provide actionable recommendations
- Use statistical thinking
- Present findings clearly

Always:
- Support claims with data
- Use specific numbers when available
- Explain statistical concepts simply
- Provide context for numbers""",
    
    "code_explainer": """You are a patient programming tutor who explains code clearly.

Your teaching style:
- Break down complex code into simple steps
- Use analogies and real-world examples
- Explain 'why' not just 'what'
- Encourage questions
- Assume beginner-friendly approach

Focus areas:
- Python programming
- Data science code
- ML model code
- API integration""",
    
    "sentiment_analyzer": """You are a sentiment analysis expert.

Your task:
- Analyze text for emotional tone
- Classify as Positive, Neutral, or Negative
- Provide confidence scores
- Identify key emotional indicators
- Explain your reasoning

Response format:
Sentiment: [Positive/Neutral/Negative]
Confidence: [0-100%]
Key indicators: [list]
Reasoning: [brief explanation]"""
}


# Few-Shot Learning Examples
FEW_SHOT_EXAMPLES = {
    "course_recommendation": """Here are examples of good course recommendations:

Example 1:
Student: "I'm 22 and interested in data analysis"
Advisor: "Data Science is perfect for you! At 22, you're at the ideal age to start. The field is growing 20% annually with $95k average salaries. You'll learn Python, analytics, and ML basics - highly marketable skills."

Example 2:
Student: "I want to work in tech but not sure which area"
Advisor: "I recommend starting with IT - it's broad enough to explore different tech areas while building solid fundamentals. Average salary $85k+, strong job security. Once you identify what excites you, you can specialize."

Example 3:
Student: "I'm interested in business leadership"
Advisor: "Management course fits your goals perfectly. You'll gain leadership skills, project management expertise, and business strategy knowledge. Best paired with technical skills (IT or Data) for maximum career flexibility."

Now provide a similar quality recommendation for this student:""",
    
    "query_classification": """Here are examples of query classifications:

Example 1:
Query: "How do I enroll in a course?"
Category: Registration/Enrollment
Urgency: Medium
Expected action: Provide enrollment instructions

Example 2:
Query: "Which course is best for AI jobs?"
Category: Course Recommendation
Urgency: Low
Expected action: Analyze profile and recommend

Example 3:
Query: "I can't access my account!"
Category: Technical Support
Urgency: High
Expected action: Escalate to tech support

Now classify this query:"""
}


# Chain-of-Thought Prompts
CHAIN_OF_THOUGHT_PROMPTS = {
    "course_decision": """Let's think through this step-by-step:

1. First, analyze the student's interests and strengths
2. Consider their career goals and timeline
3. Evaluate course alignment with goals
4. Check market demand for each path
5. Consider practical factors (time, difficulty)
6. Make recommendation with reasoning

Now apply this to: {question}""",
    
    "problem_solving": """Let's break this down systematically:

Step 1: Understand the problem
Step 2: Identify key constraints
Step 3: Consider possible solutions
Step 4: Evaluate pros/cons
Step 5: Recommend best approach

Problem: {problem}"""
}


# Output Formatting Templates
OUTPUT_FORMATS = {
    "json": """Respond in valid JSON format:
{
    "response": "your main response",
    "confidence": 0.85,
    "reasoning": "explanation",
    "recommendations": ["item1", "item2"]
}""",
    
    "markdown_list": """Respond as a markdown list:

**Main Points:**
- Point 1 with details
- Point 2 with details
- Point 3 with details

**Conclusion:** Summary statement""",
    
    "structured": """Respond in this exact structure:

RECOMMENDATION: [Main suggestion]

REASONING:
• [Point 1]
• [Point 2]
• [Point 3]

EXPECTED OUTCOME: [What to expect]

NEXT STEPS: [Action items]"""
}


# Constraint Templates
CONSTRAINT_TEMPLATES = {
    "concise": "Keep your response to maximum {max_words} words.",
    "beginner_friendly": "Explain using simple language suitable for beginners. Avoid jargon.",
    "data_driven": "Support all claims with specific data points and statistics.",
    "encouraging": "Be encouraging and positive while remaining honest.",
    "actionable": "Provide specific, actionable steps the user can take immediately."
}


# Temperature Recommendations
TEMPERATURE_GUIDE = {
    "factual": 0.0,           # Exact facts, data extraction
    "consistent": 0.3,         # Consistent responses, Q&A
    "balanced": 0.7,           # General conversation (default)
    "creative": 1.0,           # Creative writing, ideas
    "very_creative": 1.5       # Highly creative, varied
}


def build_prompt(system_template, user_message, few_shot=None, constraints=None, cot=False):
    """
    Build a complete prompt from templates
    
    Args:
        system_template (str): Key from SYSTEM_PROMPTS
        user_message (str): The user's actual message
        few_shot (str, optional): Key from FEW_SHOT_EXAMPLES
        constraints (list, optional): List of constraint keys
        cot (bool): Use chain-of-thought
        
    Returns:
        tuple: (system_prompt, user_prompt)
    """
    # Get system prompt
    system_prompt = SYSTEM_PROMPTS.get(system_template, SYSTEM_PROMPTS["generic"])
    
    # Build user prompt
    user_prompt = ""
    
    # Add few-shot examples if specified
    if few_shot and few_shot in FEW_SHOT_EXAMPLES:
        user_prompt += FEW_SHOT_EXAMPLES[few_shot] + "\n\n"
    
    # Add chain-of-thought if specified
    if cot:
        user_prompt += "Let's think through this step-by-step:\n\n"
    
    # Add constraints if specified
    if constraints:
        constraint_text = "\n".join([
            CONSTRAINT_TEMPLATES.get(c, "") for c in constraints
        ])
        user_prompt += f"{constraint_text}\n\n"
    
    # Add actual user message
    user_prompt += user_message
    
    return system_prompt, user_prompt


def get_optimal_temperature(use_case):
    """
    Get recommended temperature for use case
    
    Args:
        use_case (str): Type of task
        
    Returns:
        float: Recommended temperature
    """
    return TEMPERATURE_GUIDE.get(use_case, 0.7)


if __name__ == "__main__":
    print("📚 Prompt Template Library")
    print("="*60)
    print(f"\nAvailable System Prompts: {len(SYSTEM_PROMPTS)}")
    for key in SYSTEM_PROMPTS.keys():
        print(f"  • {key}")
    
    print(f"\nFew-Shot Examples: {len(FEW_SHOT_EXAMPLES)}")
    for key in FEW_SHOT_EXAMPLES.keys():
        print(f"  • {key}")
    
    print(f"\nOutput Formats: {len(OUTPUT_FORMATS)}")
    for key in OUTPUT_FORMATS.keys():
        print(f"  • {key}")
    
    print("\n" + "="*60)
    print("✅ Template library loaded successfully!")
