from functools import wraps
from flask import session, redirect, url_for, render_template
from application.models import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        id = session.get('user_id')
        this_user = User.query.filter_by(id=id).first()
        if this_user is None:
            session.clear()
            return redirect(url_for('auth.login'))
        if this_user.is_blacklisted:
            session.clear()
            return render_template('message.html', title='Blacklisted', message='You have been blacklisted by the admin.', href=url_for('auth.login'), a_text='Return to Login Page')
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            id = session.get('user_id')
            this_user = User.query.filter_by(id=id).first()
            if this_user is None:
                session.clear()
                return redirect(url_for('auth.login'))
            if this_user.is_blacklisted:
                session.clear()
                return render_template('message.html', title='Blacklisted', message='You have been blacklisted by the admin.', href=url_for('auth.login'), a_text='Return to Login Page')
            if this_user.role != role:
                return render_template('message.html', title='Unauthorized', message='You are not authorized to view this page.', href=url_for('auth.login'), a_text='Return to Login Page')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

            