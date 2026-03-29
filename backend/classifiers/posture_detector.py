# backend/classifiers/posture_detector.py

"""
Real-time posture detection using MediaPipe Tasks PoseLandmarker (mediapipe >= 0.10).

Classifies posture into:
  Straight | Slouching | Slouching Forward | Leaning Sideways | Leaning Back | Looking Down

The lite pose model (~3 MB) is auto-downloaded to backend/assets/ on first use.
"""

import math
import os
import urllib.request
from typing import Dict

# Model asset (lite = fastest, ~3 MB)
_MODEL_URL  = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
)
_ASSET_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
_MODEL_PATH = os.path.join(_ASSET_DIR, "pose_landmarker_lite.task")


def _ensure_model():
    """Download the model file once if not already present."""
    if os.path.exists(_MODEL_PATH):
        return True
    os.makedirs(_ASSET_DIR, exist_ok=True)
    try:
        print("[PostureDetector] Downloading pose_landmarker_lite.task (~3 MB)...")
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
        print("[PostureDetector] pose_landmarker_lite.task downloaded.")
        return True
    except Exception as e:
        print(f"[PostureDetector] Could not download pose model: {e}")
        return False


# Lazy import of the Tasks vision API — avoids the broken mediapipe __init__ chain
def _import_tasks():
    try:
        from mediapipe.tasks.python.vision.pose_landmarker import (
            PoseLandmarker,
            PoseLandmarkerOptions,
        )
        from mediapipe.tasks.python.core.base_options import BaseOptions
        from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
        import mediapipe as _mp
        return PoseLandmarker, PoseLandmarkerOptions, BaseOptions, VisionTaskRunningMode, _mp
    except Exception as e:
        print(f"[PostureDetector] MediaPipe Tasks import failed: {e}")
        return None, None, None, None, None


class PostureDetector:
    """
    Detects posture from a video frame using MediaPipe Tasks PoseLandmarker.

    Usage:
        detector = PostureDetector()
        result = detector.detect(frame)   # BGR numpy array
        # -> {"posture": "Slouching", "confidence": 0.82, "details": {...}}
    """

    # PoseLandmarker landmark indices
    _NOSE       = 0
    _L_EAR      = 7
    _R_EAR      = 8
    _L_SHOULDER = 11
    _R_SHOULDER = 12
    _L_HIP      = 23
    _R_HIP      = 24

    def __init__(self):
        self.available = False
        self._landmarker = None
        self._mp = None

        if not _ensure_model():
            return

        PoseLandmarker, PoseLandmarkerOptions, BaseOptions, RunMode, mp_mod = _import_tasks()
        if PoseLandmarker is None:
            return

        try:
            options = PoseLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=_MODEL_PATH),
                running_mode=RunMode.IMAGE,
                num_poses=1,
                min_pose_detection_confidence=0.5,
                min_pose_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self._landmarker = PoseLandmarker.create_from_options(options)
            self._mp = mp_mod
            self.available = True
            print("[PostureDetector] Ready (MediaPipe Tasks PoseLandmarker).")
        except Exception as e:
            print(f"[PostureDetector] Failed to create PoseLandmarker: {e}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(self, frame) -> Dict:
        """
        Run posture detection on a BGR frame (numpy array).
        Returns dict with keys: posture, confidence, details.
        """
        if not self.available or self._landmarker is None:
            return self._fallback("PostureDetector not available")

        try:
            import cv2
            mp = self._mp
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = self._landmarker.detect(mp_image)
        except Exception as e:
            return self._fallback(f"Detection error: {e}")

        if not result.pose_landmarks or len(result.pose_landmarks) == 0:
            return self._fallback("No pose detected")

        lm = result.pose_landmarks[0]   # first (only) pose
        h, w = frame.shape[:2]

        def pt(idx):
            p = lm[idx]
            return p.x * w, p.y * h

        try:
            nx,  ny  = pt(self._NOSE)
            lsx, lsy = pt(self._L_SHOULDER)
            rsx, rsy = pt(self._R_SHOULDER)
            lhx, lhy = pt(self._L_HIP)
            rhx, rhy = pt(self._R_HIP)
            lex, ley = pt(self._L_EAR)
            rex, rey = pt(self._R_EAR)
        except Exception:
            return self._fallback("Landmark extraction failed")

        # --- Derived mid-points ---
        mid_sx = (lsx + rsx) / 2
        mid_sy = (lsy + rsy) / 2
        mid_hx = (lhx + rhx) / 2
        mid_hy = (lhy + rhy) / 2
        mid_ex = (lex + rex) / 2
        mid_ey = (ley + rey) / 2

        # --- Features ---
        # 1. Shoulder slope (°) from horizontal → lateral lean
        shoulder_slope_deg = math.degrees(math.atan2(rsy - lsy, rsx - lsx))

        # 2. Shoulder width normalised → scale-invariant slouch/lean-back signal
        shoulder_width_norm = abs(rsx - lsx) / w

        # 3. Spine angle (°): hip-mid → shoulder-mid vector, 0° = upright
        spine_angle_deg = math.degrees(
            math.atan2(mid_sx - mid_hx, -(mid_sy - mid_hy))
        )

        # 4. Ear forward offset: how far ears are ahead of shoulders (norm by ~10% w)
        ear_forward_norm = (mid_sx - mid_ex) / (w * 0.1 + 1e-6)

        # 5. Nose vertical drop below shoulder line (negative = head tilted down)
        nose_drop_norm = (ny - mid_sy) / (h * 0.1 + 1e-6)

        details = {
            "shoulder_slope_deg":  round(shoulder_slope_deg, 1),
            "shoulder_width_norm": round(shoulder_width_norm, 3),
            "spine_angle_deg":     round(spine_angle_deg, 1),
            "ear_forward_norm":    round(ear_forward_norm, 2),
            "nose_drop_norm":      round(nose_drop_norm, 2),
        }

        posture, confidence = self._classify(
            shoulder_slope_deg,
            shoulder_width_norm,
            spine_angle_deg,
            ear_forward_norm,
            nose_drop_norm,
        )

        return {"posture": posture, "confidence": round(confidence, 2), "details": details}

    def close(self):
        if self._landmarker is not None:
            self._landmarker.close()
            self._landmarker = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _classify(shoulder_slope, shoulder_width, spine_angle, ear_forward, nose_drop):
        """Rule-based mapping from geometric features → posture label + confidence."""

        # Looking Down — head dropped below shoulder line
        if nose_drop < -3.5:
            return "Looking Down", min(1.0, abs(nose_drop) / 6.0)

        # Leaning Sideways — steep shoulder tilt
        if abs(shoulder_slope) > 8.0:
            return "Leaning Sideways", min(1.0, abs(shoulder_slope) / 20.0)

        # Leaning Back — wide shoulders + backward spine vector
        if shoulder_width > 0.55 and spine_angle > 10:
            return "Leaning Back", min(1.0, (shoulder_width - 0.5) * 4)

        # Slouching Forward — ears in front of shoulders
        if ear_forward > 2.5:
            return "Slouching Forward", min(1.0, ear_forward / 5.0)

        # Slouching — narrow shoulders or collapsed spine
        if shoulder_width < 0.28 or (spine_angle < -8 and shoulder_width < 0.38):
            return "Slouching", min(1.0, max(0.5, 1.0 - shoulder_width / 0.35))

        # Straight — good posture
        conf = min(1.0, max(0.6, 1.0 - abs(shoulder_slope) / 15.0 - abs(ear_forward) / 6.0))
        return "Straight", conf

    @staticmethod
    def _fallback(reason: str = "") -> Dict:
        return {"posture": "Unknown", "confidence": 0.0, "details": {"reason": reason}}
