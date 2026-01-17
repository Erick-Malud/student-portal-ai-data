"""
Chat Routes - AI Student Advisor Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from api.models import ChatRequest, ChatResponse
from api.middleware.auth import verify_api_key, limiter
from ai.student_advisor import AIStudentAdvisor
from ai.student_data_loader import StudentDataLoader
from api.config import settings
from student import Student
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Services - lazy initialization
_advisor = None
_data_loader = None

def get_advisor():
    """Lazy initialize advisor"""
    global _advisor
    if _advisor is None:
        _advisor = AIStudentAdvisor()
    return _advisor

def get_data_loader():
    """Lazy initialize data loader"""
    global _data_loader
    if _data_loader is None:
        if not settings.MOCK_MODE:
            try:
                _data_loader = StudentDataLoader(use_database=True)
            except Exception as e:
                print(f"⚠️  Warning: Could not load from database: {e}, using JSON fallback")
                _data_loader = StudentDataLoader(use_database=False)
        else:
             _data_loader = StudentDataLoader(use_database=False)
    return _data_loader

# Store active sessions (in production, use Redis or database)
active_sessions = {}


@router.post("", response_model=ChatResponse)
@limiter.limit("30/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Chat with AI Student Advisor.
    
    The advisor provides:
    - Course recommendations
    - Study advice
    - Performance insights
    - Learning path guidance
    
    Rate limit: 30 requests per minute
    """
    try:
        # Load student data - check existence but allow proceeding (handled by advisor)
        student_data = get_data_loader().get_student_by_id(chat_request.student_id)
        # if not student_data:
        #     # Allow advisor to handle not found cases for consistent schema
        #     pass
        
        # Create or retrieve session
        session_id = chat_request.session_id or str(uuid.uuid4())
        
        if session_id not in active_sessions:
            # New session - reset context
            get_advisor().context_manager.reset_conversation()
            active_sessions[session_id] = {
                "student_id": chat_request.student_id,
                "created_at": datetime.now(),
                "message_count": 0
            }
        
        # Get AI response
        ai_output = get_advisor().chat(chat_request.student_id, chat_request.message)
        
        # Update session
        active_sessions[session_id]["message_count"] += 1
        active_sessions[session_id]["last_message"] = datetime.now()
        
        response_text = ""
        suggested_courses = None
        student_summary = None
        mode = None
        recommendations = []

        if isinstance(ai_output, dict):
            # Structure from Mock
            response_text = ai_output.get("response", "")
            recommendations = ai_output.get("recommendations", [])
            suggested_courses = ai_output.get("suggested_courses")
            student_summary = ai_output.get("student_summary")
            mode = ai_output.get("mode")
        else:
            response_text = ai_output
            # Simple keyword extraction (legacy/OpenAI mode)
            for course in ["Python Fundamentals", "Advanced Python", "Data Structures", 
                        "Machine Learning", "Deep Learning", "Web Development"]:
                if course.lower() in response_text.lower():
                    recommendations.append(course)
        
        return ChatResponse(
            response=response_text,
            recommendations=recommendations if recommendations else None,
            suggested_courses=suggested_courses,
            student_summary=student_summary,
            mode=mode,
            session_id=session_id,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "CHAT_ERROR",
                "message": f"Error processing chat: {str(e)}"
            }
        )


@router.post("/reset")
@limiter.limit("10/minute")
async def reset_conversation(
    session_id: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Reset conversation history for a session.
    
    Use this when starting a new conversation or clearing context.
    """
    if session_id in active_sessions:
        del active_sessions[session_id]
    
    get_advisor().context_manager.reset_conversation()
    
    return {
        "message": "Conversation reset successfully",
        "session_id": session_id
    }


@router.get("/history/{student_id}")
@limiter.limit("20/minute")
async def get_chat_history(
    student_id: str,
    request: Request,
    limit: int = 10,
    api_key: str = Depends(verify_api_key)
):
    """
    Get recent chat history for a student.
    
    Returns the last N messages from conversations.
    """
    # Get conversation history from context manager
    history = get_advisor().context_manager.get_conversation_history()
    
    # Filter by student and limit
    filtered_history = [
        {
            "role": msg["role"],
            "content": msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"],
            "timestamp": msg.get("timestamp", "")
        }
        for msg in history[-limit:]
    ]
    
    return {
        "student_id": student_id,
        "messages": filtered_history,
        "total_messages": len(history)
    }


@router.get("/sessions")
@limiter.limit("10/minute")
async def get_active_sessions(
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Get list of active chat sessions.
    
    Admin endpoint to monitor active conversations.
    """
    return {
        "active_sessions": len(active_sessions),
        "sessions": [
            {
                "session_id": sid,
                "student_id": data["student_id"],
                "message_count": data["message_count"],
                "created_at": data["created_at"].isoformat(),
                "last_message": data.get("last_message", data["created_at"]).isoformat()
            }
            for sid, data in active_sessions.items()
        ]
    }
