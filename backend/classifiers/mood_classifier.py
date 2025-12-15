# backend/classifiers/mood_state.py

"""
Classifies emotional mood based on detected facial emotion label.
"""

class MoodStateClassifier:
    def __init__(self):
        # Basic mapping (can be extended later)
        self.mood_map = {
            "Happy": "Positive",
            "Neutral": "Calm",
            "Sad": "Low",
            "Angry": "Tense",
            "Surprised": "Alert",
            "Fear": "Anxious",
        }

    def classify(self, data):
        emotion = data.get("emotion", "Neutral")
        mood = self.mood_map.get(emotion, "Neutral")
        return {"emotion": emotion, "mood": mood}
