# detectors/emotion_detector.py

"""
Simplified emotion detection using OpenCV facial regions.
Uses facial geometry to infer emotion-like states
(since we’re not using deep models).
"""

import cv2
import numpy as np

class EmotionDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        emotion = "Neutral"
        emotion_confidence = 0.5

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            smiles = self.smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
            eyes = self.eye_cascade.detectMultiScale(roi_gray)

            if len(smiles) > 0 and len(eyes) >= 2:
                emotion = "Happy"
                emotion_confidence = 0.9
            elif len(smiles) == 0 and len(eyes) == 0:
                emotion = "Sad"
                emotion_confidence = 0.7
            elif len(smiles) == 0 and len(eyes) > 0:
                emotion = "Neutral"
                emotion_confidence = 0.6
            elif len(eyes) < 2:
                emotion = "Tired"
                emotion_confidence = 0.5

        return {"emotion": emotion, "confidence": emotion_confidence, "faces_detected": len(faces)}
