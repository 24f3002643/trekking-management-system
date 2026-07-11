from application.models import *
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from application.decorators import role_required
from application.controllers.admin_bp import admin_bp
from decimal import Decimal
from datetime import date


# ================= Admin-Treks Route ==============================

# To view all the existing treks
@admin_bp.route('/admin/treks', methods=["GET"])
@role_required('admin')
def admin_treks_page():
    id = session.get('user_id')
    this_user = User.query.filter_by(id=id).first()

    status_order = db.case(
        (Trek.status == "ongoing", 1),
        (Trek.status == "upcoming", 2),
        (Trek.status == "completed", 3),
        (Trek.status == "cancelled", 4),
        else_=5
    )

    difficulty = request.args.get('difficulty')
    location = request.args.get("location", "").strip()
    trekname = request.args.get("trekname", "").strip()
    status = request.args.get("status")


    query = Trek.query
    if status:
        query = query.filter(Trek.status == status)
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))
    if trekname:
        query = query.filter(Trek.trekname.ilike(f"%{trekname}%"))
    

    all_treks = query.order_by(status_order, Trek.start_date.asc(), Trek.trekname.asc()).all()
    return render_template("admin/admin_treks.html", this_user=this_user, all_treks=all_treks)



# To view the details of a particular trek
@admin_bp.route('/admin/treks/<trek_id>', methods=["GET"])
@role_required('admin')
def admin_treks_view(trek_id):
    id = session.get('user_id')
    this_user = User.query.filter_by(id=id).first()
    trek = Trek.query.filter_by(id=trek_id).first()
    if trek is None:
        return render_template("message.html", title="Not Found", message="Trek not found.", href=url_for('admin.admin_treks_page'), a_text='Back to Treks')
    status_order = db.case(
        (Booking.booking_status == 'pending', 1),
        (Booking.booking_status == 'booked', 2),
        (Booking.booking_status == 'completed', 3),
        (Booking.booking_status == 'cancelled', 4),
        else_=5
    )
    today = date.today()
    bookings = Booking.query.filter_by(trek_id=trek.id).order_by(status_order, Booking.booking_date.desc()).all()
    staff_assigned = User.query.join(StaffTrekAssignment, User.id ==StaffTrekAssignment.user_id).filter(StaffTrekAssignment.trek_id == trek.id).order_by(User.name.asc()).all()
    return render_template('admin/admin_treks_details.html', 
                        trek=trek, 
                        this_user=this_user, 
                        bookings=bookings, 
                        staff_assigned=staff_assigned,
                        today = today)




# To view and submit trek creation form for role="admin"
@admin_bp.route('/admin/treks/create', methods=["GET", "POST"])
@role_required('admin')
def admin_treks_create():
    if request.method == "GET":
        id = session.get('user_id')
        this_user = User.query.filter_by(id=id).first()
        return render_template('admin/admin_treks_create.html', this_user=this_user)
    
    if request.method == "POST":
        try :
            trekname = request.form.get("trekname")
            location = request.form.get("location")
            difficulty = request.form.get("difficulty")
            total_slots = int(request.form.get('total_slots'))
            start_date = date.fromisoformat(request.form.get('start_date'))
            end_date = date.fromisoformat(request.form.get('end_date'))
            amount = Decimal(request.form.get('amount'))
            additional_info = request.form.get('additional_info')
        except Exception:
            return render_template("message.html", title="Incorrect Format", message="Value submitted are not in correct format.", href=url_for('admin.admin_treks_create'), a_text='Back to Trek Creation Page')
        
        trek = Trek.query.filter_by(trekname=trekname).first()
        if trek is not None:
            return render_template("message.html", title="Incorrect Value", message="Trek Name already exist. Try again with some other Trek Name.", href=url_for('admin.admin_treks_create'), a_text='Back to Trek Creation Page')

        if start_date >= end_date:
            return render_template("message.html", title="Incorrect Date", message="Start date must be earlier than end date.", href=url_for('admin.admin_treks_create'), a_text='Back to Trek Creation Page')
        
        trek = Trek(
            trekname = trekname,
            location = location,
            total_slots = total_slots,
            available_slots = total_slots,
            difficulty = difficulty,
            start_date = start_date,
            end_date = end_date,
            amount = amount,
            status = 'upcoming',
            additional_info = additional_info
        )
        db.session.add(trek)
        db.session.commit()
        
        return render_template("message.html", title="Trek Creation Successful", message="Trek has been successfully created.", href=url_for('admin.admin_treks_page'), a_text='Back to Trek Page')





# To view and submit trek edit form for role="admin"
@admin_bp.route('/admin/treks/<trek_id>/edit', methods=["GET", "POST"])
@role_required('admin')
def admin_treks_edit(trek_id):
    if request.method == "GET":
        id = session.get('user_id')
        this_user = User.query.filter_by(id=id).first()
        trek = Trek.query.filter_by(id=trek_id).first()
        if trek is None:
            return render_template("message.html", title="Not Found", message="Trek not found.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
        if trek.status == "ongoing":
            return render_template("message.html", title="Not Allowed", message="Ongoing Trek cannot be edited.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
        if trek.status == "cancelled":
            return render_template("message.html", title="Not Allowed", message="Cancelled Trek cannot be edited.", href=url_for('admin.admin_treks_page'), a_text='Back to  Admin Trek Page')
        if trek.status == "completed":
            return render_template("message.html", title="Not Allowed", message="Completed Trek cannot be edited.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
        today = date.today()
        if today > trek.end_date:
            return render_template("message.html", title="Not Allowed", message="Trek cannot be edited after start date.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')    
        return render_template('admin/admin_treks_edit.html', this_user=this_user, trek=trek)
    
    if request.method == "POST":
        trek = Trek.query.filter_by(id=trek_id).first()
        if trek is None:
            return render_template("message.html", title="Not Found", message="Trek not found.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
        if trek.status == "ongoing":
            return render_template("message.html", title="Not Allowed", message="Ongoing Trek cannot be edited.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
        if trek.status == "cancelled":
            return render_template("message.html", title="Not Allowed", message="Cancelled Trek cannot be edited.", href=url_for('admin.admin_treks_page'), a_text='Back to  Admin Trek Page')
        if trek.status == "completed":
            return render_template("message.html", title="Not Allowed", message="Completed Trek cannot be edited.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
        today = date.today()
        if today > trek.end_date:
            return render_template("message.html", title="Not Allowed", message="Trek cannot be edited after end date.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')    
        try :
            trekname = request.form.get("trekname")
            location = request.form.get("location")
            difficulty = request.form.get("difficulty")
            total_slots = int(request.form.get('total_slots'))
            start_date = date.fromisoformat(request.form.get('start_date'))
            end_date = date.fromisoformat(request.form.get('end_date'))
            amount = Decimal(request.form.get('amount'))
            additional_info = request.form.get('additional_info')
        except Exception:
            return render_template("message.html", title="Incorrect Format", message="Value submitted are not in correct format.", href=url_for('admin.admin_treks_page'), a_text='Back to Treks Page')
        
        existing = Trek.query.filter(Trek.trekname == trekname, Trek.id != trek_id).first()
        if existing is not None:
            return render_template("message.html", title="Incorrect Value", message="Trek Name already exist. Try again with some other Trek Name.", href=url_for('admin.admin_treks_page'), a_text='Back to Treks Page')

        booked_slots = trek.total_slots - trek.available_slots
        new_available_slots = total_slots - booked_slots
        if new_available_slots < 0:
            return render_template("message.html", title="Incorrect Value", message="Cannot reduce total slots below the number already booked.", href=url_for('admin.admin_treks_page'), a_text='Back to Treks Page')

        trek.trekname = trekname
        trek.location = location
        trek.total_slots = total_slots
        trek.available_slots = new_available_slots
        trek.difficulty = difficulty
        trek.start_date = start_date
        trek.end_date = end_date
        trek.amount = amount
        trek.additional_info = additional_info
        db.session.commit()

        return render_template("message.html", title="Trek Edit Successful", message="Trek has been successfully Edited.", href=url_for('admin.admin_treks_page'), a_text='Back to Trek Page')



# To submit the request to delete the trek for role="admin"
@admin_bp.route('/admin/treks/<trek_id>/delete', methods=["POST"])
@role_required('admin')
def admin_treks_delete(trek_id):
    trek = Trek.query.filter_by(id=trek_id).first()
    if trek is None:
        return render_template("message.html", title="Not Exists", message="Trek with the given id does not exists.", href=url_for('admin.admin_treks_page'), a_text='Back to Trek Page')

    active_bookings = Booking.query.filter(
        Booking.trek_id == trek.id,
        Booking.booking_status.in_(['pending', 'booked'])
    ).first()

    if active_bookings is not None:
        return render_template("message.html", title="Deletion Failed", message="This trek has active bookings. Cancel those bookings before deleting this trek.", href=url_for('admin.admin_treks_page'), a_text='Back to Trek Page')

    StaffTrekAssignment.query.filter_by(trek_id=trek.id).delete()
    Booking.query.filter_by(trek_id=trek.id).delete()
    db.session.delete(trek)
    db.session.commit()

    return render_template("message.html", title="Trek Deleted", message="Trek has been successfully deleted.", href=url_for('admin.admin_treks_page'), a_text='Back to Trek Page')

# To change the status of trek to 'ongoing'
@admin_bp.route('/admin/treks/<trek_id>/ongoing', methods=["POST"])
@role_required('admin')
def admin_treks_ongoing(trek_id):
    id = session.get('user_id')
    this_user = User.query.get(id)
    trek = Trek.query.get(trek_id)
    if trek is None:
        return render_template("message.html", title="Not Found", message="Trek not found.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
    if trek.status == "ongoing":
        return render_template("message.html", title="Not Allowed", message="Trek is already 'ongoing'", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
    if trek.status == "cancelled":
        return render_template("message.html", title="Not Allowed", message="Cancelled Trek cannot be marked as ongoing.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
    if trek.status == "completed":
        return render_template("message.html", title="Not Allowed", message="Completed Trek cannot be marked as ongoing.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
    today = date.today()
    if today < trek.start_date:
        return render_template("message.html", title="Not Allowed", message="Trek cannot start before the start date.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
    trek.status = "ongoing"
    db.session.commit()
    return render_template("message.html", title="Successful", message="Trek have started successfully.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')


# To change the status of trek to 'completed'
@admin_bp.route('/admin/treks/<trek_id>/completed', methods=["POST"])
@role_required('admin')
def admin_treks_completed(trek_id):
    id = session.get('user_id')
    this_user = User.query.get(id)
    trek = Trek.query.get(trek_id)
    if trek is None:
        return render_template("message.html", title="Not Found", message="Trek not found.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
    if trek.status == "upcoming":
        return render_template("message.html", title="Not Allowed", message="Upcoming trek cannot be marked as completed", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
    if trek.status == "cancelled":
        return render_template("message.html", title="Not Allowed", message="Cancelled Trek cannot be marked as completed.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
    if trek.status == "completed":
        return render_template("message.html", title="Not Allowed", message="Completed Trek cannot be marked as completed.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
    today = date.today()
    if today < trek.start_date:
        return render_template("message.html", title="Not Allowed", message="Trek cannot be marked as complete before the start date.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
    trek.status = "completed"
    all_active_bookings = Booking.query.filter(Booking.trek_id == trek_id, Booking.booking_status.in_(["booked", "pending"])).all()
    for booking in all_active_bookings:
        if booking.booking_status == "booked":
            booking.booking_status = "completed"
        if booking.booking_status == "pending":
            booking.booking_status = "cancelled"
            booking.payment_status = "refunded"
    db.session.commit()
    return render_template("message.html", title="Successful", message="Trek is completed successfully.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')


# To change the status of trek to 'cancelled'
@admin_bp.route('/admin/treks/<trek_id>/cancelled', methods=["POST"])
@role_required('admin')
def admin_treks_cancelled(trek_id):
    id = session.get('user_id')
    this_user = User.query.get(id)
    trek = Trek.query.get(trek_id)
    if trek is None:
        return render_template("message.html", title="Not Found", message="Trek not found.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
    if trek.status == "cancelled":
        return render_template("message.html", title="Not Allowed", message="Cancelled Trek cannot be marked as cancelled.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
    if trek.status == "completed":
        return render_template("message.html", title="Not Allowed", message="Completed Trek cannot be marked as cancelled.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
    today = date.today()
    if today > trek.end_date:
        return render_template("message.html", title="Not Allowed", message="Trek cannot be marked as cancelled after end date.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')    
    trek.status = "cancelled"
    all_active_bookings = Booking.query.filter(Booking.trek_id == trek_id, Booking.booking_status.in_(["booked", "pending"])).all()
    for booking in all_active_bookings:
        booking.booking_status = "cancelled"
        booking.payment_status = "refunded"
    db.session.commit()
    return render_template("message.html", title="Successful", message="Trek is cancelled successfully.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')
 

