"""
Backend emotion detector adapter.
Uses the new src/core emotion analyzer implementation.
"""
from typing import Dict, Tuple

import numpy as np

from backend.src.core.analyzer import EmotionAnalyzer


class EmotionCNN:
    """
    Compatibility adapter for legacy backend API.
    Delegates emotion analysis to src.core.analyzer.EmotionAnalyzer.
    """

    def __init__(self):
        self.emotions = ["Happy", "Neutral"]
        self._analyzer = EmotionAnalyzer()
        self._analyzer.start()

    def _to_title_probs(self, probabilities: Dict[str, float]) -> Dict[str, float]:
        if not probabilities:
            return {"Happy": 0.0, "Neutral": 1.0}

        title_probs = {k.title(): float(v) for k, v in probabilities.items()}
        if "Happy" not in title_probs:
            title_probs["Happy"] = 0.0
        if "Neutral" not in title_probs:
            title_probs["Neutral"] = 0.0

        total = sum(title_probs.values())
        if total > 0:
            title_probs = {k: v / total for k, v in title_probs.items()}

        return title_probs

    def process_frame(self, frame: np.ndarray, face_bbox: Tuple[int, int, int, int]) -> Dict:
        x, y, w, h = face_bbox

        if frame is None or frame.size == 0 or w <= 0 or h <= 0:
            return {
                "emotion": "Neutral",
                "confidence": 0.0,
                "probabilities": {"Happy": 0.0, "Neutral": 1.0},
                "intensity": "Low",
                "features": {},
            }

        frame_h, frame_w = frame.shape[:2]
        x = max(0, x)
        y = max(0, y)
        w = min(w, frame_w - x)
        h = min(h, frame_h - y)

        face_roi = frame[y : y + h, x : x + w]
        if face_roi.size == 0:
            return {
                "emotion": "Neutral",
                "confidence": 0.0,
                "probabilities": {"Happy": 0.0, "Neutral": 1.0},
                "intensity": "Low",
                "features": {},
            }

        self._analyzer.analyze(face_roi)
        emotion, probabilities = self._analyzer.get_results()

        emotion_title = str(emotion).title() if emotion else "Neutral"
        mapped_probabilities = self._to_title_probs(probabilities)
        confidence = float(mapped_probabilities.get(emotion_title, 0.0))

        if confidence > 0.8:
            intensity = "High"
        elif confidence > 0.5:
            intensity = "Medium"
        else:
            intensity = "Low"

        return {
            "emotion": emotion_title,
            "confidence": confidence,
            "probabilities": mapped_probabilities,
            "intensity": intensity,
            "features": {},
        }

    def close(self):
        self._analyzer.stop()
