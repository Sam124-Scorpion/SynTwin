# # backend/detectors/combined_detector.py
#
# import cv2
# import mediapipe as mp
#
#
# class CombinedDetector:
#     """
#     Combines face, smile, eye, and posture detection
#     using Haar Cascades + MediaPipe Pose.
#     """
#
#     def __init__(self):
#         # Load Haar cascades
#         self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
#         self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")
#         self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
#
#         # Initialize MediaPipe Pose
#         self.mp_pose = mp.solutions.pose
#         self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
#         self.mp_drawing = mp.solutions.drawing_utils
#
#     def detect(self, frame):
#         """
#         Run all detectors on a frame and return structured results.
#         """
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
#
#         emotion = "Neutral"
#         smile_status = "Not Smiling"
#         eye_status = "Eyes Open"
#
#         for (x, y, w, h) in faces:
#             roi_gray = gray[y:y + h, x:x + w]
#
#             # Smile detection
#             smiles = self.smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.7, minNeighbors=20)
#             if len(smiles) > 0:
#                 smile_status = "Smiling"
#                 emotion = "Happy"
#
#             # Eye detection
#             eyes = self.eye_cascade.detectMultiScale(roi_gray)
#             if len(eyes) == 0:
#                 eye_status = "Eyes Closed"
#                 if emotion == "Neutral":
#                     emotion = "Sleepy"
#
#         # Posture detection
#         posture_status = "Unknown"
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = self.pose.process(rgb_frame)
#
#         if results.pose_landmarks:
#             landmarks = results.pose_landmarks.landmark
#
#             left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
#             right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
#             left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
#             right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
#             nose = landmarks[self.mp_pose.PoseLandmark.NOSE]
#
#             # Shoulder tilt
#             shoulder_tilt = right_shoulder.y - left_shoulder.y
#             if shoulder_tilt > 0.05:
#                 posture_status = "Leaning Left"
#             elif shoulder_tilt < -0.05:
#                 posture_status = "Leaning Right"
#             else:
#                 mid_hip_y = (left_hip.y + right_hip.y) / 2
#                 if nose.y - mid_hip_y > 1.2:
#                     posture_status = "Slouching"
#                 else:
#                     posture_status = "Straight"
#
#         return {
#             "emotion": emotion,
#             "smile": smile_status,
#             "eyes": eye_status,
#             "posture": posture_status,
#             "faces_detected": len(faces),
#             "pose_landmarks": results.pose_landmarks
#         }
#
#     def draw_detections(self, frame, results):
#         """
#         Draw annotations and text overlays on the frame.
#         """
#         if results.get("pose_landmarks"):
#             self.mp_drawing.draw_landmarks(
#                 frame, results["pose_landmarks"], self.mp_pose.POSE_CONNECTIONS
#             )
#
#         cv2.putText(frame, f"Emotion: {results['emotion']}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
#         cv2.putText(frame, f"Smile: {results['smile']}", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)
#         cv2.putText(frame, f"Eyes: {results['eyes']}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,255), 2)
#         cv2.putText(frame, f"Posture: {results['posture']}", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
#
#         return frame


# backend/detectors/combined_detector.py
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='google.protobuf')

import cv2
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("WARNING: mediapipe not available, advanced pose detection disabled")

from backend.analytics.data_logger import DataLogger


class CombinedDetector:
    """
    Advanced Combined Detector for SynTwin
    -----------------------------------------------------
    Detects:
      - Face
      - Eyes (open/closed)
      - Smile (intensity)
      - Emotion (Happy, Angry, Drowsy, Focused, Sad, Neutral)
      - Posture (Straight, Slouching, Leaning)
    """

    def __init__(self, enable_logging=True):
        # Load Haar cascades
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
        
        # Additional cascades for emotion detection
        # Use frontalface cascade for eyebrow region detection (proxy for furrowed brows)
        self.eyebrow_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        # Mediapipe Pose model (optional)
        if MEDIAPIPE_AVAILABLE:
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)
            self.mp_drawing = mp.solutions.drawing_utils
        else:
            self.mp_pose = None
            self.pose = None
            self.mp_drawing = None

        # Logger setup
        self.enable_logging = enable_logging
        if self.enable_logging:
            self.logger = DataLogger()

        # Emotion color map for visualization
        self.color_map = {
            "Happy": (0, 255, 0),
            "Angry": (0, 0, 255),
            "Drowsy": (255, 0, 0),
            "Sad": (128, 0, 128),
            "Focused": (0, 255, 255),
            "Neutral": (200, 200, 200)
        }
        
        # Smoothing for detection stability (reduce flickering)
        self.prev_emotion = "Neutral"
        self.prev_posture = "Straight"
        self.prev_smile = "Not Smiling"
        self.prev_eyes = "Eyes Open"
        self.emotion_counter = {}
        self.posture_counter = {}
        self.smile_counter = {}
        self.eyes_counter = {}
        self.smoothing_window = 3  # Reduced for faster real-time response
        
        # Drowsy detection tracking
        self.eyes_closed_frames = 0
        self.drowsy_threshold = 3  # Consecutive frames before marking as drowsy
        
        # Frame skip counter for performance optimization
        self.frame_count = 0

    # ----------------------------------------------------------------------
    def _smooth_detection(self, current_value, counter_dict, prev_value):
        """Apply temporal smoothing with faster response to real changes."""
        # Add current detection to counter
        if current_value not in counter_dict:
            counter_dict[current_value] = 0
        counter_dict[current_value] += 2  # Weight current frame more heavily
        
        # Faster decay for more responsive detection
        for key in list(counter_dict.keys()):
            if key != current_value:
                counter_dict[key] = max(0, counter_dict[key] - 1.5)
                if counter_dict[key] < 1:
                    del counter_dict[key]
        
        # Return most stable value with lower threshold
        if not counter_dict:
            return current_value
        
        max_count = max(counter_dict.values())
        if max_count >= self.smoothing_window:
            return max(counter_dict, key=counter_dict.get)
        
        # Return current value if significantly different
        return current_value if current_value != prev_value and counter_dict.get(current_value, 0) >= 2 else prev_value
    
    # ----------------------------------------------------------------------
    def detect(self, frame):
        """Run detection on a single frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        emotion, smile_status, eye_status = "Neutral", "Not Smiling", "Eyes Open"

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + w]

            # ========== ADVANCED EYE DETECTION ==========
            # Detect eyes in upper half of face for accuracy
            upper_roi = roi_gray[0:int(h*0.6), :]
            eyes = self.eye_cascade.detectMultiScale(
                upper_roi, 
                scaleFactor=1.1, 
                minNeighbors=10,
                minSize=(int(w*0.15), int(h*0.1)),
                maxSize=(int(w*0.4), int(h*0.3))
            )
            
            # Filter eyes by position (should be in upper portion and horizontally separated)
            valid_eyes = []
            for (ex, ey, ew, eh) in eyes:
                # Eye should be in upper half and reasonable size
                eye_area = ew * eh
                face_area = w * h
                if 0.02 < (eye_area / face_area) < 0.15:
                    valid_eyes.append((ex, ey, ew, eh))
            
            # Check if we have two eyes that are horizontally separated
            eye_count = len(valid_eyes)
            eye_openness = 0.0  # 0 = closed, 1+ = wide open
            
            if eye_count >= 2:
                # Sort by x position to get left and right eye
                valid_eyes_sorted = sorted(valid_eyes, key=lambda e: e[0])
                left_eye = valid_eyes_sorted[0]
                right_eye = valid_eyes_sorted[1]
                eye_distance = abs(right_eye[0] - left_eye[0])
                
                # Eyes should be reasonably separated (at least 20% of face width)
                if eye_distance > w * 0.2:
                    eye_status = "Eyes Open"
                    eye_count = 2
                    
                    # Calculate eye openness intensity
                    # Normal eye area is ~5-8% of face, wide eyes are 10%+
                    left_eye_area = left_eye[2] * left_eye[3]
                    right_eye_area = right_eye[2] * right_eye[3]
                    total_eye_area = left_eye_area + right_eye_area
                    face_area = w * h
                    eye_openness = total_eye_area / face_area
                    
                    # Normalize: 0.1 = normal, 0.15+ = wide open
                    # Scale so 1.0 = normal, 1.5+ = wide
                    eye_openness = eye_openness / 0.1
                else:
                    eye_status = "Eyes Closed"
                    eye_count = 0
                    eye_openness = 0
            else:
                eye_status = "Eyes Closed"
                eye_count = 0
                eye_openness = 0
            
            # Detect wide eyes (staring, intense gaze)
            are_eyes_wide = eye_openness > 1.4

            # ========== SMILE DETECTION ==========
            # Detect smile in mouth region (lower 60% of face)
            mouth_roi = roi_gray[int(h*0.5):, :]
            smiles = self.smile_cascade.detectMultiScale(
                mouth_roi,
                scaleFactor=1.7,
                minNeighbors=18,
                minSize=(int(w*0.25), int(h*0.1))
            )
            
            smile_intensity = 0
            smile_count = len(smiles)
            smile_status = "Not Smiling"
            
            if smile_count > 0:
                # Get the largest smile detection
                largest_smile = max(smiles, key=lambda s: s[2] * s[3])
                (sx, sy, sw, sh) = largest_smile
                
                # Calculate smile intensity based on area
                smile_area = sw * sh
                face_area = w * h
                smile_intensity = smile_area / face_area
                
                # Consider it smiling if area is significant (more lenient)
                if smile_intensity > 0.08:
                    smile_status = "Smiling"
                    # Boost confidence with multiple detections
                    if smile_count >= 2:
                        smile_intensity = min(1.0, smile_intensity * 1.3)

            # ========== EYEBROW/FOREHEAD TENSION DETECTION (for Angry) ==========
            # Detect tension in upper face region (forehead/eyebrow area)
            forehead_roi = roi_gray[0:int(h*0.35), :]
            # Look for sharp edge features indicating furrowed brows
            forehead_edges = cv2.Canny(forehead_roi, 50, 150)
            tension_density = cv2.countNonZero(forehead_edges) / (forehead_roi.shape[0] * forehead_roi.shape[1])
            
            # High tension in forehead indicates furrowed brows (angry)
            is_tense_forehead = tension_density > 0.11
            
            # Detect mouth compression (tight lips, no smile) for angry
            mouth_compressed = (smile_count == 0 and smile_intensity < 0.05)
            
            # Detect jaw tension in lower face
            jaw_roi = roi_gray[int(h*0.6):, :]
            jaw_edges = cv2.Canny(jaw_roi, 40, 120)
            jaw_tension = cv2.countNonZero(jaw_edges) / (jaw_roi.shape[0] * jaw_roi.shape[1])
            is_jaw_tense = jaw_tension > 0.08

            # ========== EMOTION CLASSIFICATION ==========
            # Priority-based emotion detection with enhanced accuracy
            
            # Track eyes closed duration for better drowsy detection
            if eye_count == 0:
                self.eyes_closed_frames += 1
            else:
                self.eyes_closed_frames = 0
            
            # Calculate anger score (multi-factor)
            anger_indicators = 0
            if are_eyes_wide: anger_indicators += 2  # Wide eyes is strong indicator
            if mouth_compressed: anger_indicators += 1.5
            if is_tense_forehead: anger_indicators += 1.5
            if is_jaw_tense: anger_indicators += 1
            
            # 1. ANGRY - Multiple indicators present
            # Method 1: Wide eyes + no smile (strong angry signal)
            # Method 2: Tense forehead + mouth + eyes open
            if (are_eyes_wide and mouth_compressed and eye_count == 2) or anger_indicators >= 3.5:
                emotion = "Angry"
            
            # 2. DROWSY - Eyes closed for multiple frames (more confident)
            elif self.eyes_closed_frames >= self.drowsy_threshold:
                emotion = "Drowsy"
            
            # 3. HAPPY - Smiling detected
            elif smile_status == "Smiling" and smile_intensity > 0.08:
                emotion = "Happy"
            
            # 4. FOCUSED - Eyes open, neutral face, close to camera, no tension
            elif eye_count == 2 and smile_status == "Not Smiling" and w > 140 and not is_tense_forehead and not are_eyes_wide:
                emotion = "Focused"
            
            # 5. NEUTRAL - Default for normal expressions
            else:
                emotion = "Neutral"
            
            # Smooth all detections to reduce flickering
            emotion = self._smooth_detection(emotion, self.emotion_counter, self.prev_emotion)
            smile_status = self._smooth_detection(smile_status, self.smile_counter, self.prev_smile)
            eye_status = self._smooth_detection(eye_status, self.eyes_counter, self.prev_eyes)
            
            self.prev_emotion = emotion
            self.prev_smile = smile_status
            self.prev_eyes = eye_status

            # Draw face bounding box
            color = self.color_map.get(emotion, (255, 255, 255))
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"{emotion}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # ========== ENHANCED POSTURE DETECTION ==========
        posture_status = "Straight"
        results = None  # Initialize results variable
        
        if MEDIAPIPE_AVAILABLE and self.pose is not None:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)

            if results.pose_landmarks:
                # Draw pose landmarks with lighter color for better visibility
                self.mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 200, 0), thickness=2)
                )

                landmarks = results.pose_landmarks.landmark
                
                # Get key landmarks with visibility check
                left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
                left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
                right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
                nose = landmarks[self.mp_pose.PoseLandmark.NOSE]
                left_ear = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR]
                right_ear = landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR]
                
                # Only proceed if key landmarks are visible
                min_visibility = 0.5
                if (left_shoulder.visibility > min_visibility and 
                    right_shoulder.visibility > min_visibility and
                    nose.visibility > min_visibility):
                    
                    # Calculate reference points
                    shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
                    shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
                    hip_center_y = (left_hip.y + right_hip.y) / 2
                    ear_center_y = (left_ear.y + right_ear.y) / 2
                    
                    # Calculate comprehensive posture metrics
                    # 1. Shoulder alignment (side tilt)
                    shoulder_tilt = right_shoulder.y - left_shoulder.y
                    
                    # 2. Head-shoulder alignment (forward/back)
                    head_forward = nose.x - shoulder_center_x
                    
                    # 3. Neck angle (head up/down relative to shoulders)
                    neck_vertical = nose.y - shoulder_center_y
                    
                    # 4. Spine alignment (shoulders relative to hips)
                    if left_hip.visibility > min_visibility and right_hip.visibility > min_visibility:
                        hip_center_x = (left_hip.x + right_hip.x) / 2
                        spine_alignment = shoulder_center_x - hip_center_x
                        torso_length = abs(shoulder_center_y - hip_center_y)
                    else:
                        spine_alignment = 0
                        torso_length = 0.3
                    
                    # 5. Head tilt using ears
                    if left_ear.visibility > min_visibility and right_ear.visibility > min_visibility:
                        head_tilt = right_ear.y - left_ear.y
                    else:
                        head_tilt = 0
                    
                    # ========== POSTURE CLASSIFICATION ==========
                    # Clear hierarchy with calibrated thresholds
                    
                    # 1. SIDE LEAN (Left/Right) - Check shoulder tilt first
                    if abs(shoulder_tilt) > 0.04:
                        if shoulder_tilt > 0.04:
                            posture_status = "Leaning Left"
                        else:
                            posture_status = "Leaning Right"
                    
                    # 2. HEAD TILT (using ear alignment)
                    elif abs(head_tilt) > 0.035:
                        if head_tilt > 0:
                            posture_status = "Head Tilted Left"
                        else:
                            posture_status = "Head Tilted Right"
                    
                    # 3. FORWARD SLOUCH (head forward of body centerline)
                    elif abs(head_forward) > 0.08:
                        if neck_vertical > 0.08:  # Head also dropped down
                            posture_status = "Slouching Forward"
                        else:
                            posture_status = "Leaning Forward"
                    
                    # 4. VERTICAL HEAD POSITION (looking up/down)
                    elif neck_vertical < -0.08:
                        posture_status = "Looking Up"
                    elif neck_vertical > 0.10:
                        posture_status = "Looking Down"
                    
                    # 5. SPINE MISALIGNMENT (shoulders off center from hips)
                    elif torso_length > 0.2 and abs(spine_alignment) > 0.06:
                        if spine_alignment > 0:
                            posture_status = "Torso Shifted Right"
                        else:
                            posture_status = "Torso Shifted Left"
                    
                    # 6. GOOD POSTURE (upright and aligned)
                    else:
                        posture_status = "Straight"

                    # Apply lighter smoothing for real-time response
                    posture_status = self._smooth_detection(posture_status, self.posture_counter, self.prev_posture)
                    self.prev_posture = posture_status
                    
                    # Enhanced posture-emotion correlation for better Drowsy detection
                    if posture_status in ["Looking Down", "Slouching Forward"] and self.eyes_closed_frames >= 1:
                        # Head down + eyes closed = definitely drowsy (even with fewer frames)
                        emotion = "Drowsy"
                    elif posture_status in ["Slouching Forward", "Looking Down"] and emotion == "Neutral":
                        emotion = "Sad"
                    elif posture_status == "Straight" and emotion == "Neutral" and eye_count == 2:
                        emotion = "Focused"
        else:
            # Fallback: Basic posture detection without mediapipe
            posture_status = "Straight"

        # ---------------- FINAL DATA PACKAGE ----------------
        result_data = {
            "emotion": emotion,
            "smile": smile_status,
            "eyes": eye_status,
            "posture": posture_status,
            "faces_detected": len(faces),
            "pose_landmarks": results.pose_landmarks if results else None
        }

        if self.enable_logging:
            self.logger.log_entry(result_data)

        return result_data, frame

    # ----------------------------------------------------------------------
    def draw_detections(self, frame, results):
        """Overlay emotion and posture text on frame"""
        if results is None:
            return frame

        cv2.putText(frame, f"Emotion: {results['emotion']}", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"Smile: {results['smile']}", (30, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, f"Eyes: {results['eyes']}", (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
        cv2.putText(frame, f"Posture: {results['posture']}", (30, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        return frame
