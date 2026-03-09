# backend/services/nlp_service.py
"""
NLP Service - API endpoints for task recommendations, sentiment analysis,
and Gemini AI mental wellness advice.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from backend.nlp.task_recommender import TaskRecommender
from backend.nlp.sentiment_analyzer import SentimentAnalyzer
from backend.nlp.gemini_advisor import get_gemini_advisor

router = APIRouter(prefix="/api/nlp", tags=["NLP"])

# Initialize services
recommender = TaskRecommender()
sentiment_analyzer = SentimentAnalyzer()


# Request/Response Models
class SentimentRequest(BaseModel):
    text: Optional[str] = None
    emotion: Optional[str] = None
    smile: Optional[str] = None
    eyes: Optional[str] = None
    posture: Optional[str] = None


class TaskSuggestionRequest(BaseModel):
    minutes: Optional[int] = 10


class GeminiAdviceRequest(BaseModel):
    """Payload for AI mental wellness advice."""
    # Core detection fields
    emotion:         Optional[str]   = "Neutral"
    confidence:      Optional[float] = 0.0
    smile:           Optional[str]   = "Not Smiling"
    eyes:            Optional[str]   = "Eyes Open"
    posture:         Optional[str]   = "Straight"
    drowsy_score:    Optional[float] = 0.0
    blink_rate:      Optional[float] = 0.0
    # Optional enrichment
    recent_emotions: Optional[List[str]] = []
    session_minutes: Optional[int]       = None
    # Gemini API key (overrides env var GEMINI_API_KEY if supplied)
    api_key:         Optional[str]       = None


# Endpoints
@router.get("/suggestions")
def get_task_suggestions(minutes: int = 10):
    """
    Get personalized task suggestions based on recent detection data.
    
    Query params:
    - minutes: How many minutes of data to analyze (default: 10)
    """
    try:
        result = recommender.get_task_suggestions(minutes=minutes)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/state")
def get_current_state(minutes: int = 10):
    """
    Get analysis of current user state.
    
    Query params:
    - minutes: How many minutes of data to analyze (default: 10)
    """
    try:
        state = recommender.analyze_current_state(minutes=minutes)
        return {
            "success": True,
            "data": state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily-summary")
def get_daily_summary(hours: int = 24):
    """
    Get daily summary and insights.
    
    Query params:
    - hours: How many hours of data to include (default: 24)
    """
    try:
        summary = recommender.get_daily_summary(hours=hours)
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment/analyze")
def analyze_sentiment(request: SentimentRequest):
    """
    Analyze sentiment from text or behavioral data.
    
    Body:
    - text: Text to analyze (optional)
    - emotion, smile, eyes, posture: Behavioral data (optional)
    """
    try:
        result = {}
        
        # Text sentiment analysis
        if request.text:
            text_sentiment = sentiment_analyzer.analyze_text_sentiment(request.text)
            result["text_sentiment"] = text_sentiment
        
        # Behavioral sentiment analysis
        if any([request.emotion, request.smile, request.eyes, request.posture]):
            behavior_data = {}
            if request.emotion:
                behavior_data["emotion"] = request.emotion
            if request.smile:
                behavior_data["smile"] = request.smile
            if request.eyes:
                behavior_data["eyes"] = request.eyes
            if request.posture:
                behavior_data["posture"] = request.posture
            
            behavior_sentiment = sentiment_analyzer.analyze_behavioral_sentiment(behavior_data)
            result["behavioral_sentiment"] = behavior_sentiment
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment/emotion/{emotion}")
def get_emotion_sentiment(emotion: str):
    """
    Get sentiment score for a specific emotion.
    
    Path params:
    - emotion: Emotion name (e.g., 'Happy', 'Neutral', 'Drowsy')
    """
    try:
        score = sentiment_analyzer.analyze_emotion_sentiment(emotion)
        return {
            "success": True,
            "data": {
                "emotion": emotion,
                "sentiment_score": score
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def health_check():
    """Check if NLP service is running."""
    return {
        "success": True,
        "service": "NLP",
        "status": "running"
    }


# ── Gemini AI Wellness Advisor ───────────────────────────────────────────────
@router.post("/gemini/advice")
def get_gemini_advice(request: GeminiAdviceRequest):
    """
    Send current detection data to Google Gemini and receive
    personalised mental-wellness tasks + motivation.

    Body (all optional):
    - emotion, confidence, smile, eyes, posture
    - drowsy_score, blink_rate
    - recent_emotions: list of recent emotion strings
    - session_minutes: how long user has been at desk
    - api_key: Gemini API key (overrides GEMINI_API_KEY env var)
    """
    try:
        advisor = get_gemini_advisor(api_key=request.api_key or None)
        detection_data = {
            "emotion":         request.emotion,
            "confidence":      request.confidence,
            "smile":           request.smile,
            "eyes":            request.eyes,
            "posture":         request.posture,
            "drowsy_score":    request.drowsy_score,
            "blink_rate":      request.blink_rate,
            "recent_emotions": request.recent_emotions,
            "session_minutes": request.session_minutes,
        }
        result = advisor.get_advice(detection_data)
        return {
            "success": result["success"],
            "data": {
                "advice":  result["advice"],
                "emotion": result["emotion"],
                "gemini_available": result["success"],
                "error":   result.get("error"),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gemini/status")
def gemini_status():
    """Check whether Gemini API is configured and reachable."""
    advisor = get_gemini_advisor()
    return {
        "success":   True,
        "available": advisor.ready,
        "message":   "Gemini ready" if advisor.ready
                     else "Gemini unavailable – check GEMINI_API_KEY"
    }


@router.get("/gemini/auto-advice")
def get_auto_gemini_advice(minutes: int = 10):
    """
    Automatically read the latest detection state from the DB and
    get Gemini AI wellness advice — no request body needed.
    The frontend can call this with a single GET request.
    """
    try:
        # Pull current state from the database
        state = recommender.analyze_current_state(minutes=minutes)

        # Guard: do not call Gemini if there is no real detection data yet
        if state.get("data_points", 0) == 0:
            return {
                "success": False,
                "no_data": True,
                "data": {
                    "advice":           None,
                    "emotion":          None,
                    "gemini_available": False,
                    "state_summary":    state,
                    "error":            "No detection data yet — start detection first.",
                }
            }

        # Build a detection_data dict from the DB state
        detection_data = {
            "emotion":         state.get("dominant_emotion", "Neutral"),
            "confidence":      state.get("confidence", 0.0),
            "smile":           state.get("smile", "Not Smiling"),
            "eyes":            state.get("eyes", "Eyes Open"),
            "posture":         state.get("posture_status", "Straight"),
            "drowsy_score":    state.get("drowsy_score", 0.0),
            "blink_rate":      state.get("blink_rate", 0.0),
            "recent_emotions": state.get("recent_emotions", []),
            "session_minutes": state.get("session_minutes", None),
        }

        advisor = get_gemini_advisor()
        result  = advisor.get_advice(detection_data)

        return {
            "success": True,
            "data": {
                "advice":           result["advice"],
                "emotion":          result["emotion"],
                "gemini_available": result["success"],
                "state_summary":    state,
                "error":            result.get("error"),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))