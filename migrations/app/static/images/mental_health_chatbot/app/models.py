
from flask_login import UserMixin
from datetime import datetime
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200),nullable=False)
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'bot'
    message = db.Column(db.Text,  nullable=False)
    response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,  nullable=False)
    emergency_flagged = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='messages')

    def __repr__(self):
        return f"<ChatMessage from user_id={self.user_id}>"

class FlaggedChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref='flagged_chats')
