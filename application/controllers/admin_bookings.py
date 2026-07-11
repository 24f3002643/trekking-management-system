from application.models import *
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from application.decorators import role_required
from application.controllers.admin_bp import admin_bp


# ==================================== Admin-Booking Routes =============================

# To view all booking records
@admin_bp.route('/admin/bookings', methods=["GET"])
@role_required('admin')
def admin_bookings_page():
    id = session.get('user_id')
    this_user = User.query.get(id)
    status_order = db.case(
        (Booking.booking_status == 'pending', 1),
        (Booking.booking_status == 'booked', 2),
        (Booking.booking_status == 'completed', 3),
        (Booking.booking_status == 'cancelled', 4),
        else_=5
    )
    trek_id = request.args.get("trek_id", type=int)
    trekker_id = request.args.get("trekker_id", type=int)
    booking_date = request.args.get("booking_date")
    booking_status = request.args.get("booking_status")
    payment_status = request.args.get("payment_status")
    
    query = Booking.query
    if trek_id:
        query = query.filter(Booking.trek_id == trek_id)
    if trekker_id:
        query = query.filter(Booking.user_id == trekker_id)
    if booking_date:
        query = query.filter(db.func.date(Booking.booking_date) == booking_date)
    if booking_status:
        query = query.filter(Booking.booking_status == booking_status)
    if payment_status:
        query = query.filter(Booking.payment_status == payment_status)
    all_bookings = query.order_by(status_order, Booking.booking_date.asc()).all()
    return render_template('admin/admin_bookings.html', this_user=this_user, all_bookings=all_bookings)


# To view the details of a particular booking
@admin_bp.route('/admin/bookings/<booking_id>', methods=["GET"])
@role_required('admin')
def admin_bookings_view(booking_id):
    id = session.get('user_id')
    this_user = User.query.get(id)
    booking = Booking.query.get(booking_id)
    if booking is None:
        return render_template("message.html", title="Not Found", message="Booking with given ID not found.", href=url_for('admin.admin_bookings_page'), a_text='Back to Admin Bookings Page')
    trekker = booking.trekker
    trek = booking.trek 
    return render_template("admin/admin_bookings_details.html", this_user=this_user, booking=booking, trekker=trekker, trek=trek)


# To view all pending booking records
@admin_bp.route('/admin/bookings/pending', methods=["GET"])
@role_required('admin')
def admin_bookings_pending():
    id = session.get('user_id')
    this_user = User.query.get(id)
    trek_id = request.args.get("trek_id", type=int)
    trekker_id = request.args.get("trekker_id", type=int)
    booking_date = request.args.get("booking_date")
    
    query = Booking.query
    if trek_id:
        query = query.filter(Booking.trek_id == trek_id)
    if trekker_id:
        query = query.filter(Booking.user_id == trekker_id)
    if booking_date:
        query = query.filter(db.func.date(Booking.booking_date) == booking_date)
    all_pending_bookings = query.filter_by(booking_status="pending").order_by(Booking.booking_date.asc()).all()
    return render_template('admin/admin_bookings_pending.html', this_user=this_user, all_pending_bookings=all_pending_bookings)


# To submit the request to approve a pending booking
@admin_bp.route('/admin/bookings/<booking_id>/approve', methods=["POST"])
@role_required('admin')
def admin_bookings_approve(booking_id):
    booking = Booking.query.get(booking_id)
    if booking is None:
        return render_template("message.html", title="Not Found", message="Booking with given ID not found.", href=url_for('admin.admin_bookings_page'), a_text='Back to Admin Bookings Page')
    if booking.booking_status != "pending":
        return render_template("message.html", title="Payment Not Done", message="Payment is pending for this booking.", href=url_for('admin.admin_bookings_page'), a_text='Back to Admin Bookings Page')        
    booking.booking_status = "booked"
    db.session.commit()
    return render_template("message.html", title="Booking Approved", message="Booking has been successfully approved.", href=url_for('admin.admin_bookings_page'), a_text='Back to Admin Bookings Page')


# To submit the request to reject a pending booking
@admin_bp.route('/admin/bookings/<booking_id>/reject', methods=["POST"])
@role_required('admin')
def admin_bookings_reject(booking_id):
    booking = Booking.query.get(booking_id)
    if booking is None:
        return render_template("message.html", title="Not Found", message="Booking with given ID not found.", href=url_for('admin.admin_bookings_page'), a_text='Back to Admin Bookings Page')
    if booking.booking_status != "pending":
        return render_template("message.html", title="Payment Not Done", message="Payment is pending for this booking.", href=url_for('admin.admin_bookings_page'), a_text='Back to Admin Bookings Page')        
    booking.booking_status = "cancelled"
    booking.payment_status = "refunded"
    db.session.commit()
    return render_template("message.html", title="Booking Rejected", message="Booking has been successfully rejected .", href=url_for('admin.admin_bookings_page'), a_text='Back to Admin Bookings Page')

# To submit the request to cancel a booked booking
@admin_bp.route('/admin/bookings/<booking_id>/cancel', methods=["POST"])
@role_required('admin')
def admin_bookings_cancel(booking_id):
    booking = Booking.query.get(booking_id)
    if booking is None:
        return render_template("message.html", title="Not Found", message="Booking with given ID not found.", href=url_for('admin.admin_bookings_page'), a_text='Back to Admin Bookings Page')
    if booking.booking_status != "booked":
        return render_template("message.html", title="Not Booked", message="This booking is not approved by  the admin.", href=url_for('admin.admin_bookings_page'), a_text='Back to Admin Bookings Page')        
    booking.booking_status = "cancelled"
    booking.payment_status = "refunded"
    db.session.commit()
    return render_template("message.html", title="Booking Rejected", message="Booking has been successfully cancelled .", href=url_for('admin.admin_bookings_page'), a_text='Back to Admin Bookings Page')
