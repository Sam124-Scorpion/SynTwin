import cv2
import mediapipe as mp

# Load Haar cascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

# Mediapipe Pose for posture detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # ---------------- FACE + SMILE + EYE DETECTION ----------------
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    emotion = "Neutral"
    smile_status = "Not Smiling"
    eye_status = "Eyes Open"

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]

        # Smile detection
        smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.7, minNeighbors=20)
        if len(smiles) > 0:
            smile_status = "Smiling"
            emotion = "Happy"

        # Eye detection
        eyes = eye_cascade.detectMultiScale(roi_gray)
        if len(eyes) == 0:
            eye_status = "Eyes Closed"
            if emotion == "Neutral":
                emotion = "Sleepy"

        # Draw rectangle on face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 2)

    # ---------------- POSTURE DETECTION ----------------
    posture_status = "Unknown"
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        landmarks = results.pose_landmarks.landmark

        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
        nose = landmarks[mp_pose.PoseLandmark.NOSE]

        # Shoulder tilt check
        shoulder_tilt = right_shoulder.y - left_shoulder.y
        if shoulder_tilt > 0.05:
            posture_status = "Leaning Left"
        elif shoulder_tilt < -0.05:
            posture_status = "Leaning Right"
        else:
            # Head to hip alignment
            mid_hip_y = (left_hip.y + right_hip.y)/2
            if nose.y - mid_hip_y > 1.2:
                posture_status = "Slouching"
            else:
                posture_status = "Straight"

    # ---------------- DISPLAY RESULTS ----------------
    cv2.putText(frame, f"Emotion: {emotion}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.putText(frame, f"Smile: {smile_status}", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)
    cv2.putText(frame, f"Eyes: {eye_status}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,255), 2)
    cv2.putText(frame, f"Posture: {posture_status}", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

    cv2.imshow("SynTwin - All Detectors", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
