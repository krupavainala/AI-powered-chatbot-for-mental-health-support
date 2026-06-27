from datetime import datetime
from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Link to User table
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'bot'
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)  # Optional: bot's response
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    emergency_flagged = db.Column(db.Boolean, default=False)
    is_admin_reply = db.Column(db.Boolean, default=False)
    delivered = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='messages')

    def __repr__(self):
        return f"<ChatMessage from user_id={self.user_id}, sender={self.sender}>"

def get_flagged_chats():
    return ChatMessage.query.filter_by(emergency_flagged=True).order_by(ChatMessage.timestamp.desc()).all()

def get_all_users():
    return User.query.order_by(User.username).all()
