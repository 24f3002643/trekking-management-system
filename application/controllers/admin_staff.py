from application.models import *
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from application.decorators import role_required
from application.controllers.admin_bp import admin_bp


# ============================ Admin-Staff Routes ===========================

# To view all the existing staffs
@admin_bp.route('/admin/staff', methods=["GET"])
@role_required('admin')
def admin_staff_page():
    id = session.get('user_id')
    this_user = User.query.filter_by(id=id).first()
    status_order = db.case(
        (User.approval_status == "pending", 1),
        (User.approval_status == "approved", 2),
        (User.approval_status == "rejected", 3),
        else_=4
    )
    all_staff = User.query.filter_by(role="staff").order_by(status_order, User.name.asc()).all()
    return render_template("admin/admin_staff.html", this_user=this_user, all_staff=all_staff)
    

# To view the details of a particular staff.
@admin_bp.route('/admin/staff/<staff_id>', methods=["GET"])
@role_required('admin')
def admin_staff_view(staff_id):
    id = session.get('user_id')
    this_user = User.query.filter_by(id=id).first()

    staff = User.query.filter_by(id=staff_id).first()
    if staff is None or staff.role != "staff":
        return render_template("message.html", title="No Staff Found", message="No staff with the given id exists.", href=url_for('admin.admin_staff_page'), a_text='Back to Admin Staff Page')

    status_order = db.case(
        (Trek.status == "ongoing", 1),
        (Trek.status == "upcoming", 2),
        (Trek.status == "completed", 3),
        (Trek.status == "cancelled", 4),
        else_=5
    )
    assignments = staff.assignments #list of StaffTrekAssignment objects
    trek_ids = [a.trek_id for a in assignments]  # get the trek_id from each row of StaffTrekAssignment object
    all_assigned_treks = Trek.query.filter(Trek.id.in_(trek_ids)).order_by(status_order, Trek.start_date.asc()).all() #fetches the actual treks assigned to this staff
    # all_treks = Trek.query.join(StaffTrekAssignment, Trek.id ==StaffTrekAssignment.trek_id).filter(StaffTrekAssignment.user_id == staff_id).order_by(status_order, Trek.start_date.asc()).all()
    return render_template("admin/admin_staff_details.html", this_user=this_user, staff=staff, all_assigned_treks=all_assigned_treks)



# To view all the staff with pending request for registration
@admin_bp.route('/admin/staff/pending', methods=["GET"])
@role_required('admin')
def admin_staff_pending():
    id = session.get('user_id')
    this_user = User.query.get(id)

    all_pending_staff = User.query.filter_by(role="staff", approval_status="pending").all()
    return render_template("admin/admin_staff_pending.html", this_user=this_user, all_pending_staff=all_pending_staff)



# To submit the request to accept the staff 's registration
@admin_bp.route('/admin/staff/<staff_id>/approve', methods=["POST"])
@role_required('admin')
def admin_staff_approve(staff_id):
    staff = User.query.get(staff_id)
    if staff is None or staff.role != "staff":
        return render_template("message.html", title="No Staff Found", message="No staff with the given id exists.", href=url_for('admin.admin_staff_pending'), a_text='Back to Admin Staff Pending Page')
    if staff.approval_status != "pending":
        return render_template("message.html", title="Error", message="The approval request for this staff is not pending.", href=url_for('admin.admin_staff_pending'), a_text='Back to Admin Staff Pending Page')
    staff.approval_status = "approved"
    db.session.commit()
    return render_template("message.html", title="Approved", message="The registration request of this staff has been approved successfully.", href=url_for('admin.admin_staff_pending'), a_text='Back to Admin Staff Pending Page')

# To submit the request to reject the staff 's registration
@admin_bp.route('/admin/staff/<staff_id>/reject', methods=["POST"])
@role_required('admin')
def admin_staff_reject(staff_id):
    staff = User.query.get(staff_id)
    if staff is None or staff.role != "staff":
        return render_template("message.html", title="No Staff Found", message="No staff with the given id exists.", href=url_for('admin.admin_staff_pending'), a_text='Back to Admin Staff Pending Page')
    if staff.approval_status != "pending":
        return render_template("message.html", title="Error", message="The approval request for this staff is not pending.", href=url_for('admin.admin_staff_pending'), a_text='Back to Admin Staff Pending Page')
    staff.approval_status = "rejected"
    db.session.commit()
    return render_template("message.html", title="Rejected", message="The registration request of this staff has been rejected successfully.", href=url_for('admin.admin_staff_pending'), a_text='Back to Admin Staff Pending Page')


# To submit the request tp blacklist the staff
@admin_bp.route('/admin/staff/<staff_id>/blacklist', methods=["POST"])
@role_required('admin')
def admin_staff_blacklist(staff_id):
    staff = User.query.get(staff_id)
    if staff is None or staff.role != "staff":
        return render_template("message.html", title="No Staff Found", message="No staff with the given id exists.", href=url_for('admin.admin_staff_page'), a_text='Back to Admin Staff Page')
    staff.is_blacklisted = True
    db.session.commit()
    return render_template("message.html", title="Blacklisted", message="The staff has been blacklisted successfully.", href=url_for('admin.admin_staff_page'), a_text='Back to Admin Staff Page')


# To submit the request tp unblacklist the staff
@admin_bp.route('/admin/staff/<staff_id>/unblacklist', methods=["POST"])
@role_required('admin')
def admin_staff_unblacklist(staff_id):
    staff = User.query.get(staff_id)
    if staff is None or staff.role != "staff":
        return render_template("message.html", title="No Staff Found", message="No staff with the given id exists.", href=url_for('admin.admin_staff_page'), a_text='Back to Admin Staff Page')
    staff.is_blacklisted = False
    db.session.commit()
    return render_template("message.html", title="Unblacklisted", message="The staff has been unblacklisted successfully.", href=url_for('admin.admin_staff_page'), a_text='Back to Admin Staff Page')
