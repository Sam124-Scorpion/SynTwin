# backend/nlp/sentiment_analyzer.py
"""
Sentiment Analysis Module
Analyzes emotional sentiment from text and behavioral data.
"""
from typing import Dict, List


class SentimentAnalyzer:
    """
    Analyzes sentiment from emotions and behavioral patterns.
    """

    # Sentiment scores for different emotions
    EMOTION_SENTIMENT_MAP = {
        "Happy": 0.8,
        "Excited": 0.9,
        "Focused": 0.6,
        "Neutral": 0.0,
        "Sad": -0.7,
        "Angry": -0.8,
        "Frustrated": -0.6,
        "Drowsy": -0.3,
        "Tired": -0.4,
        "Anxious": -0.5,
        "Surprised": 0.3,
        "Confused": -0.2
    }

    def analyze_emotion_sentiment(self, emotion: str) -> float:
        """
        Convert emotion to sentiment score (-1 to 1).
        """
        return self.EMOTION_SENTIMENT_MAP.get(emotion, 0.0)

    def analyze_text_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment from text input (basic keyword-based).
        For more advanced analysis, integrate with transformers or TextBlob.
        """
        positive_words = [
            "good", "great", "happy", "excellent", "wonderful", "amazing",
            "love", "like", "enjoy", "fantastic", "awesome", "perfect"
        ]
        negative_words = [
            "bad", "terrible", "hate", "dislike", "awful", "horrible",
            "sad", "angry", "frustrated", "annoyed", "tired", "stressed"
        ]

        text_lower = text.lower()
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            sentiment_score = 0.0
            label = "Neutral"
        else:
            sentiment_score = (pos_count - neg_count) / total
            if sentiment_score > 0.3:
                label = "Positive"
            elif sentiment_score < -0.3:
                label = "Negative"
            else:
                label = "Neutral"
        
        return {
            "score": round(sentiment_score, 2),
            "label": label,
            "positive_words": pos_count,
            "negative_words": neg_count
        }

    def analyze_behavioral_sentiment(self, behavior_data: Dict) -> Dict:
        """
        Analyze sentiment from behavioral patterns.
        behavior_data: {emotion, posture, eyes, smile, etc.}
        """
        score = 0.0
        factors = []

        # Emotion sentiment
        if "emotion" in behavior_data:
            emotion_score = self.analyze_emotion_sentiment(behavior_data["emotion"])
            score += emotion_score * 0.5
            factors.append(f"Emotion: {behavior_data['emotion']}")

        # Smile detection
        if behavior_data.get("smile") == "Smiling":
            score += 0.3
            factors.append("Smiling detected")
        elif behavior_data.get("smile") == "Not Smiling":
            score -= 0.1

        # Posture
        if behavior_data.get("posture") == "Slouching":
            score -= 0.2
            factors.append("Poor posture")
        elif behavior_data.get("posture") == "Upright":
            score += 0.1

        # Eyes
        if behavior_data.get("eyes") == "Closed":
            score -= 0.3
            factors.append("Drowsy signs")

        # Normalize to -1 to 1 range
        score = max(-1.0, min(1.0, score))

        if score > 0.3:
            label = "Positive"
        elif score < -0.3:
            label = "Negative"
        else:
            label = "Neutral"

        return {
            "score": round(score, 2),
            "label": label,
            "factors": factors
        }

    def get_sentiment_trend(self, sentiment_history: List[float]) -> str:
        """
        Analyze sentiment trend over time.
        """
        if len(sentiment_history) < 2:
            return "Insufficient data"

        recent = sentiment_history[-5:]  # Last 5 data points
        older = sentiment_history[-10:-5] if len(sentiment_history) >= 10 else sentiment_history[:-5]

        if not older:
            return "Stable"

        avg_recent = sum(recent) / len(recent)
        avg_older = sum(older) / len(older)

        diff = avg_recent - avg_older

        if diff > 0.2:
            return "Improving"
        elif diff < -0.2:
            return "Declining"
        else:
            return "Stable"


if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    # Test emotion sentiment
    print("Emotion Sentiment Analysis:")
    print(f"Happy: {analyzer.analyze_emotion_sentiment('Happy')}")
    print(f"Sad: {analyzer.analyze_emotion_sentiment('Sad')}")
    
    # Test text sentiment
    print("\nText Sentiment Analysis:")
    text = "I had a great day! The work was excellent."
    print(f"Text: '{text}'")
    print(analyzer.analyze_text_sentiment(text))
    
    # Test behavioral sentiment
    print("\nBehavioral Sentiment Analysis:")
    behavior = {
        "emotion": "Happy",
        "smile": "Smiling",
        "posture": "Upright",
        "eyes": "Open"
    }
    print(analyzer.analyze_behavioral_sentiment(behavior))
