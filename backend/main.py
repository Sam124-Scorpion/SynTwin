# backend/main.py
"""
SynTwin Backend API
Main FastAPI application with all service routes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.services import (
    nlp_service,
    detection_service,
    analytics_service,
    state_service,
    stream_service
)

# Initialize FastAPI app
app = FastAPI(
    title="SynTwin API",
    description="Backend API for SynTwin - Digital Twin with Emotion Detection and Task Recommendations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from services
app.include_router(nlp_service.router)
app.include_router(detection_service.router)
app.include_router(analytics_service.router)
app.include_router(state_service.router)
app.include_router(stream_service.router)


# Root endpoint
@app.get("/")
def read_root():
    """
    API root endpoint - returns basic information.
    """
    return {
        "message": "Welcome to SynTwin API",
        "version": "1.0.0",
        "services": [
            "NLP (Task Recommendations & Sentiment Analysis)",
            "Detection (Face & Posture Detection Logging)",
            "Analytics (Data Analysis & Visualization)",
            "State (Digital Twin State Management)"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/api/health")
def health_check():
    """
    Overall health check for all services.
    """
    return {
        "status": "healthy",
        "services": {
            "nlp": "running",
            "detection": "running",
            "analytics": "running",
            "state": "running"
        }
    }


# Run with: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
