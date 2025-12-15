# detectors/eye_tracker.py

import cv2

class EyeTracker:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        eye_open = False
        blink_rate = 0
        eyes_detected = 0

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            eyes_detected = len(eyes)

            if eyes_detected >= 2:
                eye_open = True
            else:
                blink_rate += 1

        return {
            "eye_open": eye_open,
            "blink_rate": blink_rate,
            "eyes_detected": eyes_detected
        }
