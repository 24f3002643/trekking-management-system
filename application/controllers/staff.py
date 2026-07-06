from application.models import *
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from application.decorators import role_required
from application.controllers.staff_bp import staff_bp

# ====================================== Staff Routes =================================

@staff_bp.route('/staff', methods=["GET"])
def staff_dashboard():
    pass