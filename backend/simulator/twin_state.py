# simulator/twin_state.py

"""
Maintains and updates the internal state of the SynTwin
based on emotional, cognitive, and environmental inputs.
"""

# backend/simulator/twin_state.py

from datetime import datetime
from backend.analytics.data_logger import DataLogger


class TwinState:
    """
    Represents internal state of the user's digital twin.
    Automatically logs each update.
    """

    def __init__(self):
        self.energy = 100
        self.focus = 80
        self.mood = "Neutral"
        self.health = 90
        self.social_level = 50
        self.last_update = datetime.now().strftime("%H:%M:%S")
        self.logger = DataLogger()

    def update_from_inputs(self, cognitive, mood, sentiment=None, environment_feedback=None):
        # Update based on current inputs
        self.focus = 70 if cognitive.get("state") == "Distracted" else 90 if cognitive.get("state") == "Focused" else 50
        self.mood = mood.get("mood", "Neutral")
        self.energy = max(0, min(100, self.energy + (sentiment or 0) * 10))
        self.health = max(0, min(100, self.health - (0.1 if self.energy < 30 else 0)))
        self.social_level = min(100, self.social_level + (0.5 if sentiment and sentiment > 0 else -0.3))
        self.last_update = datetime.now().strftime("%H:%M:%S")

        # ✅ Log simulation cycle
        self.logger.log_entry({
            "emotion": self.mood,
            "cognitive_state": cognitive.get("state"),
            "mood": self.mood,
            "sentiment": sentiment,
            "environment_feedback": environment_feedback
        })

    def get_snapshot(self):
        return {
            "energy": self.energy,
            "focus": self.focus,
            "mood": self.mood,
            "health": self.health,
            "social_level": self.social_level,
            "last_update": self.last_update
        }


# Example
if __name__ == "__main__":
    twin = TwinState()
    twin.update_from_inputs(
        {"state": "Focused"}, {"mood": "Calm"}, sentiment=0.6
    )
    print(twin.get_snapshot())
