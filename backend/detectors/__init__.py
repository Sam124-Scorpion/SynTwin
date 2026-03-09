"""
SynTwin Detectors Module
Simplified emotion detection: Happy, Neutral
"""

from .combined_detector import CombinedDetector
from .emotion_cnn import EmotionCNN
from .cnn_face_detector import CNNFaceDetector

__all__ = ['CombinedDetector', 'EmotionCNN', 'CNNFaceDetector']
