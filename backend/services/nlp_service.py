# backend/services/nlp_service.py
"""
NLP Service - API endpoints for task recommendations, sentiment analysis,
and AI model-driven mental wellness advice.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
from backend.nlp.task_recommender import TaskRecommender
from backend.nlp.decision_tree_fallback import build_decision_tree_fallback
from backend.nlp.sentiment_analyzer import SentimentAnalyzer
from backend.nlp.model_chain import call_api_chain

router = APIRouter(prefix="/api/nlp", tags=["NLP"])

# Initialize services
recommender = TaskRecommender()
sentiment_analyzer = SentimentAnalyzer()


def _describe_drowsy_score(score: float) -> str:
    if score >= 0.75:
        return "severely drowsy (eyes heavily closed, low blink rate)"
    if score >= 0.45:
        return "moderately drowsy (frequent eye closure)"
    if score >= 0.20:
        return "mildly fatigued"
    return "alert and awake"


def _describe_posture(posture: str) -> str:
    mapping = {
        "Straight": "upright and well-aligned",
        "Slouching": "slouching forward (spine curved)",
        "Leaning Sideways": "leaning sideways (asymmetric load on spine)",
        "Leaning Back": "leaning back / reclining",
        "Slouching Forward": "slouching forward with neck strain",
        "Looking Down": "looking down (neck flexed forward)",
    }
    return mapping.get(posture, posture)


def _time_of_day() -> str:
    hour = __import__("datetime").datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "late night"


def _build_ai_prompt(data: dict) -> str:
    emotion = data.get("emotion", "Neutral")
    confidence = data.get("confidence", 0.0)
    smile = data.get("smile", "Not Smiling")
    eyes = data.get("eyes", "Eyes Open")
    posture = data.get("posture", "Straight")
    drowsy_score = float(data.get("drowsy_score", 0.0))
    blink_rate = float(data.get("blink_rate", 0.0))
    session_mins = data.get("session_minutes", None)
    recent_emots = data.get("recent_emotions", [])

    lines = [
        f"It is currently {_time_of_day()}.",
        f"The user's detected emotion is **{emotion}** (confidence: {confidence:.0%}).",
        f"Their eyes are currently **{eyes}**.",
        f"Smile status: **{smile}**.",
        f"Posture: **{_describe_posture(posture)}**.",
        f"Drowsiness level: **{_describe_drowsy_score(drowsy_score)}** (score {drowsy_score:.2f}/1.0).",
    ]

    if blink_rate > 0:
        lines.append(
            f"Blink rate: **{blink_rate:.0f} blinks/min** ({'low - possible fatigue' if blink_rate < 10 else 'normal'})."
        )

    if session_mins:
        lines.append(f"The user has been at their desk for approximately **{session_mins} minutes**.")

    if recent_emots:
        lines.append(f"Recent emotion history (last few detections): {', '.join(recent_emots[-8:])}.")

    observation = "\n".join(lines)

    return f"""You are SynTwin's AI wellness advisor. You analyse real-time biometric 
data captured by a webcam-based emotion & drowsiness detection system and suggest 
concise, actionable tasks to improve the user's mental state and productivity.

CURRENT USER STATE
{observation}

YOUR TASK
Based strictly on the data above, provide:
1. Mental State Assessment
2. Immediate Action
3. Top 5 Personalised Tasks
4. Motivational Nudge

Keep the entire response under 250 words. Use plain readable language.
Do NOT repeat the raw numbers back to the user.
"""


# Request/Response Models
class SentimentRequest(BaseModel):
    text: Optional[str] = None
    emotion: Optional[str] = None
    smile: Optional[str] = None
    eyes: Optional[str] = None
    posture: Optional[str] = None


class TaskSuggestionRequest(BaseModel):
    minutes: Optional[int] = 10


class AIAdviceRequest(BaseModel):
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
    # Reserved for future per-request provider overrides.
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


# ── AI Wellness Advisor ───────────────────────────────────────────────────────
@router.post("/ai/advice")
def get_ai_advice(request: AIAdviceRequest):
    """
    Send current detection data to the AI model chain and receive
    personalised mental-wellness tasks + motivation.

    Body (all optional):
    - emotion, confidence, smile, eyes, posture
    - drowsy_score, blink_rate
    - recent_emotions: list of recent emotion strings
    - session_minutes: how long user has been at desk
    - api_key: Reserved for future provider overrides
    """
    try:
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
        prompt = _build_ai_prompt(detection_data)
        result = call_api_chain(prompt)

        if result["status"] == "success":
            advice = result["content"]
            ai_model_available = True
            fallback_source = None
        else:
            fallback = build_decision_tree_fallback({
                "emotion": detection_data.get("emotion", "Neutral"),
                "posture": detection_data.get("posture", "Straight"),
                "drowsy_score": detection_data.get("drowsy_score", 0.0),
                "avg_sentiment": 0.0,
                "data_points": 1,
            })
            advice = fallback["advice"]
            ai_model_available = False
            fallback_source = fallback.get("source")

        return {
            "success": True,
            "data": {
                "advice":  advice,
                "emotion": detection_data["emotion"],
                "ai_model_available": ai_model_available,
                "fallback_source": fallback_source,
                "error":   None if ai_model_available else "All AI models failed; using decision-tree fallback.",
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/status")
def ai_status():
    """Check whether the AI model chain is configured and reachable."""
    available = bool(os.getenv("OPENROUTER_API_KEY"))
    return {
        "success":   True,
        "available": available,
        "message":   "AI model chain ready" if available
                     else "AI model chain unavailable – check OPENROUTER_API_KEY"
    }


@router.get("/ai/auto-advice")
def get_auto_ai_advice(minutes: int = 10):
    """
    Automatically read the latest detection state from the DB and
    get AI wellness advice — no request body needed.
    The frontend can call this with a single GET request.
    """
    try:
        # Pull current state from the database
        state = recommender.analyze_current_state(minutes=minutes)

        # Guard: do not call the AI chain if there is no real detection data yet
        if state.get("data_points", 0) == 0:
            return {
                "success": False,
                "no_data": True,
                "data": {
                    "advice":           None,
                    "emotion":          None,
                    "ai_model_available": False,
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
        prompt = _build_ai_prompt(detection_data)
        result = call_api_chain(prompt)

        if result["status"] == "success":
            advice = result["content"]
            ai_model_available = True
            fallback_source = None
        else:
            fallback = build_decision_tree_fallback({
                "dominant_emotion": detection_data.get("emotion", "Neutral"),
                "posture_status": detection_data.get("posture", "Straight"),
                "drowsy_score": detection_data.get("drowsy_score", 0.0),
                "avg_sentiment": state.get("avg_sentiment", 0.0),
                "data_points": state.get("data_points", 0),
            })
            advice = fallback["advice"]
            ai_model_available = False
            fallback_source = fallback.get("source")

        return {
            "success": True,
            "data": {
                "advice":           advice,
                "emotion":          detection_data["emotion"],
                "ai_model_available": ai_model_available,
                "fallback_source":  fallback_source,
                "state_summary":    state,
                "error":            None if ai_model_available else "All AI models failed; using decision-tree fallback.",
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))