# backend/analytics/plotter.py
import matplotlib.pyplot as plt
import pandas as pd
import os


class Plotter:
    """
    Visualizes logged simulation data.
    Provides emotion, posture, and sentiment charts.
    """

    def __init__(self, log_file="tests/logs/syntwin_log.csv"):
        if not os.path.exists(log_file):
            raise FileNotFoundError("Log file not found. Please run the simulation first.")
        self.data = pd.read_csv(log_file)

    def plot_emotion_distribution(self):
        """Bar chart for emotion frequency."""
        counts = self.data["emotion"].value_counts()
        plt.figure(figsize=(8, 5))
        counts.plot(kind="bar")
        plt.title("Emotion Frequency Distribution")
        plt.xlabel("Emotion")
        plt.ylabel("Occurrences")
        plt.tight_layout()
        plt.show()

    def plot_posture_distribution(self):
        """Pie chart for posture analysis."""
        counts = self.data["posture"].value_counts()
        plt.figure(figsize=(6, 6))
        counts.plot(kind="pie", autopct="%1.1f%%", startangle=90)
        plt.title("Posture Analysis")
        plt.ylabel("")
        plt.tight_layout()
        plt.show()

    def plot_sentiment_trend(self):
        """Line chart of sentiment scores over time."""
        if "sentiment" in self.data.columns:
            plt.figure(figsize=(10, 5))
            plt.plot(self.data["sentiment"], marker='o', linestyle='-')
            plt.title("Sentiment Trend Over Time")
            plt.xlabel("Frame / Cycle")
            plt.ylabel("Sentiment Score")
            plt.tight_layout()
            plt.show()

