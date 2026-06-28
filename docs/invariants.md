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

### Booking
1. Every booking belongs to exactly one trekker and one trek.
2. One trekker can have at most one booking for a particular trek.
3. One booking reserves exactly one slot.
4. A booking can never exist without both a valid user and a valid trek.
5. Every booking has exactly one booking status (`initiated`/`pending`/`booked`/`completed`/`cancelled`).
6. A booking can only be created if the trek has `available_slots` > 0.

### Trek Staff Assignment
1. Every record in `StaffTrekAssignment` table must reference:
    - a user whose `role == 'staff'`, and
    - a valid trek.
2. Multiple `staff` members can be assigned to the same trek.
3. A Trek `staff` member may be assigned to multiple treks, provided the trek durations do not overlap (i.e. cannot be assigned to overlapping treks).
4. A Trek `staff` member can only manage treks assigned to them.
5. Only approved Trek `staff` can be assigned to a trek.