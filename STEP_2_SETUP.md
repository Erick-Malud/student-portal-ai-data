# 🚀 Level 5, Step 2: Setup Instructions

## ✅ What Was Created

Step 2 is complete with all prompt engineering tools ready!

## 📋 How to Use

### Option 1: Run Prompt Engineering Experiments

Test different prompt strategies and compare results:

```powershell
python ai/prompt_engineering.py
```

**What it does:**
- Tests different system prompts
- Compares temperature settings
- Demonstrates few-shot learning
- Tests constraints
- Generates detailed report

**Output:** `ai/outputs/prompt_comparison.txt`

---

### Option 2: Try the Advanced Chatbot

Use the improved chatbot with prompt engineering:

```powershell
python ai/advanced_chatbot.py
```

**Choose from 4 modes:**
1. Standard mode (Temperature: 0.7)
2. Factual mode (Temperature: 0.0) - Consistent answers
3. Creative mode (Temperature: 1.2) - More varied
4. Expert mode - With few-shot learning

---

### Option 3: See Before/After Comparison

Compare Step 1 vs Step 2 chatbot quality:

```powershell
python ai/advanced_chatbot.py --demo
```

**Shows:** How prompt engineering improves responses!

---

### Option 4: Explore Prompt Templates

View available templates:

```powershell
python ai/prompt_templates.py
```

**Displays:**
- System prompts
- Few-shot examples
- Output formats
- Constraint templates

---

## 📚 Reference Materials

### Quick Reference
- File: `PROMPT_QUICK_REFERENCE.md`
- What: Cheat sheet for prompt engineering
- Use: Quick lookup while coding

### Template Library
- File: `ai/prompt_templates.py`
- What: Reusable prompts
- Use: Import and use in your code

---

## 💡 Example Usage in Code

```python
from ai.advanced_chatbot import AdvancedStudentBot

# Create expert bot with few-shot learning
bot = AdvancedStudentBot(temperature=0.7, use_few_shot=True)

# Chat
response, tokens = bot.chat("I'm interested in AI")
print(response)

# Get stats
stats = bot.get_stats()
print(f"Tokens used: {stats['total_tokens']}")
```

---

## 🎯 Learning Path

### Step 1: Run Experiments
```powershell
python ai/prompt_engineering.py
```
**Learn:** How different prompts affect responses

### Step 2: Try Different Modes
```powershell
python ai/advanced_chatbot.py
```
**Learn:** Temperature and few-shot effects

### Step 3: See Comparison
```powershell
python ai/advanced_chatbot.py --demo
```
**Learn:** Quality improvements

### Step 4: Build Your Own
Use templates to create custom prompts!

---

## 📊 Expected Results

### Experiment Output:
- 10-15 API calls
- ~2,000-3,000 tokens
- Cost: ~$0.04-0.06
- Report: Detailed comparison

### Chatbot Quality:
- ✅ More relevant responses
- ✅ Better context understanding
- ✅ Follows instructions better
- ✅ More professional tone

---

## 🆘 Troubleshooting

### "Module not found"
Make sure you're in the project root directory and virtual environment is activated.

### "API key not found"
Ensure `.env` file exists with your OpenAI API key (from Step 1).

### High costs
Don't worry! Step 2 costs less than $0.10 total.

---

## 🎓 What You Learned

After Step 2, you now understand:
- ✅ System vs user prompts
- ✅ Temperature effects
- ✅ Few-shot learning
- ✅ Constraint application
- ✅ Prompt optimization
- ✅ Quality measurement

---

## 🚀 Next Steps

**Step 3: Building AI Student Advisor**
- Integrate prompts with your data
- Build production chatbot
- Add context from student portal

---

**Ready to continue?** Check the generated reports and try different configurations!

Generated: December 30, 2025
