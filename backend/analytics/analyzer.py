# backend/analytics/analyzer.py
import pandas as pd
import os


class Analyzer:
    """
    Analyzes logged data to extract insights about
    emotion trends, posture consistency, and mood balance.
    """

    def __init__(self, log_file="tests/logs/syntwin_log.csv"):
        if not os.path.exists(log_file):
            raise FileNotFoundError("Log file not found. Run data_logger first.")
        self.data = pd.read_csv(log_file)

    def emotion_distribution(self):
        """Return count of each emotion detected."""
        return self.data["emotion"].value_counts().to_dict()

    def posture_summary(self):
        """Return posture occurrences (Straight, Slouching, Leaning Left, etc.)"""
        return self.data["posture"].value_counts().to_dict()

    def mood_trend(self):
        """Track frequency of moods logged over time."""
        return self.data["mood"].value_counts().to_dict()

    def sentiment_overview(self):
        """Returns average sentiment score."""
        if "sentiment" in self.data.columns:
            return float(self.data["sentiment"].mean())
        return 0.0

    def overall_summary(self):
        """Return all key insights together."""
        return {
            "emotions": self.emotion_distribution(),
            "postures": self.posture_summary(),
            "moods": self.mood_trend(),
            "avg_sentiment": self.sentiment_overview(),
            "total_entries": len(self.data)
        }
