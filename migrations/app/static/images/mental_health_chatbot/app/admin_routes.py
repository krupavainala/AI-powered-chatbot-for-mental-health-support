from flask import render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models import User, ChatMessage
from app.forms import BroadcastForm

def register_admin_routes(app):

    def is_admin_session():
        return 'username' in session and session['username'] == 'Deekshitha'

    @app.route('/admin')
    def admin_dashboard():
        form = BroadcastForm()
        if not is_admin_session():
            flash('Access denied.', 'danger')
            return redirect(url_for('admin_login'))

        form = BroadcastForm()
        flagged_chats = ChatMessage.query.filter_by(emergency_flagged=True).all()
        users = User.query.all()
        return render_template('admin_dashboard.html', flagged_chats=flagged_chats, users=users, form=form)  # ✅ pass form here

    @app.route('/admin_login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            ADMIN_USERNAME = 'Deekshitha'
            ADMIN_PASSWORD = 'Deekshitha123'

            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['username'] = username
                flash('Admin login successful.', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials.', 'danger')
                return redirect(url_for('admin_login'))

        return render_template('admin_login.html')

    @app.route('/admin/logout')
    def admin_logout():
        session.pop('username', None)
        flash('Logged out successfully.', 'info')
        return redirect(url_for('admin_login'))

    @app.route('/admin/block_user/<int:user_id>')
    def block_user(user_id):
        if not is_admin_session():
            flash('Access denied.', 'danger')
            return redirect(url_for('admin_login'))

        user = User.query.get(user_id)
        if user:
            user.is_blocked = True
            db.session.commit()
            flash(f'User {user.username} has been blocked.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/unblock_user/<int:user_id>')
    def unblock_user(user_id):
        if not is_admin_session():
            flash('Access denied.', 'danger')
            return redirect(url_for('admin_login'))

        user = User.query.get(user_id)
        if user:
            user.is_blocked = False
            db.session.commit()
            flash(f'User {user.username} has been unblocked.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/delete_user/<int:user_id>')
    def delete_user(user_id):
        if not is_admin_session():
            flash('Access denied.', 'danger')
            return redirect(url_for('admin_login'))

        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash(f'User {user.username} has been deleted.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/broadcast', methods=['POST'])
    def send_broadcast():
        if not is_admin_session():
            flash('Access denied.', 'danger')
            return redirect(url_for('admin_login'))

        form = BroadcastForm()
        if form.validate_on_submit():
            message = form.message.data
            # Logic to broadcast message goes here
            flash('Broadcast message sent.', 'success')
        else:
            flash('Message cannot be empty.', 'warning')

        return redirect(url_for('admin_dashboard'))


   
