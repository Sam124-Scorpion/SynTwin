"""
SynTwin main module.
Contains FastAPI app and desktop detection runner.
"""
import argparse
import time

import cv2
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


def run_desktop_detection():
    from backend.src.config import Config
    from backend.src.core.analyzer import EmotionAnalyzer
    from backend.src.core.camera import VideoStream
    from backend.src.ui.visualizer import Visualizer
    from backend.src.utils.fps_counter import FPSCounter

    try:
        import mediapipe as mp
        if hasattr(mp, "solutions") and hasattr(mp.solutions, "face_detection"):
            use_mediapipe = True
            print("Using MediaPipe for face detection")
        else:
            from backend.src.core.face_detector import SimpleFaceDetector
            use_mediapipe = False
            print("MediaPipe solutions API unavailable, using OpenCV Haar Cascade")
    except ImportError:
        from backend.src.core.face_detector import SimpleFaceDetector
        use_mediapipe = False
        print("MediaPipe not available, using OpenCV Haar Cascade")

    print("Starting Advanced Emotion Analytics System...")

    camera = VideoStream(src=Config.CAMERA_ID, width=Config.CAMERA_WIDTH, height=Config.CAMERA_HEIGHT).start()
    analyzer = EmotionAnalyzer()
    analyzer.start()
    visualizer = Visualizer()

    if use_mediapipe:
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.7)
    else:
        face_detection = SimpleFaceDetector()

    fps_counter = FPSCounter(window_size=30)
    recording = False
    out = None
    frame_count = 0

    print("System ready. Press 'q' to exit, 'r' to toggle recording.")

    try:
        while True:
            frame = camera.read()
            if frame is None:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_img = None
            face_coords = None

            if use_mediapipe:
                results = face_detection.process(rgb_frame)
                if results and results.detections:
                    for detection in results.detections:
                        bbox = detection.location_data.relative_bounding_box
                        x = int(bbox.xmin * w)
                        y = int(bbox.ymin * h)
                        bw = int(bbox.width * w)
                        bh = int(bbox.height * h)

                        x, y = max(0, x), max(0, y)
                        bw, bh = min(w - x, bw), min(h - y, bh)

                        if bw > 0 and bh > 0:
                            face_img = frame[y : y + bh, x : x + bw]
                            face_coords = (x, y, bw, bh)
                            break
            else:
                faces = face_detection.detect(frame)
                if len(faces) > 0:
                    x, y, bw, bh = faces[0]
                    face_img = frame[y : y + bh, x : x + bw]
                    face_coords = (x, y, bw, bh)

            if face_img is not None and frame_count % Config.ANALYSIS_THROTTLE == 0:
                analyzer.analyze(face_img)

            frame_count += 1
            emotion, probs = analyzer.get_results()

            if face_coords:
                visualizer.draw_face_box(frame, face_coords, emotion)

            fps_counter.update()
            fps = fps_counter.get_fps()
            visualizer.draw_hud(frame, emotion, probs, fps)

            if recording:
                cv2.circle(frame, (w - 30, 30), 10, (0, 0, 255), -1)
                if out:
                    out.write(frame)

            cv2.imshow(Config.WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("r"):
                recording = not recording
                if recording:
                    filename = f"recording_{int(time.time())}.avi"
                    fourcc = cv2.VideoWriter_fourcc(*"XVID")
                    out = cv2.VideoWriter(filename, fourcc, 20.0, (w, h))
                    print(f"Recording started: {filename}")
                else:
                    if out:
                        out.release()
                        out = None
                    print("Recording stopped")
    except KeyboardInterrupt:
        pass
    finally:
        print("Shutting down desktop detector...")
        camera.stop()
        analyzer.stop()
        if out:
            out.release()
        cv2.destroyAllWindows()


def run_api_server(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SynTwin unified main entry")
    parser.add_argument("--mode", choices=["api", "desktop"], default="api")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.mode == "desktop":
        run_desktop_detection()
    else:
        run_api_server(host=args.host, port=args.port)
