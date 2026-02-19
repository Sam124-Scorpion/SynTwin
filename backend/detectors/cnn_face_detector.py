"""
CNN-Based Face Detection Module
Uses OpenCV DNN with Caffe model for robust face detection
"""
import cv2
import numpy as np
import os
from typing import List, Tuple


class CNNFaceDetector:
    """
    CNN-based face detector using OpenCV's DNN module
    Uses pre-trained Caffe model for robust detection
    """
    
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize the CNN face detector
        
        Args:
            confidence_threshold: Minimum confidence for face detection (0.0 - 1.0)
        """
        self.confidence_threshold = confidence_threshold
        self.net = None
        self.model_loaded = False
        
        # Model paths
        self.prototxt_path = None
        self.model_path = None
        
        # Detection parameters
        self.input_size = (300, 300)
        self.scale_factor = 1.0
        self.mean_val = (104.0, 177.0, 123.0)
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load the CNN model from assets"""
        try:
            # Get the current file's directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Navigate to backend/assets
            assets_dir = os.path.join(os.path.dirname(current_dir), 'assets')
            
            # Model file paths
            self.prototxt_path = os.path.join(assets_dir, 'deploy.prototxt')
            self.model_path = os.path.join(assets_dir, 'res10_300x300_ssd_iter_140000.caffemodel')
            
            # Check if files exist
            if not os.path.exists(self.prototxt_path):
                print(f"Warning: Prototxt not found at {self.prototxt_path}")
                self._use_fallback()
                return
            
            if not os.path.exists(self.model_path):
                print(f"Warning: Model not found at {self.model_path}")
                self._use_fallback()
                return
            
            # Load the model
            self.net = cv2.dnn.readNetFromCaffe(self.prototxt_path, self.model_path)
            self.model_loaded = True
            print("CNN Face Detector: Model loaded successfully")
            
        except Exception as e:
            print(f"Error loading CNN model: {e}")
            self._use_fallback()
    
    def _use_fallback(self):
        """Use Haar Cascade as fallback"""
        print("CNN Face Detector: Using Haar Cascade fallback")
        self.model_loaded = False
        
        # Load Haar Cascade as backup
        try:
            self.haar_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        except:
            print("Warning: Could not load Haar Cascade either")
            self.haar_cascade = None
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in frame
        
        Args:
            frame: Input BGR frame
            
        Returns:
            List of face bounding boxes as (x, y, w, h) tuples
        """
        if frame is None or frame.size == 0:
            return []
        
        h, w = frame.shape[:2]
        
        # Use CNN model if loaded
        if self.model_loaded and self.net is not None:
            return self._detect_with_cnn(frame, w, h)
        else:
            return self._detect_with_haar(frame)
    
    def _detect_with_cnn(self, frame: np.ndarray, width: int, height: int) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using CNN model
        
        Args:
            frame: Input frame
            width: Frame width
            height: Frame height
            
        Returns:
            List of face bounding boxes
        """
        # Create blob from image
        blob = cv2.dnn.blobFromImage(
            frame,
            scalefactor=self.scale_factor,
            size=self.input_size,
            mean=self.mean_val,
            swapRB=False,
            crop=False
        )
        
        # Set input and perform forward pass
        self.net.setInput(blob)
        detections = self.net.forward()
        
        faces = []
        
        # Process detections
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            # Filter by confidence threshold
            if confidence > self.confidence_threshold:
                # Get bounding box coordinates
                box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                x1, y1, x2, y2 = box.astype(int)
                
                # Convert to (x, y, w, h) format
                x = max(0, x1)
                y = max(0, y1)
                w = min(x2 - x1, width - x)
                h = min(y2 - y1, height - y)
                
                # Validate bounding box
                if w > 0 and h > 0:
                    faces.append((x, y, w, h))
        
        return faces
    
    def _detect_with_haar(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using Haar Cascade fallback
        
        Args:
            frame: Input frame
            
        Returns:
            List of face bounding boxes
        """
        if self.haar_cascade is None:
            return []
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.haar_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Convert to list of tuples
        return [tuple(face) for face in faces]
    
    def set_confidence_threshold(self, threshold: float):
        """
        Set new confidence threshold
        
        Args:
            threshold: New confidence threshold (0.0 - 1.0)
        """
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        print(f"CNN Face Detector: Confidence threshold set to {self.confidence_threshold}")
    
    def is_model_loaded(self) -> bool:
        """Check if CNN model is loaded"""
        return self.model_loaded
    
    def get_model_info(self) -> dict:
        """Get information about loaded model"""
        return {
            'model_loaded': self.model_loaded,
            'model_type': 'CNN (Caffe)' if self.model_loaded else 'Haar Cascade',
            'confidence_threshold': self.confidence_threshold,
            'input_size': self.input_size,
            'prototxt_path': self.prototxt_path,
            'model_path': self.model_path
        }


# Standalone testing
if __name__ == "__main__":
    print("CNNFaceDetector - Test Mode")
    print("=" * 60)
    
    detector = CNNFaceDetector(confidence_threshold=0.5)
    
    # Print model info
    info = detector.get_model_info()
    print("\nModel Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Create test frame
    test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 120
    
    # Simulate a bright face-like region
    test_frame[100:300, 200:400] = 150
    
    # Test detection
    faces = detector.detect_faces(test_frame)
    print(f"\nTest Detection: {len(faces)} face(s) found")
    
    for i, (x, y, w, h) in enumerate(faces):
        print(f"  Face {i+1}: x={x}, y={y}, w={w}, h={h}")
    
    print("\n" + "=" * 60)
    print("CNNFaceDetector initialized successfully!")
