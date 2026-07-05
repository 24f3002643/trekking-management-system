from application.models import User
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from application.decorators import login_required

trekker_bp = Blueprint('trekker', __name__)

# ======================================== Trekker Routes =============================

@app.route('/trekker', methods=["GET"])
def trekker_dashboard():
    pass