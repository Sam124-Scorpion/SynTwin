# backend/classifiers/cognitive_state.py

"""
Classifies cognitive focus state based on attention, blink rate, and yawning.
"""

class CognitiveStateClassifier:
    def __init__(self):
        pass

    def classify(self, data):
        attention = data.get("attention", 0.5)
        blink_rate = data.get("blink_rate", 15)
        yawn_freq = data.get("yawn_freq", 1)

        if attention > 0.8 and blink_rate < 15:
            state = "Focused"
        elif attention < 0.3 or yawn_freq > 3:
            state = "Drowsy"
        elif blink_rate > 25:
            state = "Distracted"
        else:
            state = "Neutral"

        return {"state": state, "attention": attention, "blink_rate": blink_rate}
