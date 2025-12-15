import sqlite3
from pathlib import Path
from backend.database.models import DETECTOR_LOGS_SCHEMA, create_table_query

DB_PATH = Path(__file__).parent / "syntwin.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(create_table_query(DETECTOR_LOGS_SCHEMA))
    conn.commit()
    conn.close()

# Auto-create table
initialize_db()
