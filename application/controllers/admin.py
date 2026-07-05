from application.models import *
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from application.decorators import role_required
from application.controllers.admin_bp import admin_bp


@admin_bp.route('/admin', methods=["GET"])
@role_required('admin')
def admin_dashboard():
    id = session.get('user_id')
    this_user = User.query.filter_by(id=id).first()
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(10).all()
    total_treks = Trek.query.count()
    total_staff = User.query.filter_by(role='staff').count()
    total_trekkers = User.query.filter_by(role='trekker').count()
    total_bookings = Booking.query.count()
    return render_template('admin/admin_dashboard.html', 
                           this_user=this_user, 
                           recent_bookings=recent_bookings, 
                           total_treks=total_treks, 
                           total_staff=total_staff, 
                           total_trekkers=total_trekkers, 
                           total_bookings=total_bookings)



# ============================ Admin-Staff Routes ===========================

# To view all the existing staffs
@admin_bp.route('/admin/staff', methods=["GET"])
def admin_staff_page():
    pass 

# To view the details of a particular staff.
@admin_bp.route('/admin/staff/<staff_id>', methods=["GET"])
def admin_staff_view(staff_id):
    pass

# To view all the staff with pending request for registration
@admin_bp.route('/admin/staff/pending', methods=["GET"])
def admin_staff_pending():
    pass 

# To submit the request to accept the staff 's registration
@admin_bp.route('/admin/staff/<staff_id>/approve', methods=["POST"])
def admin_staff_approve(staff_id):
    pass

# To submit the request to reject the staff 's registration
@admin_bp.route('/admin/staff/<staff_id>/reject', methods=["POST"])
def admin_staff_reject(staff_id):
    pass

# To submit the request tp blacklist the staff
@admin_bp.route('/admin/staff/<staff_id>/blacklist', methods=["POST"])
def admin_staff_blacklist(staff_id):
    pass 

# To submit the request tp unblacklist the staff
@admin_bp.route('/admin/staff/<staff_id>/unblacklist', methods=["POST"])
def admin_staff_unblacklist(staff_id):
    pass 

# ============================== Admin-Trekker Routes ==============================

# To view all the existing trekkers
@admin_bp.route('/admin/trekkers', methods=["GET"])
def admin_trekkers_page():
    pass 

# To view the details of a particular trekker
@admin_bp.route('/admin/trekkers/<trekker_id>', methods=["GET"])
def admin_trekkers_view(trekker_id):
    pass 

# To submit the request tp blacklist the trekker
@admin_bp.route('/admin/trekkers/<trekker_id>/blacklist', methods=["POST"])
def admin_trekkers_blacklist(trekker_id):
    pass 

# To submit the request tp unblacklist the trekker
@admin_bp.route('/admin/trekkers/<trekker_id>/unblacklist', methods=["POST"])
def admin_trekkers_unblacklist(trekker_id):
    pass 

# =================================== Admin-Staff-Trek Routes ==============================

# To view and update the staff (assign or unassign) to a trek
@admin_bp.route('/admin/treks/<trek_id>/assign', methods=["GET", "POST"])
def admin_treks_assign_staff(trek_id):
    pass 

# ==================================== Admin-Search Routes ==========================

#To search treks, staffs or trekkers by name or ID
@admin_bp.route('/admin/search', methods=["GET"])
def admin_search():
    pass 


# ==================================== Admin-Booking Routes =============================

# To view all booking records
@admin_bp.route('/admin/bookings', methods=["GET"])
def admin_bookings_page():
    pass 

# To view the details of a particular booking
@admin_bp.route('/admin/bookings/<booking_id>', methods=["GET"])
def admin_bookings_view(booking_id):
    pass

# To submit the request to approve a pending booking
@admin_bp.route('/admin/bookings/<booking_id>/approve', methods=["POST"])
def admin_bookings_approve(booking_id):
    pass 

# To submit the request to cancel a pending booking
@admin_bp.route('/admin/bookings/<booking_id>/cancel', methods=["POST"])
def admin_bookings_cancel(booking_id):
    pass

# ==================================== Admin-Search Routes ==========================

#To view all the summary by admin
@admin_bp.route('/admin/summary', methods=["GET"])
def admin_summary():
    pass 