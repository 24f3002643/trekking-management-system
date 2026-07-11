"""
Seed script for local debugging.

Usage (in app.py, inside `with app.app_context():` block, after db.create_all()):

    from application.seed import seed_dummy_data
    seed_dummy_data()

Notes
-----
- Trek status is NEVER derived from dates automatically (per invariants.md #6),
  so each trek's status below is set explicitly and its dates are chosen to be
  *consistent* with that status (e.g. an 'ongoing' trek has start_date in the
  past and end_date in the future), as if an admin/staff had manually
  transitioned it at the right time.
- Bookings are seeded to reflect a plausible history relative to each trek's
  current status (invariants.md, Booking section):
    * upcoming treks  -> pending / booked bookings (still paid, still active)
    * ongoing treks   -> booked bookings only (they were 'booked' before the
                         trek started; nothing has completed yet)
    * completed treks -> booked -> completed, and any leftover pending ->
                         cancelled + refunded (invariant Booking #9)
    * cancelled treks -> every pending/booked booking is cancelled + refunded
                         (invariant Booking #8); no active bookings remain
  available_slots is derived to stay consistent with active (pending/booked)
  bookings on each trek (invariant Trek #5: never negative).
- Staff assignments are only created for 'upcoming' treks (invariant Trek #8),
  using only approved, non-blacklisted staff (invariant StaffTrekAssignment
  #5), and a staff member is never assigned to two overlapping treks
  (invariant StaffTrekAssignment #3).
- All trekkers and staff use the same password: "password".
"""

from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash

from application.database import db
from application.models import *


PASSWORD = "password"

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
]

LOCATIONS = [
    "Nepal",
    "Uttarakhand",
    "Himachal Pradesh",
    "Ladakh",
    "Sikkim",
    "Kashmir",
    "Uttarakhand",
    "Himachal Pradesh",
    "Kashmir",
    "Ladakh",
]

DIFFICULTIES = [
    "moderate", "hard", "easy", "moderate", "easy",
    "hard", "moderate", "moderate", "easy", "hard",
]


def seed_dummy_data():

    existing = User.query.filter(User.email == "trekker1@example.com").first()
    if existing:
        print("Dummy data already exists — skipping.")
        return

    password_hash = generate_password_hash(PASSWORD)

    # ---------------- Trekkers (10 total, 3 blacklisted) ----------------
    # approval_status is NULL for trekkers (invariant: User #3)

    trekker_blacklist_flags = [
        True, True, True,  # trekker1, trekker2, trekker3 -> blacklisted
        False, False, False, False, False, False, False,
    ]

    for i in range(1, 11):
        trekker = User(
            name=f"Trekker {i}",
            email=f"trekker{i}@example.com",
            password_hash=password_hash,
            phone_number=f"90000{i:05d}",
            role="trekker",
            approval_status=None,
            is_blacklisted=trekker_blacklist_flags[i - 1],
        )
        db.session.add(trekker)

    # ---------------- Staff (10 total) ----------------
    # 2 blacklisted, 2 unapproved (pending), 1 rejected, rest approved & clean
    # approval_status is meaningful for staff (invariant: User #3)

    # staff1, staff2 -> blacklisted (approved, but blacklisted)
    # staff3, staff4 -> pending (unapproved)
    # staff5         -> rejected
    # staff6-10      -> approved, not blacklisted

    staff_config = {
        1: ("approved", True),
        2: ("approved", True),
        3: ("pending", False),
        4: ("pending", False),
        5: ("rejected", False),
        6: ("approved", False),
        7: ("approved", False),
        8: ("approved", False),
        9: ("approved", False),
        10: ("approved", False),
    }

    for i in range(1, 11):
        approval_status, is_blacklisted = staff_config[i]
        staff = User(
            name=f"Staff {i}",
            email=f"staff{i}@example.com",
            password_hash=password_hash,
            phone_number=f"91000{i:05d}",
            role="staff",
            approval_status=approval_status,
            is_blacklisted=is_blacklisted,
        )
        db.session.add(staff)

    db.session.commit()

    # ---------------- Treks (10 total, mixed statuses) ----------------
    # Dates are chosen to be consistent with the manually-set status,
    # per invariant Trek #6 (status is never auto-derived from dates).

    today = date.today()

    # (status, start_offset_days, end_offset_days)
    # upcoming  -> both dates in the future
    # ongoing   -> start in the past, end in the future
    # completed -> both dates in the past
    # cancelled -> mix of upcoming-cancelled (future dates) and
    #              ongoing-cancelled (start past, end future) cases,
    #              but never past-end-date (invariant Trek #6 last bullet)
    trek_plan = [
        ("upcoming",   10, 20),   # 1
        ("upcoming",   15, 25),   # 2
        ("upcoming",   30, 40),   # 3
        ("ongoing",    -3, 5),    # 4
        ("ongoing",    -5, 2),    # 5
        ("completed", -30, -20),  # 6
        ("completed", -15, -5),   # 7
        ("cancelled",  20, 30),   # 8  (was upcoming, admin cancelled)
        ("cancelled",  -2, 6),    # 9  (was ongoing, cancelled for ground emergency)
        ("upcoming",    7, 14),   # 10
    ]

    treks = []  # keep references (with real ids) for bookings/assignments below

    for i in range(1, 11):
        status, start_offset, end_offset = trek_plan[i - 1]
        start = today + timedelta(days=start_offset)
        end = today + timedelta(days=end_offset)

        total_slots = 10 + i  # 11..20, varied but simple

        trek = Trek(
            trekname=f"{TREK_NAMES[i - 1]}",
            location=LOCATIONS[i - 1],
            difficulty=DIFFICULTIES[i - 1],
            total_slots=total_slots,
            available_slots=total_slots,  # corrected below once bookings exist
            status=status,
            start_date=start,
            end_date=end,
            amount=round(5000 + i * 1500.0, 2),
            additional_info=f"A guided trekking experience through {TREK_NAMES[i - 1]}.",
        )
        db.session.add(trek)
        treks.append(trek)

    db.session.commit()  # flush so trek.id is populated

    # ---------------- Bookings ----------------
    # trekker4..trekker10 are clean (not blacklisted) and used for bookings.
    # trekker1-3 are blacklisted and deliberately given NO bookings, since a
    # blacklisted trekker cannot log in / book (invariant User #6).

    clean_trekkers = User.query.filter(
        User.role == "trekker",
        User.is_blacklisted == False,  # noqa: E712
    ).order_by(User.id.asc()).all()  # trekker4..trekker10 (7 trekkers)

    now = datetime.now()

    # trek index (1-based, matches trek_plan) -> list of (trekker_offset, booking_status)
    # trekker_offset indexes into clean_trekkers (0-based)
    booking_plan = {
        # upcoming treks: mix of pending (awaiting admin review) and booked
        1: [(0, "booked"), (1, "pending")],
        2: [(2, "booked")],
        3: [(3, "pending"), (4, "booked")],
        10: [(5, "pending")],

        # ongoing treks: only 'booked' (nothing pending -- once a trek is
        # underway, any earlier pending request has already been resolved
        # to booked or cancelled by the admin)
        4: [(6, "booked"), (0, "booked")],
        5: [(1, "booked")],

        # completed treks: booked -> completed, leftover pending -> cancelled+refunded
        # (invariant Booking #9)
        6: [(2, "completed"), (3, "completed"), (4, "cancelled")],
        7: [(5, "completed"), (6, "cancelled")],

        # cancelled treks: everything must be cancelled + refunded
        # (invariant Booking #8 -- these were booked/pending before the trek
        # itself got cancelled)
        8: [(0, "cancelled"), (1, "cancelled")],
        9: [(2, "cancelled")],
    }

    for trek_index, entries in booking_plan.items():
        trek = treks[trek_index - 1]

        for trekker_offset, booking_status in entries:
            trekker = clean_trekkers[trekker_offset % len(clean_trekkers)]

            payment_status = "refunded" if booking_status == "cancelled" else "paid"

            booking = Booking(
                user_id=trekker.id,
                trek_id=trek.id,
                booking_date=now - timedelta(days=3),
                booking_status=booking_status,
                payment_status=payment_status,
            )
            db.session.add(booking)

    db.session.commit()

    # ---------------- Recompute available_slots ----------------
    # Only 'pending' and 'booked' bookings occupy a slot (invariant Trek #5,
    # Booking #3). 'completed' and 'cancelled' bookings free the slot back up.

    for trek in treks:
        active_bookings = Booking.query.filter(
            Booking.trek_id == trek.id,
            Booking.booking_status.in_(["pending", "booked"]),
        ).count()
        trek.available_slots = max(0, trek.total_slots - active_bookings)

    db.session.commit()

    # ---------------- Staff assignments ----------------
    # Only for 'upcoming' treks (invariant Trek #8), only approved &
    # non-blacklisted staff (invariant StaffTrekAssignment #5), and never two
    # overlapping treks for the same staff member (invariant #3).
    # Eligible staff here: staff6..staff10 (approved, not blacklisted).

    eligible_staff = User.query.filter(
        User.role == "staff",
        User.approval_status == "approved",
        User.is_blacklisted == False,  # noqa: E712
    ).order_by(User.id.asc()).all()

    upcoming_treks = [t for t in treks if t.status == "upcoming"]
    upcoming_treks.sort(key=lambda t: t.start_date)

    # staff.id -> list of (start_date, end_date) already assigned
    schedule = {staff.id: [] for staff in eligible_staff}

    def overlaps(a_start, a_end, b_start, b_end):
        return a_start <= b_end and a_end >= b_start

    # Deliberate rotation: try to assign 2 staff per upcoming trek, skipping
    # anyone whose existing assignment would overlap this trek's dates.
    for idx, trek in enumerate(upcoming_treks):
        assigned_count = 0
        for offset in range(len(eligible_staff)):
            staff = eligible_staff[(idx + offset) % len(eligible_staff)]

            conflict = any(
                overlaps(trek.start_date, trek.end_date, s, e)
                for s, e in schedule[staff.id]
            )
            if conflict:
                continue

            db.session.add(StaffTrekAssignment(user_id=staff.id, trek_id=trek.id))
            schedule[staff.id].append((trek.start_date, trek.end_date))
            assigned_count += 1

            if assigned_count == 2:
                break

    db.session.commit()

    print(
        "Seeded 10 trekkers (3 blacklisted: trekker1-3), "
        "10 staff (2 blacklisted: staff1-2, 2 pending: staff3-4, "
        "1 rejected: staff5, 5 approved & clean: staff6-10), "
        "10 treks (4 upcoming, 2 ongoing, 2 completed, 2 cancelled), "
        "a mix of bookings consistent with each trek's status, and "
        "staff assignments on upcoming treks (non-overlapping, approved "
        "staff only)."
    )