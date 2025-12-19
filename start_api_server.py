"""
SynTwin API Server Startup Script
Run this to start the FastAPI backend server.
"""
import subprocess
import sys
from pathlib import Path

def main():
    print("="*60)
    print("Starting SynTwin Backend API Server")
    print("="*60)
    print()
    
    # Check if uvicorn is installed
    try:
        import uvicorn
        import fastapi
        print("FastAPI and Uvicorn are installed")
    except ImportError:
        print("Missing dependencies!")
        print("Installing FastAPI and Uvicorn...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "pydantic"])
        print(" Dependencies installed")
    
    print()
    print("Starting server...")
    print("   - Host: 0.0.0.0")
    print("   - Port: 8000")
    print()
    print("Access the API at:")
    print("   - Root: http://localhost:8000")
    print("   - Docs: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print()
    print("Press CTRL+C to stop the server")
    print("="*60)
    print()
    
    # Start the server
    try:
        import uvicorn
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n Server stopped by user")
    except Exception as e:
        print(f"\n Error starting server: {e}")
        print("\nTry running manually:")
        print("  uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")


if __name__ == "__main__":
    main()
