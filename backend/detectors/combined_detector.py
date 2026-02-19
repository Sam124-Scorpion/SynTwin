"""
Combined Face and Emotion Detection Module
Integrates CNN face detection with CNN emotion recognition
"""
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from .cnn_face_detector import CNNFaceDetector
from .emotion_cnn import EmotionCNN


class CombinedDetector:
    """
    Combined detector that performs face detection and emotion recognition
    Optimized for real-time video processing with happy emotion detection
    """
    
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize the combined detector
        
        Args:
            confidence_threshold: Minimum confidence for face detection (0.0 - 1.0)
        """
        self.face_detector = CNNFaceDetector(confidence_threshold=confidence_threshold)
        self.emotion_detector = EmotionCNN()
        
        # Processing parameters
        self.min_face_size = (30, 30)
        self.max_faces = 5
        
        # Temporal smoothing for stable emotion detection
        self.emotion_history = []
        self.history_size = 7  # Increased from 5 for more stability
        self.last_stable_emotion = None  # Track last confident emotion
        
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in frame
        
        Args:
            frame: Input BGR frame
            
        Returns:
            List of face bounding boxes as (x, y, w, h) tuples
        """
        return self.face_detector.detect_faces(frame)
    
    def process_frame(self, frame: np.ndarray, apply_smoothing: bool = True) -> Dict:
        """
        Process a frame: detect faces and recognize emotions
        
        Args:
            frame: Input BGR frame
            apply_smoothing: Whether to apply temporal smoothing
            
        Returns:
            Dictionary containing detection results
        """
        if frame is None or frame.size == 0:
            return self._empty_result()
        
        # Detect faces
        faces = self.detect_faces(frame)
        
        if len(faces) == 0:
            return {
                'faces_detected': 0,
                'faces': [],
                'primary_emotion': 'Neutral',
                'confidence': 0.0
            }
        
        # Process each face
        results = []
        for face_bbox in faces[:self.max_faces]:
            x, y, w, h = face_bbox
            
            # Skip small faces
            if w < self.min_face_size[0] or h < self.min_face_size[1]:
                continue
            
            # Extract and process face
            emotion_result = self.emotion_detector.process_frame(frame, face_bbox)
            
            results.append({
                'bbox': face_bbox,
                'emotion': emotion_result['emotion'],
                'confidence': emotion_result['confidence'],
                'probabilities': emotion_result['probabilities'],
                'intensity': emotion_result.get('intensity', None),
                'features': emotion_result.get('features', {})
            })
        
        if len(results) == 0:
            return {
                'faces_detected': len(faces),
                'faces': [],
                'primary_emotion': 'Neutral',
                'confidence': 0.0
            }
        
        # Select primary result (largest face or highest confidence)
        primary_result = max(results, key=lambda r: r['bbox'][2] * r['bbox'][3])
        
        # Apply temporal smoothing if enabled
        if apply_smoothing:
            primary_result = self._smooth_emotion(primary_result)
        
        return {
            'faces_detected': len(faces),
            'faces': results,
            'primary_emotion': primary_result['emotion'],
            'confidence': primary_result['confidence'],
            'probabilities': primary_result['probabilities'],
            'intensity': primary_result.get('intensity', None),
            'bbox': primary_result['bbox']
        }
    
    def _smooth_emotion(self, current_result: Dict) -> Dict:
        """
        Apply temporal smoothing to emotion detection with hysteresis
        
        Args:
            current_result: Current frame's emotion result
            
        Returns:
            Smoothed emotion result
        """
        # Add current result to history
        self.emotion_history.append(current_result)
        
        # Keep only recent history
        if len(self.emotion_history) > self.history_size:
            self.emotion_history.pop(0)
        
        # If not enough history, return current result
        if len(self.emotion_history) < 4:  # Increased from 3
            return current_result
        
        # Average probabilities across history with exponential weighting (recent frames matter more)
        avg_probabilities = {
            'Happy': 0.0,
            'Angry': 0.0,
            'Neutral': 0.0
        }
        
        total_weight = 0.0
        for i, result in enumerate(self.emotion_history):
            # Exponential weight: recent frames weighted more heavily
            weight = 0.7 + (i / len(self.emotion_history)) * 0.3  # 0.7 to 1.0
            total_weight += weight
            
            for emotion, prob in result['probabilities'].items():
                avg_probabilities[emotion] += prob * weight
        
        # Normalize by total weight
        for emotion in avg_probabilities:
            avg_probabilities[emotion] /= total_weight
        
        # Determine smoothed emotion
        smoothed_emotion = max(avg_probabilities, key=avg_probabilities.get)
        smoothed_confidence = avg_probabilities[smoothed_emotion]
        
        # Apply hysteresis: require significant change to switch emotions
        if self.last_stable_emotion and self.last_stable_emotion != smoothed_emotion:
            # Current emotion needs at least 20% lead to override previous stable emotion
            if avg_probabilities[smoothed_emotion] - avg_probabilities[self.last_stable_emotion] < 0.20:
                smoothed_emotion = self.last_stable_emotion
                smoothed_confidence = avg_probabilities[self.last_stable_emotion]
        
        # Update last stable emotion if confidence is high
        if smoothed_confidence > 0.60:
            self.last_stable_emotion = smoothed_emotion
        
        # Update result with smoothed values
        smoothed_result = current_result.copy()
        smoothed_result['emotion'] = smoothed_emotion
        smoothed_result['confidence'] = smoothed_confidence
        smoothed_result['probabilities'] = avg_probabilities
        
        return smoothed_result
    
    def reset_smoothing(self):
        """Reset emotion history for temporal smoothing"""
        self.emotion_history = []
        self.last_stable_emotion = None
    
    def draw_results(self, frame: np.ndarray, results: Dict) -> np.ndarray:
        """
        Draw detection results on frame
        
        Args:
            frame: Input frame
            results: Detection results from process_frame
            
        Returns:
            Frame with drawn annotations
        """
        annotated = frame.copy()
        
        if results['faces_detected'] == 0:
            return annotated
        
        for face_result in results['faces']:
            x, y, w, h = face_result['bbox']
            emotion = face_result['emotion']
            confidence = face_result['confidence']
            
            # Choose color based on emotion
            if emotion == 'Happy':
                color = (0, 255, 0)  # Green
            elif emotion == 'Angry':
                color = (0, 0, 255)  # Red
            else:
                color = (255, 255, 0)  # Cyan
            
            # Draw bounding box
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
            
            # Prepare label
            label = f"{emotion} ({confidence:.0%})"
            if face_result.get('intensity'):
                label += f" [{face_result['intensity']}]"
            
            # Draw label background
            (label_w, label_h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            cv2.rectangle(
                annotated,
                (x, y - label_h - 10),
                (x + label_w, y),
                color,
                -1
            )
            
            # Draw label text
            cv2.putText(
                annotated,
                label,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
        
        # Draw summary at top
        summary = f"Faces: {results['faces_detected']} | Primary: {results['primary_emotion']}"
        cv2.putText(
            annotated,
            summary,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        return annotated
    
    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            'faces_detected': 0,
            'faces': [],
            'primary_emotion': 'Neutral',
            'confidence': 0.0
        }
    
    def get_statistics(self) -> Dict:
        """
        Get current detection statistics
        
        Returns:
            Dictionary with detector statistics
        """
        emotion_counts = {'Happy': 0, 'Angry': 0, 'Neutral': 0}
        
        for result in self.emotion_history:
            emotion = result['emotion']
            emotion_counts[emotion] += 1
        
        return {
            'history_size': len(self.emotion_history),
            'emotion_distribution': emotion_counts,
            'smoothing_enabled': len(self.emotion_history) >= 3
        }


# Standalone testing
if __name__ == "__main__":
    print("CombinedDetector - Test Mode")
    print("=" * 60)
    
    detector = CombinedDetector(confidence_threshold=0.5)
    
    # Create test frame
    test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 120
    
    # Simulate face region
    test_frame[100:300, 200:400] = 140  # Brighter face region
    test_frame[220:280, 240:360] = 160  # Bright mouth (smile)
    
    # Process frame
    results = detector.process_frame(test_frame, apply_smoothing=False)
    
    print(f"\nDetection Results:")
    print(f"Faces Detected: {results['faces_detected']}")
    print(f"Primary Emotion: {results['primary_emotion']}")
    print(f"Confidence: {results['confidence']:.2%}")
    
    if 'probabilities' in results:
        print(f"\nEmotion Probabilities:")
        for emotion, prob in results['probabilities'].items():
            print(f"  {emotion}: {prob:.2%}")
    
    print("\n" + "=" * 60)
    print("CombinedDetector initialized successfully!")
    print("Ready for real-time video processing!")
