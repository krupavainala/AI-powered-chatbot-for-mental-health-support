from flask import render_template, request, redirect, url_for, flash, session, jsonify, abort
from app.extensions import db
from app.models import User, ChatMessage
from app.forms import BroadcastForm

def register_admin_routes(app):
    # Prevent multiple registrations of the same routes
    if hasattr(app, 'admin_routes_registered'):
        return
    app.admin_routes_registered = True

    def is_admin_session():
        user_id = session.get('user_id')
        if not user_id:
            return False
        user = User.query.get(user_id)
        return user and user.is_admin

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            username = request.form.get('username')  # fixed here: get() method with parentheses
            password = request.form.get('password')

            user = User.query.filter_by(username=username).first()
            if user and user.is_admin and user.check_password(password):
                session['user_id'] = user.id
                session['username'] = user.username  # added to allow session username checks
                flash('Admin login successful.', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials.', 'danger')
                return redirect(url_for('admin_login'))

        return render_template('admin_login.html')

    @app.route('/admin/logout')
    def admin_logout():
        session.pop('user_id', None)
        session.pop('username', None)
        flash('Logged out successfully.', 'info')
        return redirect(url_for('admin_login'))

    def admin_required(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_admin_session():
                flash('Access denied. Admins only.', 'danger')
                return redirect(url_for('admin_login'))
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/admin/block_user/<int:user_id>')
    @admin_required
    def block_user(user_id):
        user = User.query.get_or_404(user_id)
        user.is_blocked = True
        db.session.commit()
        flash(f'User {user.username} has been blocked.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/unblock_user/<int:user_id>')
    @admin_required
    def unblock_user(user_id):
        user = User.query.get_or_404(user_id)
        user.is_blocked = False
        db.session.commit()
        flash(f'User {user.username} has been unblocked.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/delete_user/<int:user_id>')
    @admin_required
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} has been deleted.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/broadcast', methods=['POST'])
    @admin_required
    def send_broadcast():
        form = BroadcastForm()
        if form.validate_on_submit():
            message = form.message.data
            # TODO: Implement broadcast logic here (e.g. save to DB, notify users)
            flash('Broadcast message sent.', 'success')
        else:
            flash('Message cannot be empty.', 'warning')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/emergencies')
    @admin_required
    def view_emergencies():
        emergencies = ChatMessage.query.filter_by(
            emergency_flagged=True,
            is_admin_reply=False
        ).order_by(ChatMessage.timestamp.desc()).all()
        return render_template('admin_emergencies.html', emergencies=emergencies)

    @app.route('/admin/reply', methods=['POST'])
    @admin_required
    def admin_reply():
        # Removed session username check here since we already verify admin session
        user_id = request.form.get('user_id')
        reply_message = request.form.get('reply_message')

        if not user_id or not reply_message:
            flash("Missing user or reply message", "danger")
            return redirect(url_for('view_emergencies'))

        user = User.query.get(user_id)
        if not user:
            flash("User not found", "danger")
            return redirect(url_for('view_emergencies'))

        reply = ChatMessage(
            user_id=user.id,
            sender='bot',
            message=reply_message,
            emergency_flagged=False,
            is_admin_reply=True,
            delivered=False
        )
        db.session.add(reply)

        emergencies = ChatMessage.query.filter_by(
            user_id=user.id,
            emergency_flagged=True,
            is_admin_reply=False
        ).all()
        for em in emergencies:
            em.emergency_flagged = False
        db.session.commit()

        flash("Reply sent successfully", "success")
        return redirect(url_for('view_emergencies'))

    @app.route('/get_admin_replies/<int:user_id>')
    @admin_required
    def get_admin_replies(user_id):
        messages = ChatMessage.query.filter_by(
            user_id=user_id,
            sender='bot',
            is_admin_reply=True,
            delivered=False
        ).order_by(ChatMessage.timestamp.asc()).all()

        for msg in messages:
            msg.delivered = True
        db.session.commit()

        reply_list = [{"text": msg.message, "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")} for msg in messages]
        return jsonify({"messages": reply_list})

    @app.route('/admin/dashboard')
    @admin_required
    def admin_dashboard():
        form = BroadcastForm()
        flagged_chats = ChatMessage.query.filter_by(emergency_flagged=True).order_by(ChatMessage.timestamp.desc()).all()
        users = User.query.order_by(User.username).all()
        return render_template('admin_dashboard.html', flagged_chats=flagged_chats, users=users, form=form)
