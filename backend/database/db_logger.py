from backend.database.db import get_connection

def log_detection_to_db(entry: dict):
    """
    Insert a single detection entry into the database.
    entry: {
        timestamp, emotion, smile, eyes, posture, sentiment, environment_feedback
    }
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO detector_logs
            (timestamp, emotion, smile, eyes, posture, sentiment, environment_feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.get("timestamp"),
            entry.get("emotion"),
            entry.get("smile"),
            entry.get("eyes"),
            entry.get("posture"),
            entry.get("sentiment"),
            entry.get("environment_feedback")
        ))
        conn.commit()
    except Exception as e:
        print(f"❌ DB Logging Error: {e}")
    finally:
        conn.close()
