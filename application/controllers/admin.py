from application.models import *
from application.database import db
from flask import Blueprint, Flask, render_template, url_for, redirect, request, session
from application.decorators import role_required
from application.controllers.admin_bp import admin_bp
from datetime import date, timedelta
from application.charts import *


@admin_bp.route('/admin', methods=["GET"])
@role_required('admin')
def admin_dashboard():
    id = session.get('user_id')
    this_user = User.query.filter_by(id=id).first()
    status_order = db.case(
        (Booking.booking_status == 'pending', 1),
        (Booking.booking_status == 'booked', 2),
        (Booking.booking_status == 'completed', 3),
        (Booking.booking_status == 'cancelled', 4),
        else_=5
    )
    recent_bookings = Booking.query.order_by(status_order, Booking.booking_date.asc()).all()
    #recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(10).all()
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




# =================================== Admin-Staff-Trek Routes ==============================

# To view and update the staff (assign or unassign) to a trek
@admin_bp.route('/admin/treks/<trek_id>/manage', methods=["GET", "POST"])
@role_required('admin')
def admin_treks_manage_staff(trek_id):
    id = session.get('user_id')
    this_user = User.query.get(id)

    trek = Trek.query.get(trek_id)
    if trek is None:
        return render_template("message.html", title="Not Found", message="Trek not found.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')

    # Assignment is only allowed while the trek is still 'upcoming'.
    if trek.status != "upcoming":
        return render_template("message.html", title="Not Allowed", message="Staff can only be assigned to a trek while it is 'upcoming'.", href=url_for('admin.admin_treks_page'), a_text='Back to Admin Trek Page')

    if request.method == "GET":
        already_assigned_ids = {a.user_id for a in trek.assignments}

        all_staff = User.query.filter(
            User.role == "staff",
            User.approval_status == "approved",
            User.is_blacklisted == False
        ).order_by(User.name.asc()).all()

        staff_rows = []
        for staff in all_staff:
            if staff.id in already_assigned_ids:
                staff_rows.append({"staff": staff, "state": "assigned"})
                continue

            has_conflict = False
            for assignment in staff.assignments:
                other_trek = assignment.trek
                if other_trek.id == trek.id:
                    continue
                if trek.start_date <= other_trek.end_date and trek.end_date >= other_trek.start_date:
                    has_conflict = True
                    break

            if has_conflict:
                staff_rows.append({"staff": staff, "state": "unavailable"})
            else:
                staff_rows.append({"staff": staff, "state": "available"})

        return render_template("admin/admin_treks_manage_staff.html", this_user=this_user, trek=trek, staff_rows=staff_rows)

    if request.method == "POST":
        # Re-fetch "already assigned" fresh, so we validate against the CURRENT state.
        # This is to ensure server side safety
        already_assigned_ids = {a.user_id for a in trek.assignments}

        try:
            submitted_ids = set(int(sid) for sid in request.form.getlist("assigned_staff_ids"))
        except ValueError:
            return render_template("message.html", title="Incorrect Format", message="Invalid staff selection submitted.", href=url_for('admin.admin_treks_manage_staff', trek_id=trek.id), a_text='Back to Trek Manage Staff Page')

        to_add = submitted_ids - already_assigned_ids
        to_remove = already_assigned_ids - submitted_ids

        # Validate every staff id being newly added: must exist, must be
        # role=='staff', approved, not blacklisted, and must not have a
        # date-overlapping assignment elsewhere. If ANY of these fail, the
        # entire request is rejected outright. 
        for staff_id in to_add:
            staff = User.query.get(staff_id)
            if staff is None or staff.role != "staff":
                return render_template("message.html", title="Invalid Staff", message=f"Staff with id {staff_id} does not exist.", href=url_for('admin.admin_treks_manage_staff', trek_id=trek.id), a_text='Back to Trek Manage Staff Page')
            if staff.approval_status != "approved" or staff.is_blacklisted:
                return render_template("message.html", title="Invalid Staff", message=f"{staff.name} is not an approved, active staff member.", href=url_for('admin.admin_treks_manage_staff', trek_id=trek.id), a_text='Back to Trek Manage Staff Page')

            for assignment in staff.assignments:
                other_trek = assignment.trek
                if other_trek.id == trek.id:
                    continue
                if trek.start_date <= other_trek.end_date and trek.end_date >= other_trek.start_date:
                    return render_template("message.html", title="Scheduling Conflict", message=f"{staff.name} is already assigned to a trek with overlapping dates.", href=url_for('admin.admin_treks_manage_staff', trek_id=trek.id), a_text='Back to Assign Staff Page')

        # Only reached if every staff_id in to_add passed validation above —
        # apply all additions and removals together.
        for staff_id in to_add:
            db.session.add(StaffTrekAssignment(user_id=staff_id, trek_id=trek.id))

        for staff_id in to_remove:
            StaffTrekAssignment.query.filter_by(user_id=staff_id, trek_id=trek.id).delete()

        db.session.commit()
        return render_template("message.html", title="Successful", message="Staff assignments have been updated successfully.", href=url_for('admin.admin_treks_view', trek_id=trek.id), a_text='Back to Admin Trek Details Page')

# ==================================== Admin-Search Routes ==========================

#To search treks, staffs or trekkers by name or ID
@admin_bp.route('/admin/search', methods=["GET"])
@role_required('admin')
def admin_search():
    id = session.get('user_id')
    this_user = User.query.filter_by(id=id).first()
    entity_id = request.args.get("id", type=int)
    name = request.args.get("name", "").strip()
    entity = request.args.get("entity")
    all_entities = None
    

    if entity == "trekker":
        query = User.query.filter_by(role="trekker")
        if entity_id:
            query = query.filter(User.id == entity_id)
        if name:
            query = query.filter(User.name.ilike(f"%{name}%"))
        all_entities = query.order_by(User.name.asc()).all()

    if entity == "staff":
        query = User.query.filter_by(role="staff")
        if entity_id:
            query = query.filter(User.id == entity_id)
        if name:
            query = query.filter(User.name.ilike(f"%{name}%"))
        status_order = db.case(
            (User.approval_status == "pending", 1),
            (User.approval_status == "approved", 2),
            (User.approval_status == "rejected", 3),
            else_=4
        )
        all_entities = query.order_by(status_order, User.name.asc()).all()

    if entity == "trek":
        query = Trek.query
        status_order = db.case(
            (Trek.status == "ongoing", 1),
            (Trek.status == "upcoming", 2),
            (Trek.status == "completed", 3),
            (Trek.status == "cancelled", 4),
            else_=5
        )
        if entity_id:
            query = query.filter(Trek.id == entity_id)
        if name:
            query = query.filter(Trek.trekname.ilike(f"%{name}%"))
        all_entities = query.order_by(status_order, Trek.start_date.asc(), Trek.trekname.asc()).all()

    return render_template('admin/admin_search.html', this_user=this_user, entity=entity, all_entities=all_entities)




# ==================================== Admin-Search Routes ==========================

#To view all the summary by admin
@admin_bp.route('/admin/summary', methods=["GET"])
@role_required('admin')
def admin_summary():
    id = session.get('user_id')
    this_user = User.query.get(id)

    total_treks = Trek.query.count()
    total_staff = User.query.filter_by(role='staff').count()
    total_trekkers = User.query.filter_by(role='trekker').count()
    total_bookings = Booking.query.count()

    booking_counts = db.session.query(
        Trek.id, Trek.trekname, db.func.count(Booking.id).label("booking_count")
    ).join(Booking, Booking.trek_id == Trek.id
    ).group_by(Trek.id
    ).order_by(db.desc("booking_count")
    ).limit(10).all()

    top_treks = [
        {"trekname": trekname, "count": count}
        for trek_id, trekname, count in booking_counts
    ]

    pending_count = Booking.query.filter_by(booking_status="pending").count()
    booked_count = Booking.query.filter_by(booking_status="booked").count()

    today = date.today()
    last_7_days = []
    for i in range(6, -1, -1):  # oldest to newest, left-to-right on the chart
        day = today - timedelta(days=i)
        count = Booking.query.filter(db.func.date(Booking.booking_date) == day).count()
        last_7_days.append({"date": day, "count": count})

    trekker_blacklisted = User.query.filter_by(role="trekker", is_blacklisted=True).count()
    trekker_active = total_trekkers - trekker_blacklisted

    staff_blacklisted = User.query.filter_by(role="staff", is_blacklisted=True).count()
    staff_active = total_staff - staff_blacklisted

    staff_approved = User.query.filter_by(role="staff", approval_status="approved").count()
    staff_pending = User.query.filter_by(role="staff", approval_status="pending").count()
    staff_rejected = User.query.filter_by(role="staff", approval_status="rejected").count()

    top_treks_chart = make_top_treks_chart(top_treks)
    pending_booked_chart = make_pending_booked_chart(pending_count, booked_count)
    staff_approval_chart = make_staff_approval_chart(staff_approved, staff_pending, staff_rejected)
    last_7_days_chart = make_last_7_days_chart(last_7_days)
    trekker_blacklist_chart = make_trekker_blacklist_chart(trekker_active, trekker_blacklisted)
    staff_blacklist_chart = make_staff_blacklist_chart(staff_active, staff_blacklisted)

    return render_template(
        "admin/admin_summary.html",
        this_user=this_user,
        total_treks=total_treks,
        total_staff=total_staff,
        total_trekkers=total_trekkers,
        total_bookings=total_bookings,
        top_treks_chart=top_treks_chart,
        pending_booked_chart=pending_booked_chart,
        staff_approval_chart=staff_approval_chart,
        last_7_days_chart=last_7_days_chart,
        trekker_blacklist_chart=trekker_blacklist_chart,
        staff_blacklist_chart=staff_blacklist_chart,
    )