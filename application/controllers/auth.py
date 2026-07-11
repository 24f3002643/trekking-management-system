from application.models import User
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from application.decorators import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=["GET"])
@login_required
def home():
    id = session.get('user_id')
    this_user = User.query.filter_by(id=id).first()
    if this_user.role == "admin":
        return redirect(url_for('admin.admin_dashboard'))
    if this_user.role == "staff":
        return redirect(url_for('staff.staff_dashboard'))
    if this_user.role == "trekker":
        return redirect(url_for('trekker.trekker_dashboard'))
    

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET": 
        return render_template('login.html')
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        this_user = User.query.filter_by(email=email).first()
        
        if this_user is None:
            return render_template('message.html', title='Invalid Login', message='Invalid Email or Password', href=url_for( 'auth.login' ), a_text='Return to Login Page')
        if check_password_hash(this_user.password_hash, password) == False:
            return render_template('message.html', title='Invalid Login', message='Invalid Email or Password', href=url_for( 'auth.login' ), a_text='Return to Login Page')

        if this_user.role == 'admin':
            session['user_id'] = this_user.id
            session['role'] = this_user.role
            return redirect(url_for('admin.admin_dashboard'))
        
        if this_user.role == 'staff':
            if this_user.approval_status == "pending" :
                return render_template('message.html', title='Registration Pending', message='Your request for registration is not approved by admin yet. Try login in after some time.', href=url_for( 'auth.login' ), a_text='Return to Login Page')
            if this_user.approval_status == "rejected" :
                return render_template('message.html', title='Registration Rejected', message='Your request for registration is rejected by the admin.', href=url_for( 'auth.login' ), a_text='Return to Login Page')
            if this_user.approval_status == "approved" :
                if this_user.is_blacklisted :
                    return render_template('message.html', title='Blacklisted', message='You have been blacklisted by the admin.', href=url_for( 'auth.login' ), a_text='Return to Login Page')
                session['user_id'] = this_user.id
                session['role'] = this_user.role
                return redirect(url_for('staff.staff_dashboard'))
            
        if this_user.role == "trekker": 
            if this_user.is_blacklisted :
                return render_template('message.html', title='Blacklisted', message='You have been blacklisted by the admin.', href=url_for( 'auth.login' ), a_text='Return to Login Page')
            session['user_id'] = this_user.id
            session['role'] = this_user.role
            return redirect(url_for('trekker.trekker_dashboard'))

@auth_bp.route('/logout', methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register/trekker', methods=["GET", "POST"])
def register_trekker():
    if request.method == "GET":
        return render_template('register_trekker.html')
    
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        phone_number = request.form.get("phone_number")
        role = "trekker"
        this_user = User.query.filter_by(email=email).first()

        if this_user is not None:
            return render_template('message.html', title='User Exists', message='User already exists.', href=url_for( 'auth.login' ), a_text='Return to Login Page')

        this_user = User.query.filter_by(phone_number=phone_number).first()
        if this_user is not None:
            return render_template('message.html', title='Phone Number Already Exists', message='This Phone Number is already registered. Register with another phone number', href=url_for( 'auth.register_trekker' ), a_text='Return to Trekker Registration Page')

        approval_status = None 
        is_blacklisted = False 
        password_hash = generate_password_hash(password)
        new_user = User(name=name, email=email, password_hash=password_hash, phone_number=phone_number, role=role, approval_status=approval_status, is_blacklisted=is_blacklisted)
        db.session.add(new_user)
        db.session.commit()
        return render_template('message.html', title='Registration Successful', message='You have been successfully been registered as trekker. Login in to access the application.', href=url_for( 'auth.login' ), a_text='Return to Login Page')
    

@auth_bp.route('/register/staff', methods=["GET", "POST"])
def register_staff():
    if request.method == "GET":
        return render_template('register_staff.html')
    
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        phone_number = request.form.get("phone_number")
        role = "staff"
        this_user = User.query.filter_by(email=email).first()

        if this_user is not None:
            return render_template('message.html', title='User Exists', message='User already exists.', href=url_for( 'auth.login' ), a_text='Return to Login Page')

        this_user = User.query.filter_by(phone_number=phone_number).first()
        if this_user is not None:
            return render_template('message.html', title='Phone Number Already Exists', message='This Phone Number is already registered. Register with another phone number', href=url_for( 'auth.register_staff' ), a_text='Return to Staff Registration Page')

        approval_status = "pending"
        is_blacklisted = False 
        password_hash = generate_password_hash(password)
        new_user = User(name=name, email=email, password_hash=password_hash, phone_number=phone_number, role=role, approval_status=approval_status, is_blacklisted=is_blacklisted)
        db.session.add(new_user)
        db.session.commit()
        return render_template('message.html', title='Registration Request Successful', message='Your request for registration has been successfully been sent to Admin. Try login in after some time.', href=url_for( 'auth.login' ), a_text='Return to Login Page')
    
