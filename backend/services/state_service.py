# backend/services/state_service.py
"""
State Service - API endpoints for twin state management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from backend.simulator.twin_state import TwinState

router = APIRouter(prefix="/api/state", tags=["State"])

# Initialize twin state
twin_state = TwinState()


# Request Models
class StateUpdateRequest(BaseModel):
    cognitive: Optional[Dict] = None
    mood: Optional[Dict] = None
    sentiment: Optional[float] = None
    environment: Optional[str] = None


# Endpoints
@router.get("/")
def get_twin_state():
    """
    Get current twin state.
    
    Returns all state information including cognitive, mood, physical, social, etc.
    """
    try:
        state_dict = twin_state.to_dict()
        return {
            "success": True,
            "data": state_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update")
def update_twin_state(request: StateUpdateRequest):
    """
    Update twin state with new inputs.
    
    Body:
    - cognitive: Cognitive state data (dict)
    - mood: Mood state data (dict)
    - sentiment: Sentiment score (float)
    - environment: Environment feedback (string)
    """
    try:
        twin_state.update_from_inputs(
            cognitive=request.cognitive,
            mood=request.mood,
            sentiment=request.sentiment,
            environment_feedback=request.environment
        )
        
        return {
            "success": True,
            "message": "Twin state updated successfully",
            "data": twin_state.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cognitive")
def get_cognitive_state():
    """Get only cognitive state."""
    return {
        "success": True,
        "data": twin_state.cognitive_state
    }


@router.get("/mood")
def get_mood_state():
    """Get only mood state."""
    return {
        "success": True,
        "data": twin_state.mood_state
    }


@router.get("/physical")
def get_physical_state():
    """Get only physical state."""
    return {
        "success": True,
        "data": twin_state.physical_state
    }


@router.get("/social")
def get_social_state():
    """Get only social state."""
    return {
        "success": True,
        "data": twin_state.social_state
    }


@router.post("/reset")
def reset_twin_state():
    """
    Reset twin state to default values.
    """
    try:
        # Re-initialize the state
        global twin_state
        twin_state = TwinState()
        
        return {
            "success": True,
            "message": "Twin state reset to defaults",
            "data": twin_state.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def health_check():
    """Check if state service is running."""
    return {
        "success": True,
        "service": "State",
        "status": "running"
    }
