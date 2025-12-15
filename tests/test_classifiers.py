# tests/test_classifiers.py

"""
Test module for SynTwin Classifiers.
Evaluates the cognitive and mood state classification logic independently.
"""

from backend.classifiers.state_classifier import CognitiveStateClassifier
from backend.classifiers.mood_classifier import MoodStateClassifier

def run_classifiers_test():
    print("🧩 Starting SynTwin Classifiers Test...\n")

    cognitive_classifier = CognitiveStateClassifier()
    mood_classifier = MoodStateClassifier()

    # Example simulated data inputs
    test_samples = [
        {"attention": 0.9, "blink_rate": 10, "yawn_freq": 0, "emotion": "Happy"},
        {"attention": 0.4, "blink_rate": 20, "yawn_freq": 2, "emotion": "Neutral"},
        {"attention": 0.2, "blink_rate": 30, "yawn_freq": 5, "emotion": "Sad"},
        {"attention": 0.7, "blink_rate": 12, "yawn_freq": 0, "emotion": "Angry"},
    ]

    # Run test cycles
    for i, sample in enumerate(test_samples):
        print(f"🔹 Test {i+1}:")
        cog_state = cognitive_classifier.classify(sample)
        mood_state = mood_classifier.classify(sample)

        print(f"   Input Data: {sample}")
        print(f"   → Cognitive State: {cog_state}")
        print(f"   → Mood State: {mood_state}")
        print("-------------------------------------------------\n")

    print("✅ Classifiers test completed successfully!")

if __name__ == "__main__":
    run_classifiers_test()
