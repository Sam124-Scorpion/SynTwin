# backend/services/stream_service.py
"""
Stream Service - Real-time webcam detection with WebSocket support
"""
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='google.protobuf')

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import cv2
import asyncio
import json
import base64
from datetime import datetime
from backend.detectors.combined_detector import CombinedDetector
from backend.simulator.twin_state import TwinState
from backend.database.db_logger import log_detection_to_db
from backend.analytics.data_logger import DataLogger
from backend.nlp.sentiment_analyzer import SentimentAnalyzer

router = APIRouter(prefix="/api/stream", tags=["Stream"])

# Global state
detector = None
twin_state = None
csv_logger = None
sentiment_analyzer = None
active_connections: List[WebSocket] = []
detection_active = False


class DetectionManager:
    """Manages the detection process."""
    
    def __init__(self):
        self.detector = CombinedDetector()
        self.twin = TwinState()
        self.csv_logger = DataLogger(log_dir="logs")
        self.sentiment_analyzer = SentimentAnalyzer()
        self.cap = None
        self.is_running = False
    
    def start_camera(self):
        """Initialize camera with optimized settings."""
        if self.cap is not None and self.cap.isOpened():
            return True
        
        for idx in range(3):
            self.cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if self.cap.isOpened():
                # Set camera properties for better performance
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to minimize lag
                
                # Quick warm up
                for _ in range(3):
                    self.cap.read()
                
                print(f"Camera {idx} initialized successfully")
                return True
        
        print("Failed to initialize any camera")
        return False
    
    def stop_camera(self):
        """Release camera."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def process_frame(self):
        """Process a single frame and return results."""
        try:
            if self.cap is None or not self.cap.isOpened():
                # Try to reconnect camera
                print("Camera not opened, attempting to reconnect...")
                if not self.start_camera():
                    print("Failed to reconnect camera")
                    return None
            
            # Read frame directly (buffer=1 prevents lag)
            ret, frame = self.cap.read()
            if not ret or frame is None or frame.size == 0:
                # Skip this frame but don't stop - camera might recover
                print("Failed to read frame, will retry")
                return None
        except Exception as e:
            print(f"Error in process_frame (camera read): {e}")
            return None
        
        # Detect
        try:
            results, annotated_frame = self.detector.detect(frame)
        except Exception as e:
            print(f"Error in detector.detect(): {e}")
            return None
        
        # Normalize emotion
        try:
            normalized_emotion = results["emotion"].strip().lower()
            if normalized_emotion in ["tired", "sleepy", "drowsy"]:
                results["emotion"] = "Drowsy"
            elif normalized_emotion in ["sad", "down", "unhappy"]:
                results["emotion"] = "Sad"
            elif normalized_emotion == "neutral":
                if results.get("eyes") == "Closed":
                    results["emotion"] = "Drowsy"
                elif results.get("posture") in ["Slouching", "Lean Forward"]:
                    results["emotion"] = "Sad"
        except Exception as e:
            print(f"Error normalizing emotion: {e}")
        
        # Calculate sentiment
        try:
            behavior = {
                "emotion": results["emotion"],
                "smile": results["smile"],
                "posture": results["posture"],
                "eyes": results["eyes"]
            }
            sentiment_result = self.sentiment_analyzer.analyze_behavioral_sentiment(behavior)
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            sentiment_result = {"score": 0, "label": "Neutral", "factors": []}
        
        # Update Twin State
        self.twin.update_from_inputs(
            cognitive={"state": "Focused" if results["emotion"] in ["Happy", "Focused"] else "Distracted"},
            mood={"mood": results["emotion"]},
            sentiment=sentiment_result["score"],
            environment_feedback=f"Posture: {results['posture']}"
        )
        
        # Log data
        cognitive_state = "Focused" if results["emotion"] in ["Happy", "Focused"] else "Distracted"
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "emotion": results["emotion"],
            "smile": results["smile"],
            "eyes": results["eyes"],
            "posture": results["posture"],
            "cognitive_state": cognitive_state,
            "mood": results["emotion"],
            "sentiment": sentiment_result["score"],
            "environment_feedback": f"Posture: {results['posture']}"
        }
        log_detection_to_db(entry)
        self.csv_logger.log_entry(entry)
        
        # Draw detections on frame
        try:
            processed_frame = self.detector.draw_detections(annotated_frame.copy(), results)
        except Exception as e:
            print(f"Error drawing detections: {e}")
            processed_frame = annotated_frame
        
        # Convert frame to base64 for sending
        try:
            _, buffer = cv2.imencode('.jpg', processed_frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            print(f"Error encoding frame: {e}")
            return None
        
        # Prepare JSON-serializable results (remove any non-serializable objects)
        clean_results = {
            "emotion": str(results.get("emotion", "Unknown")),
            "smile": str(results.get("smile", "Unknown")),
            "eyes": str(results.get("eyes", "Unknown")),
            "posture": str(results.get("posture", "Unknown"))
        }
        
        clean_sentiment = {
            "score": float(sentiment_result.get("score", 0)),
            "label": str(sentiment_result.get("label", "Neutral")),
            "factors": [str(f) for f in sentiment_result.get("factors", [])]
        }
        
        return {
            "frame": frame_base64,
            "results": clean_results,
            "sentiment": clean_sentiment,
            "twin_state": self.twin.get_snapshot()
        }


# Global detection manager
detection_manager = DetectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time detection streaming."""
    await websocket.accept()
    active_connections.append(websocket)
    
    async def send_detection_data():
        """Continuously send detection data while running."""
        print(f"Detection loop started for this connection. is_running={detection_manager.is_running}")
        frame_count = 0
        
        # Wait for detection to be started
        while not detection_manager.is_running:
            await asyncio.sleep(0.1)
        
        print("Detection is active, streaming frames to this connection")
        
        # Stream frames while detection is running AND connection is open
        while detection_manager.is_running:
            try:
                result = detection_manager.process_frame()
                if result:
                    try:
                        await websocket.send_json({
                            "type": "detection",
                            "data": result
                        })
                        frame_count += 1
                        if frame_count % 100 == 0:
                            print(f"Sent {frame_count} frames to this connection")
                    except Exception as send_err:
                        # Connection issue - stop streaming to THIS connection
                        print(f"Failed to send frame (connection closed): {send_err}")
                        break  # Exit loop but don't stop global detection
                else:
                    # No result from camera
                    await asyncio.sleep(0.05)
                    continue
                    
                await asyncio.sleep(0.033)  # ~30 FPS
            except Exception as e:
                print(f"Detection loop error: {e}")
                await asyncio.sleep(0.1)
                # Don't break - keep trying to send frames
                continue
        
        print(f"Streaming ended for this connection. Total frames: {frame_count}")
        # DON'T stop detection here - other connections might be active
    
    async def handle_commands():
        """Handle start/stop commands from client."""
        should_stop = False
        while not should_stop:
            try:
                data = await websocket.receive_text()
                command = json.loads(data)
                print(f"Received command: {command.get('action')}")
                
                if command.get("action") == "start":
                    if not detection_manager.is_running:
                        if detection_manager.start_camera():
                            detection_manager.is_running = True
                            print("Detection started by command")
                            await websocket.send_json({
                                "type": "status",
                                "message": "Detection started",
                                "running": True
                            })
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "message": "Failed to start camera"
                            })
                
                elif command.get("action") == "stop":
                    print("Stop command received from client")
                    detection_manager.is_running = False
                    detection_manager.stop_camera()
                    await websocket.send_json({
                        "type": "status",
                        "message": "Detection stopped by user",
                        "running": False
                    })
                    should_stop = True  # Exit loop on stop command
                    
            except WebSocketDisconnect:
                print("Client disconnected from command handler")
                should_stop = True
            except Exception as e:
                print(f"Command handler error: {e}")
                # Don't stop on errors, keep listening
                await asyncio.sleep(0.1)
    
    # Run both tasks concurrently
    try:
        detection_task = asyncio.create_task(send_detection_data())
        command_task = asyncio.create_task(handle_commands())
        
        # Wait for either task to complete (stop command or connection issue)
        done, pending = await asyncio.wait(
            [detection_task, command_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        print("One task completed, cleaning up...")
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
    except Exception as e:
        print(f"WebSocket main error: {e}")
    finally:
        # Clean up connection but DON'T stop detection
        # This allows reconnection without restarting detection
        if websocket in active_connections:
            active_connections.remove(websocket)
        # Only stop if explicitly commanded, not on connection close
        # detection_manager.is_running = False  # Commented out to allow reconnection
        # detection_manager.stop_camera()  # Don't stop camera on disconnect
        print(f"WebSocket connection closed. Detection still running: {detection_manager.is_running}")


@router.post("/start")
async def start_detection():
    """Start detection process."""
    global detection_active
    
    if detection_active:
        return {
            "success": False,
            "message": "Detection already running"
        }
    
    if detection_manager.start_camera():
        detection_active = True
        return {
            "success": True,
            "message": "Detection started"
        }
    else:
        return {
            "success": False,
            "message": "Failed to start camera"
        }


@router.post("/stop")
async def stop_detection():
    """Stop detection process."""
    global detection_active
    
    detection_manager.stop_camera()
    detection_active = False
    
    return {
        "success": True,
        "message": "Detection stopped"
    }


@router.get("/status")
def get_detection_status():
    """Get current detection status."""
    return {
        "success": True,
        "data": {
            "running": detection_active,
            "has_camera": detection_manager.cap is not None and detection_manager.cap.isOpened()
        }
    }


@router.get("/health")
def health_check():
    """Check if stream service is running."""
    return {
        "success": True,
        "service": "Stream",
        "status": "running"
    }
