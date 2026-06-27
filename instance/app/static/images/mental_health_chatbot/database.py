import sqlite3
from datetime import datetime

DATABASE = 'chatbot.db'
 # Or whatever your DB filename is

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (username, role, message, timestamp) VALUES (?, ?, ?, ?)",
        (username, role, message, datetime.now())
    )
    conn.commit()
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
    cursor.execute("SELECT role, message, timestamp FROM messages WHERE username = ? ORDER BY timestamp", (username,))
    history = cursor.fetchall()
    conn.close()
    return history
def delete_chat_history(username):
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE username = ?", (username,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized!")


