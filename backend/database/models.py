# Optional: models.py for structured schema

DETECTOR_LOGS_SCHEMA = {
    "table_name": "detector_logs",
    "columns": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "timestamp": "TEXT",
        "emotion": "TEXT",
        "smile": "TEXT",
        "eyes": "TEXT",
        "posture": "TEXT",
        "sentiment": "REAL",
        "environment_feedback": "TEXT"
    }
}

def create_table_query(schema: dict) -> str:
    """
    Generates a CREATE TABLE SQL query from the schema dictionary.
    """
    table_name = schema["table_name"]
    cols = ", ".join([f"{col} {dtype}" for col, dtype in schema["columns"].items()])
    return f"CREATE TABLE IF NOT EXISTS {table_name} ({cols})"
