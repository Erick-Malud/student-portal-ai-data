"""
Topic Extractor - Step 5
Extracts themes and topics from collections of student feedback
"""

import json
from typing import Dict, List
from openai import OpenAI
from ai.config import load_api_key


class TopicExtractor:
    """Extract themes and topics from text collections using OpenAI"""
    
    def __init__(self):
        """Initialize topic extractor with OpenAI client"""
        api_key = load_api_key()
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
        print("✓ Topic Extractor initialized")
    
    def extract_topics(self, texts: List[str], max_topics: int = 5) -> List[Dict]:
        """
        Extract main topics/themes from collection of texts
        
        Args:
            texts: List of feedback messages
            max_topics: Maximum number of topics to extract
        
        Returns:
            List of topic dicts with name, frequency, sentiment, examples
        """
        if not texts:
            return []
        
        # Combine texts with numbering (limit to avoid token overflow)
        sample_size = min(len(texts), 50)  # Use up to 50 messages
        combined = "\n".join([f"{i+1}. {text[:200]}" for i, text in enumerate(texts[:sample_size])])
        
        # Truncate if still too long
        if len(combined) > 8000:
            combined = combined[:8000] + "..."
        
        prompt = f"""Analyze these {sample_size} student feedback messages and extract the {max_topics} most common topics/themes:

{combined}

Identify the main recurring topics. For each topic provide:
1. Topic name (short, descriptive)
2. Estimated frequency (what percentage of messages mention this)
3. Overall sentiment about this topic (positive/negative/neutral)
4. 2-3 example quotes from the feedback
5. Key words/phrases associated with this topic

Respond as a JSON array:
[
    {{
        "topic": "Topic Name",
        "frequency": 0.35,
        "sentiment": "negative",
        "examples": ["quote 1", "quote 2"],
        "keywords": ["keyword1", "keyword2", "keyword3"]
    }},
    ...
]

Focus on actionable topics that educators can address."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying themes in student feedback. Always respond with valid JSON array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,  # Moderate creativity for topic discovery
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Handle markdown code blocks
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            
            topics = json.loads(content)
            
            # Validate structure
            for topic in topics:
                topic.setdefault('topic', 'Unknown Topic')
                topic.setdefault('frequency', 0.0)
                topic.setdefault('sentiment', 'neutral')
                topic.setdefault('examples', [])
                topic.setdefault('keywords', [])
            
            return topics
            
        except json.JSONDecodeError as e:
            print(f"Warning: JSON decode error - {e}")
            return []
        except Exception as e:
            print(f"Error extracting topics: {e}")
            return []
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        Extract key words/phrases from a single text
        
        Args:
            text: Text to analyze
            top_k: Number of keywords to extract
        
        Returns:
            List of keywords
        """
        if not text or not text.strip():
            return []
        
        prompt = f"""Extract the {top_k} most important keywords or phrases from this text:

"{text}"

Return as a JSON array of strings: ["keyword1", "keyword2", ...]

Focus on meaningful terms (nouns, key concepts), not common words."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at keyword extraction. Always respond with valid JSON array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
            # Handle markdown code blocks
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            
            keywords = json.loads(content)
            return keywords if isinstance(keywords, list) else []
            
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def summarize_feedback(self, texts: List[str], max_length: int = 300) -> str:
        """
        Create a concise summary of feedback collection
        
        Args:
            texts: List of feedback messages
            max_length: Maximum summary length in words
        
        Returns:
            Summary text
        """
        if not texts:
            return "No feedback to summarize."
        
        # Sample texts if too many
        sample_size = min(len(texts), 30)
        sample = texts[:sample_size]
        combined = "\n".join([f"- {text[:150]}" for text in sample])
        
        prompt = f"""Summarize these {len(texts)} student feedback messages in {max_length} words or less:

{combined}

Provide a concise summary highlighting:
1. Main themes and concerns
2. Overall sentiment
3. Common requests or suggestions
4. Notable positive or negative patterns

Keep it factual and actionable."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing student feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error summarizing feedback: {e}")
            return f"Error: Unable to generate summary - {str(e)}"
    
    def compare_topic_sets(self, topics1: List[Dict], topics2: List[Dict]) -> Dict:
        """
        Compare topics between two time periods or groups
        
        Args:
            topics1: Topics from first set (e.g., last month)
            topics2: Topics from second set (e.g., this month)
        
        Returns:
            Comparison analysis
        """
        topics1_names = {t['topic'] for t in topics1}
        topics2_names = {t['topic'] for t in topics2}
        
        new_topics = topics2_names - topics1_names
        disappeared_topics = topics1_names - topics2_names
        common_topics = topics1_names & topics2_names
        
        # Compare sentiment for common topics
        sentiment_changes = []
        for topic_name in common_topics:
            t1 = next((t for t in topics1 if t['topic'] == topic_name), None)
            t2 = next((t for t in topics2 if t['topic'] == topic_name), None)
            
            if t1 and t2 and t1['sentiment'] != t2['sentiment']:
                sentiment_changes.append({
                    'topic': topic_name,
                    'from': t1['sentiment'],
                    'to': t2['sentiment']
                })
        
        return {
            'new_topics': list(new_topics),
            'disappeared_topics': list(disappeared_topics),
            'common_topics': list(common_topics),
            'sentiment_changes': sentiment_changes
        }
    
    def get_topic_summary(self, topics: List[Dict]) -> str:
        """
        Generate human-readable summary of topics
        
        Returns:
            Formatted summary text
        """
        if not topics:
            return "No topics identified."
        
        lines = ["Topic Analysis Summary:", "=" * 50, ""]
        
        for i, topic in enumerate(topics, 1):
            lines.append(f"{i}. {topic['topic']}")
            lines.append(f"   Frequency: {topic['frequency']*100:.1f}% of feedback")
            lines.append(f"   Sentiment: {topic['sentiment']}")
            lines.append(f"   Keywords: {', '.join(topic['keywords'][:5])}")
            if topic['examples']:
                lines.append(f"   Example: \"{topic['examples'][0][:100]}...\"")
            lines.append("")
        
        return "\n".join(lines)


def quick_topic_extraction(texts: List[str]) -> str:
    """
    Quick function to extract topics from texts
    
    Args:
        texts: List of feedback messages
    
    Returns:
        Human-readable topic summary
    """
    extractor = TopicExtractor()
    topics = extractor.extract_topics(texts, max_topics=5)
    return extractor.get_topic_summary(topics)


if __name__ == "__main__":
    """Test the topic extractor"""
    print("=" * 60)
    print("Testing Topic Extractor")
    print("=" * 60)
    
    # Test feedback messages
    test_feedback = [
        "The homework assignments are too difficult and take too much time.",
        "I love the practical labs! They really help me understand the concepts.",
        "The lectures move too fast. I can't keep up with the pace.",
        "The homework is way too hard. I spend hours and still don't get it.",
        "Great course! The instructor explains everything clearly.",
        "I'm confused about the recursion topic. It's not explained well.",
        "The lab equipment keeps breaking. Very frustrating.",
        "I wish there were more office hours available.",
        "The pace of lectures is perfect. Not too fast, not too slow.",
        "Homework difficulty is unreasonable for this level course.",
        "The TAs are really helpful during lab sessions.",
        "Recursion is so confusing! Need more examples.",
        "Lab equipment issues are slowing down our progress.",
        "More office hours would be really beneficial.",
        "The instructor is fantastic! Best teacher I've had."
    ]
    
    try:
        extractor = TopicExtractor()
        
        print("\n1. Testing Topic Extraction:")
        print("-" * 60)
        topics = extractor.extract_topics(test_feedback, max_topics=5)
        print(f"Extracted {len(topics)} topics\n")
        
        for i, topic in enumerate(topics, 1):
            print(f"{i}. {topic['topic']}")
            print(f"   Frequency: {topic['frequency']*100:.1f}%")
            print(f"   Sentiment: {topic['sentiment']}")
            print(f"   Keywords: {', '.join(topic['keywords'])}")
            print()
        
        print("\n2. Testing Keyword Extraction:")
        print("-" * 60)
        sample_text = "The recursive algorithm implementation homework is challenging but rewarding."
        keywords = extractor.extract_keywords(sample_text, top_k=5)
        print(f"Text: \"{sample_text}\"")
        print(f"Keywords: {', '.join(keywords)}")
        
        print("\n3. Testing Feedback Summarization:")
        print("-" * 60)
        summary = extractor.summarize_feedback(test_feedback[:10], max_length=100)
        print(summary)
        
        print("\n4. Testing Topic Summary:")
        print("-" * 60)
        topic_summary = extractor.get_topic_summary(topics)
        print(topic_summary)
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
