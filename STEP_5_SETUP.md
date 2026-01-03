# Step 5: Sentiment Analysis & Text Classification - Setup Guide

## 🎯 What You Built

A comprehensive text analysis system that automatically:
- **Analyzes sentiment** (positive/negative/neutral) in student feedback
- **Classifies messages** into categories (technical, academic, at-risk, etc.)
- **Extracts topics** from collections of feedback
- **Generates alerts** for students needing attention
- **Creates reports** with actionable insights

**Core Value**: Transform qualitative feedback into quantitative, actionable insights automatically!

---

## 📋 Prerequisites

Ensure you completed:
- ✅ Step 1: OpenAI API setup
- ✅ `.env` file with API key
- ✅ `students.json` with student data
- ✅ Virtual environment activated

---

## 🚀 Quick Start

### **1. Load Sample Feedback Data**

Sample feedback is provided in `data/student_feedback.json` with 20 realistic feedback messages from students.

### **2. Run Complete Analysis**

```powershell
python -c "
from ai.feedback_analyzer import FeedbackAnalyzer
import json

# Load sample feedback
with open('data/student_feedback.json', 'r', encoding='utf-8') as f:
    feedback = json.load(f)

# Analyze
analyzer = FeedbackAnalyzer()
results = analyzer.analyze_feedback(feedback)

# Save results
analyzer.save_analysis(results)
"
```

This will:
- Analyze all 20 feedback messages
- Generate sentiment scores
- Classify by category
- Extract common topics
- Identify at-risk students
- Save full analysis to `ai/outputs/`

---

## 📚 Component Guide

### **Component 1: Sentiment Analyzer**

**Purpose**: Detect emotions and sentiment in text

**Test it:**
```powershell
python ai/sentiment_analyzer.py
```

**Use it in code:**
```python
from ai.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Analyze single text
result = analyzer.analyze_sentiment("I love this course!")
print(result['sentiment'])  # 'positive'
print(result['score'])      # 0.95
print(result['emotion'])    # 'joy'

# Analyze multiple texts
texts = ["Great class!", "Too hard", "It's okay"]
results = analyzer.analyze_batch(texts)

# Get summary statistics
summary = analyzer.get_sentiment_summary(results)
print(f"Positive: {summary['positive_percentage']:.1f}%")
```

**Output Example:**
```json
{
  "sentiment": "positive",
  "score": 0.92,
  "emotion": "joy",
  "confidence": 0.95,
  "reasoning": "Strong positive language with enthusiasm"
}
```

---

### **Component 2: Text Classifier**

**Purpose**: Categorize messages by type and priority

**Test it:**
```powershell
python ai/text_classifier.py
```

**Use it in code:**
```python
from ai.text_classifier import TextClassifier

classifier = TextClassifier()

# Classify single message
result = classifier.classify("I'm thinking about dropping this class")
print(result['category'])  # 'at_risk_alert'
print(result['priority'])  # 'critical'

# Get action items
results = classifier.classify_batch(messages)
action_items = classifier.get_action_items(results)
print(f"Need response: {len(action_items)} messages")
```

**Categories:**
- `technical_support` - Platform/system issues
- `academic_difficulty` - Struggling with content
- `administrative` - Deadlines, policies, schedules
- `feedback_positive` - Praise and satisfaction
- `feedback_negative` - Complaints and suggestions
- `career_guidance` - Job prospects, career paths
- `course_recommendation` - What to take next
- `at_risk_alert` - 🚨 Signs of dropping out
- `general_question` - Other inquiries

**Priority Levels:**
- `critical` - 🚨 Immediate action required (< 1 hour)
- `high` - ⚠️ Urgent (< 4 hours)
- `medium` - 📌 Standard (< 24 hours)
- `low` - 📋 Can wait (< 48 hours)

---

### **Component 3: Topic Extractor**

**Purpose**: Discover themes without predefined categories

**Test it:**
```powershell
python ai/topic_extractor.py
```

**Use it in code:**
```python
from ai.topic_extractor import TopicExtractor

extractor = TopicExtractor()

# Extract topics from feedback collection
texts = [feedback1, feedback2, feedback3, ...]
topics = extractor.extract_topics(texts, max_topics=5)

for topic in topics:
    print(f"{topic['topic']}: {topic['frequency']*100:.0f}%")
    print(f"  Sentiment: {topic['sentiment']}")
    print(f"  Keywords: {', '.join(topic['keywords'])}")

# Summarize feedback
summary = extractor.summarize_feedback(texts)
print(summary)
```

**Output Example:**
```python
[
  {
    "topic": "Homework Difficulty",
    "frequency": 0.35,  # 35% of messages
    "sentiment": "negative",
    "keywords": ["homework", "difficult", "time-consuming"],
    "examples": ["The homework takes too long", "Too difficult"]
  },
  ...
]
```

---

### **Component 4: Feedback Analyzer (Main System)**

**Purpose**: Orchestrates all components for complete analysis

**Test it:**
```powershell
python ai/feedback_analyzer.py
```

**Use it in code:**
```python
from ai.feedback_analyzer import FeedbackAnalyzer
import json

# Load feedback data
with open('data/student_feedback.json', 'r') as f:
    feedback = json.load(f)

# Initialize analyzer
analyzer = FeedbackAnalyzer()

# Run complete analysis
results = analyzer.analyze_feedback(feedback)

# Access results
print(f"Total: {results['total_feedback']}")
print(f"Positive: {results['sentiment_analysis']['positive_percentage']:.1f}%")
print(f"Alerts: {len(results['alerts'])} students")
print(f"Topics: {len(results['topics'])} themes")

# Print insights
for insight in results['insights']:
    print(f"- {insight}")

# Print recommendations
for rec in results['recommendations']:
    print(f"- {rec}")

# Save results
analyzer.save_analysis(results)
analyzer.export_alerts(results)

# Analyze by course
course_results = analyzer.analyze_by_course(feedback)
for course, analysis in course_results.items():
    print(f"\n{course}: {analysis['sentiment_analysis']['average_score']:.2f}")

# Analyze specific student
student_results = analyzer.analyze_by_student(student_id=1, feedback_data=feedback)
```

---

### **Component 5: Report Generator**

**Purpose**: Create human-readable reports

**Use it in code:**
```python
from ai.analysis_report_generator import AnalysisReportGenerator

generator = AnalysisReportGenerator()

# Generate markdown report
report = generator.generate_report(results, format='markdown')
print(report)

# Generate text report
text_report = generator.generate_report(results, format='text')

# Generate executive summary
summary = generator.generate_executive_summary(results)
print(summary)

# Save report
filepath = generator.save_report(report, format='markdown')
print(f"Saved to: {filepath}")
```

---

## 🎮 Complete Workflow Example

```python
from ai.feedback_analyzer import FeedbackAnalyzer
from ai.analysis_report_generator import AnalysisReportGenerator
import json

# 1. Load feedback
with open('data/student_feedback.json', 'r') as f:
    feedback = json.load(f)

# 2. Analyze
analyzer = FeedbackAnalyzer()
results = analyzer.analyze_feedback(feedback)

# 3. Generate report
generator = AnalysisReportGenerator()
report = generator.generate_report(results, format='markdown')

# 4. Save everything
analyzer.save_analysis(results)
analyzer.export_alerts(results)
generator.save_report(report)

# 5. Print key findings
print("\n=== EXECUTIVE SUMMARY ===")
print(generator.generate_executive_summary(results))

print("\n=== ALERTS ===")
for alert in results['alerts'][:3]:
    print(f"Student {alert['student_id']}: {alert['priority'].upper()}")
    print(f"  {alert['text'][:80]}...")
    print(f"  Action: {alert['recommended_action'][:80]}...")
    print()
```

---

## 📂 Output Files

All results saved to `ai/outputs/`:

```
ai/outputs/
├── feedback_analysis_20260103_143022.json    # Full analysis results
├── alerts_20260103_143022.json               # Student alerts only
└── feedback_report_20260103_143022.md        # Human-readable report
```

---

## 🎯 Real-World Use Cases

### **Use Case 1: Course Feedback Analysis**

```python
# End-of-semester analysis
analyzer = FeedbackAnalyzer()
results = analyzer.analyze_feedback(course_feedback)

# Identify what to improve
for topic in results['topics']:
    if topic['sentiment'] == 'negative':
        print(f"Fix: {topic['topic']} ({topic['frequency']*100:.0f}% mentioned)")
```

### **Use Case 2: At-Risk Student Detection**

```python
# Weekly monitoring
analyzer = FeedbackAnalyzer()
results = analyzer.analyze_feedback(weekly_feedback)

# Alert advisors about at-risk students
for alert in results['alerts']:
    if alert['priority'] == 'critical':
        send_email(advisor, alert['student_id'], alert['recommended_action'])
```

### **Use Case 3: Support Ticket Triage**

```python
# Automatic prioritization
classifier = TextClassifier()
tickets = load_support_tickets()

for ticket in tickets:
    result = classifier.classify(ticket['message'])
    ticket['priority'] = result['priority']
    ticket['category'] = result['category']
    ticket['response_time'] = result['suggested_response_time']

# Route by priority
urgent = [t for t in tickets if t['priority'] in ['critical', 'high']]
```

### **Use Case 4: Trend Analysis Over Time**

```python
# Compare this month vs last month
analyzer = FeedbackAnalyzer()
this_month = analyzer.analyze_feedback(current_feedback)
last_month = analyzer.analyze_feedback(previous_feedback)

# Compare sentiment
print(f"This month: {this_month['sentiment_analysis']['average_score']:.2f}")
print(f"Last month: {last_month['sentiment_analysis']['average_score']:.2f}")

# Compare topics
extractor = TopicExtractor()
comparison = extractor.compare_topic_sets(
    last_month['topics'],
    this_month['topics']
)
print(f"New issues: {comparison['new_topics']}")
```

---

## 🔧 Customization

### **Adjust Classification Categories**

Edit `ai/text_classifier.py`:
```python
QUERY_CATEGORIES = {
    'your_custom_category': 'Description here',
    # Add more categories...
}
```

### **Change Priority Thresholds**

Edit `feedback_analyzer.py`:
```python
def _is_alert(self, sentiment, classification):
    if sentiment['score'] < -0.8:  # Adjust threshold
        return True
    # Add custom logic...
```

### **Modify Report Format**

Edit `analysis_report_generator.py` to customize report sections.

---

## 💰 Cost Estimates

**Per Analysis** (20 feedback messages):
- Sentiment: 20 × 200 tokens = 4,000 tokens ≈ $0.002
- Classification: 20 × 150 tokens = 3,000 tokens ≈ $0.0015
- Topics: 1 × 800 tokens = 800 tokens ≈ $0.0004
- **Total: ~$0.004 per 20 messages**

**Monthly** (500 students, 2 feedback each = 1,000 messages):
- 1,000 messages ÷ 20 × $0.004 = **$0.20/month**
- Very affordable!

---

## 🐛 Troubleshooting

### **Error: "API key not found"**
- Verify `.env` file exists with `OPENAI_API_KEY=sk-...`
- Run Step 1 setup again

### **Warning: "JSON decode error"**
- OpenAI occasionally returns malformed JSON
- The system handles this gracefully with fallbacks
- Not critical - analysis continues

### **Slow Performance**
- Batch analysis is sequential (one at a time)
- For 100+ messages, expect 2-3 minutes
- Consider implementing async processing for production

### **Empty Topics List**
- Need at least 5-10 messages for meaningful topics
- Ensure feedback has varied content

---

## ✅ Success Criteria

Step 5 is complete when:
1. ✅ Sentiment analyzer detects positive/negative/neutral
2. ✅ Classifier categorizes messages correctly
3. ✅ Topic extractor identifies themes
4. ✅ Alerts generated for at-risk students
5. ✅ Reports saved to outputs folder
6. ✅ All test files run without errors

---

## 🎓 What You Learned

- ✅ **Sentiment Analysis**: Detecting emotions in text
- ✅ **Text Classification**: Automatic categorization
- ✅ **Topic Modeling**: Theme extraction without labels
- ✅ **Alert Systems**: Building early warning mechanisms
- ✅ **Report Generation**: Converting data to insights
- ✅ **Prompt Engineering for NLP**: Specialized analysis prompts

---

## 🚀 Next Steps: Integration

**Combine with Step 3 (AI Advisor):**
```python
# Analyze conversations from AI advisor
from ai.student_advisor import AIStudentAdvisor
from ai.feedback_analyzer import FeedbackAnalyzer

advisor = AIStudentAdvisor()
# ... conversations happen ...

# Analyze conversation sentiment
feedback_data = [
    {'student_id': 1, 'text': msg, 'course': 'Chat'}
    for msg in conversation_history
]
analyzer = FeedbackAnalyzer()
results = analyzer.analyze_feedback(feedback_data)
```

**Combine with Step 4 (Recommendations):**
```python
# Analyze feedback on recommended courses
# "Students who took ML reported 85% positive sentiment"
```

---

**Ready for Step 6: REST API Backend!** 🚀

Turn all your AI features into web services that can be accessed from any frontend application!
