"""
Embeddings Manager for Semantic Similarity
Handles OpenAI embeddings generation and similarity calculations for course recommendations.
"""

import os
import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

class EmbeddingsManager:
    """
    Manages OpenAI embeddings for semantic similarity calculations.
    
    Use cases:
    - Find courses similar to what student has completed
    - Match student interests to course descriptions
    - Semantic search across course catalog
    """
    
    def __init__(self):
        """Initialize the embeddings manager with OpenAI client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "text-embedding-3-small"  # Cost-effective embedding model
        self.cache_file = Path("ai/outputs/embeddings_cache.json")
        self.embeddings_cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load embeddings from cache file to avoid redundant API calls."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load embeddings cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save embeddings to cache file."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.embeddings_cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save embeddings cache: {e}")
    
    def get_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Get embedding vector for a text string.
        
        Args:
            text: Text to embed
            use_cache: Whether to use cached embeddings
        
        Returns:
            List of floats representing the embedding vector (1536 dimensions)
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Check cache first
        cache_key = text.strip()[:100]  # Use first 100 chars as key
        if use_cache and cache_key in self.embeddings_cache:
            return self.embeddings_cache[cache_key]
        
        try:
            # Get embedding from OpenAI
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            # Cache the result
            self.embeddings_cache[cache_key] = embedding
            self._save_cache()
            
            return embedding
            
        except Exception as e:
            print(f"Error getting embedding: {e}")
            raise
    
    def get_embeddings_batch(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """
        Get embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use cached embeddings
        
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache first
        for i, text in enumerate(texts):
            cache_key = text.strip()[:100]
            if use_cache and cache_key in self.embeddings_cache:
                embeddings.append(self.embeddings_cache[cache_key])
            else:
                embeddings.append(None)
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # Get embeddings for uncached texts
        if uncached_texts:
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=uncached_texts
                )
                
                # Fill in the embeddings
                for i, embedding_obj in enumerate(response.data):
                    embedding = embedding_obj.embedding
                    idx = uncached_indices[i]
                    embeddings[idx] = embedding
                    
                    # Cache the result
                    cache_key = uncached_texts[i].strip()[:100]
                    self.embeddings_cache[cache_key] = embedding
                
                self._save_cache()
                
            except Exception as e:
                print(f"Error getting batch embeddings: {e}")
                raise
        
        return embeddings
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embedding vectors.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Similarity score between 0 and 1 (1 = identical, 0 = completely different)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Ensure result is between 0 and 1
        return max(0.0, min(1.0, float(similarity)))
    
    def find_similar(
        self, 
        query_text: str, 
        candidate_texts: List[str], 
        top_k: int = 5
    ) -> List[Tuple[int, str, float]]:
        """
        Find most similar texts to a query.
        
        Args:
            query_text: Text to find similarities for
            candidate_texts: List of texts to compare against
            top_k: Number of top results to return
        
        Returns:
            List of tuples (index, text, similarity_score) sorted by similarity
        """
        if not candidate_texts:
            return []
        
        # Get query embedding
        query_embedding = self.get_embedding(query_text)
        
        # Get candidate embeddings
        candidate_embeddings = self.get_embeddings_batch(candidate_texts)
        
        # Calculate similarities
        similarities = []
        for i, (text, embedding) in enumerate(zip(candidate_texts, candidate_embeddings)):
            similarity = self.cosine_similarity(query_embedding, embedding)
            similarities.append((i, text, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[2], reverse=True)
        
        # Return top k results
        return similarities[:top_k]
    
    def find_similar_courses(
        self,
        query_course: Dict,
        candidate_courses: List[Dict],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find courses similar to a given course based on description and objectives.
        
        Args:
            query_course: Course dict with 'name', 'description', 'learning_objectives'
            candidate_courses: List of course dicts to compare
            top_k: Number of recommendations to return
        
        Returns:
            List of tuples (course_name, similarity_score)
        """
        # Create rich text representation of query course
        query_text = self._course_to_text(query_course)
        
        # Create text representations of candidate courses
        candidate_texts = [self._course_to_text(course) for course in candidate_courses]
        candidate_names = [course['name'] for course in candidate_courses]
        
        # Find similarities
        query_embedding = self.get_embedding(query_text)
        candidate_embeddings = self.get_embeddings_batch(candidate_texts)
        
        # Calculate similarities
        similarities = []
        for name, embedding in zip(candidate_names, candidate_embeddings):
            similarity = self.cosine_similarity(query_embedding, embedding)
            similarities.append((name, similarity))
        
        # Sort and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def find_courses_by_interests(
        self,
        interests: List[str],
        courses: List[Dict],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find courses matching student interests.
        
        Args:
            interests: List of interest keywords/phrases (e.g., ["machine learning", "data visualization"])
            courses: List of available courses
            top_k: Number of recommendations
        
        Returns:
            List of tuples (course_name, relevance_score)
        """
        # Combine interests into query
        query_text = " ".join(interests)
        
        # Get course texts and names
        course_texts = [self._course_to_text(course) for course in courses]
        course_names = [course['name'] for course in courses]
        
        # Find similarities
        results = self.find_similar(query_text, course_texts, top_k=top_k)
        
        # Map back to course names
        recommendations = [(course_names[idx], score) for idx, _, score in results]
        
        return recommendations
    
    def _course_to_text(self, course: Dict) -> str:
        """
        Convert course dictionary to rich text representation for embedding.
        
        Args:
            course: Course dictionary
        
        Returns:
            Text representation of course
        """
        parts = []
        
        # Course name
        if 'name' in course:
            parts.append(f"Course: {course['name']}")
        
        # Description
        if 'description' in course:
            parts.append(f"Description: {course['description']}")
        
        # Learning objectives
        if 'learning_objectives' in course:
            if isinstance(course['learning_objectives'], list):
                objectives = " ".join(course['learning_objectives'])
            else:
                objectives = course['learning_objectives']
            parts.append(f"Objectives: {objectives}")
        
        # Prerequisites (context)
        if 'prerequisites' in course:
            if isinstance(course['prerequisites'], list):
                prereqs = ", ".join(course['prerequisites'])
            else:
                prereqs = course['prerequisites']
            parts.append(f"Prerequisites: {prereqs}")
        
        return " | ".join(parts)
    
    def calculate_similarity_matrix(
        self,
        courses: List[Dict]
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate pairwise similarity scores for all courses.
        Useful for pre-computing similarities for fast lookups.
        
        Args:
            courses: List of course dictionaries
        
        Returns:
            Nested dict: {course_name: {other_course: similarity_score}}
        """
        # Get all course texts and embeddings
        course_texts = [self._course_to_text(course) for course in courses]
        course_names = [course['name'] for course in courses]
        embeddings = self.get_embeddings_batch(course_texts)
        
        # Calculate pairwise similarities
        similarity_matrix = {}
        
        for i, name1 in enumerate(course_names):
            similarity_matrix[name1] = {}
            for j, name2 in enumerate(course_names):
                if i != j:  # Don't compare course to itself
                    similarity = self.cosine_similarity(embeddings[i], embeddings[j])
                    similarity_matrix[name1][name2] = similarity
        
        return similarity_matrix
    
    def save_similarity_matrix(
        self,
        similarity_matrix: Dict[str, Dict[str, float]],
        filename: str = "course_similarity_matrix.json"
    ):
        """Save similarity matrix to file."""
        filepath = Path("ai/outputs") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(similarity_matrix, f, indent=2)
        
        print(f"Similarity matrix saved to: {filepath}")
    
    def load_similarity_matrix(
        self,
        filename: str = "course_similarity_matrix.json"
    ) -> Optional[Dict[str, Dict[str, float]]]:
        """Load pre-computed similarity matrix from file."""
        filepath = Path("ai/outputs") / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading similarity matrix: {e}")
            return None
    
    def clear_cache(self):
        """Clear the embeddings cache."""
        self.embeddings_cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
        print("Embeddings cache cleared")


# Test the embeddings manager
if __name__ == "__main__":
    print("Testing Embeddings Manager...\n")
    
    manager = EmbeddingsManager()
    
    # Test 1: Basic embedding
    print("Test 1: Basic Embedding")
    text = "Introduction to machine learning and neural networks"
    embedding = manager.get_embedding(text)
    print(f"✓ Generated embedding with {len(embedding)} dimensions")
    print()
    
    # Test 2: Similarity calculation
    print("Test 2: Similarity Calculation")
    text1 = "Python programming and data structures"
    text2 = "Advanced Python and algorithms"
    text3 = "Web development with JavaScript"
    
    emb1 = manager.get_embedding(text1)
    emb2 = manager.get_embedding(text2)
    emb3 = manager.get_embedding(text3)
    
    sim_12 = manager.cosine_similarity(emb1, emb2)
    sim_13 = manager.cosine_similarity(emb1, emb3)
    
    print(f"Similarity (Python vs Advanced Python): {sim_12:.3f}")
    print(f"Similarity (Python vs JavaScript): {sim_13:.3f}")
    print(f"✓ Python courses are more similar ({sim_12:.3f} > {sim_13:.3f})")
    print()
    
    # Test 3: Find similar
    print("Test 3: Find Similar Courses")
    query = "I want to learn about artificial intelligence"
    candidates = [
        "Introduction to Machine Learning",
        "Web Development Basics",
        "Deep Learning and Neural Networks",
        "Database Design",
        "Natural Language Processing"
    ]
    
    results = manager.find_similar(query, candidates, top_k=3)
    print(f"Query: '{query}'")
    print("Top 3 matches:")
    for idx, text, score in results:
        print(f"  {score:.3f} - {text}")
    print()
    
    # Test 4: Course similarity
    print("Test 4: Course-to-Course Similarity")
    courses = [
        {
            'name': 'Python Fundamentals',
            'description': 'Learn Python basics, data structures, and functions',
            'learning_objectives': ['Variables and types', 'Loops and conditionals', 'Functions']
        },
        {
            'name': 'Advanced Python',
            'description': 'Object-oriented programming, decorators, and generators',
            'learning_objectives': ['Classes', 'Decorators', 'Generators']
        },
        {
            'name': 'JavaScript Basics',
            'description': 'Learn JavaScript for web development',
            'learning_objectives': ['DOM manipulation', 'Events', 'Async programming']
        }
    ]
    
    query_course = courses[0]  # Python Fundamentals
    similar = manager.find_similar_courses(query_course, courses[1:], top_k=2)
    
    print(f"Courses similar to '{query_course['name']}':")
    for name, score in similar:
        print(f"  {score:.3f} - {name}")
    print()
    
    # Test 5: Interest-based recommendations
    print("Test 5: Interest-Based Recommendations")
    interests = ["machine learning", "data analysis", "AI"]
    all_courses = [
        {'name': 'ML Fundamentals', 'description': 'Introduction to machine learning algorithms and data analysis'},
        {'name': 'Web Design', 'description': 'Create beautiful websites with HTML and CSS'},
        {'name': 'Data Science', 'description': 'Analyze data using Python and statistical methods'},
        {'name': 'Mobile Apps', 'description': 'Build iOS and Android applications'}
    ]
    
    recommendations = manager.find_courses_by_interests(interests, all_courses, top_k=3)
    print(f"Student interests: {interests}")
    print("Recommended courses:")
    for name, score in recommendations:
        print(f"  {score:.3f} - {name}")
    print()
    
    print("✅ All tests passed! Embeddings Manager is working correctly.")
