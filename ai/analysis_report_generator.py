"""
Analysis Report Generator - Step 5
Generates human-readable reports from feedback analysis results
"""

from typing import Dict, List
from datetime import datetime
from pathlib import Path


class AnalysisReportGenerator:
    """Generate comprehensive analysis reports in various formats"""
    
    def __init__(self):
        """Initialize report generator"""
        self.output_dir = Path(__file__).parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_report(self, analysis_results: Dict, format: str = 'markdown') -> str:
        """
        Generate comprehensive report from analysis results
        
        Args:
            analysis_results: Results from FeedbackAnalyzer
            format: 'markdown' or 'text'
        
        Returns:
            Formatted report string
        """
        if format == 'markdown':
            return self._generate_markdown_report(analysis_results)
        else:
            return self._generate_text_report(analysis_results)
    
    def _generate_markdown_report(self, results: Dict) -> str:
        """Generate markdown-formatted report"""
        report = []
        
        # Header
        report.append("# 📊 Student Feedback Analysis Report")
        report.append("")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Total Feedback Analyzed:** {results.get('total_feedback', 0)}")
        report.append("")
        report.append("---")
        report.append("")
        
        # Executive Summary
        report.append("## 📋 Executive Summary")
        report.append("")
        
        sent = results.get('sentiment_analysis', {})
        if sent:
            overall = sent.get('overall_sentiment', 'neutral').upper()
            avg_score = sent.get('average_score', 0)
            
            report.append(f"**Overall Sentiment:** {overall} (score: {avg_score:.2f})")
            report.append("")
            report.append(f"- ✅ Positive: {sent.get('positive_percentage', 0):.1f}% ({sent.get('positive_count', 0)} messages)")
            report.append(f"- ⚠️ Negative: {sent.get('negative_percentage', 0):.1f}% ({sent.get('negative_count', 0)} messages)")
            report.append(f"- ➖ Neutral: {sent.get('neutral_percentage', 0):.1f}% ({sent.get('neutral_count', 0)} messages)")
            report.append("")
            
            # Common emotions
            emotions = sent.get('common_emotions', {})
            if emotions:
                report.append("**Common Emotions:**")
                for emotion, count in list(emotions.items())[:5]:
                    report.append(f"- {emotion}: {count} occurrences")
                report.append("")
        
        # Alerts Section
        alerts = results.get('alerts', [])
        if alerts:
            report.append("---")
            report.append("")
            report.append(f"## ⚠️ ALERTS ({len(alerts)} Students Need Attention)")
            report.append("")
            report.append("These students require immediate follow-up:")
            report.append("")
            
            for i, alert in enumerate(alerts[:10], 1):  # Show top 10
                priority = alert.get('priority', 'low').upper()
                priority_emoji = {'CRITICAL': '🚨', 'HIGH': '⚠️', 'MEDIUM': '📌', 'LOW': '📋'}.get(priority, '📋')
                
                report.append(f"### {priority_emoji} Alert #{i}: Student ID {alert.get('student_id')}")
                report.append("")
                report.append(f"**Priority:** {priority}")
                report.append(f"**Course:** {alert.get('course', 'Unknown')}")
                report.append("")
                report.append(f"**Message:**")
                report.append(f"> {alert.get('text', 'N/A')[:200]}...")
                report.append("")
                report.append(f"**Sentiment:** {alert.get('sentiment', {}).get('sentiment', 'unknown')} (score: {alert.get('sentiment', {}).get('score', 0):.2f})")
                report.append(f"**Emotion:** {alert.get('sentiment', {}).get('emotion', 'unknown')}")
                report.append(f"**Category:** {alert.get('classification', {}).get('category', 'unknown')}")
                report.append("")
                report.append(f"**Recommended Action:**")
                report.append(f"{alert.get('recommended_action', 'Follow up as needed')}")
                report.append("")
        
        # Topics Section
        topics = results.get('topics', [])
        if topics:
            report.append("---")
            report.append("")
            report.append("## 📌 Common Topics & Themes")
            report.append("")
            report.append("Main topics identified in feedback:")
            report.append("")
            
            for i, topic in enumerate(topics, 1):
                sentiment_emoji = {'positive': '😊', 'negative': '😟', 'neutral': '😐'}.get(topic.get('sentiment'), '😐')
                
                report.append(f"### {i}. {sentiment_emoji} {topic.get('topic', 'Unknown Topic')}")
                report.append("")
                report.append(f"**Frequency:** {topic.get('frequency', 0)*100:.1f}% of feedback")
                report.append(f"**Sentiment:** {topic.get('sentiment', 'neutral')}")
                report.append(f"**Keywords:** {', '.join(topic.get('keywords', [])[:8])}")
                report.append("")
                
                examples = topic.get('examples', [])
                if examples:
                    report.append("**Example Quotes:**")
                    for ex in examples[:2]:
                        report.append(f"- \"{ex[:150]}...\"")
                    report.append("")
        
        # Classification Summary
        classif = results.get('classifications', {})
        if classif:
            summary = classif.get('summary', {})
            by_category = summary.get('by_category', {})
            
            if by_category:
                report.append("---")
                report.append("")
                report.append("## 📊 Feedback Categories")
                report.append("")
                report.append("| Category | Count | Percentage |")
                report.append("|----------|-------|------------|")
                
                total = summary.get('total_count', 1)
                for category, count in by_category.items():
                    pct = (count / total * 100) if total > 0 else 0
                    report.append(f"| {category} | {count} | {pct:.1f}% |")
                report.append("")
        
        # Key Insights
        insights = results.get('insights', [])
        if insights:
            report.append("---")
            report.append("")
            report.append("## 💡 Key Insights")
            report.append("")
            for insight in insights:
                report.append(f"- {insight}")
            report.append("")
        
        # Recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            report.append("---")
            report.append("")
            report.append("## 🎯 Recommendations")
            report.append("")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        # Footer
        report.append("---")
        report.append("")
        report.append("*Report generated by AI-powered Feedback Analysis System*")
        
        return "\n".join(report)
    
    def _generate_text_report(self, results: Dict) -> str:
        """Generate plain text report"""
        report = []
        
        # Header
        report.append("=" * 70)
        report.append("STUDENT FEEDBACK ANALYSIS REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Feedback: {results.get('total_feedback', 0)}")
        report.append("")
        
        # Sentiment
        sent = results.get('sentiment_analysis', {})
        if sent:
            report.append("SENTIMENT SUMMARY")
            report.append("-" * 70)
            report.append(f"Overall: {sent.get('overall_sentiment', 'neutral').upper()}")
            report.append(f"Positive: {sent.get('positive_percentage', 0):.1f}%")
            report.append(f"Negative: {sent.get('negative_percentage', 0):.1f}%")
            report.append(f"Average Score: {sent.get('average_score', 0):.2f}")
            report.append("")
        
        # Alerts
        alerts = results.get('alerts', [])
        if alerts:
            report.append(f"ALERTS: {len(alerts)} STUDENTS NEED ATTENTION")
            report.append("-" * 70)
            for i, alert in enumerate(alerts[:5], 1):
                report.append(f"\n{i}. Student {alert.get('student_id')} - {alert.get('priority', 'unknown').upper()}")
                report.append(f"   Message: {alert.get('text', '')[:100]}...")
                report.append(f"   Action: {alert.get('recommended_action', '')[:100]}...")
            report.append("")
        
        # Topics
        topics = results.get('topics', [])
        if topics:
            report.append("COMMON TOPICS")
            report.append("-" * 70)
            for i, topic in enumerate(topics, 1):
                report.append(f"{i}. {topic.get('topic', 'Unknown')} ({topic.get('frequency', 0)*100:.0f}%)")
                report.append(f"   Sentiment: {topic.get('sentiment', 'unknown')}")
            report.append("")
        
        # Insights
        insights = results.get('insights', [])
        if insights:
            report.append("KEY INSIGHTS")
            report.append("-" * 70)
            for insight in insights:
                report.append(f"- {insight}")
            report.append("")
        
        return "\n".join(report)
    
    def generate_executive_summary(self, results: Dict) -> str:
        """Generate brief executive summary (1-2 paragraphs)"""
        lines = []
        
        total = results.get('total_feedback', 0)
        sent = results.get('sentiment_analysis', {})
        alerts = results.get('alerts', [])
        
        # First paragraph: Overview
        overall = sent.get('overall_sentiment', 'neutral') if sent else 'neutral'
        pos_pct = sent.get('positive_percentage', 0) if sent else 0
        neg_pct = sent.get('negative_percentage', 0) if sent else 0
        
        lines.append(f"Analysis of {total} student feedback messages reveals {overall} sentiment overall, "
                    f"with {pos_pct:.0f}% positive and {neg_pct:.0f}% negative feedback.")
        
        # Second paragraph: Action items
        if alerts:
            critical = sum(1 for a in alerts if a.get('priority') == 'critical')
            if critical > 0:
                lines.append(f"URGENT: {critical} students show critical signs requiring immediate intervention. "
                           f"Total of {len(alerts)} students need follow-up.")
            else:
                lines.append(f"{len(alerts)} students require follow-up and support.")
        else:
            lines.append("No critical alerts identified. Students appear to be managing well overall.")
        
        return " ".join(lines)
    
    def save_report(self, report: str, filename: str = None, format: str = 'markdown') -> str:
        """
        Save report to file
        
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = 'md' if format == 'markdown' else 'txt'
            filename = f"feedback_report_{timestamp}.{ext}"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return str(filepath)


if __name__ == "__main__":
    """Test the report generator"""
    print("=" * 60)
    print("Testing Analysis Report Generator")
    print("=" * 60)
    
    # Mock analysis results
    mock_results = {
        'total_feedback': 10,
        'sentiment_analysis': {
            'positive_count': 6,
            'negative_count': 3,
            'neutral_count': 1,
            'positive_percentage': 60.0,
            'negative_percentage': 30.0,
            'neutral_percentage': 10.0,
            'average_score': 0.25,
            'overall_sentiment': 'positive',
            'common_emotions': {
                'joy': 4,
                'frustration': 3,
                'confusion': 2
            }
        },
        'alerts': [
            {
                'student_id': 3,
                'course': 'Python',
                'text': 'I am thinking about dropping this class',
                'priority': 'critical',
                'sentiment': {'sentiment': 'negative', 'score': -0.9, 'emotion': 'anxiety'},
                'classification': {'category': 'at_risk_alert'},
                'recommended_action': 'Contact immediately'
            }
        ],
        'topics': [
            {
                'topic': 'Homework Difficulty',
                'frequency': 0.40,
                'sentiment': 'negative',
                'keywords': ['homework', 'difficult', 'time'],
                'examples': ['The homework is too hard']
            },
            {
                'topic': 'Teaching Quality',
                'frequency': 0.30,
                'sentiment': 'positive',
                'keywords': ['instructor', 'clear', 'helpful'],
                'examples': ['The instructor explains well']
            }
        ],
        'insights': [
            'Overall sentiment is positive (60% positive feedback)',
            '1 student shows critical signs requiring immediate attention',
            'Homework difficulty is a common concern'
        ],
        'recommendations': [
            'Contact at-risk student immediately',
            'Review homework difficulty levels'
        ]
    }
    
    try:
        generator = AnalysisReportGenerator()
        
        print("\n1. Testing Markdown Report Generation:")
        print("-" * 60)
        markdown_report = generator.generate_report(mock_results, format='markdown')
        print(f"Generated {len(markdown_report)} characters")
        print("\nFirst 500 characters:")
        print(markdown_report[:500])
        print("...")
        
        print("\n2. Testing Text Report Generation:")
        print("-" * 60)
        text_report = generator.generate_report(mock_results, format='text')
        print(f"Generated {len(text_report)} characters")
        
        print("\n3. Testing Executive Summary:")
        print("-" * 60)
        summary = generator.generate_executive_summary(mock_results)
        print(summary)
        
        print("\n4. Testing Save Functionality:")
        print("-" * 60)
        filepath = generator.save_report(markdown_report, format='markdown')
        print(f"Saved to: {filepath}")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
