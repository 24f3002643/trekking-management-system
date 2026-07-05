from application.models import *
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from application.decorators import role_required
from application.controllers.admin_bp import admin_bp
from decimal import Decimal
from datetime import date
from application.utilities import refresh_trek_status


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
    all_treks = Trek.query.order_by(status_order, Trek.start_date.asc()).all()
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
        (Booking.booking_status == 'initiated', 4),
        (Booking.booking_status == 'cancelled', 5),
        else_=6
    )
    bookings = Booking.query.filter_by(trek_id=trek.id).order_by(status_order, Booking.booking_date.desc()).all()
    staff_assigned = trek.assignments

    return render_template('admin/admin_treks_details.html', 
                        trek=trek, 
                        this_user=this_user, 
                        bookings=bookings, 
                        staff_assigned=staff_assigned)




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
        return render_template('admin/admin_treks_edit.html', this_user=this_user, trek=trek)
    
    if request.method == "POST":
        trek = Trek.query.filter_by(id=trek_id).first()
        if trek is None:
            return render_template("message.html", title="Not Exists", message="Trek with the given id does not exists.", href=url_for('admin.admin_treks_page'), a_text='Back to Trek Page')

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
        refresh_trek_status(trek)
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
        Booking.booking_status.in_(['initiated', 'pending', 'booked'])
    ).first()

    if active_bookings is not None:
        return render_template("message.html", title="Deletion Failed", message="This trek has active bookings. Cancel those bookings before deleting this trek.", href=url_for('admin.admin_treks_page'), a_text='Back to Trek Page')

    StaffTrekAssignment.query.filter_by(trek_id=trek.id).delete()
    Booking.query.filter_by(trek_id=trek.id).delete()
    db.session.delete(trek)
    db.session.commit()

    return render_template("message.html", title="Trek Deleted", message="Trek has been successfully deleted.", href=url_for('admin.admin_treks_page'), a_text='Back to Trek Page')

# =================================== Admin-Staff-Trek Routes ==============================

# To view and update the staff (assign or unassign) to a trek
@admin_bp.route('/admin/treks/<trek_id>/assign', methods=["GET", "POST"])
@role_required
def admin_treks_assign_staff(trek_id):
    pass 