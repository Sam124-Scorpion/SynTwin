# detectors/fusion.py
"""
Fusion module for SynTwin Detectors.

Combines results from:
- EmotionDetector
- SmileDetector
- EyeTracker
- PostureDetector

and returns a single unified snapshot of the user’s physical-emotional state.
"""

import cv2
from backend.detectors.emotion_detector import EmotionDetector
from backend.detectors.smile_detector import SmileDetector
from backend.detectors.eye_tracker import EyeTracker
from backend.detectors.posture_detector import PostureDetector


class DetectorFusion:
    def __init__(self):
        self.emotion_detector = EmotionDetector()
        self.smile_detector = SmileDetector()
        self.eye_tracker = EyeTracker()
        self.posture_detector = PostureDetector()

    def analyze_frame(self, frame):
        """
        Runs all detectors on a single frame and fuses the results.
        Returns a dictionary summarizing the user's state.
        """
        results = {}
        results["emotion"] = self.emotion_detector.detect(frame)
        results["smile"] = self.smile_detector.detect(frame)
        results["eyes"] = self.eye_tracker.detect(frame)
        results["posture"] = self.posture_detector.detect(frame)

        # Derive higher-level features for classifier
        fused_state = {
            "emotion": results["emotion"]["emotion"],
            "smile_score": results["smile"]["smile_score"],
            "blink_rate": results["eyes"]["blink_rate"],
            "eyes_detected": results["eyes"]["eyes_detected"],
            "posture": results["posture"]["posture"],
            "faces_detected": results["emotion"]["faces_detected"],
            "attention": self._derive_attention(results),
            "yawn_freq": self._estimate_yawn(results),
        }

        return {"raw": results, "fused": fused_state}

    def _derive_attention(self, results):
        """
        Simple heuristic for 'attention' based on eyes and posture.
        """
        eyes = results["eyes"]
        posture = results["posture"]["posture"]

        attention = 0.5
        if eyes["eyes_detected"] >= 2 and "Centered" in posture:
            attention = 0.9
        elif eyes["eyes_detected"] == 1 or "Leaning" in posture:
            attention = 0.6
        elif eyes["eyes_detected"] == 0:
            attention = 0.2

        return round(attention, 2)

    def _estimate_yawn(self, results):
        """
        Placeholder for yawning estimation (if mouth open detection is added later).
        Currently approximates yawn frequency inversely to smile detection.
        """
        smile_score = results["smile"]["smile_score"]
        if smile_score > 50:
            return 0
        elif smile_score > 20:
            return 1
        else:
            return 2

