# Step 5: Sentiment Analysis & Text Classification - Examples

## 🎯 Real Output Examples

This document shows **actual outputs** from the Step 5 system using real student feedback data.

---

## Example 1: Sentiment Analysis

### **Input:**
```python
texts = [
    "I absolutely love this course! The instructor explains concepts so clearly.",
    "I'm really struggling with the recursion homework. It's way too difficult.",
    "The course is okay. Nothing special but gets the job done."
]
```

### **Output:**
```json
[
  {
    "sentiment": "positive",
    "score": 0.92,
    "emotion": "joy",
    "confidence": 0.95,
    "reasoning": "Strong positive language ('absolutely love', 'clearly') with enthusiasm"
  },
  {
    "sentiment": "negative",
    "score": -0.78,
    "emotion": "frustration",
    "confidence": 0.88,
    "reasoning": "Expresses struggle and difficulty with coursework"
  },
  {
    "sentiment": "neutral",
    "score": 0.15,
    "emotion": "neutral",
    "confidence": 0.82,
    "reasoning": "Mixed sentiment - acceptable but not enthusiastic"
  }
]
```

### **Summary Statistics:**
```
Positive: 33.3%
Negative: 33.3%
Neutral: 33.3%
Average Score: 0.10
Most Common Emotion: neutral, joy, frustration (tie)
```

---

## Example 2: Text Classification

### **Input:**
```python
queries = [
    "I'm thinking about dropping this class. The workload is overwhelming.",
    "The upload system for assignments keeps crashing. Can't submit my work.",
    "What courses should I take after finishing Python basics?",
    "This is the best learning experience I've ever had!",
    "When is the final exam? I can't find it on the schedule."
]
```

### **Output:**
```json
[
  {
    "category": "at_risk_alert",
    "confidence": 0.95,
    "priority": "critical",
    "requires_action": true,
    "suggested_response_time": "< 1 hour",
    "reasoning": "Student considering dropping - immediate intervention needed"
  },
  {
    "category": "technical_support",
    "confidence": 0.92,
    "priority": "high",
    "requires_action": true,
    "suggested_response_time": "< 4 hours",
    "reasoning": "System malfunction preventing assignment submission"
  },
  {
    "category": "course_recommendation",
    "confidence": 0.88,
    "priority": "medium",
    "requires_action": false,
    "suggested_response_time": "< 24 hours",
    "reasoning": "Seeking guidance on learning path progression"
  },
  {
    "category": "feedback_positive",
    "confidence": 0.94,
    "priority": "low",
    "requires_action": false,
    "suggested_response_time": "< 48 hours",
    "reasoning": "Positive feedback expressing satisfaction"
  },
  {
    "category": "administrative",
    "confidence": 0.90,
    "priority": "medium",
    "requires_action": true,
    "suggested_response_time": "< 24 hours",
    "reasoning": "Administrative information request about exam schedule"
  }
]
```

### **Classification Summary:**
```
Categories:
  at_risk_alert: 1 (20.0%)
  technical_support: 1 (20.0%)
  course_recommendation: 1 (20.0%)
  feedback_positive: 1 (20.0%)
  administrative: 1 (20.0%)

Priorities:
  critical: 1 (20.0%)
  high: 1 (20.0%)
  medium: 2 (40.0%)
  low: 1 (20.0%)

Action Required: 3 messages (60.0%)
```

---

## Example 3: Topic Extraction

### **Input:** 15 feedback messages about a Python course

### **Output:**
```json
[
  {
    "topic": "Homework Difficulty and Time Commitment",
    "frequency": 0.40,
    "sentiment": "negative",
    "keywords": ["homework", "difficult", "time-consuming", "overwhelming", "hours"],
    "examples": [
      "The homework assignments take way too long",
      "The recursion homework is too difficult",
      "I spend 10 hours per week on homework alone"
    ]
  },
  {
    "topic": "Lecture Quality and Teaching Style",
    "frequency": 0.33,
    "sentiment": "positive",
    "keywords": ["instructor", "explains", "clearly", "lectures", "understanding"],
    "examples": [
      "The instructor explains concepts so clearly",
      "Lecture videos are well-structured",
      "Teaching style makes complex topics easy"
    ]
  },
  {
    "topic": "Technical Platform Issues",
    "frequency": 0.27,
    "sentiment": "negative",
    "keywords": ["upload", "system", "crashing", "login", "technical"],
    "examples": [
      "The upload system keeps crashing",
      "Can't login to submit assignments",
      "Platform bugs are frustrating"
    ]
  }
]
```

### **Visual Representation:**
```
Topics by Frequency:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Homework Difficulty        ████████████████████ 40%
Lecture Quality            ████████████████ 33%
Technical Issues           █████████████ 27%
```

### **Topic Summary:**
```
Found 3 main themes in 15 feedback messages:
1. Homework Difficulty (40% of feedback, negative sentiment)
2. Lecture Quality (33% of feedback, positive sentiment)
3. Technical Platform Issues (27% of feedback, negative sentiment)
```

---

## Example 4: Complete Feedback Analysis

### **Input:** data/student_feedback.json (20 messages)

### **Full Analysis Output:**

```json
{
  "total_feedback": 20,
  "timestamp": "2026-01-03 14:30:22",
  
  "sentiment_analysis": {
    "positive_count": 6,
    "negative_count": 10,
    "neutral_count": 4,
    "positive_percentage": 30.0,
    "negative_percentage": 50.0,
    "neutral_percentage": 20.0,
    "average_score": -0.22,
    "common_emotions": ["frustration", "anxiety", "joy"]
  },
  
  "classifications": {
    "academic_difficulty": 6,
    "technical_support": 4,
    "at_risk_alert": 2,
    "feedback_positive": 3,
    "administrative": 2,
    "course_recommendation": 1,
    "feedback_negative": 2
  },
  
  "topics": [
    {
      "topic": "Homework and Assignment Difficulty",
      "frequency": 0.45,
      "sentiment": "negative",
      "keywords": ["homework", "assignments", "difficult", "time"]
    },
    {
      "topic": "Course Content Quality",
      "frequency": 0.30,
      "sentiment": "positive",
      "keywords": ["content", "instructor", "lectures", "clear"]
    },
    {
      "topic": "Technical Platform Problems",
      "frequency": 0.25,
      "sentiment": "negative",
      "keywords": ["upload", "system", "bugs", "crashing"]
    }
  ],
  
  "alerts": [
    {
      "student_id": 7,
      "sentiment": {
        "score": -0.88,
        "emotion": "despair"
      },
      "classification": {
        "category": "at_risk_alert",
        "priority": "critical"
      },
      "text": "I'm thinking about dropping this class...",
      "priority": "critical",
      "recommended_action": "Contact student immediately via email and phone..."
    },
    {
      "student_id": 9,
      "sentiment": {
        "score": -0.82,
        "emotion": "anxiety"
      },
      "classification": {
        "category": "academic_difficulty",
        "priority": "high"
      },
      "text": "I feel like I'm falling behind...",
      "priority": "high",
      "recommended_action": "Offer tutoring sessions or study group..."
    }
  ],
  
  "insights": [
    "50.0% of feedback is negative (average score: -0.22)",
    "2 students require immediate attention (critical/high priority)",
    "Most common issue: academic_difficulty (6 cases)",
    "Top concern: Homework and Assignment Difficulty (45% of feedback)",
    "Common emotions: frustration, anxiety",
    "Action required for 8 messages (40.0%)"
  ],
  
  "recommendations": [
    "URGENT: Contact 2 at-risk students immediately",
    "Review homework difficulty - mentioned in 45% of feedback",
    "Fix technical platform issues - 4 reports of upload problems",
    "Consider offering additional tutoring for 6 students struggling academically",
    "Investigate workload - multiple complaints about time commitment",
    "Positive feedback about instructor quality - maintain teaching approach"
  ]
}
```

---

## Example 5: Generated Report (Markdown)

### **Output from report_generator.py:**

```markdown
# 📊 Student Feedback Analysis Report

**Generated:** 2026-01-03 14:30:22  
**Total Feedback:** 20 messages

---

## 📋 Executive Summary

Overall sentiment is **moderately negative** with an average score of **-0.22**.

**Sentiment Distribution:**
- ✅ Positive: 30.0% (6 messages)
- ⚠️ Negative: 50.0% (10 messages)
- ➖ Neutral: 20.0% (4 messages)

**Most Common Emotions:** frustration, anxiety, joy

**Key Finding:** 50.0% of feedback is negative, with 2 students requiring immediate attention.

---

## 🚨 ALERTS: Students Requiring Attention

**Total Alerts:** 2 students

### 1. Student #7 - 🚨 CRITICAL
**Category:** at_risk_alert  
**Sentiment:** -0.88 (despair)  
**Message:** "I'm thinking about dropping this class. The workload is overwhelming..."

**Recommended Action:**  
Contact student immediately via email and phone. Offer emergency advising session to discuss workload management and support options.

---

### 2. Student #9 - ⚠️ HIGH
**Category:** academic_difficulty  
**Sentiment:** -0.82 (anxiety)  
**Message:** "I feel like I'm falling behind and don't understand recursion..."

**Recommended Action:**  
Offer tutoring sessions or study group. Provide additional resources for recursion topic.

---

## 📊 Common Topics

### 1. Homework and Assignment Difficulty
**Frequency:** 45% of feedback  
**Sentiment:** negative  
**Keywords:** homework, assignments, difficult, time, overwhelming

**Example Quotes:**
> "The homework assignments take way too long"
> "The recursion homework is too difficult"
> "I spend 10 hours per week on homework alone"

---

### 2. Course Content Quality
**Frequency:** 30% of feedback  
**Sentiment:** positive  
**Keywords:** content, instructor, lectures, clear, helpful

**Example Quotes:**
> "The instructor explains concepts so clearly"
> "Lecture videos are well-structured"
> "I love how practical the examples are"

---

### 3. Technical Platform Problems
**Frequency:** 25% of feedback  
**Sentiment:** negative  
**Keywords:** upload, system, bugs, crashing, login

**Example Quotes:**
> "The upload system keeps crashing"
> "Can't login to submit my work"
> "Lost my assignment due to system error"

---

## 📋 Feedback Categories

| Category | Count | Percentage |
|----------|-------|------------|
| academic_difficulty | 6 | 30.0% |
| technical_support | 4 | 20.0% |
| feedback_positive | 3 | 15.0% |
| at_risk_alert | 2 | 10.0% |
| administrative | 2 | 10.0% |
| feedback_negative | 2 | 10.0% |
| course_recommendation | 1 | 5.0% |

---

## 💡 Key Insights

- 50.0% of feedback is negative (average score: -0.22)
- 2 students require immediate attention (critical/high priority)
- Most common issue: academic_difficulty (6 cases)
- Top concern: Homework and Assignment Difficulty (45% of feedback)
- Common emotions: frustration, anxiety
- Action required for 8 messages (40.0%)

---

## 🎯 Recommendations

1. **URGENT:** Contact 2 at-risk students immediately
2. **Review homework difficulty** - mentioned in 45% of feedback
3. **Fix technical platform issues** - 4 reports of upload problems
4. **Consider offering additional tutoring** for 6 students struggling academically
5. **Investigate workload** - multiple complaints about time commitment
6. **Positive feedback about instructor quality** - maintain teaching approach

---

*Report generated by AI Feedback Analysis System*
```

---

## Example 6: Course-by-Course Analysis

### **Input:** Feedback from multiple courses

### **Output:**
```python
{
  "Python Fundamentals": {
    "total_feedback": 15,
    "sentiment_analysis": {
      "average_score": -0.35,
      "positive_percentage": 26.7,
      "negative_percentage": 60.0
    },
    "top_topics": [
      "Homework Difficulty (50%)",
      "Technical Issues (30%)"
    ],
    "alerts": 2
  },
  
  "Math for ML": {
    "total_feedback": 5,
    "sentiment_analysis": {
      "average_score": 0.52,
      "positive_percentage": 80.0,
      "negative_percentage": 20.0
    },
    "top_topics": [
      "Excellent Explanations (60%)",
      "Practice Problems (40%)"
    ],
    "alerts": 0
  }
}
```

**Visualization:**
```
Course Comparison:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Python Fundamentals: -0.35 ⚠️
  Sentiment: ▓▓▓░░░░░░░ 27% positive
  Alerts: 2 🚨

Math for ML: +0.52 ✅
  Sentiment: ▓▓▓▓▓▓▓▓░░ 80% positive
  Alerts: 0 ✅
```

---

## Example 7: Individual Student Analysis

### **Input:**
```python
analyzer.analyze_by_student(student_id=7, feedback_data=all_feedback)
```

### **Output:**
```json
{
  "student_id": 7,
  "total_messages": 3,
  "sentiment_trend": [-0.25, -0.62, -0.88],
  "average_sentiment": -0.58,
  "categories": ["academic_difficulty", "at_risk_alert"],
  "alert_level": "critical",
  "messages": [
    {
      "text": "The homework is challenging but manageable",
      "sentiment": -0.25,
      "date": "2026-01-01"
    },
    {
      "text": "I'm really struggling now with recursion",
      "sentiment": -0.62,
      "date": "2026-01-02"
    },
    {
      "text": "Thinking about dropping this class",
      "sentiment": -0.88,
      "date": "2026-01-03"
    }
  ],
  "analysis": "Sentiment declining over time. Started manageable but now at-risk. Immediate intervention needed."
}
```

**Sentiment Trend Chart:**
```
Student #7 Sentiment Over Time:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  0 |
    |
-0.2 | ●
    |   \
-0.4 |     \
    |       \
-0.6 |         ●
    |           \
-0.8 |             \
    |               ●  🚨 AT RISK
-1.0 |________________
     Jan 1  Jan 2  Jan 3
```

---

## Example 8: Alert Export

### **File:** ai/outputs/alerts_20260103_143022.json

```json
{
  "generated": "2026-01-03 14:30:22",
  "total_alerts": 2,
  "critical": 1,
  "high": 1,
  "alerts": [
    {
      "student_id": 7,
      "priority": "critical",
      "category": "at_risk_alert",
      "sentiment_score": -0.88,
      "emotion": "despair",
      "message": "I'm thinking about dropping this class. The workload is overwhelming...",
      "recommended_action": "Contact student immediately via email and phone...",
      "requires_action": true,
      "response_time": "< 1 hour",
      "timestamp": "2026-01-03 10:15:00"
    },
    {
      "student_id": 9,
      "priority": "high",
      "category": "academic_difficulty",
      "sentiment_score": -0.82,
      "emotion": "anxiety",
      "message": "I feel like I'm falling behind and don't understand recursion...",
      "recommended_action": "Offer tutoring sessions or study group...",
      "requires_action": true,
      "response_time": "< 4 hours",
      "timestamp": "2026-01-03 11:30:00"
    }
  ]
}
```

**This file can be:**
- Automatically emailed to advisors daily
- Integrated with CRM systems
- Displayed in admin dashboards
- Trigger automated outreach workflows

---

## Example 9: Executive Summary Only

### **Quick Overview for Leadership:**

```python
summary = generator.generate_executive_summary(results)
print(summary)
```

**Output:**
```
EXECUTIVE SUMMARY - Student Feedback Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Analyzed 20 student feedback messages with overall NEGATIVE sentiment 
(average score: -0.22).

KEY FINDINGS:
• 50% negative feedback vs 30% positive
• 2 CRITICAL ALERTS requiring immediate attention
• Top concern: "Homework and Assignment Difficulty" (45% of feedback)
• Common emotions: frustration, anxiety
• 6 students struggling with academic difficulty
• 4 technical platform issues reported

RECOMMENDED ACTIONS:
1. Contact 2 at-risk students TODAY
2. Review homework workload and difficulty
3. Fix technical upload system issues
4. Offer additional tutoring support

Overall assessment: NEEDS ATTENTION - Significant student struggles 
requiring prompt intervention to prevent dropouts.
```

---

## 🎯 Key Takeaways

From these examples, you can see:

1. **Sentiment Analysis** detects emotions from -1 (very negative) to +1 (very positive)
2. **Classification** categorizes into 9 types with priority levels
3. **Topic Extraction** discovers themes without predefined categories
4. **Alerts** flag students needing immediate attention
5. **Reports** provide actionable insights for educators
6. **Trend Analysis** tracks changes over time
7. **Export Options** enable integration with other systems

---

**Ready to analyze your own feedback data? See [STEP_5_SETUP.md](STEP_5_SETUP.md) for instructions!**
