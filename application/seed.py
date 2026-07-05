"""
Seed script for local debugging.

Usage (in app.py, inside `with app.app_context():` block, after db.create_all()):

    from application.seed import seed_dummy_data, assign_dummy_staff_to_treks
    seed_dummy_data()
    assign_dummy_staff_to_treks()

Safe to run multiple times: it checks for existing dummy data (by email prefix)
before inserting, so it won't create duplicates on repeated app restarts.

Note: Trek.start_date / Trek.end_date are `date` objects (matching the
models.py Date() column type). Booking.booking_date stays a full `datetime`,
since a booking's exact timestamp is meaningful (ordering, audit trail).
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
    "Everest Base Camp", "Annapurna Circuit", "Valley of Flowers", "Hampta Pass",
    "Kedarkantha Trek", "Roopkund Trek", "Chadar Trek", "Har Ki Dun",
    "Triund Trek", "Kashmir Great Lakes", "Rupin Pass", "Goecha La",
    "Sandakphu Trek", "Brahmatal Trek", "Pin Parvati Pass"
]

LOCATIONS = [
    "Nepal", "Uttarakhand", "Himachal Pradesh", "Ladakh", "Sikkim",
    "Kashmir", "Meghalaya", "Arunachal Pradesh"
]

DIFFICULTIES = ["easy", "moderate", "hard"]
TREK_STATUSES = ["upcoming", "ongoing", "completed", "cancelled"]
BOOKING_STATUSES = ["initiated", "pending", "booked", "cancelled", "completed"]
PAYMENT_STATUSES = ["pending", "paid", "refunded"]

DUMMY_EMAIL_PREFIX = "dummy_"
DUMMY_PASSWORD = "password123"


def seed_dummy_data(
    num_trekkers=15,
    num_staff=15,
    num_treks=15,
    num_bookings=15,
):
    """Creates dummy trekkers, staff, treks and bookings."""

    existing = User.query.filter(User.email.like(f"{DUMMY_EMAIL_PREFIX}%")).first()
    if existing is not None:
        print("Dummy data already exists — skipping seed.")
        return

    password_hash = generate_password_hash(DUMMY_PASSWORD)

    # ---------------- Trekkers ----------------
    trekkers = []

    for i in range(1, num_trekkers + 1):
        base_name = TREKKER_NAMES[(i - 1) % len(TREKKER_NAMES)]

        trekker = User(
            name=f"{base_name} {i}",
            email=f"{DUMMY_EMAIL_PREFIX}trekker{i}@example.com",
            password_hash=password_hash,
            phone_number=f"90000{i:05d}",
            role="trekker",
            approval_status=None,
            is_blacklisted=random.choice([False, False, False, True])
        )

        trekkers.append(trekker)
        db.session.add(trekker)

    # ---------------- Staff ----------------
    staff_members = []

    for i in range(1, num_staff + 1):
        base_name = STAFF_NAMES[(i - 1) % len(STAFF_NAMES)]

        staff = User(
            name=f"{base_name} {i}",
            email=f"{DUMMY_EMAIL_PREFIX}staff{i}@example.com",
            password_hash=password_hash,
            phone_number=f"91000{i:05d}",
            role="staff",
            approval_status=random.choice(
                ["approved", "approved", "approved", "pending", "rejected"]
            ),
            is_blacklisted=random.choice([False, False, False, True])
        )

        staff_members.append(staff)
        db.session.add(staff)

    db.session.commit()

    # ---------------- Treks ----------------
    treks = []

    for i in range(1, num_treks + 1):
        base_name = TREK_NAMES[(i - 1) % len(TREK_NAMES)]

        total_slots = random.randint(10, 50)
        booked_slots = random.randint(0, total_slots)

        # Trek.start_date / end_date are `date` columns -> use date.today(),
        # not datetime.now(), to match the column type exactly.
        start = date.today() + timedelta(days=random.randint(-30, 60))
        end = start + timedelta(days=random.randint(3, 12))

        trek = Trek(
            trekname=f"{base_name} {i}",
            location=random.choice(LOCATIONS),
            difficulty=random.choice(DIFFICULTIES),
            total_slots=total_slots,
            available_slots=total_slots - booked_slots,
            status=random.choice(TREK_STATUSES),
            start_date=start,
            end_date=end,
            amount=round(random.uniform(5000, 25000), 2),
            additional_info=f"A wonderful trekking experience through {base_name}."
        )

        treks.append(trek)
        db.session.add(trek)

    db.session.commit()

    # ---------------- Bookings ----------------
    created = set()

    while len(created) < num_bookings:

        trekker = random.choice(trekkers)
        trek = random.choice(treks)

        # one booking per trek per trekker
        if (trekker.id, trek.id) in created:
            continue

        created.add((trekker.id, trek.id))

        booking = Booking(
            user_id=trekker.id,
            trek_id=trek.id,
            # Booking.booking_date stays a full datetime (exact timestamp matters
            # for ordering/audit), unlike Trek's plain date columns.
            booking_date=datetime.now() - timedelta(days=random.randint(0, 45)),
            booking_status=random.choice(BOOKING_STATUSES),
            payment_status=random.choice(PAYMENT_STATUSES),
            additional_info=None
        )

        db.session.add(booking)

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
    Respects the invariant that a staff member cannot be assigned
    to overlapping treks.
    """

    if StaffTrekAssignment.query.first():
        print("Staff assignments already exist — skipping.")
        return

    approved_staff = User.query.filter_by(
        role="staff",
        approval_status="approved",
        is_blacklisted=False,
    ).all()

    treks = Trek.query.order_by(Trek.start_date).all()

    # staff_id -> list[(start,end)]
    schedule = {staff.id: [] for staff in approved_staff}

    for trek in treks:

        available = []

        for staff in approved_staff:

            conflict = False

            for start, end in schedule[staff.id]:
                if trek.start_date <= end and trek.end_date >= start:
                    conflict = True
                    break

            if not conflict:
                available.append(staff)

        if not available:
            continue

        upper = min(max_staff_per_trek, len(available))
        lower = min(min_staff_per_trek, upper)

        count = random.randint(lower, upper)

        for staff in random.sample(available, count):

            db.session.add(
                StaffTrekAssignment(
                    user_id=staff.id,
                    trek_id=trek.id,
                )
            )

            schedule[staff.id].append(
                (trek.start_date, trek.end_date)
            )

    db.session.commit()

    print("Dummy staff assignments created.")