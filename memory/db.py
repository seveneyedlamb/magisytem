import sqlite3
import os

DB_PATH = "data/magi.db"

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize the MAGI SQLite database with required tables."""
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS conversation_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_query TEXT,
                melchior_response TEXT,
                balthasar_response TEXT,
                casper_response TEXT,
                final_decision TEXT,
                keypoints TEXT
            )
        ''')
        conn.commit()

# Ensure DB is initialized on module load
init_db()
