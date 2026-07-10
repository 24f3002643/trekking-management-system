from application.models import *
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from application.decorators import role_required
from application.controllers.trekker_bp import trekker_bp
from werkzeug.security import check_password_hash, generate_password_hash

# To view the profile page
@trekker_bp.route('/trekker/profile', methods=["GET"])
@role_required('trekker')
def trekker_profile():
    id = session.get('user_id')
    this_user = User.query.get(id)
    return render_template("trekker/trekker_profile.html", this_user=this_user)

# To view and submit the profile update page
@trekker_bp.route('/trekker/profile/update', methods=["GET", "POST"])
@role_required('trekker')
def trekker_profile_update():
    if request.method == "GET":
        id = session.get('user_id')
        this_user = User.query.get(id)
        return render_template("trekker/trekker_profile_update.html", this_user=this_user)

    if request.method == "POST":
        id = session.get('user_id')
        this_user = User.query.get(id)
        name = request.form.get("name", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        if not name:
            return render_template("message.html", title="Error", message="Name cannot be empty.", href=url_for('trekker.trekker_profile_update'), a_text="Back to Profile Update Page")
        if not phone_number:
            return render_template("message.html", title="Error", message="Phone Number cannot be empty.", href=url_for('trekker.trekker_profile_update'), a_text="Back to Profile Update Page")
        if phone_number:
            user = User.query.filter_by(phone_number=phone_number).first()
            if user and user.id != this_user.id:
                return render_template("message.html", title="Error", message="Phone Number already exists. Try adding different phone number", href=url_for('trekker.trekker_profile_update'), a_text='Back to Profile Update Page')
            this_user.phone_number = phone_number
        if current_password or new_password:
            if not current_password:
                return render_template("message.html", title="Error", message="Current Password is empty.", href=url_for('trekker.trekker_profile_update'), a_text='Back to Profile Update Page')
            if not new_password:
                return render_template("message.html", title="Error", message="New Password is empty.", href=url_for('trekker.trekker_profile_update'), a_text='Back to Profile Update Page')
            if not check_password_hash(this_user.password_hash, current_password):
                return render_template("message.html", title="Error", message="Current Password is Wrong.", href=url_for('trekker.trekker_profile_update'), a_text='Back to Profile Update Page')
            this_user.password_hash = generate_password_hash(new_password)
        if name:
            this_user.name = name
        db.session.add(this_user)
        db.session.commit()
        return render_template("message.html", title="Successful", message="Profile Updated Successfully", href=url_for('trekker.trekker_profile'), a_text='Back to Profile Page')