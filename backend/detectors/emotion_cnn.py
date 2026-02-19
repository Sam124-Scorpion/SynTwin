"""
CNN-Based Emotion Detection Module
Optimized for Happy Emotion Detection with Multi-Tier Sensitivity
"""
import numpy as np
import cv2
from typing import Dict, Tuple


class EmotionCNN:
    """
    CNN-style emotion detector using computer vision features
    Optimized for detecting happiness with 3-tier sensitivity
    """
    
    def __init__(self):
        """Initialize the emotion detector with optimized thresholds"""
        self.emotions = ['Happy', 'Angry', 'Neutral']
        
        # Optimized thresholds for happy detection (lowered by 30-40%)
        self.thresholds = {
            'happy_subtle': {
                'brightness': 95,       # Highly sensitive - Was 100
                'mouth_bright': 105,    # Lower threshold - Was 110
                'variance': 120,        # Accept more variance - Was 150
                'smile_ratio': 0.83    # Very sensitive - Was 1.05
            },
            'happy_moderate': {
                'brightness': 110,      # Was 115
                'mouth_bright': 120,    # Was 125
                'variance': 220,        # Was 250
                'smile_ratio': 1.0     # Was 1.10
            },
            'happy_strong': {
                'brightness': 125,      # Was 130
                'mouth_bright': 135,    # Was 140
                'variance': 380,        # Was 400
                'smile_ratio': 1.02     # Was 1.15
            },
            'angry': {
                'darkness': 90,
                'variance_low': 100,
                'mouth_dark': 85
            },
            'neutral': {
                'brightness_min': 95,       # Neutral brightness range
                'brightness_max': 115,
                'variance_min': 80,         # Neutral variance range
                'variance_max': 220,
                'mouth_contrast_max': 5     # Max mouth activity for neutral
            }
        }
        
        # Increased weights for happy detection (30% boost)
        self.weights = {
            'brightness': 2.5,          # Was 1.8
            'mouth_brightness': 3.2,    # Was 2.2
            'variance': 2.0,            # Was 1.5
            'eye_brightness': 2.8,      # New feature
            'smile_ratio': 2.3          # Was 1.7
        }
        
    def extract_features(self, face_image: np.ndarray) -> Dict:
        """
        Extract CNN-style features from face image
        
        Args:
            face_image: BGR face image
            
        Returns:
            Dictionary of extracted features
        """
        if face_image is None or face_image.size == 0:
            return self._default_features()
        
        # Convert to grayscale for processing
        if len(face_image.shape) == 3:
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_image
            
        h, w = gray.shape
        
        # Overall brightness (global feature)
        mean_brightness = np.mean(gray)
        
        # Variance (texture feature)
        variance = np.var(gray)
        
        # Region-based features (mimicking CNN receptive fields)
        mouth_region = gray[int(h*0.60):int(h*0.90), int(w*0.20):int(w*0.80)]
        eye_region = gray[int(h*0.25):int(h*0.45), int(w*0.15):int(w*0.85)]
        
        # Mouth features (critical for smile detection)
        mouth_brightness = np.mean(mouth_region) if mouth_region.size > 0 else mean_brightness
        mouth_variance = np.var(mouth_region) if mouth_region.size > 0 else variance
        
        # Enhanced smile ratio calculation
        if mouth_region.size > 0:
            mouth_h_profile = np.mean(mouth_region, axis=0)
            mouth_v_profile = np.mean(mouth_region, axis=1)
            h_spread = np.std(mouth_h_profile)
            v_spread = np.std(mouth_v_profile)
            smile_ratio = (h_spread / v_spread) if v_spread > 0 else 1.0
            
            # Boost smile_ratio if mouth is significantly brighter than face
            if mouth_brightness > mean_brightness + 5:
                smile_ratio *= 1.15  # Bright mouth indicates smile
        else:
            smile_ratio = 1.0
        
        # Eye brightness (new feature for happiness)
        eye_brightness = np.mean(eye_region) if eye_region.size > 0 else mean_brightness
        
        # Mouth brightness contrast (strong smile indicator)
        mouth_contrast = mouth_brightness - mean_brightness
        
        # Edge density (captures facial muscle activation)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        return {
            'brightness': mean_brightness,
            'variance': variance,
            'mouth_brightness': mouth_brightness,
            'mouth_variance': mouth_variance,
            'mouth_contrast': mouth_contrast,
            'eye_brightness': eye_brightness,
            'smile_ratio': smile_ratio,
            'edge_density': edge_density
        }
    
    def _default_features(self) -> Dict:
        """Return default neutral features"""
        return {
            'brightness': 105,
            'variance': 100,
            'mouth_brightness': 105,
            'mouth_variance': 100,
            'mouth_contrast': 0,
            'eye_brightness': 105,
            'smile_ratio': 1.0,
            'edge_density': 0.1
        }
    
    def calculate_happy_score(self, features: Dict) -> Tuple[float, str]:
        """
        Calculate happiness score with 3-tier detection
        
        Returns:
            Tuple of (score, tier) where tier is 'subtle', 'moderate', 'strong', or None
        """
        brightness = features['brightness']
        mouth_bright = features['mouth_brightness']
        mouth_contrast = features.get('mouth_contrast', 0)
        variance = features['variance']
        smile_ratio = features['smile_ratio']
        eye_bright = features['eye_brightness']
        
        # Bonus for bright mouth contrast (strong smile indicator)
        mouth_bonus = max(0, mouth_contrast * 2.5)
        
        # Check for strong happiness
        if (brightness >= self.thresholds['happy_strong']['brightness'] and
            mouth_bright >= self.thresholds['happy_strong']['mouth_bright'] and
            variance >= self.thresholds['happy_strong']['variance']):
            
            score = (
                (brightness - 105) * self.weights['brightness'] +
                (mouth_bright - 105) * self.weights['mouth_brightness'] +
                (variance / 100) * self.weights['variance'] +
                (smile_ratio - 1.0) * 100 * self.weights['smile_ratio'] +
                (eye_bright - 105) * self.weights['eye_brightness'] +
                mouth_bonus
            )
            return min(score * 1.5, 100.0), 'strong'
        
        # Check for moderate happiness
        elif (brightness >= self.thresholds['happy_moderate']['brightness'] and
              mouth_bright >= self.thresholds['happy_moderate']['mouth_bright'] and
              variance >= self.thresholds['happy_moderate']['variance']):
            
            score = (
                (brightness - 105) * self.weights['brightness'] +
                (mouth_bright - 105) * self.weights['mouth_brightness'] +
                (variance / 100) * self.weights['variance'] +
                (smile_ratio - 1.0) * 80 * self.weights['smile_ratio'] +
                (eye_bright - 105) * self.weights['eye_brightness'] +
                mouth_bonus
            )
            return min(score * 1.2, 100.0), 'moderate'
        
        # Check for subtle happiness (40% more sensitive)
        elif (brightness >= self.thresholds['happy_subtle']['brightness'] and
              mouth_bright >= self.thresholds['happy_subtle']['mouth_bright'] and
              smile_ratio >= self.thresholds['happy_subtle']['smile_ratio']):
            
            score = (
                (brightness - 105) * self.weights['brightness'] * 1.0 +  # Increased from 0.8
                (mouth_bright - 105) * self.weights['mouth_brightness'] * 1.1 +  # Increased from 0.9
                (variance / 100) * self.weights['variance'] * 0.9 +  # Increased from 0.7
                (smile_ratio - 1.0) * 80 * self.weights['smile_ratio'] +  # Increased from 60
                (eye_bright - 105) * self.weights['eye_brightness'] * 1.0 +  # Increased from 0.85
                mouth_bonus * 0.8
            )
            return min(score * 1.1, 100.0), 'subtle'  # Increased from base score
        
        # Calculate base happiness score even if thresholds not met
        score = (
            max(0, (brightness - 105)) * self.weights['brightness'] * 0.5 +
            max(0, (mouth_bright - 105)) * self.weights['mouth_brightness'] * 0.5 +
            max(0, (smile_ratio - 1.0)) * 40 * self.weights['smile_ratio'] +
            mouth_bonus * 0.5
        )
        return min(score * 0.6, 100.0), None
    
    def calculate_angry_score(self, features: Dict) -> float:
        """Calculate anger score based on features"""
        brightness = features['brightness']
        variance = features['variance']
        mouth_bright = features['mouth_brightness']
        edge_density = features['edge_density']
        
        # Angry: dark, low variance, tense features
        score = 0.0
        
        if brightness < self.thresholds['angry']['darkness']:
            score += (self.thresholds['angry']['darkness'] - brightness) * 1.5
        
        if variance < self.thresholds['angry']['variance_low']:
            score += (self.thresholds['angry']['variance_low'] - variance) / 10
        
        if mouth_bright < self.thresholds['angry']['mouth_dark']:
            score += (self.thresholds['angry']['mouth_dark'] - mouth_bright) * 1.2
        
        # High edge density indicates tension
        if edge_density > 0.15:
            score += (edge_density - 0.15) * 100
        
        return min(score, 100.0)
    
    def calculate_neutral_score(self, features: Dict) -> float:
        """Calculate neutral score based on features with enhanced detection"""
        brightness = features['brightness']
        variance = features['variance']
        smile_ratio = features['smile_ratio']
        mouth_contrast = features.get('mouth_contrast', 0)
        eye_brightness = features.get('eye_brightness', 105)
        
        # Neutral: medium brightness, medium variance
        ideal_brightness = 105
        ideal_variance = 150
        
        # Calculate deviations from neutral
        brightness_diff = abs(brightness - ideal_brightness)
        variance_diff = abs(variance - ideal_variance)
        
        # Start with enhanced base score
        score = 120.0  # Increased from 100
        
        # Gentler penalties for deviations (broader neutral range)
        if brightness_diff < 5:  # Very close to ideal
            score += 15  # Bonus for perfect neutral brightness
        elif brightness_diff < 10:  # Close to ideal
            score += 5  # Small bonus
        else:
            score -= brightness_diff * 0.4  # Reduced from 0.5
        
        if variance_diff < 30:  # Low variance is neutral
            score += 10  # Bonus for stable neutral variance
        else:
            score -= (variance_diff / 100) * 1.0  # Reduced from 1.2
        
        # Bonus for truly neutral features
        if abs(mouth_contrast) < 2:  # Very neutral mouth
            score += 12  # Strong bonus for no mouth activity
        
        if abs(eye_brightness - ideal_brightness) < 5:  # Neutral eyes
            score += 8  # Bonus for neutral eye state
        
        # Moderate penalties for smile indicators (allow subtle expressions)
        if smile_ratio > 1.05:  # Only penalize clear smiles
            score -= (smile_ratio - 1.0) * 100  # Reduced from 120
        elif smile_ratio > 1.02:
            score -= (smile_ratio - 1.0) * 50  # Gentle penalty for subtle
        
        if mouth_contrast > 5:  # Only penalize clear bright mouth
            score -= mouth_contrast * 2.5  # Reduced from 3.5
        elif mouth_contrast > 3:
            score -= mouth_contrast * 1.0  # Gentle penalty for slight brightness
        
        # Gentler penalty for high brightness
        if brightness > 115:  # Only penalize very bright (raised from 110)
            score -= (brightness - 115) * 1.0  # Reduced from 1.5
        
        # Penalty for very low brightness (could be angry/sad)
        if brightness < 95:
            score -= (95 - brightness) * 0.8
        
        return max(score, 0.0)
    
    def predict_emotion(self, face_image: np.ndarray) -> Dict:
        """
        Predict emotion from face image
        
        Args:
            face_image: BGR face image
            
        Returns:
            Dictionary with emotion, confidence, and probabilities
        """
        # Extract features
        features = self.extract_features(face_image)
        
        # Calculate scores for each emotion
        happy_score, happy_tier = self.calculate_happy_score(features)
        angry_score = self.calculate_angry_score(features)
        neutral_score = self.calculate_neutral_score(features)
        
        # Check if features are truly in neutral range
        brightness = features['brightness']
        mouth_contrast = features.get('mouth_contrast', 0)
        neutral_thresholds = self.thresholds['neutral']
        
        is_in_neutral_range = (
            neutral_thresholds['brightness_min'] <= brightness <= neutral_thresholds['brightness_max'] and
            mouth_contrast <= neutral_thresholds['mouth_contrast_max']
        )
        
        # Boost neutral score if clearly in neutral range
        if is_in_neutral_range:
            neutral_score *= 1.25  # 25% boost for neutral range
        
        # Apply hysteresis: boost happy if detected to reduce flickering
        if happy_tier is not None:
            happy_score *= 1.3  # 30% boost when happy is detected
        else:
            # If no happy tier but brightness suggests neutral, reduce happy slightly
            if is_in_neutral_range:
                happy_score *= 0.85  # 15% reduction when in neutral range
        
        # Normalize scores to probabilities
        total = happy_score + angry_score + neutral_score
        if total > 0:
            probabilities = {
                'Happy': happy_score / total,
                'Angry': angry_score / total,
                'Neutral': neutral_score / total
            }
        else:
            probabilities = {
                'Happy': 0.33,
                'Angry': 0.33,
                'Neutral': 0.34
            }
        
        # Determine dominant emotion with minimum confidence threshold
        emotion = max(probabilities, key=probabilities.get)
        confidence = probabilities[emotion]
        
        # If happy vs neutral is too close, require higher margin (stability)
        if emotion == 'Happy' and probabilities['Neutral'] > 0.35:
            # Happy needs at least 15% lead to be stable
            if probabilities['Happy'] - probabilities['Neutral'] < 0.15:
                # Not confident enough, might be neutral
                if probabilities['Happy'] < 0.55:
                    emotion = 'Neutral'
                    confidence = probabilities['Neutral']
        
        # Add tier information for happy emotions
        result = {
            'emotion': emotion,
            'confidence': confidence,
            'probabilities': probabilities,
            'features': features
        }
        
        if emotion == 'Happy' and happy_tier:
            result['intensity'] = happy_tier
        
        return result
    
    def process_frame(self, frame: np.ndarray, face_bbox: Tuple[int, int, int, int]) -> Dict:
        """
        Process a frame with a detected face
        
        Args:
            frame: Full frame image
            face_bbox: Tuple of (x, y, w, h) for face location
            
        Returns:
            Dictionary with emotion prediction results
        """
        x, y, w, h = face_bbox
        
        # Extract face region
        face_roi = frame[y:y+h, x:x+w]
        
        # Resize to standard size for consistent processing
        if face_roi.size > 0:
            face_roi = cv2.resize(face_roi, (200, 200))
        
        # Predict emotion
        return self.predict_emotion(face_roi)


# Standalone testing
if __name__ == "__main__":
    print("EmotionCNN - Optimized Happy Detection Test")
    print("=" * 60)
    
    detector = EmotionCNN()
    
    # Test 1: Simulated happy face
    happy_face = np.ones((200, 200, 3), dtype=np.uint8) * 135
    happy_face[120:180, 40:160] = 155  # Bright mouth
    result = detector.predict_emotion(happy_face)
    print(f"\nHappy Test: {result['emotion']} ({result['confidence']:.0%})")
    if 'intensity' in result:
        print(f"Intensity: {result['intensity']}")
    
    # Test 2: Simulated angry face
    angry_face = np.ones((200, 200, 3), dtype=np.uint8) * 80
    result = detector.predict_emotion(angry_face)
    print(f"\nAngry Test: {result['emotion']} ({result['confidence']:.0%})")
    
    # Test 3: Neutral face
    neutral_face = np.ones((200, 200, 3), dtype=np.uint8) * 105
    result = detector.predict_emotion(neutral_face)
    print(f"\nNeutral Test: {result['emotion']} ({result['confidence']:.0%})")
    
    print("\n" + "=" * 60)
    print("EmotionCNN initialized successfully!")
