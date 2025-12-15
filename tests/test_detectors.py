# tests/test_detectors.py

import cv2
from backend.detectors.emotion_detector import EmotionDetector
from backend.detectors.smile_detector import SmileDetector
from backend.detectors.eye_tracker import EyeTracker
from backend.detectors.posture_detector import PostureDetector

def run_detectors_test():
    print("🔍 Running SynTwin Detectors Test...")

    # Initialize detectors
    emotion_detector = EmotionDetector()
    smile_detector = SmileDetector()
    eye_tracker = EyeTracker()
    posture_detector = PostureDetector()

    cap = cv2.VideoCapture(0)
    print("📸 Press 'q' to stop the webcam test.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        emotion = emotion_detector.detect(frame)
        smile = smile_detector.detect(frame)
        eyes = eye_tracker.detect(frame)
        posture = posture_detector.detect(frame)

        print(f"Emotion: {emotion} | Smile: {smile} | Eyes: {eyes} | Posture: {posture}")

        cv2.imshow("SynTwin Detectors", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_detectors_test()
