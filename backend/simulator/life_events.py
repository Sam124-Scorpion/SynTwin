# simulator/life_events.py

"""
Generates life events for the twin based on current emotional and cognitive state.
Simulates daily actions, reflections, and evolving personality patterns.
"""

import random
import datetime


class LifeEventGenerator:
    def __init__(self):
        # Template event categories based on emotional context
        self.event_pool = {
            "Positive": [
                "starts a new creative project",
                "reconnects with an old friend",
                "explores a new learning topic"
            ],
            "Calm": [
                "spends time reading quietly",
                "takes a reflective nature walk",
                "journals thoughts peacefully"
            ],
            "Low": [
                "takes time to rest and recharge",
                "reflects on challenges faced today",
                "listens to calming music"
            ],
            "Tense": [
                "tries breathing exercises to relax",
                "steps away from the screen to reset",
                "organizes tasks to reduce pressure"
            ],
            "Neutral": [
                "continues with daily tasks",
                "reviews goals for the week",
                "reflects on overall balance"
            ]
        }

    def generate_event(self, twin_snapshot):
        """Create a new event entry based on mood and focus level."""
        mood = twin_snapshot.get("mood", "Neutral")
        focus = twin_snapshot.get("focus", 50)
        energy = twin_snapshot.get("energy", 60)

        mood_events = self.event_pool.get(mood, self.event_pool["Neutral"])
        base_event = random.choice(mood_events)

        # Add nuance based on energy/focus
        if focus > 80:
            detail = "with strong determination."
        elif energy < 40:
            detail = "but feels a bit tired."
        else:
            detail = "maintaining steady effort."

        event_description = f"{base_event} ({detail})"

        # Return structured event data
        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": event_description,
            "mood": mood,
            "energy": energy,
            "focus": focus
        }


# Example
if __name__ == "__main__":
    gen = LifeEventGenerator()
    print(gen.generate_event({"mood": "Positive", "focus": 85, "energy": 75}))
