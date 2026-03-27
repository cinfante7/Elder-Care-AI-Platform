import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'elder_assistant.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            speaker TEXT NOT NULL,
            text TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def log_conversation(speaker, text, timestamp=None):
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO conversations (timestamp, speaker, text) VALUES (?, ?, ?)',
        (timestamp, speaker, text)
    )
    conn.commit()
    conn.close()

def get_last_n_conversations(n=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, speaker, text FROM conversations ORDER BY id DESC LIMIT ?", (n,))
    rows = cursor.fetchall()
    conn.close()
    return list(reversed(rows))

def get_conversations_by_date(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, speaker, text FROM conversations
        WHERE date(timestamp) BETWEEN date(?) AND date(?)
        ORDER BY timestamp ASC
    ''', (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_conversations_by_keyword(keyword, start_date=None, end_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    if start_date and end_date:
        cursor.execute('''
            SELECT timestamp, speaker, text FROM conversations
            WHERE text LIKE ? AND date(timestamp) BETWEEN date(?) AND date(?)
            ORDER BY timestamp ASC
        ''', (f'%{keyword}%', start_date, end_date))
    else:
        cursor.execute('''
            SELECT timestamp, speaker, text FROM conversations
            WHERE text LIKE ?
            ORDER BY timestamp ASC
        ''', (f'%{keyword}%',))
    rows = cursor.fetchall()
    conn.close()
    return rows

def initialize_posts_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            author TEXT NOT NULL,
            text TEXT,
            image_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Call this in main initialization
initialize_posts_table()

def add_post(author, text, image_path=None, timestamp=None):
    from datetime import datetime
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO posts (timestamp, author, text, image_path) VALUES (?, ?, ?, ?)',
        (timestamp, author, text, image_path)
    )
    conn.commit()
    conn.close()

def get_recent_posts(limit=20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, author, text, image_path FROM posts ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return list(reversed(rows))

# Initialize DB when script is run directly
if __name__ == "__main__":
    initialize_db()
    print("Database initialized.")