from application.models import *
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from application.decorators import role_required
from application.controllers.admin_bp import admin_bp


# ============================== Admin-Trekker Routes ==============================

# To view all the existing trekkers
@admin_bp.route('/admin/trekkers', methods=["GET"])
@role_required('admin')
def admin_trekkers_page():
    id = session.get('user_id')
    this_user = User.query.filter_by(id=id).first()
    trekker_id = request.args.get("id", type=int)
    name = request.args.get("name", "").strip()
    email = request.args.get("email", "").strip()
    is_blacklisted = request.args.get("is_blacklisted")
    query = User.query.filter_by(role="trekker")
    if trekker_id:
        query = query.filter(User.id == trekker_id)
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if is_blacklisted == "true":
        query = query.filter(User.is_blacklisted.is_(True))
    elif is_blacklisted == "false":
        query = query.filter(User.is_blacklisted.is_(False))
    all_trekkers = query.order_by(User.name.asc()).all()
    return render_template("admin/admin_trekkers.html", this_user=this_user, all_trekkers=all_trekkers)

# To view the details of a particular trekker
@admin_bp.route('/admin/trekkers/<trekker_id>', methods=["GET"])
@role_required('admin')
def admin_trekkers_view(trekker_id):
    id = session.get('user_id')
    this_user = User.query.filter_by(id=id).first()

    trekker = User.query.filter_by(id=trekker_id).first()
    if trekker is None or trekker.role != "trekker":
        return render_template("message.html", title="No Trekker Found", message="No trekker with the given id exists.", href=url_for('admin.admin_trekkers_page'), a_text='Back to Admin Trekker Page')

    status_order = db.case(
        (Booking.booking_status == 'pending', 1),
        (Booking.booking_status == 'booked', 2),
        (Booking.booking_status == 'completed', 3),
        (Booking.booking_status == 'cancelled', 4),
        else_=5
    )
    bookings = Booking.query.filter_by(user_id=trekker.id).order_by(status_order, Booking.booking_date.desc()).all()
    return render_template("admin/admin_trekkers_details.html", this_user=this_user, trekker=trekker, bookings=bookings)

# To submit the request to blacklist the trekker
@admin_bp.route('/admin/trekkers/<trekker_id>/blacklist', methods=["POST"])
@role_required('admin')
def admin_trekkers_blacklist(trekker_id):
    trekker = User.query.get(trekker_id)
    if trekker is None or trekker.role != "trekker":
        return render_template("message.html", title="No Trekker Found", message="No Trekker with the given id exists.", href=url_for('admin.admin_trekkers_page'), a_text='Back to Admin Trekker Page')
    trekker.is_blacklisted = True
    db.session.commit()
    return render_template("message.html", title="Blacklisted", message="The trekker has been blacklisted successfully.", href=url_for('admin.admin_trekkers_page'), a_text='Back to Admin Trekker Page')


# To submit the request tp un-blacklist the trekker
@admin_bp.route('/admin/trekkers/<trekker_id>/unblacklist', methods=["POST"])
@role_required('admin')
def admin_trekkers_unblacklist(trekker_id):
    trekker = User.query.get(trekker_id)
    if trekker is None or trekker.role != "trekker":
        return render_template("message.html", title="No Trekker Found", message="No Trekker with the given id exists.", href=url_for('admin.admin_trekkers_page'), a_text='Back to Admin Trekker Page')
    trekker.is_blacklisted = False
    db.session.commit()
    return render_template("message.html", title="Un-Blacklisted", message="The trekker has been un-blacklisted successfully.", href=url_for('admin.admin_trekkers_page'), a_text='Back to Admin Trekker Page')

