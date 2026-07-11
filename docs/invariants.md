# Invariants
The rules that must remain true throughout the lifetime of the application.

### User 
1. Every user has exactly one role : `admin`, `staff` or `trekker`.
2. The `admin` must exist predefined in the database.
3. `approval_status` is meaningful only for users with `role == 'staff'`. For users with `role == 'admin' or 'trekker'`, `approval_status` must be `NULL`.
4. `is_blacklisted` is always `false` for the `admin`.
5. A `staff` cannot access the staff dashboard until approved by the `admin`.
6. A blacklisted `staff` or `trekker` cannot log in to the application.

### Trek
1. Every trek is always in exactly one of the following states:
    - `upcoming`
    - `ongoing`
    - `completed`
    - `cancelled`
2. A `cancelled` trek can never become `ongoing` or `completed`.
3. A `completed` trek can never become `cancelled`.
4. `start_date` must be earlier than `end_date`.
5. `available_slots` can never be negative.
6. Trek status is changed only by explicit action (Trek Staff or Admin), never automatically computed from dates. The permitted transitions are:
    - `upcoming` -> `ongoing` : Trek Staff or Admin. Blocked if `today < start_date`.
    - `ongoing` -> `completed` : Trek Staff or Admin. `upcoming` -> `completed` directly is never allowed, for anyone.
    - `ongoing` -> `cancelled` : Trek Staff or Admin. Blocked if `today > end_date`.
    - `upcoming` -> `cancelled` : Admin only (Trek Staff cannot cancel a trek that hasn't started, since staff's cancel power exists specifically for ground emergencies, which only arise once a trek is underway).
    - Any transition to `cancelled` is blocked once `today > end_date`, regardless of who is attempting it.
7. A trek can be edited (`admin_treks_edit`) only while `status == 'upcoming'`.
8. Staff can only be assigned to or unassigned from a trek while its `status == 'upcoming'`.
9. Staff can only update a trek's `total_slots` while its `status == 'upcoming'`; the new value must not be less than the number of currently active (`pending`/`booked`) bookings.
10. There is no automatic safety net preventing trekker booking based on `start_date` alone — booking is gated purely on `status == 'upcoming'`. If Trek Staff is late to mark a trek `ongoing`, it may remain bookable past its actual start date. This is a deliberately accepted simplification, not an oversight.

### Booking
1. Every booking belongs to exactly one trekker and one trek.
2. One trekker can have at most one active (non-`cancelled`) booking for a particular trek.
3. One booking reserves exactly one slot.
4. A booking can never exist without both a valid user and a valid trek.
5. Every booking has exactly one booking status: `pending`, `booked`, `completed`, or `cancelled`. (There is no `initiated` state — booking and payment are a single combined step; a Booking row is only ever created after payment succeeds, so no "payment still pending" state can exist.)
6. `payment_status` has exactly two values: `paid` or `refunded`. Every booking is paid at creation time; `refunded` only applies once a paid booking is cancelled.
7. A booking can only be created if the trek has `available_slots > 0` and `status == 'upcoming'`.
8. When a trek becomes `cancelled`, every booking on it with `booking_status` in (`pending`, `booked`) becomes `cancelled`, and `payment_status` becomes `refunded`.
9. When a trek becomes `completed`, every booking on it with `booking_status == 'booked'` becomes `completed`; any booking still at `pending` becomes `cancelled` (+ `refunded`), since that trekker never actually went on the trek.

### Trek Staff Assignment
1. Every record in `StaffTrekAssignment` table must reference:
    - a user whose `role == 'staff'`, and
    - a valid trek.
2. Multiple `staff` members can be assigned to the same trek.
3. A Trek `staff` member may be assigned to multiple treks, provided the trek durations do not overlap (i.e. cannot be assigned to overlapping treks).
4. A Trek `staff` member can only manage treks assigned to them.
5. Only approved, non-blacklisted Trek `staff` can be assigned to a trek.
6. Assignment/unassignment is only permitted while the target trek's `status == 'upcoming'`.