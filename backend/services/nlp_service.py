# backend/services/nlp_service.py
"""
NLP Service - API endpoints for task recommendations and sentiment analysis
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from backend.nlp.task_recommender import TaskRecommender
from backend.nlp.sentiment_analyzer import SentimentAnalyzer

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
    - emotion: Emotion name (e.g., 'Happy', 'Sad', 'Angry')
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
