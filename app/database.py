import sqlite3
from datetime import datetime

DB_PATH = r'C:\Users\Admin\OneDrive\Desktop\mental_health_chatbot\chat.db'  # single source


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist yet."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create messages table with only core columns at first
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT CHECK(role IN ('user', 'bot')) NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create mood_tracker table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            mood TEXT,
            emoji TEXT,
            category TEXT,
            timestamp TEXT
        )
    ''')

    conn.commit()
    conn.close()

    # Create emergencies table separately
    init_emergencies_table()

    # Add any missing columns in messages table (is_admin_reply, delivered)
    update_messages_table()

def update_messages_table():
    """Add missing columns to messages table if not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(messages)")
    columns = [row["name"] for row in cursor.fetchall()]

    if 'is_admin_reply' not in columns:
        cursor.execute("ALTER TABLE messages ADD COLUMN is_admin_reply INTEGER DEFAULT 0")
    if 'delivered' not in columns:
        cursor.execute("ALTER TABLE messages ADD COLUMN delivered INTEGER DEFAULT 0")

    conn.commit()
    conn.close()

def init_emergencies_table():
    """Create emergencies table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emergencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            replied INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def save_message(username, role, message, timestamp=None, is_admin_reply=0, delivered=0):
    """
    Save a message to the database.

    Parameters:
    - username: string, username of sender
    - role: 'user' or 'bot' only (IMPORTANT: must respect CHECK constraint)
    - message: string, the message text
    - timestamp: optional datetime string, if None current time used
    - is_admin_reply: int 0 or 1, marks if message was from admin reply
    - delivered: int 0 or 1, delivery status
    """
    if isinstance(username, list):
        username = username[0]  # Defensive: use first element if list

    if role not in ('user', 'bot'):
        raise ValueError("Role must be 'user' or 'bot' to comply with DB CHECK constraint")

    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO messages (username, role, message, timestamp, is_admin_reply, delivered)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, role, message, timestamp, is_admin_reply, delivered))
    conn.commit()
    conn.close()

def get_user_messages(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, message, timestamp FROM messages WHERE username = ? ORDER BY timestamp",
        (username,)
    )
    messages = cursor.fetchall()
    conn.close()
    return messages

def get_chat_history(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, message, is_admin_reply FROM messages WHERE username = ? ORDER BY timestamp",
        (username,)
    )
    rows = cursor.fetchall()
    conn.close()

    chat_history = []
    for row in rows:
        try:
            # Defensive default values in case keys are missing
            role = row['role'] if 'role' in row.keys() else 'user'
            is_admin_reply = row['is_admin_reply'] if 'is_admin_reply' in row.keys() else 0
            message = row['message'] if 'message' in row.keys() else ''

            sender = 'bot' if is_admin_reply else role
            chat_history.append({'sender': sender, 'message': message})
        except Exception as e:
            print("Error building chat history entry:", e)
            print("Row content:", dict(row))

    print(f"DEBUG: chat_history for user {username}: {chat_history}")
    return chat_history






def delete_chat_history(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def save_emergency(username, message):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emergencies (username, message) 
            VALUES (?, ?)
        """, (username, message))
        conn.commit()
    except Exception as e:
        print("Emergency DB Error:", e)
    finally:
        conn.close()

def get_emergencies():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, message, timestamp FROM emergencies ORDER BY timestamp DESC")
    emergencies = cursor.fetchall()
    conn.close()
    return emergencies

def save_user_message(user, message):
    emergency_flag = check_if_emergency(message)  # Your logic to detect emergencies
    chat_msg = ChatMessage(
        user=user,
        message=message,
        emergency_flagged=emergency_flag
    )
    db.session.add(chat_msg)
    db.session.commit()


if __name__ == "__main__":
    init_db()
    print("Database tables created or updated.")
