# simulator/environment.py

"""
Adapts the environment's mood and conditions based on
the twin’s internal state. This can be reflected in UI visuals,
notifications, or motivational feedback.
"""

class Environment:
    def __init__(self):
        # Environment themes for different emotional contexts
        self.modes = {
            "Positive": {"theme": "bright", "color": "#9bff9b", "message": "Your twin feels motivated!"},
            "Calm": {"theme": "cool", "color": "#9edbff", "message": "Peaceful and steady progress."},
            "Low": {"theme": "dim", "color": "#d0d0d0", "message": "Encourage your twin to rest or reflect."},
            "Tense": {"theme": "warm", "color": "#ffb38b", "message": "Twin is under mild stress."},
            "Neutral": {"theme": "default", "color": "#ffffff", "message": "Stable, awaiting new inputs."}
        }

    def adapt_environment(self, twin_snapshot):
        """Adjust environment visuals and prompts based on twin mood."""
        mood = twin_snapshot.get("mood", "Neutral")
        return self.modes.get(mood, self.modes["Neutral"])

# Example
if __name__ == "__main__":
    env = Environment()
    sample_twin = {"mood": "Positive"}
    print(env.adapt_environment(sample_twin))
