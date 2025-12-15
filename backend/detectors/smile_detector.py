# detectors/smile_detector.py

import cv2

class SmileDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        smile_detected = False
        smile_score = 0

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            smiles = self.smile_cascade.detectMultiScale(roi_gray, 1.8, 20)

            if len(smiles) > 0:
                smile_detected = True
                smile_score = min(100, len(smiles) * 10)

        return {"smile": smile_detected, "smile_score": smile_score}
