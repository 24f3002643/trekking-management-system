from application.models import *
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from application.decorators import role_required
from application.controllers.staff_bp import staff_bp
from datetime import date

# ====================================== Staff Routes =================================

# To access the dashboard by staff
@staff_bp.route('/staff', methods=["GET"])
@role_required('staff')
def staff_dashboard():
    id = session.get('user_id')
    this_user = User.query.get(id)
    status_order = db.case(
        (Trek.status == "ongoing", 1),
        (Trek.status == "upcoming", 2),
        (Trek.status == "completed", 3),
        (Trek.status == "cancelled", 4),
        else_=5
    )
    today = date.today()
    all_assigned_treks = Trek.query.join(StaffTrekAssignment, Trek.id == StaffTrekAssignment.trek_id).filter(StaffTrekAssignment.user_id == id).order_by(status_order, Trek.start_date.asc()).all()
    total_upcoming_treks = len(Trek.query.join(StaffTrekAssignment, Trek.id == StaffTrekAssignment.trek_id).filter(StaffTrekAssignment.user_id == id, Trek.status=="upcoming").order_by(Trek.start_date.asc()).all())
    total_ongoing_treks = len(Trek.query.join(StaffTrekAssignment, Trek.id == StaffTrekAssignment.trek_id).filter(StaffTrekAssignment.user_id == id, Trek.status=="ongoing").order_by(Trek.start_date.asc()).all())
    all_associated_bookings = Booking.query.join(StaffTrekAssignment, StaffTrekAssignment.trek_id==Booking.trek_id).filter(StaffTrekAssignment.user_id == id, Booking.booking_status == "booked").all()
    total_participants = len({b.user_id for b in all_associated_bookings})
    trek_participant_counts = {}
    for booking in all_associated_bookings:
        trek_participant_counts[booking.trek_id] = trek_participant_counts.get(booking.trek_id, 0) + 1
    return render_template('staff/staff_dashboard.html', this_user=this_user, today=today, all_assigned_treks=all_assigned_treks, total_ongoing_treks=total_ongoing_treks, total_upcoming_treks=total_upcoming_treks, total_participants=total_participants, trek_participant_counts=trek_participant_counts)




# To view of list of treks assigned to staff
@staff_bp.route('/staff/treks', methods=["GET"])
@role_required('staff')
def staff_treks_page():
    id = session.get('user_id')
    this_user = User.query.get(id)
    status_order = db.case(
        (Trek.status == "ongoing", 1),
        (Trek.status == "upcoming", 2),
        (Trek.status == "completed", 3),
        (Trek.status == "cancelled", 4),
        else_=5
    )
    today = date.today()
    status = request.args.get('status')
    difficulty = request.args.get('difficulty')
    location = request.args.get("location")
    trekname = request.args.get("trekname")
    query = Trek.query.join(StaffTrekAssignment, Trek.id == StaffTrekAssignment.trek_id).filter(StaffTrekAssignment.user_id == id)
    if status:
        query = query.filter(Trek.status == status)
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))
    if trekname:
        query = query.filter(Trek.trekname.ilike(f"%{trekname}%"))
    all_assigned_treks = query.order_by(status_order, Trek.start_date.asc()).all()
    all_associated_bookings = Booking.query.join(StaffTrekAssignment, StaffTrekAssignment.trek_id==Booking.trek_id).filter(StaffTrekAssignment.user_id == id, Booking.booking_status == "booked").all()
    trek_participant_counts = {}
    for booking in all_associated_bookings:
        trek_participant_counts[booking.trek_id] = trek_participant_counts.get(booking.trek_id, 0) + 1
    return render_template('staff/staff_treks.html', this_user=this_user, today=today, all_assigned_treks=all_assigned_treks, trek_participant_counts=trek_participant_counts)


# To view of details of a particular trek assigned to staff
@staff_bp.route('/staff/treks/<trek_id>', methods=["GET"])
@role_required('staff')
def staff_treks_view(trek_id):
    id = session.get('user_id')
    this_user = User.query.get(id)
    staff_assigned = StaffTrekAssignment.query.filter_by(user_id=id, trek_id=trek_id).first()
    if staff_assigned is None:
        return render_template("message.html", title="Not Allowed", message="You are not assigned to this trek.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks Assigned')
    trek = Trek.query.get(trek_id)
    if trek is None:
        return render_template("message.html", title="Not Found", message="Trek not found.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    today = date.today()
    all_assigned_trekkers = db.session.query(User, Booking).join(Booking, User.id==Booking.user_id).filter(Booking.trek_id==trek_id, Booking.booking_status=="booked").order_by(User.name.asc()).all()
    return render_template('staff/staff_treks_details.html', today=today, this_user=this_user, trek=trek, all_assigned_trekkers=all_assigned_trekkers)

      
# To view all the participants assigned to this staff
@staff_bp.route('/staff/trekkers', methods=["GET"])
@role_required('staff')
def staff_trekkers_page():
    id = session.get('user_id')
    this_user = User.query.get(id)
    trekkername = request.args.get("trekkername")
    trekname = request.args.get("trekname")
    status = request.args.get("status")

    query = (
        db.session.query(User, Booking, Trek)
        .join(Booking, User.id==Booking.user_id)
        .join(Trek, Trek.id==Booking.trek_id)
        .join(StaffTrekAssignment, StaffTrekAssignment.trek_id==Trek.id)
        .filter(StaffTrekAssignment.user_id == id, Booking.booking_status=="booked")
    )
    if trekkername:
        query = query.filter(User.name.ilike(f"%{trekkername}%"))
    if trekname:
        query = query.filter(Trek.trekname.ilike(f"%{trekname}%"))
    if status:
        query = query.filter(Trek.status == status)
    all_trekkers = query.order_by(User.name.asc()).all()
    return render_template("staff/staff_trekkers.html", this_user=this_user, all_trekkers=all_trekkers)


