"""
Combined detector adapter for backend streaming.
Uses detector components backed by the new src implementation.
"""
from typing import Dict, List, Tuple

import cv2
import numpy as np

from .cnn_face_detector import CNNFaceDetector
from .emotion_cnn import EmotionCNN


class CombinedDetector:
    """
    Backward-compatible detector used by stream_service.
    """

    def __init__(self, confidence_threshold: float = 0.5, smoothing_window: int = 7):
        self.face_detector = CNNFaceDetector(confidence_threshold=confidence_threshold)
        self.emotion_detector = EmotionCNN()
        self.max_faces = 5
        self.min_face_size = (30, 30)
        self.smoothing_window = max(1, smoothing_window)
        self.emotion_history: List[str] = []

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        return self.face_detector.detect_faces(frame)

    def _smooth_emotion(self, emotion: str) -> str:
        self.emotion_history.append(emotion)
        if len(self.emotion_history) > self.smoothing_window:
            self.emotion_history.pop(0)

        counts: Dict[str, int] = {}
        for item in self.emotion_history:
            counts[item] = counts.get(item, 0) + 1

        return max(counts.items(), key=lambda item: item[1])[0]

    def _empty_result(self) -> Dict:
        return {
            "faces_detected": 0,
            "faces": [],
            "primary_emotion": "Neutral",
            "confidence": 0.0,
            "probabilities": {"Happy": 0.0, "Neutral": 1.0},
            "intensity": "Low",
            "face_detected": False,
        }

    def process_frame(self, frame: np.ndarray, apply_smoothing: bool = True) -> Dict:
        if frame is None or frame.size == 0:
            return self._empty_result()

        faces = self.detect_faces(frame)
        if not faces:
            return self._empty_result()

        face_results = []
        for bbox in faces[: self.max_faces]:
            x, y, w, h = bbox
            if w < self.min_face_size[0] or h < self.min_face_size[1]:
                continue

            emotion_result = self.emotion_detector.process_frame(frame, bbox)
            face_results.append(
                {
                    "bbox": bbox,
                    "emotion": emotion_result.get("emotion", "Neutral"),
                    "confidence": float(emotion_result.get("confidence", 0.0)),
                    "probabilities": emotion_result.get("probabilities", {"Happy": 0.0, "Neutral": 1.0}),
                    "intensity": emotion_result.get("intensity", "Low"),
                    "features": emotion_result.get("features", {}),
                }
            )

        if not face_results:
            return self._empty_result()

        primary = max(face_results, key=lambda item: item["bbox"][2] * item["bbox"][3])
        primary_emotion = primary["emotion"]
        if apply_smoothing:
            primary_emotion = self._smooth_emotion(primary_emotion)

        return {
            "faces_detected": len(faces),
            "faces": face_results,
            "primary_emotion": primary_emotion,
            "confidence": float(primary.get("confidence", 0.0)),
            "probabilities": primary.get("probabilities", {"Happy": 0.0, "Neutral": 1.0}),
            "intensity": primary.get("intensity", "Low"),
            "bbox": primary.get("bbox"),
            "face_detected": True,
            "lighting_condition": "normal",
            "lighting_quality": "good",
        }

    def draw_results(self, frame: np.ndarray, results: Dict) -> np.ndarray:
        annotated = frame.copy()

        if not results.get("face_detected"):
            cv2.putText(
                annotated,
                "No Face Detected",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )
            return annotated

        bbox = results.get("bbox")
        if not bbox and results.get("faces"):
            bbox = results["faces"][0].get("bbox")
        if not bbox:
            return annotated

        x, y, w, h = bbox
        emotion = results.get("primary_emotion", "Neutral")
        confidence = float(results.get("confidence", 0.0))

        color = (0, 255, 0) if emotion == "Happy" else (255, 200, 0)
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

        label = f"{emotion} ({confidence * 100:.0f}%)"
        cv2.putText(
            annotated,
            label,
            (x, max(20, y - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
        )
        return annotated

    def detect_and_annotate(self, frame: np.ndarray, apply_smoothing: bool = True, show_detailed_box: bool = True):
        results = self.process_frame(frame, apply_smoothing=apply_smoothing)
        return self.draw_results(frame, results), results

    def reset_smoothing(self):
        self.emotion_history = []

    def close(self):
        self.emotion_detector.close()
