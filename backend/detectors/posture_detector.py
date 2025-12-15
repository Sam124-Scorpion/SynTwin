# detectors/posture_detector.py

import cv2

class PostureDetector:
    """
    Detects user's head alignment and posture orientation using face position.
    Works purely with OpenCV (no external ML model).
    """

    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        posture = "Straight"

        h, w = frame.shape[:2]
        center_x = w // 2
        center_y = h // 2

        if len(faces) == 0:
            posture = "Straight"
        else:
            for (x, y, fw, fh) in faces:
                face_center_x = x + fw // 2
                face_center_y = y + fh // 2

                # Calculate horizontal and vertical offsets
                horizontal_offset = abs(face_center_x - center_x)
                vertical_offset = abs(face_center_y - center_y)

                # Determine primary lean direction (horizontal vs vertical)
                if horizontal_offset > vertical_offset:
                    # Horizontal lean is more pronounced
                    if face_center_x < center_x - 80:
                        posture = "Leaning Left"
                    elif face_center_x > center_x + 80:
                        posture = "Leaning Right"
                    else:
                        posture = "Straight"
                else:
                    # Vertical lean is more pronounced
                    if face_center_y < center_y - 60:
                        posture = "Leaning Up"
                    elif face_center_y > center_y + 60:
                        posture = "Leaning Down"
                    else:
                        posture = "Straight"

        return {"posture": posture, "faces_detected": len(faces)}
