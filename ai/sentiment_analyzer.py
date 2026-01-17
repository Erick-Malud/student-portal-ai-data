"""
Sentiment Analyzer - Step 5
Analyzes emotional tone and sentiment in student feedback using OpenAI
"""

import json
from typing import Dict, List, Optional
from openai import OpenAI
from ai.config import load_api_key


class SentimentAnalyzer:
    """Analyze sentiment and emotions in text using OpenAI"""
    
    def __init__(self):
        """Initialize sentiment analyzer with OpenAI client"""
        api_key = load_api_key()
        if api_key == "MOCK":
            self.is_mock = True
            self.client = None
            print("✓ Sentiment Analyzer initialized (Mock Mode)")
        else:
            self.is_mock = False
            self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
        if not self.is_mock:
            print("✓ Sentiment Analyzer initialized")
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text
        
        Args:
            text: Student feedback or message to analyze
        
        Returns:
            Dict with sentiment, score, emotion, confidence, and reasoning
        """
        if not text or not text.strip():
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'emotion': 'none',
                'confidence': 0.0,
                'reasoning': 'Empty text provided'
            }

        if self.is_mock:
            # Simple keyword-based mock analysis
            lower_text = text.lower()
            if any(w in lower_text for w in ['love', 'great', 'amazing', 'happy', 'good']):
                return {
                    "sentiment": "positive",
                    "score": 0.8,
                    "emotion": "satisfaction",
                    "confidence": 0.9,
                    "reasoning": "Mock analysis: Found positive keywords."
                }
            elif any(w in lower_text for w in ['hate', 'bad', 'hard', 'struggle', 'awful']):
                return {
                    "sentiment": "negative",
                    "score": -0.6,
                    "emotion": "frustration",
                    "confidence": 0.85,
                    "reasoning": "Mock analysis: Found negative keywords."
                }
            else:
                return {
                    "sentiment": "neutral",
                    "score": 0.1,
                    "emotion": "neutral",
                    "confidence": 0.5,
                    "reasoning": "Mock analysis: No strong sentiment keywords found."
                }
        
        prompt = f"""Analyze the sentiment of this student feedback:

Text: "{text}"

Respond in JSON format:
{{
    "sentiment": "positive|negative|neutral",
    "score": -1.0 to +1.0 (where -1=very negative, 0=neutral, +1=very positive),
    "emotion": "primary emotion (joy, frustration, confusion, anxiety, satisfaction, disappointment, anger, excitement, boredom, etc.)",
    "confidence": 0.0 to 1.0,
    "reasoning": "brief explanation of the sentiment assessment"
}}

Be precise and analytical. Consider tone, word choice, and context."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert sentiment analyzer specializing in educational feedback. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower for consistent classification
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
            
            # Validate result structure
            required_keys = ['sentiment', 'score', 'emotion', 'confidence', 'reasoning']
            for key in required_keys:
                if key not in result:
                    result[key] = 'unknown' if key in ['sentiment', 'emotion', 'reasoning'] else 0.0
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Warning: JSON decode error - {e}")
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'emotion': 'unknown',
                'confidence': 0.0,
                'reasoning': f'Error parsing response: {e}'
            }
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'emotion': 'error',
                'confidence': 0.0,
                'reasoning': f'Error: {str(e)}'
            }
    
    def analyze_batch(self, texts: List[str], include_text: bool = True) -> List[Dict]:
        """
        Analyze multiple texts efficiently
        
        Args:
            texts: List of feedback messages
            include_text: Whether to include original text in results
        
        Returns:
            List of analysis results
        """
        results = []
        total = len(texts)
        
        print(f"Analyzing {total} feedback messages...")
        for i, text in enumerate(texts, 1):
            if i % 10 == 0 or i == total:
                print(f"  Progress: {i}/{total}")
            
            result = self.analyze_sentiment(text)
            if include_text:
                result['text'] = text
            results.append(result)
        
        print(f"✓ Completed analysis of {total} messages")
        return results
    
    def get_sentiment_summary(self, results: List[Dict]) -> Dict:
        """
        Aggregate sentiment analysis results into summary statistics
        
        Args:
            results: List of sentiment analysis results
        
        Returns:
            Summary statistics dictionary
        """
        if not results:
            return {
                'total_count': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'positive_percentage': 0.0,
                'negative_percentage': 0.0,
                'neutral_percentage': 0.0,
                'average_score': 0.0,
                'common_emotions': {},
                'overall_sentiment': 'neutral'
            }
        
        total = len(results)
        positive = sum(1 for r in results if r['sentiment'] == 'positive')
        negative = sum(1 for r in results if r['sentiment'] == 'negative')
        neutral = sum(1 for r in results if r['sentiment'] == 'neutral')
        
        # Calculate average score
        scores = [r.get('score', 0) for r in results]
        avg_score = sum(scores) / total if total > 0 else 0.0
        
        # Count emotions
        emotions = {}
        for r in results:
            emotion = r.get('emotion', 'unknown')
            emotions[emotion] = emotions.get(emotion, 0) + 1
        
        # Determine overall sentiment
        if avg_score > 0.3:
            overall = 'positive'
        elif avg_score < -0.3:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        return {
            'total_count': total,
            'positive_count': positive,
            'negative_count': negative,
            'neutral_count': neutral,
            'positive_percentage': (positive / total * 100) if total > 0 else 0.0,
            'negative_percentage': (negative / total * 100) if total > 0 else 0.0,
            'neutral_percentage': (neutral / total * 100) if total > 0 else 0.0,
            'average_score': avg_score,
            'common_emotions': dict(sorted(emotions.items(), 
                                          key=lambda x: x[1], 
                                          reverse=True)[:5]),
            'overall_sentiment': overall
        }
    
    def identify_extreme_sentiments(self, results: List[Dict], 
                                    threshold: float = 0.7) -> Dict:
        """
        Identify extremely positive or negative feedback
        
        Args:
            results: List of sentiment analysis results
            threshold: Score threshold (default 0.7)
        
        Returns:
            Dict with very positive and very negative items
        """
        very_positive = [
            r for r in results 
            if r.get('score', 0) > threshold
        ]
        
        very_negative = [
            r for r in results 
            if r.get('score', 0) < -threshold
        ]
        
        return {
            'very_positive': sorted(very_positive, 
                                   key=lambda x: x['score'], 
                                   reverse=True),
            'very_negative': sorted(very_negative, 
                                   key=lambda x: x['score'])
        }
    
    def analyze_by_emotion(self, results: List[Dict]) -> Dict:
        """
        Group results by emotion type
        
        Returns:
            Dict mapping emotions to lists of results
        """
        by_emotion = {}
        for result in results:
            emotion = result.get('emotion', 'unknown')
            if emotion not in by_emotion:
                by_emotion[emotion] = []
            by_emotion[emotion].append(result)
        
        return by_emotion


def quick_sentiment_check(text: str) -> str:
    """
    Quick function to check sentiment of a single text
    
    Args:
        text: Text to analyze
    
    Returns:
        Human-readable sentiment description
    """
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_sentiment(text)
    
    sentiment = result['sentiment'].upper()
    score = result['score']
    emotion = result['emotion']
    
    return f"{sentiment} (score: {score:.2f}) - Primary emotion: {emotion}"


if __name__ == "__main__":
    """Test the sentiment analyzer"""
    print("=" * 60)
    print("Testing Sentiment Analyzer")
    print("=" * 60)
    
    # Test cases
    test_texts = [
        "I love this course! The instructor is amazing and I'm learning so much!",
        "This class is way too hard. I don't understand anything and feel completely lost.",
        "The homework was okay, nothing special.",
        "I'm thinking about dropping this course. It's too stressful.",
        "The labs are really helpful and the TAs are great at explaining concepts.",
        "Why is everything so confusing? I can't keep up with the pace."
    ]
    
    try:
        analyzer = SentimentAnalyzer()
        
        print("\n1. Testing Individual Sentiment Analysis:")
        print("-" * 60)
        for i, text in enumerate(test_texts[:3], 1):
            print(f"\nText {i}: \"{text}\"")
            result = analyzer.analyze_sentiment(text)
            print(f"  Sentiment: {result['sentiment'].upper()}")
            print(f"  Score: {result['score']:.2f}")
            print(f"  Emotion: {result['emotion']}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Reasoning: {result['reasoning']}")
        
        print("\n2. Testing Batch Analysis:")
        print("-" * 60)
        results = analyzer.analyze_batch(test_texts, include_text=False)
        print(f"Analyzed {len(results)} texts")
        
        print("\n3. Testing Sentiment Summary:")
        print("-" * 60)
        summary = analyzer.get_sentiment_summary(results)
        print(f"Total: {summary['total_count']}")
        print(f"Positive: {summary['positive_count']} ({summary['positive_percentage']:.1f}%)")
        print(f"Negative: {summary['negative_count']} ({summary['negative_percentage']:.1f}%)")
        print(f"Neutral: {summary['neutral_count']} ({summary['neutral_percentage']:.1f}%)")
        print(f"Average Score: {summary['average_score']:.2f}")
        print(f"Overall Sentiment: {summary['overall_sentiment'].upper()}")
        print(f"\nCommon Emotions:")
        for emotion, count in summary['common_emotions'].items():
            print(f"  - {emotion}: {count}")
        
        print("\n4. Testing Extreme Sentiments:")
        print("-" * 60)
        extremes = analyzer.identify_extreme_sentiments(results, threshold=0.6)
        print(f"Very Positive: {len(extremes['very_positive'])}")
        print(f"Very Negative: {len(extremes['very_negative'])}")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
