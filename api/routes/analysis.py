"""
Analysis Routes - Sentiment Analysis and Text Classification Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from api.models import (
    SentimentRequest, SentimentResponse,
    FeedbackAnalysisRequest, FeedbackAnalysisResponse,
    TextClassificationRequest, TextClassificationResponse
)
from api.middleware.auth import verify_api_key, limiter
from ai.sentiment_analyzer import SentimentAnalyzer
from ai.text_classifier import TextClassifier
from ai.topic_extractor import TopicExtractor
from ai.feedback_analyzer import FeedbackAnalyzer
from ai.analysis_report_generator import AnalysisReportGenerator
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

# Services - lazy initialization
_sentiment_analyzer = None
_text_classifier = None
_topic_extractor = None
_feedback_analyzer = None
_report_generator = None

def get_sentiment_analyzer():
    """Lazy initialize sentiment analyzer"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        try:
            _sentiment_analyzer = SentimentAnalyzer()
        except Exception as e:
            print(f"Warning: Could not initialize SentimentAnalyzer: {e}")
            _sentiment_analyzer = None
    return _sentiment_analyzer

def get_text_classifier():
    """Lazy initialize text classifier"""
    global _text_classifier
    if _text_classifier is None:
        try:
            _text_classifier = TextClassifier()
        except Exception as e:
            print(f"Warning: Could not initialize TextClassifier: {e}")
            _text_classifier = None
    return _text_classifier

def get_topic_extractor():
    """Lazy initialize topic extractor"""
    global _topic_extractor
    if _topic_extractor is None:
        try:
            _topic_extractor = TopicExtractor()
        except Exception as e:
            print(f"Warning: Could not initialize TopicExtractor: {e}")
            _topic_extractor = None
    return _topic_extractor

def get_feedback_analyzer():
    """Lazy initialize feedback analyzer"""
    global _feedback_analyzer
    if _feedback_analyzer is None:
        try:
            _feedback_analyzer = FeedbackAnalyzer()
        except Exception as e:
            print(f"Warning: Could not initialize FeedbackAnalyzer: {e}")
            _feedback_analyzer = None
    return _feedback_analyzer

def get_report_generator():
    """Lazy initialize report generator"""
    global _report_generator
    if _report_generator is None:
        try:
            _report_generator = AnalysisReportGenerator()
        except Exception as e:
            print(f"Warning: Could not initialize AnalysisReportGenerator: {e}")
            _report_generator = None
    return _report_generator


@router.post("/sentiment", response_model=SentimentResponse)
@limiter.limit("60/minute")
async def analyze_sentiment(
    req_body: SentimentRequest,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze sentiment of a text message.
    
    Returns:
    - Sentiment (positive/negative/neutral)
    - Score (-1.0 to 1.0)
    - Emotion (joy, frustration, anxiety, etc.)
    - Confidence level
    - Reasoning
    
    Rate limit: 60 requests per minute
    """
    try:
        result = get_sentiment_analyzer().analyze_sentiment(req_body.text)
        
        return SentimentResponse(
            sentiment=result["sentiment"],
            score=result["score"],
            emotion=result["emotion"] if req_body.include_emotion else None,
            confidence=result["confidence"],
            reasoning=result["reasoning"] if req_body.include_reasoning else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "SENTIMENT_ERROR",
                "message": f"Error analyzing sentiment: {str(e)}"
            }
        )


@router.post("/classify", response_model=TextClassificationResponse)
@limiter.limit("60/minute")
async def classify_text(
    req_body: TextClassificationRequest,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Classify text into categories with priority assessment.
    
    Categories:
    - technical_support
    - academic_difficulty
    - administrative
    - feedback_positive/negative
    - career_guidance
    - course_recommendation
    - at_risk_alert (critical)
    - general_question
    
    Priority levels: critical, high, medium, low
    
    Rate limit: 60 requests per minute
    """
    try:
        result = get_text_classifier().classify(req_body.text)
        
        return TextClassificationResponse(
            category=result["category"],
            confidence=result["confidence"],
            priority=result["priority"],
            requires_action=result["requires_action"],
            suggested_response_time=result["suggested_response_time"],
            reasoning=result["reasoning"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "CLASSIFICATION_ERROR",
                "message": f"Error classifying text: {str(e)}"
            }
        )


@router.post("/feedback", response_model=FeedbackAnalysisResponse)
@limiter.limit("10/minute")
async def analyze_feedback(
    req_body: FeedbackAnalysisRequest,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Comprehensive feedback analysis.
    
    Analyzes multiple feedback messages and provides:
    - Sentiment summary
    - Topic extraction
    - Alert identification (at-risk students)
    - Insights and recommendations
    - Generated report
    
    Rate limit: 10 requests per minute (computationally expensive)
    """
    try:
        # Convert request feedback to format expected by analyzer
        feedback_data = [
            {
                "student_id": item.student_id,
                "text": item.text,
                "course": item.course or "General",
                "timestamp": item.timestamp.isoformat() if item.timestamp else datetime.now().isoformat()
            }
            for item in req_body.feedback
        ]
        
        # Run analysis
        results = get_feedback_analyzer().analyze_feedback(feedback_data)
        
        # Generate report if requested
        report_id = None
        report_url = None
        if req_body.generate_report:
            report = get_report_generator().generate_report(results, format='markdown')
            report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filepath = get_report_generator().save_report(report, filename=f"{report_id}.md")
            report_url = f"/api/analysis/reports/{report_id}"
        
        return FeedbackAnalysisResponse(
            summary=results["sentiment_analysis"],
            alerts=results["alerts"],
            topics=results["topics"],
            report_id=report_id,
            report_url=report_url
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "FEEDBACK_ANALYSIS_ERROR",
                "message": f"Error analyzing feedback: {str(e)}"
            }
        )


@router.post("/topics")
@limiter.limit("20/minute")
async def extract_topics(
    texts: List[str],
    request: Request,
    max_topics: int = 5,
    api_key: str = Depends(verify_api_key)
):
    """
    Extract main topics/themes from a collection of texts.
    
    Uses unsupervised learning to discover common themes without
    predefined categories.
    
    Args:
        texts: List of text messages to analyze
        max_topics: Maximum number of topics to extract (1-10)
    
    Returns:
        List of topics with frequency, sentiment, keywords, examples
    """
    try:
        if not texts or len(texts) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_INPUT",
                    "message": "At least one text is required"
                }
            )
        
        if max_topics < 1 or max_topics > 10:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_PARAMETER",
                    "message": "max_topics must be between 1 and 10"
                }
            )
        
        topics = get_topic_extractor().extract_topics(texts, max_topics=max_topics)
        
        return {
            "topics": topics,
            "total_texts_analyzed": len(texts),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "TOPIC_EXTRACTION_ERROR",
                "message": f"Error extracting topics: {str(e)}"
            }
        )


@router.post("/batch-sentiment")
@limiter.limit("20/minute")
async def batch_sentiment_analysis(
    texts: List[str],
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze sentiment for multiple texts in batch.
    
    More efficient than calling /sentiment endpoint multiple times.
    
    Rate limit: 20 requests per minute
    Max texts per request: 100
    """
    try:
        if not texts or len(texts) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_INPUT",
                    "message": "At least one text is required"
                }
            )
        
        if len(texts) > 100:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "TOO_MANY_TEXTS",
                    "message": "Maximum 100 texts per batch request"
                }
            )
        
        results = get_sentiment_analyzer().analyze_batch(texts)
        summary = get_sentiment_analyzer().get_sentiment_summary(results)
        
        return {
            "results": results,
            "summary": summary,
            "total_analyzed": len(texts),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "BATCH_SENTIMENT_ERROR",
                "message": f"Error in batch sentiment analysis: {str(e)}"
            }
        )


@router.post("/batch-classify")
@limiter.limit("20/minute")
async def batch_classification(
    texts: List[str],
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Classify multiple texts in batch.
    
    More efficient than calling /classify endpoint multiple times.
    
    Rate limit: 20 requests per minute
    Max texts per request: 100
    """
    try:
        if not texts or len(texts) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_INPUT",
                    "message": "At least one text is required"
                }
            )
        
        if len(texts) > 100:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "TOO_MANY_TEXTS",
                    "message": "Maximum 100 texts per batch request"
                }
            )
        
        results = get_text_classifier().classify_batch(texts)
        summary = get_text_classifier().get_classification_summary(results)
        action_items = get_text_classifier().get_action_items(results)
        
        return {
            "results": results,
            "summary": summary,
            "action_items_count": len(action_items),
            "action_items": action_items,
            "total_analyzed": len(texts),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "BATCH_CLASSIFICATION_ERROR",
                "message": f"Error in batch classification: {str(e)}"
            }
        )


@router.get("/reports/{report_id}")
@limiter.limit("30/minute")
async def get_report(
    report_id: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Retrieve a previously generated analysis report.
    
    Returns the markdown-formatted report.
    """
    try:
        import os
        from pathlib import Path
        
        filepath = Path("ai/outputs") / f"{report_id}.md"
        
        if not filepath.exists():
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "REPORT_NOT_FOUND",
                    "message": f"Report {report_id} not found"
                }
            )
        
        with open(filepath, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        return {
            "report_id": report_id,
            "content": report_content,
            "format": "markdown",
            "timestamp": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "REPORT_ERROR",
                "message": f"Error retrieving report: {str(e)}"
            }
        )
