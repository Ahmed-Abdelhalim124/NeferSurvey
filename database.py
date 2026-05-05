# database.py
import sqlite3
import numpy as np
import json
from datetime import datetime
from config import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            text      TEXT    NOT NULL,
            sentiment TEXT,
            emotion   TEXT,
            key_issue TEXT,
            timestamp TEXT    NOT NULL,
            embedding TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialized.")


def insert_feedback(text, sentiment, emotion, key_issue, embedding):
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    embedding_json = json.dumps(
        embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
    )
    cursor.execute("""
        INSERT INTO feedback (text, sentiment, emotion, key_issue, timestamp, embedding)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (text, sentiment, emotion, key_issue, datetime.now().isoformat(), embedding_json))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    print(f"✅ Feedback stored with ID: {new_id}")
    return new_id


def fetch_all_feedback():
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, text, sentiment, emotion, key_issue, timestamp, embedding
        FROM feedback ORDER BY timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id":        row[0],
            "text":      row[1],
            "sentiment": row[2],
            "emotion":   row[3],
            "key_issue": row[4],
            "timestamp": row[5],
            "embedding": json.loads(row[6]) if row[6] else None
        }
        for row in rows
    ]


def fetch_embeddings():
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, embedding FROM feedback WHERE embedding IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id":        row[0],
            "text":      row[1],
            "embedding": np.array(json.loads(row[2]), dtype=np.float32)
        }
        for row in rows
    ]


def get_feedback_count():
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM feedback")
    count  = cursor.fetchone()[0]
    conn.close()
    return count
