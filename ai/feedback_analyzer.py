"""
Feedback Analyzer - Step 5
Main orchestration for comprehensive feedback analysis
Combines sentiment analysis, classification, and topic extraction
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from ai.sentiment_analyzer import SentimentAnalyzer
from ai.text_classifier import TextClassifier
from ai.topic_extractor import TopicExtractor


class FeedbackAnalyzer:
    """
    Comprehensive feedback analysis system
    Combines sentiment, classification, and topic analysis
    """
    
    def __init__(self):
        """Initialize all analysis components"""
        print("Initializing Feedback Analyzer...")
        self.sentiment_analyzer = SentimentAnalyzer()
        self.classifier = TextClassifier()
        self.topic_extractor = TopicExtractor()
        
        # Setup output directory
        self.output_dir = Path(__file__).parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        print("✓ Feedback Analyzer ready!")
    
    def analyze_feedback(self, feedback_data: List[Dict]) -> Dict:
        """
        Comprehensive analysis of student feedback
        
        Args:
            feedback_data: List of dicts with:
                - student_id: int
                - text: str (feedback message)
                - course: str (optional)
                - timestamp: str (optional)
                - metadata: dict (optional)
        
        Returns:
            Complete analysis report with all insights
        """
        if not feedback_data:
            return {
                'total_feedback': 0,
                'error': 'No feedback data provided'
            }
        
        print(f"\nAnalyzing {len(feedback_data)} feedback messages...")
        print("=" * 60)
        
        results = {
            'total_feedback': len(feedback_data),
            'analysis_timestamp': datetime.now().isoformat(),
            'sentiment_analysis': None,
            'classifications': None,
            'topics': None,
            'alerts': [],
            'insights': [],
            'recommendations': []
        }
        
        # Extract texts
        texts = [fb['text'] for fb in feedback_data if 'text' in fb]
        
        if not texts:
            results['error'] = 'No text found in feedback data'
            return results
        
        # 1. Sentiment Analysis
        print("\n1. Running Sentiment Analysis...")
        sentiment_results = self.sentiment_analyzer.analyze_batch(texts, include_text=False)
        results['sentiment_analysis'] = self.sentiment_analyzer.get_sentiment_summary(sentiment_results)
        results['sentiment_details'] = sentiment_results
        
        # 2. Classification
        print("\n2. Running Text Classification...")
        classification_results = self.classifier.classify_batch(texts, include_text=False)
        classif_summary = self.classifier.get_classification_summary(classification_results)
        results['classifications'] = {
            'summary': classif_summary,
            'details': classification_results,
            'high_priority': self.classifier.get_action_items(classification_results)
        }
        
        # 3. Topic Extraction
        print("\n3. Extracting Topics...")
        topics = self.topic_extractor.extract_topics(texts, max_topics=5)
        results['topics'] = topics
        
        # 4. Identify Alerts
        print("\n4. Identifying Alerts...")
        for i, (fb, sent, classif) in enumerate(
            zip(feedback_data, sentiment_results, classification_results)
        ):
            if self._is_alert(sent, classif):
                alert = {
                    'alert_id': i + 1,
                    'student_id': fb.get('student_id'),
                    'course': fb.get('course', 'Unknown'),
                    'text': fb['text'],
                    'sentiment': sent,
                    'classification': classif,
                    'priority': classif['priority'],
                    'recommended_action': self._get_recommended_action(sent, classif)
                }
                results['alerts'].append(alert)
        
        # Sort alerts by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        results['alerts'].sort(
            key=lambda x: priority_order.get(x['priority'], 3)
        )
        
        # 5. Generate Insights
        print("\n5. Generating Insights...")
        results['insights'] = self._generate_insights(results)
        
        # 6. Generate Recommendations
        print("\n6. Generating Recommendations...")
        results['recommendations'] = self._generate_recommendations(results)
        
        print("\n" + "=" * 60)
        print(f"✓ Analysis complete!")
        print(f"  - Sentiments: {results['sentiment_analysis']['positive_percentage']:.1f}% positive")
        print(f"  - Alerts: {len(results['alerts'])} students need attention")
        print(f"  - Topics: {len(results['topics'])} themes identified")
        
        return results
    
    def _is_alert(self, sentiment: Dict, classification: Dict) -> bool:
        """Determine if feedback requires an alert"""
        # Alert conditions:
        # 1. Highly negative sentiment
        if sentiment.get('score', 0) < -0.7:
            return True
        
        # 2. At-risk category
        if classification.get('category') == 'at_risk_alert':
            return True
        
        # 3. Critical or high priority with action required
        if classification.get('priority') in ['critical', 'high'] and classification.get('requires_action'):
            return True
        
        # 4. Severe frustration or anxiety
        if sentiment.get('emotion') in ['anxiety', 'anger', 'despair']:
            return True
        
        return False
    
    def _get_recommended_action(self, sentiment: Dict, classification: Dict) -> str:
        """Suggest appropriate action for alert"""
        category = classification.get('category', '')
        priority = classification.get('priority', 'low')
        score = sentiment.get('score', 0)
        
        if category == 'at_risk_alert' or priority == 'critical':
            return "⚠️ URGENT: Contact student immediately via email/phone. Schedule emergency advisor meeting within 24 hours."
        
        elif category == 'academic_difficulty' and score < -0.6:
            return "📚 HIGH PRIORITY: Reach out within 24-48 hours. Offer tutoring resources and academic support. Schedule check-in meeting."
        
        elif category == 'academic_difficulty':
            return "📖 Offer tutoring resources and study groups. Check in within 3-5 days to monitor progress."
        
        elif category == 'technical_support':
            return "🔧 Forward to technical support team. Ensure issue is resolved within 24 hours."
        
        elif category == 'administrative':
            return "📋 Respond with requested information within 24-48 hours."
        
        elif score < -0.8:
            return "⚡ Very negative sentiment detected. Priority follow-up needed within 24 hours to address concerns."
        
        else:
            return "📌 Standard follow-up. Respond within 48 hours."
    
    def _generate_insights(self, results: Dict) -> List[str]:
        """Generate key insights from analysis"""
        insights = []
        
        # Sentiment insights
        sent = results.get('sentiment_analysis', {})
        if sent:
            avg_score = sent.get('average_score', 0)
            pos_pct = sent.get('positive_percentage', 0)
            neg_pct = sent.get('negative_percentage', 0)
            
            if avg_score > 0.5:
                insights.append(f"✅ Overall sentiment is very positive ({pos_pct:.1f}% positive feedback)")
            elif avg_score > 0.2:
                insights.append(f"👍 Sentiment is generally positive ({pos_pct:.1f}% positive)")
            elif avg_score < -0.3:
                insights.append(f"⚠️ Overall sentiment is negative ({neg_pct:.1f}% negative feedback) - immediate attention needed")
            else:
                insights.append(f"➖ Sentiment is mixed or neutral")
            
            # Emotion insights
            emotions = sent.get('common_emotions', {})
            if emotions:
                top_emotion = list(emotions.items())[0]
                insights.append(f"😊 Most common emotion: {top_emotion[0]} ({top_emotion[1]} occurrences)")
        
        # Classification insights
        classif = results.get('classifications', {})
        if classif:
            summary = classif.get('summary', {})
            by_category = summary.get('by_category', {})
            
            if by_category:
                top_category = list(by_category.items())[0]
                insights.append(f"📊 Most common category: {top_category[0]} ({top_category[1]} messages)")
            
            action_count = summary.get('requires_action_count', 0)
            if action_count > 0:
                insights.append(f"🎯 {action_count} messages require follow-up action")
        
        # Alert insights
        alert_count = len(results.get('alerts', []))
        if alert_count > 0:
            critical = sum(1 for a in results['alerts'] if a['priority'] == 'critical')
            if critical > 0:
                insights.append(f"🚨 CRITICAL: {critical} students show signs of severe distress or dropping out")
            insights.append(f"⚠️ {alert_count} total students need attention")
        else:
            insights.append(f"✅ No critical alerts - all students appear to be managing well")
        
        # Topic insights
        topics = results.get('topics', [])
        if topics:
            negative_topics = [t for t in topics if t.get('sentiment') == 'negative']
            if negative_topics:
                insights.append(f"📉 Topics with negative sentiment: {', '.join([t['topic'] for t in negative_topics[:3]])}")
        
        return insights
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on alerts
        alert_count = len(results.get('alerts', []))
        if alert_count > 5:
            recommendations.append("🎯 High alert volume detected. Consider creating a systematic intervention plan.")
        
        # Based on sentiment
        sent = results.get('sentiment_analysis', {})
        if sent and sent.get('negative_percentage', 0) > 30:
            recommendations.append("📊 Over 30% negative feedback. Schedule course review meeting to address concerns.")
        
        # Based on topics
        topics = results.get('topics', [])
        for topic in topics[:3]:
            if topic.get('sentiment') == 'negative' and topic.get('frequency', 0) > 0.2:
                recommendations.append(f"🔧 '{topic['topic']}' is a major concern ({topic['frequency']*100:.0f}% of feedback). Prioritize addressing this.")
        
        # Based on classifications
        classif = results.get('classifications', {})
        if classif:
            summary = classif.get('summary', {})
            by_cat = summary.get('by_category', {})
            
            if by_cat.get('academic_difficulty', 0) > len(results['total_feedback']) * 0.3:
                recommendations.append("📚 Many students report academic difficulty. Consider adjusting pace or providing additional resources.")
            
            if by_cat.get('technical_support', 0) > 5:
                recommendations.append("🔧 Multiple technical issues reported. Conduct system review and user training.")
        
        if not recommendations:
            recommendations.append("✅ No major issues identified. Continue current approach and monitor feedback regularly.")
        
        return recommendations
    
    def analyze_by_course(self, feedback_data: List[Dict]) -> Dict:
        """
        Group analysis by course
        
        Returns:
            Dict mapping course names to analysis results
        """
        courses = {}
        for fb in feedback_data:
            course = fb.get('course', 'Unknown')
            if course not in courses:
                courses[course] = []
            courses[course].append(fb)
        
        print(f"\nAnalyzing feedback for {len(courses)} courses...")
        
        course_analyses = {}
        for course, course_feedback in courses.items():
            print(f"\n--- Analyzing {course} ({len(course_feedback)} messages) ---")
            course_analyses[course] = self.analyze_feedback(course_feedback)
        
        return course_analyses
    
    def analyze_by_student(self, student_id: int, feedback_data: List[Dict]) -> Dict:
        """
        Analyze all feedback from specific student
        
        Args:
            student_id: Student ID to analyze
            feedback_data: All feedback data
        
        Returns:
            Analysis results for that student
        """
        student_feedback = [
            fb for fb in feedback_data 
            if fb.get('student_id') == student_id
        ]
        
        if not student_feedback:
            return {
                'error': f'No feedback found for student {student_id}',
                'total_feedback': 0
            }
        
        print(f"\nAnalyzing feedback for student {student_id} ({len(student_feedback)} messages)...")
        return self.analyze_feedback(student_feedback)
    
    def save_analysis(self, analysis_results: Dict, filename: str = None) -> str:
        """
        Save analysis results to JSON file
        
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"feedback_analysis_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Analysis saved to: {filepath}")
        return str(filepath)
    
    def export_alerts(self, analysis_results: Dict, filename: str = None) -> str:
        """
        Export alerts to separate JSON file for quick access
        
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alerts_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        alerts = analysis_results.get('alerts', [])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(alerts, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Alerts exported to: {filepath}")
        return str(filepath)


if __name__ == "__main__":
    """Test the feedback analyzer"""
    print("=" * 60)
    print("Testing Feedback Analyzer")
    print("=" * 60)
    
    # Sample feedback data
    sample_feedback = [
        {
            'student_id': 1,
            'text': 'I love this course! The instructor explains everything so clearly.',
            'course': 'Python',
            'timestamp': '2026-01-03'
        },
        {
            'student_id': 2,
            'text': "I'm really struggling with recursion. It's way too hard and I don't understand it.",
            'course': 'Python',
            'timestamp': '2026-01-03'
        },
        {
            'student_id': 3,
            'text': "I'm thinking about dropping this class. Too much stress and I can't keep up.",
            'course': 'Python',
            'timestamp': '2026-01-03'
        },
        {
            'student_id': 4,
            'text': 'The homework assignments are helpful but take a lot of time.',
            'course': 'Python',
            'timestamp': '2026-01-03'
        },
        {
            'student_id': 5,
            'text': 'When is the final exam? I need to know so I can prepare.',
            'course': 'Python',
            'timestamp': '2026-01-03'
        }
    ]
    
    try:
        analyzer = FeedbackAnalyzer()
        
        print("\n1. Testing Comprehensive Analysis:")
        print("=" * 60)
        results = analyzer.analyze_feedback(sample_feedback)
        
        print("\n2. Analysis Results:")
        print("-" * 60)
        print(f"Total Feedback: {results['total_feedback']}")
        print(f"\nSentiment Summary:")
        sent = results['sentiment_analysis']
        print(f"  - Positive: {sent['positive_percentage']:.1f}%")
        print(f"  - Negative: {sent['negative_percentage']:.1f}%")
        print(f"  - Average Score: {sent['average_score']:.2f}")
        
        print(f"\nAlerts: {len(results['alerts'])}")
        for alert in results['alerts']:
            print(f"  - Student {alert['student_id']}: {alert['priority'].upper()}")
        
        print(f"\nTopics: {len(results['topics'])}")
        for topic in results['topics']:
            print(f"  - {topic['topic']} ({topic['frequency']*100:.0f}%)")
        
        print(f"\nInsights:")
        for insight in results['insights']:
            print(f"  {insight}")
        
        print(f"\nRecommendations:")
        for rec in results['recommendations']:
            print(f"  {rec}")
        
        print("\n3. Testing Save Functionality:")
        print("-" * 60)
        filepath = analyzer.save_analysis(results)
        print(f"Saved to: {filepath}")
        
        if results['alerts']:
            alert_path = analyzer.export_alerts(results)
            print(f"Alerts saved to: {alert_path}")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
