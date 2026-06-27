from flask import Flask, session, redirect, url_for, render_template, jsonify, request, flash
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import sqlite3
from app.chatbot import generate_bot_response  # This will use DialoGPT
from app.database import save_message, get_chat_history
from flask_login import login_required
import random

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
    LoginManager,
)
from app import db
import os
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from app import routes
import random
from dotenv import load_dotenv
from datetime import datetime
from app.models import FlaggedChat, User  # Adjust this if your model path is different
from app.quotes import motivational_quotes
from chatbot import generate_bot_response
from app.database import save_message, get_chat_history, delete_chat_history
from app.admin_routes import register_admin_routes
import re



logging.basicConfig(level=logging.DEBUG)

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = 'login'

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_default_secret')


# Load tokenizer and model once globally
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# To store chat histories per user session (dictionary keyed by session id)
chat_histories = {}


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def is_valid_phone(phone):
    # Example: only digits, length 10
    return phone.isdigit() and len(phone) == 10


def is_strong_password(password):
    # At least 6 characters, including letters and numbers
    return (
        len(password) >= 6 and
        re.search(r"[A-Za-z]", password) and
        re.search(r"[0-9]", password)
    )


if __name__ == "__main__":
    app.run(debug=True)

@app.route('/')
def home():
        return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            if user:
                if user.is_blocked:
                    flash('Your account has been blocked. Please contact support.', 'danger')
                    session.pop('username', None)
                    return redirect(url_for('login'))


                if user.is_admin:
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('chat'))

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                if user.is_blocked:
                   flash('Your account has been blocked. Please contact support.', 'danger')
                   return redirect(url_for('login'))


                session['username'] = username
                flash('Login successful. Welcome back!', 'success')

                if user.is_admin:
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('chat'))
            else:
                flash('Invalid credentials. Please try again.', 'danger')
                return redirect(url_for('login'))

        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('chat'))

    if request.method == 'POST':
        print("FORM DATA RECEIVED:", request.form.to_dict())

        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        print(f"DEBUG: email={email}")

        # Validation
        if not first_name:
            flash("First name is required.", "warning")
            return redirect(url_for('register'))

        if not last_name:
            flash("Last name is required.", "warning")
            return redirect(url_for('register'))

        if not email or not is_valid_email(email):
            flash("Please enter a valid email address.", "warning")
            return redirect(url_for('register'))

        if not phone or not is_valid_phone(phone):
            flash("Please enter a valid 10-digit phone number.", "warning")
            return redirect(url_for('register'))

        if not username:
            flash("Username is required.", "warning")
            return redirect(url_for('register'))


        if not is_strong_password(password):
            flash("Password must be at least 6 characters and include letters and numbers.", "warning")
            return redirect(url_for('register'))
        

        # Check if user exists in DB
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("User with that username or email already exists. Please log in.", "warning")
            return redirect(url_for('login'))

        # Create new user object
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            username=username,
            is_admin=False,
            is_blocked=False,
        )
        new_user.set_password(password)  # sets password_hash attribute

        # Add to DB
        db.session.add(new_user)
        db.session.commit()

        session['username'] = username
        flash('Registration successful. Welcome!', 'success')
        return redirect(url_for('chat'))

    # If GET request, just render the register form
    return render_template('register.html')

           

@app.route('/dashboard')
@login_required
def dashboard():
        username = current_user.username
        return render_template('admin_dashboard.html')

motivational_quotes = [
    "Believe in yourself!",
    "You are stronger than you think.",
    "Every day is a new opportunity.",
    "Keep pushing forward.",
    "You got this!",
    "Difficult roads often lead to beautiful destinations.",
    "It’s okay to not be okay.",
    "One step at a time.",
    "You are enough, just as you are.",
    "Your feelings are valid.",
    "Be proud of how far you’ve come.",
    "You are capable of amazing things.",
    "It’s a bad day, not a bad life.",
    "Progress, not perfection.",
    "You are not alone.",
    "This too shall pass.",
    "Healing takes time, and that’s okay.",
    "Your journey is unique.",
    "You deserve happiness.",
    "You have the power to create change.",
    "Be gentle with yourself.",
    "Start where you are. Use what you have. Do what you can.",
    "Small steps lead to big results.",
    "Rest is productive.",
    "Your mind is a garden—nurture it with kindness.",
    "One moment at a time.",
    "You’ve survived 100% of your worst days.",
    "Let your courage be stronger than your fear.",
    "You are doing better than you think.",
    "Don’t give up—you are closer than you think.",
    "Breathe. Relax. You are in control.",
    "You are worthy of love and care.",
    "Self-care is never selfish.",
    "Focus on progress, not perfection.",
    "Storms make trees take deeper roots.",
    "Growth begins where comfort ends.",
    "You’ve got what it takes.",
    "You are more than your struggles.",
    "Your voice matters.",
    "Keep showing up.",
    "Strength grows in the moments you think you can't go on but you keep going anyway.",
    "Your pace is perfect for your path.",
    "Every sunrise brings a new hope.",
    "You have a 100% success rate at surviving bad days.",
    "The comeback is always stronger than the setback.",
    "Feel it. Face it. Heal from it.",
    "You don’t need to have it all figured out.",
    "Your life is not a race.",
    "There is light, even in the darkest of times.",
    "Courage doesn’t always roar. Sometimes it’s a whisper.",
    "You are a work in progress, and that’s okay.",
    "There’s no shame in asking for help.",
    "Healing isn’t linear.",
    "Your story is not over.",
    "Let go of what you can’t control.",
    "Every effort counts.",
    "You have permission to pause.",
    "Be proud of small victories.",
    "Growth is painful, but so is staying stuck.",
    "You are not a burden.",
    "Your mental health matters.",
    "It’s brave to feel your feelings.",
    "You deserve inner peace.",
    "Recovery is possible.",
    "You are doing the best you can.",
    "Choose hope, even when it’s hard.",
    "Trust the timing of your life.",
    "Don’t compare your chapter 1 to someone else’s chapter 10.",
    "The only way out is through.",
    "You’re doing better than you were yesterday.",
    "You have the strength within you.",
    "Your dreams are valid.",
    "Keep hope in your heart.",
    "Choose yourself daily.",
    "You are enough.",
    "One day at a time.",
    "Every step forward is progress.",
    "You are growing even when it feels like you’re not.",
    "Trust yourself.",
    "Your presence matters.",
    "Be kind to your mind.",
    "Your past does not define you.",
    "Let today be a new beginning.",
    "Peace begins with you.",
    "You are not broken.",
    "Your courage inspires others.",
    "You can always begin again.",
    "Celebrate your progress.",
    "You are not weak for struggling.",
    "It’s okay to rest.",
    "Your worth is not measured by productivity.",
    "Hope is stronger than fear.",
    "You can rewrite your story.",
    "Breathe deeply. You are safe here.",
    "You are more than enough.",
    "It’s okay to start over.",
    "Your best is good enough.",
    "Your presence brings light.",
    "Even the darkest night will end and the sun will rise.",
    "Take time to recharge.",
    "You’re allowed to outgrow people, places, and versions of yourself.",
    "Kindness to yourself is a revolutionary act.",
    "Be patient with your progress."
   ]
calming_exercises = [
    "Focus on your breath. Inhale deeply for 4 seconds, hold for 4 seconds, then exhale for 4 seconds. Repeat until you feel calm.",
    "Let’s try progressive muscle relaxation. Start by tensing your feet, hold for a few seconds, and then release. Slowly move up your body—legs, abdomen, arms—tense and release each muscle group.",
    "Try box breathing: Inhale for 4 seconds, hold for 4, exhale for 4, and hold again for 4. Repeat this cycle for 2-3 minutes.",
    "Take a moment to reflect on your feelings. Try grounding yourself by identifying 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.",
    "Focus on being present. Look around and notice the details of your surroundings. Take a few slow, deep breaths to center yourself.",
    "Imagine a peaceful place, whether it's a quiet beach, forest, or mountain. Picture yourself there, feeling calm and relaxed.",
    "Let’s focus on grounding. Find 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste. This helps to bring you into the present moment.",
    "Try box breathing: Inhale for 4 seconds, hold for 4, exhale for 4, and hold again for 4. Repeat this cycle for 2-3 minutes.",
    "Put your hand over your heart and say to yourself: 'I am doing the best I can, and that’s enough. It’s okay to take it one step at a time.'",
    "Repeat these affirmations: 'I am calm. I am strong. I am in control. I can handle this moment.' Say them out loud or quietly to yourself.",
    "Try this breathing exercise: Breathe in for 5 seconds, hold for 5, and breathe out for 5. Focus only on your breath and repeat for a few minutes.",
    "Sit quietly and listen. Focus only on sounds around you—whether it’s the hum of the air, the rustling of leaves, or any soothing sound. Let yourself be absorbed by it.",
"Close your eyes and imagine your peaceful place—a quiet beach, a serene forest, or a cozy room. Visualize the sounds, smells, and feelings you associate with this place, and let it bring you calm.",
"If you can, try soaking your hands or feet in warm water. The warmth can help relax your muscles and soothe your mind.",
"Take a moment to write about how you’re feeling. It can help to get your thoughts down on paper and reflect on your emotions."

]


@app.route('/chat' , methods=['GET', 'POST'])
@login_required
def chat():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
 
    if request.method == 'POST':
        user_message = request.form.get('message', '')
        lower_msg = user_message.lower()

        # Check for distress keywords
        if "stress" in lower_msg or "anxiety" in lower_msg or "panic" in lower_msg:
            calming_message = random.choice(calming_exercises)
            save_message(username, user_message, calming_message)
            return render_template("chat.html", user_message=user_message, bot_response=calming_message)

        # Handle music playlist request locally
        if 'music' in lower_msg or 'playlist' in lower_msg:
            playlist_message = "Here’s a calming playlist for you: https://open.spotify.com/playlist/37i9dQZF1DX3PIPIT6lEg5"
            save_message(username, user_message, playlist_message)
            return render_template("chat.html", user_message=user_message, bot_response=playlist_message)

        # Motivational quotes request
        elif 'motivate' in lower_msg or 'motivation' in lower_msg or 'quote' in lower_msg:
            motivational_quote = random.choice(motivational_quotes)
            save_message(username, user_message, motivational_quote)
            return render_template("chat.html", user_message=user_message, bot_response=motivational_quote)

        # Calming exercises request
        elif 'calm' in lower_msg or 'exercise' in lower_msg or 'relax' in lower_msg:
            calming_exercise = random.choice(calming_exercises)
            save_message(username, user_message, calming_exercise)
            return render_template("chat.html", user_message=user_message, bot_response=calming_exercise)

        # Fallback: Use DialoGPT response
        bot_response = generate_bot_response(user_message, session_id=username)
        save_message(username, user_message, bot_response)
        return render_template("chat.html", user_message=user_message, bot_response=bot_response)

    # GET request: show previous chat history
    chat_history = get_chat_history(username)
    return render_template("chat.html", chat_history=chat_history)



@app.route('/send', methods=['POST'])
def send():
    if 'username' not in session:
        return jsonify({'reply': 'You are not logged in.'})

    username = session['username']
    user_message = request.json.get('message', '')
    lower_msg = user_message.lower()
    print(f"User message received: {user_message}")

    # ✅ Save the user's message to the database
    save_message(username, 'user', user_message)

    # ✅ Emergency keyword detection
    emergency_keywords = [
        "kill myself", "suicide", "help me", "emergency", "i want to die",
        "can't go on", "end my life", "harm myself"
    ]
    if any(keyword in lower_msg for keyword in emergency_keywords):
        alert_message = (
            "🚨 It seems you are going through a difficult time. "
            "Please reach out immediately to:\n\n"
            "📞 National Suicide Prevention Lifeline: 1-800-273-8255\n"
            "💬 Crisis Text Line: Text HOME to 741741\n"
            "Remember, you are not alone and help is available."
        )

        # ✅ Save flagged message to `FlaggedChat` table
        user = User.query.filter_by(username=username).first()
        if user:
            flagged = FlaggedChat(user_id=user.id, message=user_message)
            db.session.add(flagged)
            db.session.commit()
            print("🚨 Emergency message flagged and saved to admin panel.")

        # ✅ Save bot alert message to chat history
        save_message(username, 'bot', alert_message)

        # ✅ Return emergency alert response to frontend
        return jsonify({'response': alert_message})

    # ✅ Music playlist request
    if 'music' in lower_msg or 'playlist' in lower_msg:
        music_reply = "🎵 Here’s a calming playlist for you: https://www.youtube.com/watch?v=2OEL4P1Rz04"
        save_message(username, 'bot', music_reply)
        return jsonify({'response': music_reply})

    # ✅ Motivational quotes
    if 'motivate' in lower_msg or 'motivation' in lower_msg or 'quote' in lower_msg:
        motivational_quote = random.choice(motivational_quotes)
        save_message(username, 'bot', motivational_quote)
        return jsonify({'response': motivational_quote})

    # ✅ Calming exercises
    if 'calm' in lower_msg or 'exercise' in lower_msg or 'relax' in lower_msg:
        calming_exercise = random.choice(calming_exercises)
        save_message(username, 'bot', calming_exercise)
        return jsonify({'response': calming_exercise})

    # ✅ Default case: use AI chatbot response
    try:
        response = get_ai_response(user_message)
        save_message(username, 'bot', response)
        return jsonify({'response': response})
    except Exception as e:
        print(f"OpenAI API error: {e}")
        error_msg = "I'm really sorry, I couldn't process that right now. Please try again shortly."
        save_message(username, 'bot', error_msg)
        return jsonify({'response': error_msg})





@app.route('/chat_history')
def chat_history():
        if 'username' not in session:
            return redirect(url_for('login'))

        username = session['username']
        conn = sqlite3.connect(r'C:\Users\Admin\OneDrive\Desktop\mental_health_chatbot\chat.db')
        c = conn.cursor()
        try:
            c.execute('SELECT role, message, timestamp FROM messages WHERE username = ? ORDER BY timestamp', (username,))
            messages = c.fetchall()
        except sqlite3.OperationalError:
            messages = []
        conn.close()
        return render_template('history.html', messages=messages, username=username)



@app.route('/delete_chat_history', methods=['POST'])
def delete_chat_history():
    username = session.get('username')
    if not username:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

    conn = sqlite3.connect(r'C:\Users\Admin\OneDrive\Desktop\mental_health_chatbot\chat.db')
    c = conn.cursor()
    c.execute('DELETE FROM messages WHERE username = ?', (username,))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': 'Chat history deleted successfully.'})




@app.route('/end_chat')
def end_chat():
        quotes = [
            "You are braver than you believe, stronger than you seem, and smarter than you think. – A.A. Milne",
            "Keep going. Everything you need will come to you at the perfect time.",
            "You’ve got this. One step at a time.",
            "The struggle you’re in today is developing the strength you need for tomorrow.",
            "Your present circumstances don’t determine where you go. They merely determine where you start.",
            "It's okay not to be okay. Take a deep breath. You're doing great."
        ]
        backgrounds = [
            "images/bg1.jpg",
            "images/bg2.jpg",
            "images/bg3.jpg",
            "images/bg4.jpg"
        ]

        random_quote = random.choice(quotes)
        random_background = random.choice(backgrounds)
        return render_template("end_chat.html", quote=random_quote, background=random_background)

@app.route('/logout')
@login_required
def logout():
        logout_user()
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
from flask import Flask, request, jsonify, session
from app.chatbot import generate_response  # or your actual function name
from app.database import save_message



@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({'response': 'Please say something.'}), 400

    bot_response = generate_response(user_message)

    if 'user_id' in session:
        save_message(session['user_id'], 'user', user_message)
        save_message(session['user_id'], 'bot', bot_response)

    return jsonify({'response': bot_response})

@app.route('/ping')
def ping():
    return "pong"

...
# all routes here

if __name__ == "__main__":
    app.run(debug=True)

