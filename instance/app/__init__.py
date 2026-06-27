from flask import Flask, render_template, session, redirect, url_for, jsonify, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import random
import logging
import sqlite3
from datetime import datetime

from app.extensions import db, migrate, login_manager, init_extensions
from app.models import User
from app.chatbot import generate_response
from .admin_routes import register_admin_routes


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
    app.config['SERVER_NAME'] = 'localhost:5000'

    # Initialize extensions (db, login_manager, migrate, etc.)
    init_extensions(app)

    # Motivational quotes
    motivational_quotes = [
        "Believe in yourself and all that you are.",
        "You are stronger than you think.",
        "Every day is a second chance.",
        "Push yourself, because no one else is going to do it for you.",
        "Difficult roads often lead to beautiful destinations.",
        "Your only limit is your mind."
    ]

    # Calming exercises
    calming_exercises = [
        "Try deep breathing: Inhale for 4 seconds, hold for 7, exhale for 8.",
        "Close your eyes and picture a peaceful place.",
        "Stretch gently and slowly.",
        "Take a short walk and focus on your surroundings.",
        "Try progressive muscle relaxation.",
        "Listen to calming music and focus on the melody."
    ]

    def save_message(username, role, message, timestamp):
        """Save chat messages to SQLite database."""
        conn = sqlite3.connect('chatbot.db')
        c = conn.cursor()
        c.execute(
            "INSERT INTO messages (username, role, message, timestamp) VALUES (?, ?, ?, ?)",
            (username, role, message, timestamp)
        )
        conn.commit()
        conn.close()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def home():
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                session['username'] = username
                # Initialize conversation history in session
                if 'conversation' not in session:
                    session['conversation'] = []
                return redirect(url_for('chat'))
            else:
                flash('Invalid username or password', 'danger')
                return redirect(url_for('login'))

        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            username = request.form.get('username')
            password = request.form.get('password')

            if not email or not username or not password:
                flash("Email, username, and password are required.", "warning")
                return redirect(url_for('register'))

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash("Username already exists.", "danger")
                return redirect(url_for('register'))

            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                username=username,
                is_admin=0,
                is_blocked=0
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/chat')
    @login_required
    def chat():
        return render_template('chat.html')

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

        mental_health_responses = {
            "depress": "I'm really sorry you're feeling depressed. Remember, it's okay to seek help and talk about your feelings. You're not alone.",
            "depression": "Depression can be tough. I'm here to listen and support you. Would you like me to share some ways to cope or some motivational quotes?",
            "sad": "Feeling sad is a natural emotion. Sometimes sharing your thoughts can lighten the burden. I'm here if you want to talk.",
            "sadness": "Sadness can feel heavy. Remember to be kind to yourself and take small steps to care for your well-being.",
            "stress": "Stress can be overwhelming. Would you like me to guide you through some calming exercises or breathing techniques?",
            "overwhelmed": "It's okay to feel overwhelmed sometimes. Taking a moment to breathe deeply can help. Let me know if you want to try a relaxation exercise.",
            "anxiety": "Anxiety can be really hard to handle. Remember, you're strong and this feeling will pass. I'm here to support you.",
            "anxious": "Feeling anxious is tough. Would you like me to suggest some mindfulness exercises or calming tips?",
            "scared": "It's natural to feel scared sometimes. Talking about what's worrying you might help ease your mind.",
            "fear": "Fear can be paralyzing. Remember you’re safe right now. If you want, I can share some grounding techniques.",
            "panic": "Panic attacks are frightening. Try slow deep breaths with me if you'd like; I can guide you through it.",
            "nervous": "Nervousness is common. Remember to be gentle with yourself, and I’m here to listen.",
            "lonely": "Feeling lonely can hurt. Connecting with others or even talking here can help you feel less alone.",
            "hopeless": "Hopelessness can cloud your thoughts. You are valuable, and there is hope. I’m here for you.",
            "tired": "Being tired can affect your mood. Remember to rest and take care of yourself.",
            "helpless": "Feeling helpless is hard. Remember, small steps forward are progress. Let me know how I can support you.",
            "frustrated": "Frustration is a normal feeling. It’s okay to feel this way. Would you like to talk about what’s bothering you?",
            "angry": "Anger can be powerful. Taking deep breaths or a short walk can help calm those feelings. I can guide you if you want."
        }

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Emergency handling
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

            # Music request
            if 'music' in lower_msg or 'playlist' in lower_msg:
                music_link = "🎵 Here’s a calming playlist for you: https://www.youtube.com/watch?v=2OEL4P1Rz04"
                save_message(username, "user", user_message, timestamp)
                save_message(username, "bot", music_link, timestamp)
                session['conversation'].append({'role': 'user', 'message': user_message, 'timestamp': timestamp})
                session['conversation'].append({'role': 'bot', 'message': music_link, 'timestamp': timestamp})
                session.modified = True
                return jsonify({'response': music_link})

            # Motivation request
            if any(word in lower_msg for word in ['motivate', 'motivation', 'quote']):
                quote = random.choice(motivational_quotes)
                save_message(username, "user", user_message, timestamp)
                save_message(username, "bot", quote, timestamp)
                session['conversation'].append({'role': 'user', 'message': user_message, 'timestamp': timestamp})
                session['conversation'].append({'role': 'bot', 'message': quote, 'timestamp': timestamp})
                session.modified = True
                return jsonify({'response': quote})

            # Calming exercise request
            if any(word in lower_msg for word in ['calm', 'exercise', 'relax']):
                exercise = random.choice(calming_exercises)
                save_message(username, "user", user_message, timestamp)
                save_message(username, "bot", exercise, timestamp)
                session['conversation'].append({'role': 'user', 'message': user_message, 'timestamp': timestamp})
                session['conversation'].append({'role': 'bot', 'message': exercise, 'timestamp': timestamp})
                session.modified = True
                return jsonify({'response': exercise})

            # Mental health keyword-specific responses
            for keyword, response_text in mental_health_responses.items():
                if keyword in lower_msg:
                    save_message(username, "user", user_message, timestamp)
                    save_message(username, "bot", response_text, timestamp)
                    session['conversation'].append({'role': 'user', 'message': user_message, 'timestamp': timestamp})
                    session['conversation'].append({'role': 'bot', 'message': response_text, 'timestamp': timestamp})
                    session.modified = True
                    return jsonify({'response': response_text})

            # AI-generated fallback response
            chat_history = [(m['role'], m['message']) for m in session.get('conversation', [])]
            ai_response = generate_response(user_message, chat_history)

            save_message(username, "user", user_message, timestamp)
            save_message(username, "bot", ai_response, timestamp)

            session['conversation'].append({'role': 'user', 'message': user_message, 'timestamp': timestamp})
            session['conversation'].append({'role': 'bot', 'message': ai_response, 'timestamp': timestamp})
            session.modified = True

            return jsonify({'response': ai_response})

        except Exception as e:
            logging.error(f"Error processing message: {e}")
            return jsonify({'response': "Sorry, something went wrong. Please try again later."})

    @app.route('/delete_chat_history', methods=['POST'])
    @login_required
    def delete_chat_history():
        username = session['username']
        conn = sqlite3.connect('chatbot.db')
        c = conn.cursor()
        c.execute("DELETE FROM messages WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        session['conversation'] = []
        flash("Your chat history has been deleted.", "success")
        return redirect(url_for('chat'))

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

    @app.route("/end_chat")
    @login_required
    def end_chat():
        # Clear chat session on end
        session.pop('conversation', None)

        # List of background images stored in /static/images/
        backgrounds = [
            'images/bg1.jpg',
            'images/bg2.jpg',
            'images/bg3.jpg',
            'images/bg4.jpg'
        
        ]

        # List of motivational quotes
        motivational_quotes = [
            "Believe you can and you're halfway there.",
            "Every day is a second chance.",
            "You are stronger than you think.",
            "Keep going, you're doing great!",
            "Small steps lead to big changes."
        ]

        selected_background = random.choice(backgrounds)
        selected_quote = random.choice(motivational_quotes)

        return render_template(
            "end_chat.html",
            background_image=selected_background,
            quote=selected_quote,
            username=current_user.username
        )

    # Register admin routes here
    
    register_admin_routes(app)

    return app
