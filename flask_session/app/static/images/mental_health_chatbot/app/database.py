import sqlite3
from datetime import datetime

DB_PATH = r'C:\Users\Admin\OneDrive\Desktop\mental_health_chatbot\chat.db'  # single source

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT CHECK(role IN ('user', 'bot')) NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_message(username, role, message):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (username, role, message) VALUES (?, ?, ?)",
            (username, role, message)
        )
        conn.commit()
    except Exception as e:
        print("DB Error:", e)
    finally:
        conn.close()


def get_user_messages(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, message, timestamp FROM messages WHERE username = ? ORDER BY timestamp", (username,))
    messages = cursor.fetchall()
    conn.close()
    return messages

def get_chat_history(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, message FROM messages WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    return [{'sender': row[0], 'message': row[1]} for row in rows]

def delete_chat_history(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE username = ?", (username,))
    conn.commit()
    conn.close()




