from application.models import *
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from application.decorators import role_required
from application.controllers.staff_bp import staff_bp
from datetime import date



# To start the trek
@staff_bp.route('/staff/treks/<trek_id>/ongoing', methods=["POST"])
@role_required('staff')
def staff_treks_ongoing(trek_id):
    id = session.get('user_id')
    this_user = User.query.get(id)
    staff_assigned = StaffTrekAssignment.query.filter_by(user_id=id, trek_id=trek_id).first()
    if staff_assigned is None:
        return render_template("message.html", title="Not Allowed", message="You are not allowed to update this trek.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks Assigned')
    trek = Trek.query.get(trek_id)
    if trek is None:
        return render_template("message.html", title="Not Found", message="Trek not found.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    if trek.status == "ongoing":
        return render_template("message.html", title="Not Allowed", message="Trek is already started", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    if trek.status == "cancelled":
        return render_template("message.html", title="Not Allowed", message="Cancelled Trek cannot be marked as ongoing.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    if trek.status == "completed":
        return render_template("message.html", title="Not Allowed", message="Completed Trek cannot be marked as ongoing.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    today = date.today()
    if today < trek.start_date:
        return render_template("message.html", title="Not Allowed", message="Trek cannot start before the start date.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    trek.status = "ongoing"
    db.session.commit()
    return render_template("message.html", title="Successful", message="Trek have started successfully.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')

# To complete the trek
@staff_bp.route('/staff/treks/<trek_id>/completed', methods=["POST"])
@role_required('staff')
def staff_treks_completed(trek_id):
    id = session.get('user_id')
    this_user = User.query.get(id)
    staff_assigned = StaffTrekAssignment.query.filter_by(user_id=id, trek_id=trek_id).first()
    if staff_assigned is None:
        return render_template("message.html", title="Not Allowed", message="You are not allowed to update this trek.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks Assigned')
    trek = Trek.query.get(trek_id)
    if trek is None:
        return render_template("message.html", title="Not Found", message="Trek not found.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    if trek.status == "completed":
        return render_template("message.html", title="Not Allowed", message="Trek is already completed", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    if trek.status == "cancelled":
        return render_template("message.html", title="Not Allowed", message="Cancelled Trek cannot be marked as completed.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    if trek.status == "upcoming":
        return render_template("message.html", title="Not Allowed", message="Upcoming Trek cannot be marked as complete.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    today = date.today()
    if today < trek.start_date:
        return render_template("message.html", title="Not Allowed", message="Trek cannot be marked as complete before start date.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    trek.status = "completed"
    all_active_bookings = Booking.query.filter(Booking.trek_id == trek_id, Booking.booking_status.in_(["booked", "pending"])).all()
    for booking in all_active_bookings:
        if booking.booking_status == "booked":
            booking.booking_status = "completed"
        if booking.booking_status == "pending":
            booking.booking_status = "cancelled"
            booking.payment_status = "refunded"
    db.session.commit()
    return render_template("message.html", title="Successful", message="Trek is completed successfully.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')


# To cancel the trek
@staff_bp.route('/staff/treks/<trek_id>/cancelled', methods=["POST"])
@role_required('staff')
def staff_treks_cancelled(trek_id):
    id = session.get('user_id')
    this_user = User.query.get(id)
    staff_assigned = StaffTrekAssignment.query.filter_by(user_id=id, trek_id=trek_id).first()
    if staff_assigned is None:
        return render_template("message.html", title="Not Allowed", message="You are not allowed to update this trek.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks Assigned')
    trek = Trek.query.get(trek_id)
    if trek is None:
        return render_template("message.html", title="Not Found", message="Trek not found.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    if trek.status == "completed":
        return render_template("message.html", title="Not Allowed", message="Trek is already completed", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    if trek.status == "cancelled":
        return render_template("message.html", title="Not Allowed", message="Trek is already cancelled.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    if trek.status == "upcoming":
        return render_template("message.html", title="Not Allowed", message="Upcoming Trek cannot be marked as cancelled.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    today = date.today()
    if today < trek.start_date:
        return render_template("message.html", title="Not Allowed", message="Trek cannot be marked as cancelled before start date.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
    if today > trek.end_date:
        return render_template("message.html", title="Not Allowed", message="Trek cannot be marked as cancelled after end date.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')    
    trek.status = "cancelled"
    all_active_bookings = Booking.query.filter(Booking.trek_id == trek_id, Booking.booking_status.in_(["booked", "pending"])).all()
    for booking in all_active_bookings:
        booking.booking_status = "cancelled"
        booking.payment_status = "refunded"
    db.session.commit()
    return render_template("message.html", title="Successful", message="Trek is cancelled successfully.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')


# To update the total slots
@staff_bp.route('/staff/treks/<trek_id>/slots', methods=["GET", "POST"])
@role_required('staff')
def staff_treks_slots(trek_id):
    if request.method == "GET":
        id = session.get('user_id')
        this_user = User.query.get(id)
        staff_assigned = StaffTrekAssignment.query.filter_by(user_id=id, trek_id=trek_id).first()
        if staff_assigned is None:
            return render_template("message.html", title="Not Allowed", message="You are not allowed to update this trek.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks Assigned')
        trek = Trek.query.get(trek_id)
        if trek is None:
            return render_template("message.html", title="Not Found", message="Trek not found.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
        if trek.status == "completed":
            return render_template("message.html", title="Not Allowed", message="Trek is already completed", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
        if trek.status == "cancelled":
            return render_template("message.html", title="Not Allowed", message="Trek is already cancelled.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
        if trek.status == "ongoing":
            return render_template("message.html", title="Not Allowed", message="Slots of ongoing trek cannot be updated.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
        today = date.today()
        if today > trek.end_date:
            return render_template("message.html", title="Not Allowed", message="Trek cannot be updated after end date.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')    
        return render_template("staff/staff_treks_slots.html", this_user=this_user, trek=trek)
    
    if request.method == "POST":
        id = session.get('user_id')
        this_user = User.query.get(id)
        staff_assigned = StaffTrekAssignment.query.filter_by(user_id=id, trek_id=trek_id).first()
        if staff_assigned is None:
            return render_template("message.html", title="Not Allowed", message="You are not allowed to update this trek.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks Assigned')
        trek = Trek.query.get(trek_id)
        if trek is None:
            return render_template("message.html", title="Not Found", message="Trek not found.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
        if trek.status == "completed":
            return render_template("message.html", title="Not Allowed", message="Trek is already completed", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
        if trek.status == "cancelled":
            return render_template("message.html", title="Not Allowed", message="Trek is already cancelled.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
        if trek.status == "ongoing":
            return render_template("message.html", title="Not Allowed", message="Slots of ongoing trek cannot be updated.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
        today = date.today()
        if today > trek.end_date:
            return render_template("message.html", title="Not Allowed", message="Trek cannot be updated after end date.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')    
        try:
            new_total_slots = int(request.form.get("new_total_slots"))
        except (TypeError, ValueError):
            return render_template("message.html", title="Incorrect Format", message="Slot value must be a valid number.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
        booked = trek.total_slots - trek.available_slots
        if new_total_slots < booked :
            return render_template("message.html", title="Not Allowed", message="This trek already has more bookings than the new requested total slots. Cancel the trek, if the trek cannot proceed with the current bookings.", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')
        trek.total_slots = new_total_slots
        trek.available_slots = new_total_slots - booked 
        db.session.commit()
        return render_template("message.html", title="Successful", message="Total Slots have been updated successfully", href=url_for('staff.staff_treks_page'), a_text='Back to Treks assigned')       
        