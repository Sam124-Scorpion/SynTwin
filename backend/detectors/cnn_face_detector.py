"""
Backend face detector adapter.
Uses the new src/core detector implementation.
"""
from typing import List, Tuple

import numpy as np

from backend.src.core.face_detector import SimpleFaceDetector


class CNNFaceDetector:
    """
    Compatibility adapter for legacy backend API.
    Internally delegates to src.core.face_detector.SimpleFaceDetector.
    """

    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold
        self._detector = SimpleFaceDetector()

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        if frame is None or frame.size == 0:
            return []
        faces = self._detector.detect(frame)
        return [tuple(map(int, face)) for face in faces]

    def set_confidence_threshold(self, threshold: float):
        self.confidence_threshold = max(0.0, min(1.0, threshold))

    def is_model_loaded(self) -> bool:
        return True

    def get_model_info(self) -> dict:
        return {
            "model_loaded": True,
            "model_type": "SimpleFaceDetector (Haar Cascade)",
            "confidence_threshold": self.confidence_threshold,
        }
