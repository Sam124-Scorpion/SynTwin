# backend/services/detection_service.py
"""
Detection Service - API endpoints for face/posture detection and logging
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from backend.database.db_logger import log_detection_to_db
from backend.analytics.data_logger import DataLogger
import sqlite3
from pathlib import Path


router = APIRouter(prefix="/api/detection", tags=["Detection"])

# Initialize logger
csv_logger = DataLogger(log_dir="logs")


# Request/Response Models
class DetectionEntry(BaseModel):
    emotion: str
    smile: str
    eyes: str
    posture: str
    sentiment: Optional[float] = 0.0
    cognitive_state: Optional[str] = "Unknown"
    mood: Optional[str] = "Neutral"
    environment_feedback: Optional[str] = ""


class DetectionResponse(BaseModel):
    timestamp: str
    emotion: str
    smile: str
    eyes: str
    posture: str
    sentiment: float
    environment_feedback: str


# Endpoints
@router.post("/log")
def log_detection(entry: DetectionEntry):
    """
    Log a detection entry to database and CSV.
    
    Body:
    - emotion: Detected emotion
    - smile: Smile status
    - eyes: Eyes status
    - posture: Posture status
    - sentiment: Sentiment score (optional)
    - cognitive_state: Cognitive state (optional)
    - mood: Mood state (optional)
    - environment_feedback: Environment info (optional)
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare entry data
        entry_data = {
            "timestamp": timestamp,
            "emotion": entry.emotion,
            "smile": entry.smile,
            "eyes": entry.eyes,
            "posture": entry.posture,
            "sentiment": entry.sentiment,
            "cognitive_state": entry.cognitive_state,
            "mood": entry.mood,
            "environment_feedback": entry.environment_feedback
        }
        
        # Log to database
        log_detection_to_db(entry_data)
        
        # Log to CSV
        csv_logger.log_entry(entry_data)
        
        return {
            "success": True,
            "message": "Detection logged successfully",
            "data": entry_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
def get_recent_detections(limit: int = 10):
    """
    Get recent detection entries.
    
    Query params:
    - limit: Number of entries to return (default: 10)
    """
    try:
        db_path = Path(__file__).parent.parent / "database" / "syntwin.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, emotion, smile, eyes, posture, sentiment, environment_feedback
            FROM detector_logs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        detections = []
        for row in rows:
            detections.append({
                "timestamp": row[0],
                "emotion": row[1],
                "smile": row[2],
                "eyes": row[3],
                "posture": row[4],
                "sentiment": row[5],
                "environment_feedback": row[6]
            })
        
        return {
            "success": True,
            "count": len(detections),
            "data": detections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
def get_detection_stats():
    """
    Get detection statistics (counts by emotion, posture, etc.)
    """
    try:
        db_path = Path(__file__).parent.parent / "database" / "syntwin.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Total detections
        cursor.execute("SELECT COUNT(*) FROM detector_logs")
        total = cursor.fetchone()[0]
        
        # Emotion distribution
        cursor.execute("""
            SELECT emotion, COUNT(*) as count
            FROM detector_logs
            GROUP BY emotion
            ORDER BY count DESC
        """)
        emotion_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Posture distribution
        cursor.execute("""
            SELECT posture, COUNT(*) as count
            FROM detector_logs
            GROUP BY posture
            ORDER BY count DESC
        """)
        posture_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Average sentiment
        cursor.execute("SELECT AVG(sentiment) FROM detector_logs WHERE sentiment IS NOT NULL")
        avg_sentiment = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "total_detections": total,
                "emotion_distribution": emotion_stats,
                "posture_distribution": posture_stats,
                "average_sentiment": round(avg_sentiment, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline")
def get_detection_timeline(hours: int = 24):
    """
    Get detection timeline for the specified time period.
    
    Query params:
    - hours: Number of hours to look back (default: 24)
    """
    try:
        from datetime import timedelta
        
        db_path = Path(__file__).parent.parent / "database" / "syntwin.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        time_threshold = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            SELECT timestamp, emotion, posture, sentiment
            FROM detector_logs
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        """, (time_threshold,))
        
        rows = cursor.fetchall()
        conn.close()
        
        timeline = []
        for row in rows:
            timeline.append({
                "timestamp": row[0],
                "emotion": row[1],
                "posture": row[2],
                "sentiment": row[3]
            })
        
        return {
            "success": True,
            "count": len(timeline),
            "data": timeline
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
def clear_detections():
    """
    Clear all detection data (use with caution!)
    """
    try:
        db_path = Path(__file__).parent.parent / "database" / "syntwin.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM detector_logs")
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Cleared {deleted_count} detection entries"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def health_check():
    """Check if detection service is running."""
    return {
        "success": True,
        "service": "Detection",
        "status": "running"
    }
