from application.models import User
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from application.decorators import login_required

staff_bp = Blueprint('staff', __name__)


# ====================================== Staff Routes =================================

@app.route('/staff', methods=["GET"])
def staff_dashboard():
    pass