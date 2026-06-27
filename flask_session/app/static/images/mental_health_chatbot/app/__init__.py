from flask import Flask, render_template, session, redirect, url_for, jsonify, request,flash
from flask_login import LoginManager, login_user, logout_user
import random
from app.extensions import db, migrate, login_manager, init_extensions
from app.models import User  # ✅ Import here only after db is loaded
from werkzeug.security import generate_password_hash






def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
    app.config['SERVER_NAME'] = 'localhost:5000'
    
    
    init_extensions(app)

    @login_manager.user_loader
    def load_user(user_id):
        
        return User.query.get(int(user_id))
    


    # ROUTES — now defined directly
    @app.route('/')
    def home():
        return redirect(url_for('login'))

    @app.route('/chat')
    def chat():
        return render_template('chat.html')



    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            from app.models import User  # your User model
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):  # make sure you have a method to verify password
                login_user(user)
                session['username'] = username
                return redirect(url_for('chat'))
            else:
                flash('Invalid username or password')
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

        # Validate required fields
        if not email or not username or not password:
            flash("Email, username, and password are required.", "warning")
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
           flash("Username already exists.", "danger")
           return redirect(url_for('register'))

        # Create user and add to DB
        new_user = User (
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            username=username,
            is_admin=0,
            is_blocked=0
        )
        new_user.set_password(password)  # You must have set_password() in your model
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('login'))

     return render_template('register.html')

    
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

    @app.route("/send", methods=["POST"])
    def send():
        if 'username' not in session:
         return jsonify({'response': 'You are not logged in.'}), 401

         username = session['username']
    user_message = request.json.get('message', '').strip()

    if not user_message:
        return jsonify({'response': 'Please type something!'}), 400

    # Here you can integrate your DialoGPT or just send canned responses for now:
    if "stress" in user_message.lower():
        bot_reply = "I'm sorry you're feeling stressed. Try a deep breath or listen to some calming music."
    else:
        bot_reply = "I'm here to help. Tell me more about how you're feeling."

    # You could also save the messages to the DB here if desired.

    return jsonify({'response': bot_reply})


    @app.route('/chat_history')
    def chat_history():
        if 'username' not in session:
            return redirect(url_for('login'))

        username = session['username']
        import sqlite3
        conn = sqlite3.connect('chatbot.db')  # Adjust path if needed
        c = conn.cursor()
        try:
            c.execute('SELECT role, message, timestamp FROM messages WHERE username = ? ORDER BY timestamp', (username,))
            messages = c.fetchall()
        except sqlite3.OperationalError:
            messages = []
        conn.close()

        return render_template('view_chat.html', messages=messages, username=username)

    @app.route('/delete_chat_history', methods=['POST'])
    def delete_chat_history():
        if 'username' not in session:
            return jsonify({'status': 'error', 'message': 'User not logged in'}), 401
        # Add your deletion logic here
        # For example:
        username = session['username']
        import sqlite3
        conn = sqlite3.connect('chatbot.db')
        c = conn.cursor()
        c.execute('DELETE FROM messages WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Chat history deleted'})

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))
    
 


    from app.admin_routes import register_admin_routes
    with app.app_context():
        register_admin_routes(app)
    
    
    
    return app


#app.run(host="127.0.0.1", port=5000, debug=True)  # This line is unreachable!

# Database initialization for raw SQLite (optional, separate from SQLAlchemy)
import sqlite3

def init_db():
    conn = sqlite3.connect('your_database.db')  # replace with your DB path
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
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
