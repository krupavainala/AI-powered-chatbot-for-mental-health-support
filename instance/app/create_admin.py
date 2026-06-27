from app import app, db
from app.models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if admin already exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            username="admin",
            password=generate_password_hash("adminpassword"),  # hash password
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
