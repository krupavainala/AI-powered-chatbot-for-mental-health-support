from flask import Flask, render_template, request, jsonify, session
import sqlite3
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__, static_folder='app/static')
app.secret_key = 'your-secret-key'

# Initialize the database
def init_db():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Load model
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Dummy user for now
@app.before_request
def set_dummy_user():
    if 'username' not in session:
        session['username'] = 'testuser'

# Home route
@app.route('/')
def home():
    return render_template('chat.html', username=session['username'], chat_history=[])

# Chat page route
@app.route('/chat')
def chat():
    return render_template('chat.html', username=session.get('username', 'guest'), chat_history=[])

# Generate bot response
def generate_response(message):
    if "stress" in message.lower():
        return "I'm sorry you're feeling stressed. Try a deep breath or listen to some calming music."
    return "I'm here to help. Tell me more about how you're feeling."

# ✅ Correct placement of this route
@app.route("/send", methods=["POST"])
def send():
    if 'username' not in session:
        return jsonify({'response': 'You are not logged in.'})

    username = session['username']
    user_message = request.json.get('message', '').strip()

    if not user_message:
        return jsonify({'response': 'Please type something!'}), 400

    try:
        bot_reply = generate_response(user_message)
        return jsonify({'response': bot_reply})
    except Exception as e:
        return jsonify({'response': f"Error: {str(e)}"}), 500


