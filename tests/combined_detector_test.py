

# success lower codes
import cv2
import time
from backend.detectors.combined_detector import CombinedDetector
from backend.simulator.twin_state import TwinState
import random
from datetime import datetime
from backend.database.db_logger import log_detection_to_db


def draw_emotion_gauge(frame, emotion, intensity):
    """
    Draws a horizontal emotion intensity bar on the frame.
    emotion: str  -> Detected emotion (e.g., 'Happy', 'Angry')
    intensity: int -> Value between 0–100
    """
    h, w, _ = frame.shape
    bar_x, bar_y = h - 30, h - 100
    bar_width, bar_height = 300, 25

    # Background bar
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)

    # Color map for different emotions
    color_map = {
        "Happy": (0, 255, 0),
        "Angry": (0, 0, 255),
        "Sad": (29, 30, 31),
        "Drowsy": (0, 255, 255),
        "Neutral": (200, 200, 200),
        "Focused": (255, 128, 0)
    }
    color = color_map.get(emotion, (255, 255, 255))

    # Filled bar portion
    filled = int((intensity / 100) * bar_width)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + filled, bar_y + bar_height), color, -1)

    # Text label
    label = f"{emotion}: {intensity:.0f}%"
    cv2.putText(frame, label, (bar_x, bar_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return frame


def main():
    print("🎬 Starting SynTwin Combined Detector Test (1.5 min session)...")

    # Try multiple camera indexes if needed
    cap = None
    for idx in range(3):
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if cap.isOpened():
            print(f"✅ Camera initialized at index {idx}")
            break
    if not cap or not cap.isOpened():
        print("❌ Error: Could not open any webcam.")
        return

    # Warm-up
    print("⏳ Warming up camera...")
    for _ in range(10):
        cap.read()
    time.sleep(1)

    # Initialize detectors and state
    detector = CombinedDetector()
    twin = TwinState()

    start_time = time.time()
    duration = 20  # ⏱️ 1.5 minutes (90 seconds) ,,,,, for now 10 seconds

    while True:
        elapsed = time.time() - start_time
        if elapsed >= duration:
            print("🕒 1.5 minutes completed but for now 10 seconds testing — auto stopping test.")
            break

        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            print("⚠️ Empty frame — skipping.")
            time.sleep(0.05)
            continue

        # Perform detection once per frame (returns both results + annotated frame)
        results, annotated_frame = detector.detect(frame)

        # Update Twin State dynamically based on detected results
        twin.update_from_inputs(
            cognitive={"state": "Focused" if results["emotion"] == "Happy" else "Distracted"},
            mood={"mood": results["emotion"]},
            sentiment=0.8 if results["emotion"] == "Happy" else -0.2,
            environment_feedback=f"Posture: {results['posture']}"
        )

        # Overlay the summary HUD
        processed_frame = detector.draw_detections(annotated_frame.copy(), results)

        # ---- FIX START: Normalize emotion names ----
        emotion_alias = {
            "sad": "Sad",
            "down": "Sad",
            "unhappy": "Sad",
            "sleepy": "Drowsy",
            "tired": "Drowsy",
            "drowsy": "Drowsy",
        }

        # ---- FIX START: Emotion Soft-Logic ----
        normalized_emotion = results["emotion"].strip().lower()

        # Map aliases manually
        if normalized_emotion in ["tired", "sleepy", "drowsy"]:
            results["emotion"] = "Drowsy"

        elif normalized_emotion in ["sad", "down", "unhappy"]:
            results["emotion"] = "Sad"

        # Expand neutral into Sad/Drowsy using posture or eyes
        elif normalized_emotion == "neutral":
            if results.get("eyes") == "Closed":
                results["emotion"] = "Drowsy"
            elif results.get("posture") in ["Slouching", "Lean Forward"]:
                results["emotion"] = "Sad"
        # ---- FIX END ----

        intensity = random.randint(50, 100) if results["emotion"] != "Neutral" else random.randint(30, 60)
        processed_frame = draw_emotion_gauge(processed_frame, results["emotion"], intensity)

        if processed_frame is not None and processed_frame.size > 0:
            cv2.imshow("🧠 SynTwin Live Analytics", processed_frame)
        else:
            print("⚠️ Invalid processed frame.")

        # Log to database
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "emotion": results["emotion"],
            "smile": results["smile"],
            "eyes": results["eyes"],
            "posture": results["posture"],
            "sentiment": 0.8 if results["emotion"] == "Happy" else -0.2,
            "environment_feedback": f"Posture: {results['posture']}"
        }
        log_detection_to_db(entry)

        # Allow manual exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Exiting early by user request.")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("✅ SynTwin Detector Session Ended.")
    print("🔍 Raw Emotion Output:", results["emotion"])


if __name__ == "__main__":
    main()
