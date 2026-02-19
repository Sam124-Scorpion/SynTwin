# backend/classifiers/mood_classifier.py

"""
Classifies emotional mood based on detected facial emotion label from CNN.
Supports 2 primary emotions (Happy, Angry) + Neutral and Drowsy states.
"""

class MoodStateClassifier:
    def __init__(self):
        # Simplified mapping for 2-class emotion system
        self.mood_map = {
            "Happy": "Positive",
            "Neutral": "Calm",
            "Angry": "Tense",
            "Drowsy": "Tired",
            "Focused": "Concentrated"
        }

    def classify(self, data):
        emotion = data.get("emotion", "Neutral")
        mood = self.mood_map.get(emotion, "Neutral")
        return {"emotion": emotion, "mood": mood}
