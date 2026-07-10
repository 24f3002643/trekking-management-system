from application.models import *
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from application.decorators import role_required
from application.controllers.trekker_bp import trekker_bp
from datetime import date

# To submit a request to book a trek available for booking
@trekker_bp.route('/trekker/treks/<trek_id>/book', methods=["GET", "POST"])
@role_required('trekker')
def trekker_treks_book(trek_id):
    if request.method == "GET":
        id = session.get('user_id')
        this_user = User.query.get(id)
        trek = Trek.query.get(trek_id)
        if trek is None:
            return render_template("message.html", title="Not Found", message="Trek with given id does not exists", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
        if trek.status != "upcoming" or trek.available_slots <= 0:
            return render_template("message.html", title="Not Allowed", message="This trek is not available for booking", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
        booking = Booking.query.filter(Booking.user_id == id, Booking.trek_id == trek.id, Booking.booking_status != "cancelled").first()
        if booking:
            if booking.booking_status == "booked":
                return render_template("message.html", title="Already booked", message="You have already booked this trek", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
            if booking.booking_status == "pending":
                return render_template("message.html", title="Booking under review", message="You have already requested for booking. Your request is awaiting Admin's Approval", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
        return render_template("trekker/trekker_treks_booking.html", this_user=this_user, trek=trek)

    if request.method == "POST":   
        id = session.get('user_id')
        this_user = User.query.get(id)
        trek = Trek.query.get(trek_id)
        if trek is None:
            return render_template("message.html", title="Not Found", message="Trek with given id does not exists", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
        if trek.status != "upcoming" or trek.available_slots <= 0:
            return render_template("message.html", title="Not Allowed", message="This trek is not available for booking", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
        booking = Booking.query.filter(Booking.user_id == id, Booking.trek_id == trek.id, Booking.booking_status != "cancelled").first()
        if booking:
            if booking.booking_status == "booked":
                return render_template("message.html", title="Already booked", message="You have already booked this trek", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
            if booking.booking_status == "pending":
                return render_template("message.html", title="Booking under review", message="You have already requested for booking. Your request is awaiting Admin's Approval", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
        debit_name = request.form.get("debit_name")
        debit_number = request.form.get("debit_number")
        debit_expiry = request.form.get("debit_expiry")
        debit_cvv = request.form.get("debit_cvv")
        if (not debit_name) or (not debit_number) or (not debit_expiry) or (not debit_cvv):
            return render_template("message.html", title="Insufficient Card Info", message="Card Details are not filled.", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')   
        booking = Booking(
            user_id = id,
            trek_id = trek.id,
            booking_status = "pending",
            payment_status = "paid"
        )
        trek.available_slots = trek.available_slots -1
        db.session.add(booking)
        db.session.add(trek)
        db.session.commit()
        return render_template("message.html", title="Successful", message="Your request for Booking has been created and sent to Admin for approval.", href=url_for('trekker.trekker_treks_page'), a_text='Go to Available Treks Page')

# To submit a request to cancel the booking for the trek
@trekker_bp.route('/trekker/bookings/<booking_id>/cancel', methods=["POST"])
@role_required('trekker')
def trekker_bookings_cancel(booking_id):
    id = session.get('user_id')
    this_user = User.query.get(id)
    booking = Booking.query.get(booking_id)
    if booking is None or booking.user_id != id:
        return render_template("message.html", title="Not Found ", message="This booking does not exists", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
    trek = Trek.query.get(booking.trek_id)
    if booking.booking_status in ["cancelled", "completed"]:
        return render_template("message.html", title="Error", message="This booking cannot be cancelled.", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
    if date.today() >= trek.start_date:
        return render_template("message.html", title="Error", message="This booking can no longer be cancelled.", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
    booking.booking_status = "cancelled"
    booking.payment_status = "refunded"
    trek.available_slots = trek.available_slots + 1
    db.session.add(booking)
    db.session.add(trek)
    db.session.commit()
    return render_template("message.html", title="Successful", message="Your booking is cancelled", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')



# To view all ongoing and upcoming bookings done by trekker himself. 
@trekker_bp.route('/trekker/bookings', methods=["GET"])
@role_required('trekker')
def trekker_bookings_page():
    id = session.get('user_id')
    this_user = User.query.get(id)

    all_pending_bookings = Booking.query.join(Trek, Booking.trek_id==Trek.id).filter(Booking.user_id==id ,Trek.status.in_(["upcoming", "ongoing"]), Booking.booking_status.in_(["pending"])).order_by(Trek.start_date.asc()).all()
    all_booked_bookings = Booking.query.join(Trek, Booking.trek_id==Trek.id).filter(Booking.user_id==id ,Trek.status.in_(["upcoming", "ongoing"]), Booking.booking_status.in_(["booked"])).order_by(Trek.start_date.asc()).all()
    return render_template("trekker/trekker_bookings_active.html", this_user=this_user, all_pending_bookings=all_pending_bookings, all_booked_bookings=all_booked_bookings)


# To view all bookings done by trekker himself. Supports filtering using query parameter
@trekker_bp.route('/trekker/bookings/history', methods=["GET"])
@role_required('trekker')
def trekker_bookings_history():
    id = session.get('user_id')
    this_user = User.query.get(id)
    status = request.args.get('status')
    difficulty = request.args.get('difficulty')
    location = request.args.get("location")
    trekname = request.args.get("trekname")
    query = Booking.query.join(Trek).filter(Booking.user_id == id)
    if status:
        query = query.filter(Trek.status == status)
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))
    if trekname:
        query = query.filter(Trek.trekname.ilike(f"%{trekname}%"))
    all_bookings = query.order_by(Trek.start_date.desc()).all()
    return render_template("trekker/trekker_bookings_history.html", this_user=this_user, all_bookings=all_bookings)


# To view the details of a particular booking done by him
@trekker_bp.route('/trekker/bookings/<booking_id>', methods=["GET"])
@role_required('trekker')
def trekker_bookings_view(booking_id):
    id = session.get('user_id')
    this_user = User.query.get(id)
    booking = Booking.query.get(booking_id)
    if booking is None or booking.user_id != id:
        return render_template("message.html", title="Not Found ", message="This booking does not exists", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
    trek = Trek.query.get(booking.trek_id)
    all_assigned_staff = StaffTrekAssignment.query.join(User, User.id==StaffTrekAssignment.user_id ).filter(StaffTrekAssignment.trek_id==trek.id).order_by(User.name.asc()).all()
    return render_template("trekker/trekker_bookings_details.html", this_user=this_user, booking=booking, trek=trek, all_assigned_staff=all_assigned_staff)