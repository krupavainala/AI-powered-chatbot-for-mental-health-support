import os
import sqlite3
import logging
from datetime import datetime
from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, flash, session
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user, UserMixin
)
from .chatbot import generate_response

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    filename='chatbot.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from database import init_db
init_db()


# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")  # Use env var in production

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'chat.db')

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Dummy user class and example users dictionary for demo purposes
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Replace this with real user DB / auth logic
users = {
    "testuser": User("1", "testuser"),
}

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == user_id:
            return user
    return None

@login_manager.unauthorized_handler
def unauthorized_callback():
    # Return JSON 401 if AJAX, else redirect to login
    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"error": "Unauthorized"}), 401
    else:
        return redirect(url_for('login', next=request.endpoint))

def init_db():
    """Initialize the SQLite DB tables if not exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            message TEXT,
            timestamp TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS mood_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            mood TEXT NOT NULL,
            emoji TEXT NOT NULL,
            category TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

motivational_quotes = [
    "Believe in yourself. Every day is a new beginning.",
    "You are stronger than you think.",
    "Difficult roads often lead to beautiful destinations.",
    "This too shall pass. Keep going.",
    "You’ve survived 100% of your bad days so far.",
     "Your feelings are valid. It’s okay to feel this way.",
    "You are not your mistakes. You are learning and growing.",
    "Small steps every day lead to big changes over time.",
    "You have survived 100% of your hardest days — you are stronger than you know.",
    "Healing is not linear. Give yourself grace as you move forward.",
    "It’s okay to ask for help — it’s a sign of strength, not weakness.",
    "Focus on progress, not perfection.",
    "You are worthy of love, care, and kindness — especially from yourself.",
    "Take things one moment at a time.",
    "Even storms eventually give way to sunshine.",
    "Your story isn’t over — you’re writing new chapters every day.",
    "You don’t have to be perfect to be amazing.",
    "Believe in your ability to overcome.",
    "Each day is a fresh start to try again.",
    "Hope is the only thing stronger than fear."
]

calming_exercises = [
    "🧘 Take a deep breath in... and out... Do this for a minute.",
    "🌿 Close your eyes and imagine your favorite peaceful place.",
    "🎧 Listen to calming nature sounds.",
    "📝 Write down 3 things you're grateful for today.",
    "📵 Take a short break from your screen and stretch.",
    "Box Breathing: Inhale slowly for 4 seconds, hold your breath for 4 seconds, exhale for 4 seconds, and hold again for 4 seconds. Repeat 4 times.",
    "Grounding Technique: Look around and name 5 things you see, 4 things you can touch, 3 things you hear, 2 things you smell, and 1 thing you taste.",
    "Body Scan: Slowly focus on each part of your body from toes to head, noticing any tension, and consciously relaxing it.",
    "Mindful Listening: Close your eyes and focus on every sound around you for 2 minutes without judgment.",
    "Progressive Muscle Relaxation: Tense each muscle group for 5 seconds, then slowly release. Start from your feet and move upward.",
    "Visualization: Imagine a peaceful place (a beach, forest, or cozy room), and engage all your senses to experience it vividly.",
    "Journaling: Write down 3 things you’re grateful for or 3 things that went well today.",
    "Stretching: Gently stretch your arms, neck, and shoulders to release physical tension.",
    "Nature Walk: Take a slow walk outdoors focusing on the sensations of walking and the environment.",
    "5-4-3-2-1 Breathing: Combine grounding with breathing—breathe deeply while identifying sensory experiences.",
    "Affirmations: Repeat positive affirmations like “I am safe,” “I am calm,” or “I am enough.”",
    "Scent Focus: Use calming scents like lavender or chamomile and breathe deeply while focusing on the smell.",
    "Gentle Yoga: Try simple yoga poses like child’s pose or cat-cow to relax the body and mind.",
    "Hand Massage: Rub your hands together and gently massage each finger to increase mindfulness and calm.",
    "Creative Expression: Draw, doodle, or color to focus your mind on the present moment."
   
]

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))

    if request.method == 'POST':
        username = request.form.get('username')
        if username in users:
            login_user(users[username])
            flash('Logged in successfully.', 'success')
            return redirect(url_for('chat'))
        else:
            flash('Invalid username.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
def chat():
    # Renders the chat page with current username
    return render_template('chat.html', username=current_user.username)



@app.route('/chat_history_json')
@login_required
def chat_history_json():
     try:
        DB_PATH = 'chatbot.db'  # You can also load this from app config if preferred
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT role, message, timestamp FROM messages WHERE username=? ORDER BY timestamp ASC",
            (current_user.username,)
        )
        messages = c.fetchall()
        conn.close()

        messages_list = [
            {"role": row[0], "message": row[1], "timestamp": row[2]}
            for row in messages
        ]
        return jsonify(messages=messages_list, username=current_user.username)
    
     except Exception as e:
         print("Error in chat_history_json:", e)
         return jsonify(error=str(e)), 500
     






@app.route('/delete_chat_history', methods=['POST'])
@login_required
def delete_chat_history():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM messages WHERE username=?", (current_user.username,))
        conn.commit()
        conn.close()
        return jsonify({"status": "deleted"})
    except Exception as e:
        logging.error(f"Error deleting chat history: {e}")
        return jsonify({"status": "error"}), 500



def get_last_messages(username, limit=20):
    """Helper: Get last N messages from DB for a user in chronological order"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT role, message FROM messages WHERE username=? ORDER BY timestamp DESC LIMIT ?",
            (username, limit)
        )
        rows = c.fetchall()
        return list(reversed(rows))
    except Exception as e:
        logging.error(f"DB error in get_last_messages: {e}")
        return []
    finally:
        conn.close()
        
def save_message(username, role, message, timestamp):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO messages (username, role, message, timestamp) VALUES (?, ?, ?, ?)",
            (username, role, message, timestamp)
        )
        conn.commit()
    except Exception as e:
        logging.error(f"Error saving message: {e}")
    finally:
        conn.close()

@app.route('/send', methods=['POST'])
@login_required
def send():
    username = session['username']
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'response': 'Invalid request data'}), 400

    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'Empty message received'}), 400

    lower_msg = user_message.lower()

    emergency_keywords = [
        "kill myself", "suicide", "help me", "emergency", "i want to die",
        "can't go on", "end my life", "harm myself", "no reason to live"
    ]

    if 'conversation' not in session:
        session['conversation'] = []

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Emergency static alert (for safety)
        if any(keyword in lower_msg for keyword in emergency_keywords):
            alert = (
                "🚨 It seems you are going through a difficult time. "
                "Please reach out immediately to:\n\n"
                "📞 National Suicide Prevention Lifeline: 1-800-273-8255\n"
                "💬 Crisis Text Line: Text HOME to 741741\n"
                "You are not alone. We're here for you."
            )
            save_message(username, "user", user_message, timestamp)
            save_message(username, "bot", alert, timestamp)
            session['conversation'].append({'role': 'user', 'message': user_message, 'timestamp': timestamp})
            session['conversation'].append({'role': 'bot', 'message': alert, 'timestamp': timestamp})
            session.modified = True
            return jsonify({'response': alert})

        # Generate AI response for all user messages (including motivation, mood, calm, music, etc.)
        chat_history = [(m['role'], m['message']) for m in session.get('conversation', [])]

        # Optionally: You can add a system prompt here to instruct your AI to include mood tracking, motivation, meditation, music, calm exercises, etc. in responses.

        response, _ = generate_response(user_message, chat_history)

        save_message(username, "user", user_message, timestamp)
        save_message(username, "bot", response, timestamp)
        session['conversation'].append({'role': 'user', 'message': user_message, 'timestamp': timestamp})
        session['conversation'].append({'role': 'bot', 'message': response, 'timestamp': timestamp})
        session.modified = True

        return jsonify({'response': response})

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        return jsonify({'response': "Sorry, something went wrong. Please try again later."})



from flask import Flask, request, session, jsonify
from datetime import datetime
from app.extensions import db
from app.models import ChatMessage

EMERGENCY_KEYWORDS = ["help", "suicide", "kill myself", "emergency", "crisis"]

def is_emergency_message(text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in EMERGENCY_KEYWORDS)

@app.route('/send_message', methods=['POST'])
def send_message():
    username = session.get('username')
    if not username:
        return jsonify({"error": "User not logged in"}), 401

    user_message = request.form.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    emergency_flag = is_emergency_message(user_message)

    user_chat = ChatMessage(
        username=username,
        sender='user',
        message=user_message,
        emergency_flagged=emergency_flag,
        timestamp=datetime.utcnow()
    )
    db.session.add(user_chat)
    db.session.commit()

    bot_reply_text = "Thanks for your message. We're here to help."
    print("Emergency detected:", emergency_flag)

    bot_chat = ChatMessage(
        username=username,
        sender='bot',
        message=bot_reply_text,
        emergency_flagged=False,
        timestamp=datetime.utcnow()
    )
    db.session.add(bot_chat)
    db.session.commit()

    return jsonify({"bot_reply": bot_reply_text})


     


from flask import Flask, render_template, redirect, url_for, request, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Admin login page (GET) and login submission (POST)
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Replace with your real check
        if username == 'admin' and password == 'password':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials')
    return render_template('admin_login.html')

# Admin dashboard (requires login)
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    # Load flagged chats and users from DB here
    flagged_chats = []
    users = []
    return render_template('admin_dashboard.html', flagged_chats=flagged_chats, users=users)

# Admin logout
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


from flask import Flask, render_template
import random

app = Flask(__name__)

@app.route('/end_chat')
def end_chat():
    # List of 4 background image file paths (inside /static/images/)
    backgrounds = [
        'images/bg1.jpg',
        'images/bg2.jpg',
        'images/bg3.jpg',
        'images/bg4.jpg'
    ]

    # Motivational quotes
    quotes = [
        "Every day is a second chance.",
        "You are not alone. Better days are coming.",
        "Keep going. You’ve got this.",
        "Your story isn’t over yet."
    ]

    # Randomly choose one
    selected_bg = random.choice(backgrounds)
    selected_quote = random.choice(quotes)

    return render_template("end_chat.html", background=selected_bg, quote=selected_quote)

if __name__ == "__main__":
    app.run(debug=True)




