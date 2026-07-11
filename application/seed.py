"""
Seed script for local debugging.

Usage (in app.py, inside `with app.app_context():` block, after db.create_all()):

    from application.seed import seed_dummy_data, assign_dummy_staff_to_treks
    seed_dummy_data()
    assign_dummy_staff_to_treks()
"""

import random
from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash

from application.database import db
from application.models import *


TREKKER_NAMES = [
    "Aditi Sharma", "Rohan Mehta", "Sneha Iyer", "Karan Verma", "Priya Nair",
    "Arjun Reddy", "Neha Kapoor", "Vikram Singh", "Ananya Rao", "Rahul Gupta",
    "Ishita Joshi", "Manish Chandra", "Divya Menon", "Siddharth Rao", "Pooja Malhotra"
]

STAFF_NAMES = [
    "Amit Kumar", "Ravi Shankar", "Sunita Devi", "Manoj Tiwari", "Kavita Bhatt",
    "Deepak Yadav", "Anjali Saxena", "Suresh Pillai", "Meera Krishnan", "Rajesh Nair",
    "Vinay Kumar", "Shalini Desai", "Naveen Reddy", "Geeta Sharma", "Ashok Pandey"
]

TREK_NAMES = [
    "Everest Base Camp",
    "Annapurna Circuit",
    "Valley of Flowers",
    "Hampta Pass",
    "Kedarkantha Trek",
    "Roopkund Trek",
    "Chadar Trek",
    "Har Ki Dun",
    "Triund Trek",
    "Kashmir Great Lakes",
    "Rupin Pass",
    "Goecha La",
    "Sandakphu Trek",
    "Brahmatal Trek",
    "Pin Parvati Pass"
]

LOCATIONS = [
    "Nepal",
    "Uttarakhand",
    "Himachal Pradesh",
    "Ladakh",
    "Sikkim",
    "Kashmir",
    "Meghalaya",
    "Arunachal Pradesh"
]

DIFFICULTIES = [
    "easy",
    "moderate",
    "hard"
]

DUMMY_EMAIL_PREFIX = "dummy_"
DUMMY_PASSWORD = "password123"


def seed_dummy_data(
    num_trekkers=15,
    num_staff=15,
    num_treks=15,
    num_bookings=15,
):

    existing = User.query.filter(
        User.email.like(f"{DUMMY_EMAIL_PREFIX}%")
    ).first()

    if existing:
        print("Dummy data already exists — skipping.")
        return

    password_hash = generate_password_hash(DUMMY_PASSWORD)

    # ---------------- Trekkers ----------------

    trekkers = []

    for i in range(1, num_trekkers + 1):

        trekker = User(
            name=f"{TREKKER_NAMES[(i-1)%len(TREKKER_NAMES)]} {i}",
            email=f"{DUMMY_EMAIL_PREFIX}trekker{i}@example.com",
            password_hash=password_hash,
            phone_number=f"90000{i:05d}",
            role="trekker",
            approval_status=None,
            is_blacklisted=random.choice(
                [False, False, False, True]
            )
        )

        trekkers.append(trekker)
        db.session.add(trekker)

    # ---------------- Staff ----------------

    staff_members = []

    for i in range(1, num_staff + 1):

        staff = User(
            name=f"{STAFF_NAMES[(i-1)%len(STAFF_NAMES)]} {i}",
            email=f"{DUMMY_EMAIL_PREFIX}staff{i}@example.com",
            password_hash=password_hash,
            phone_number=f"91000{i:05d}",
            role="staff",
            approval_status=random.choice(
                ["approved", "approved", "approved", "pending", "rejected"]
            ),
            is_blacklisted=random.choice(
                [False, False, False, True]
            )
        )

        staff_members.append(staff)
        db.session.add(staff)

    db.session.commit()

    # ---------------- Treks ----------------

    treks = []

    today = date.today()

    for i in range(1, num_treks + 1):

        start = today + timedelta(
            days=random.randint(-30, 60)
        )

        end = start + timedelta(
            days=random.randint(3, 12)
        )

        if end < today:
            trek_status = "completed"

        elif start <= today <= end:
            trek_status = "ongoing"

        else:
            trek_status = "upcoming"

        total_slots = random.randint(10, 50)

        trek = Trek(
            trekname=f"{TREK_NAMES[(i-1)%len(TREK_NAMES)]} {i}",
            location=random.choice(LOCATIONS),
            difficulty=random.choice(DIFFICULTIES),
            total_slots=total_slots,
            available_slots=total_slots,
            status=trek_status,
            start_date=start,
            end_date=end,
            amount=round(random.uniform(5000, 25000), 2),
            additional_info=f"A wonderful trekking experience through {TREK_NAMES[(i-1)%len(TREK_NAMES)]}."
        )

        treks.append(trek)
        db.session.add(trek)

    db.session.commit()

    # ---------------- Bookings ----------------

    created = set()

    while len(created) < num_bookings:

        trekker = random.choice(trekkers)
        trek = random.choice(treks)

        # One booking per trek per trekker
        if (trekker.id, trek.id) in created:
            continue

        created.add((trekker.id, trek.id))

        # Booking status depends on trek status
        if trek.status == "completed":
            booking_status = random.choice(
                ["completed", "cancelled"]
            )

        elif trek.status in ["upcoming", "ongoing"]:
            booking_status = random.choice(
                ["pending", "booked", "cancelled"]
            )

        else:
            booking_status = "cancelled"

        if booking_status == "cancelled":
            payment_status = "refunded"
        else:
            payment_status = "paid"

        booking = Booking(
            user_id=trekker.id,
            trek_id=trek.id,
            booking_date=datetime.now() - timedelta(
                days=random.randint(0, 45)
            ),
            booking_status=booking_status,
            payment_status=payment_status,
            additional_info=None
        )

        db.session.add(booking)

    db.session.commit()

    # ---------------- Update Available Slots ----------------

    for trek in treks:

        active_bookings = Booking.query.filter(
            Booking.trek_id == trek.id,
            Booking.booking_status.in_(
                ["pending", "booked"]
            )
        ).count()

        trek.available_slots = max(
            0,
            trek.total_slots - active_bookings
        )

    db.session.commit()

    print(
        f"Seeded {num_trekkers} trekkers, "
        f"{num_staff} staff, "
        f"{num_treks} treks and "
        f"{num_bookings} bookings."
    )

def assign_dummy_staff_to_treks(
    min_staff_per_trek=5,
    max_staff_per_trek=8,
):
    """
    Assign approved staff to treks.

    A staff member cannot be assigned to overlapping treks.
    """

    if StaffTrekAssignment.query.first():
        print("Staff assignments already exist — skipping.")
        return

    approved_staff = User.query.filter_by(
        role="staff",
        approval_status="approved",
        is_blacklisted=False,
    ).all()

    treks = Trek.query.order_by(
        Trek.start_date.asc()
    ).all()

    # staff_id -> list of (start_date, end_date)
    schedule = {
        staff.id: []
        for staff in approved_staff
    }

    for trek in treks:

        available_staff = []

        for staff in approved_staff:

            overlap = False

            for start, end in schedule[staff.id]:

                if trek.start_date <= end and trek.end_date >= start:
                    overlap = True
                    break

            if not overlap:
                available_staff.append(staff)

        if not available_staff:
            continue

        upper = min(
            max_staff_per_trek,
            len(available_staff)
        )

        lower = min(
            min_staff_per_trek,
            upper
        )

        count = random.randint(
            lower,
            upper
        )

        selected_staff = random.sample(
            available_staff,
            count
        )

        for staff in selected_staff:

            assignment = StaffTrekAssignment(
                user_id=staff.id,
                trek_id=trek.id,
            )

            db.session.add(assignment)

            schedule[staff.id].append(
                (
                    trek.start_date,
                    trek.end_date
                )
            )

    db.session.commit()

    print("Dummy staff assignments created.")