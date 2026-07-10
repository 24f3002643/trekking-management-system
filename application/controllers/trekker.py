from application.models import *
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from application.decorators import role_required
from application.controllers.trekker_bp import trekker_bp

# ======================================== Trekker Routes =============================


# To access the dashboard by trekker
@trekker_bp.route('/trekker', methods=["GET"])
@role_required('trekker')
def trekker_dashboard():
    id = session.get('user_id')
    this_user = User.query.get(id)
    booked_trek_ids = db.session.query(Booking.trek_id).filter(Booking.user_id == id, Booking.booking_status.in_(["booked", "pending"]))
    all_upcoming_treks = Trek.query.filter(Trek.status=="upcoming", Trek.available_slots > 0, Trek.id.notin_(booked_trek_ids)).order_by(Trek.start_date.asc(), Trek.trekname.asc()).all()
    trekker_bookings = Booking.query.join(Trek).filter(Booking.user_id==id, Booking.booking_status.in_(["booked", "pending"])).order_by(Trek.start_date.asc()).all()
    return render_template("trekker/trekker_dashboard.html", this_user=this_user, all_upcoming_treks=all_upcoming_treks, trekker_bookings=trekker_bookings)



# To view all the treks available for booking. Supports filtering using query parameters.
@trekker_bp.route('/trekker/treks', methods=["GET"])
@role_required('trekker')
def trekker_treks_page():
    id = session.get('user_id')
    this_user = User.query.get(id)
    difficulty = request.args.get('difficulty')
    location = request.args.get("location")
    trekname = request.args.get("trekname")

    booked_trek_ids = db.session.query(Booking.trek_id).filter(Booking.user_id == id, Booking.booking_status.in_(["booked", "pending"]))
    query = Trek.query.filter(Trek.status=="upcoming", Trek.available_slots > 0, Trek.id.notin_(booked_trek_ids))

    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))
    if trekname:
        query = query.filter(Trek.trekname.ilike(f"%{trekname}%"))
    
    all_upcoming_treks = query.order_by(Trek.start_date.asc(), Trek.trekname.asc()).all()
    return render_template("trekker/trekker_treks.html", this_user=this_user, all_upcoming_treks=all_upcoming_treks)

    

# To view the details of a particular trek  available for booking
@trekker_bp.route('/trekker/treks/<trek_id>', methods=["GET"])
@role_required('trekker')
def trekker_treks_view(trek_id):
    id = session.get('user_id')
    this_user = User.query.get(id)
    trek = Trek.query.get(trek_id)
    if trek is None:
        return render_template("message.html", title="Not Found", message="This trek does not exists", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
    if trek.status != "upcoming" or trek.available_slots<=0 :
        return render_template("message.html", title="Not Allowed", message="This trek is not available for booking", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
    booking = Booking.query.filter(Booking.user_id == id, Booking.trek_id == trek.id, Booking.booking_status != "cancelled").first()
    if booking:
        if booking.booking_status == "booked":
            return render_template("message.html", title="Already booked", message="You have already booked this trek", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
        if booking.booking_status == "pending":
            return render_template("message.html", title="Booking under review", message="You have already requested for booking. Your request is awaiting Admin's Approval", href=url_for('trekker.trekker_treks_page'), a_text='Back to Available Treks Page')
    all_assigned_staff = StaffTrekAssignment.query.filter_by(trek_id=trek_id).all()
    return render_template("trekker/trekker_treks_details.html", this_user=this_user, trek=trek, all_assigned_staff=all_assigned_staff)




