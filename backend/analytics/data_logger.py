# backend/analytics/data_logger.py
import csv
import os
from datetime import datetime


class DataLogger:
    """
    Logs simulation and detection data for analysis.
    Saves data to CSV files in /logs folder.
    """

    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "syntwin_log.csv")

        # Initialize file with headers if not exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "emotion", "smile", "eyes", "posture",
                    "cognitive_state", "mood", "sentiment", "environment_feedback"
                ])

    def log_entry(self, data: dict):
        """
        Log a single frame or simulation cycle data.
        Expected keys: emotion, smile, eyes, posture, cognitive_state, mood, sentiment, environment_feedback
        """
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data.get("emotion", ""),
                data.get("smile", ""),
                data.get("eyes", ""),
                data.get("posture", ""),
                data.get("cognitive_state", ""),
                data.get("mood", ""),
                data.get("sentiment", ""),
                data.get("environment_feedback", "")
            ])
        # Reduced logging verbosity - only log errors
        pass  # print(f"🧩 Logged data at {datetime.now().strftime('%H:%M:%S')}")

    def clear_logs(self):
        """Deletes existing logs."""
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
            print("🗑️ Log file cleared.")
