# 📚 Prompt Engineering Guide - Quick Reference

## 🎯 Core Concepts

### 1. System Prompts (AI's Role)
```python
# Bad
"You are a helpful assistant."

# Good
"You are an expert student advisor with 10 years experience...
[specific role, guidelines, personality]"
```

### 2. Temperature Settings
- **0.0** - Deterministic, factual, consistent
- **0.7** - Balanced, natural (default)
- **1.5** - Creative, varied, unpredictable

### 3. Few-Shot Learning (Teaching by Example)
Give AI 2-3 examples of desired output before asking your question.

### 4. Chain-of-Thought
Add "Let's think step-by-step:" to get better reasoning.

---

## 🛠️ How to Use

### Load Templates:
```python
from ai.prompt_templates import SYSTEM_PROMPTS, build_prompt

# Use pre-built system prompt
system = SYSTEM_PROMPTS["student_advisor"]

# Build complex prompt
system, user = build_prompt(
    "student_advisor",
    "What should I study?",
    few_shot="course_recommendation",
    constraints=["concise", "actionable"]
)
```

### Test Prompts:
```bash
# Run experiments
python ai/prompt_engineering.py

# Try advanced chatbot
python ai/advanced_chatbot.py

# See comparison
python ai/advanced_chatbot.py --demo
```

---

## 💡 Best Practices

✅ **DO:**
- Use specific system prompts for each use case
- Set temperature based on task
- Add examples for complex tasks
- Define clear constraints
- Test and measure results

❌ **DON'T:**
- Use generic prompts for specialized tasks
- Ignore temperature settings
- Expect perfect results without testing
- Forget to track token usage

---

## 📊 When to Use What

| Task | System Prompt | Temperature | Few-Shot |
|------|---------------|-------------|----------|
| Facts/Data | Any specific | 0.0-0.3 | No |
| Conversation | student_advisor | 0.7 | Optional |
| Recommendations | course_recommender | 0.5-0.7 | Yes |
| Creative Writing | Any | 1.0-1.5 | Optional |
| Code Explanation | code_explainer | 0.3-0.5 | Yes |

---

## 🎯 Examples

### Example 1: Course Recommendation
```python
bot = AdvancedStudentBot(temperature=0.7, use_few_shot=True)
response = bot.chat("I'm 22 and interested in AI")
```

### Example 2: Factual Query
```python
bot = AdvancedStudentBot(temperature=0.0, use_few_shot=False)
response = bot.chat("How many students are enrolled?")
```

### Example 3: Creative Response
```python
bot = AdvancedStudentBot(temperature=1.2, use_few_shot=False)
response = bot.chat("Write a motivational message for students")
```

---

## 📈 Measuring Success

**Good response has:**
- ✅ Answers the question directly
- ✅ Appropriate length
- ✅ Follows constraints
- ✅ Relevant to context
- ✅ Actionable (when needed)

**Track:**
- Token usage (cost)
- Response quality
- User satisfaction
- Consistency

---

## 🆘 Troubleshooting

**Problem:** Generic responses
→ **Solution:** Use more specific system prompt

**Problem:** Inconsistent answers
→ **Solution:** Lower temperature (0.0-0.3)

**Problem:** Too verbose
→ **Solution:** Add "concise" constraint

**Problem:** Not following instructions
→ **Solution:** Add few-shot examples

---

Generated: Level 5, Step 2
For full guide: See PROMPT_ENGINEERING_GUIDE.md
