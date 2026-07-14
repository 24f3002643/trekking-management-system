# Database Design
This is the final database design.

## Key Terminologies
1. Admin: A user with the highest level of access who manages the entire trekking system.
2. Trek Staff: A staff member responsible for managing and coordinating assigned treks.
3. User (Trekker): A participant who books and participates in trekking activities.
4. Trek: A trekking event created and managed in the system.
5. Booking: A record of a user booking a trek.
6. Staff Profile: Details of a registered staff member.

## Design Decision
1. The project specification suggests a separate Staff Profile table. Since staff members do not have any attributes beyond those already present in User, a separate table would introduce redundancy. Therefore, staff are modeled as users with role = 'staff', while the many-to-many relationship between staff and treks is represented by the StaffTrekAssignment table.
2. Booking and payment were originally two separate steps (`booking_status` included an `initiated` state, and `payment_status` included a `pending` state, representing a booking created before payment was completed). These were merged into a single step: a Booking row is now only ever created after payment succeeds, directly as `booking_status='pending'`, `payment_status='paid'`. This removed the `initiated` value from `booking_status` and the `pending` value from `payment_status` — see `project-decisions.md` for the full reasoning.
3. `Trek.status` was originally computed automatically from `start_date`/`end_date` on every fetch. This was changed to fully manual control by Trek Staff and Admin, since the project statement's "mark trek as started/completed" language implies a deliberate action rather than a background computation — see `project-decisions.md` for the full reasoning.


## Database Modelling

### Nouns in the System
1. Admin
2. Trekker
3. Trek Staff
4. Trek
5. Booking
6. Trekking History

### Actors
Actors are the external entities that interact with the system.
1. Admin
2. Trekker
3. Trek Staff

### Entities
1. User : A Person that interact with the system.
    - User can serve as an admin/staff/trekker, based on role attribute, so a single entity suffice for all the three.
2. Trek : A trekking event created and managed in the system.
3. Booking : A record of a user booking a trek.

### Attributes
1. User
    - id (primary key)
    - name 
    - email (unique)
    - password_hash
    - phone_number (unique)
    - role (admin/staff/trekker)
    - approval_status (null/pending/approved/rejected) //only meaningful when role=="staff", null for "admin" and "trekker"
        - null : for admin (by default)
        - pending : staff has completed the registration, but the admin has not approved the request yet.
        - approved : admin has approved the staff registration request.
        - rejected : admin has rejected the staff registration request. 
    - is_blacklisted (true/false) //only meaningful when role=="staff" or role=="trekker", false for "admin"
        - true : if the admin blacklist the trekker or staff (only for staff or trekker).
        - false : always false for admin (by default). false for trekker or staff (by default). 

2. Trek
    - id (primary key)
    - trekname (unique)
    - location 
    - difficulty (easy/moderate/hard)
        - easy : trek difficulty is easy.
        - moderate : trek difficulty is medium.
        - hard : trek difficulty is hard.
    - total_slots
        - stores the maximum number of bookings that a trek can accommodate. one booking per trekker.
    - available_slots
        - stores the number of slots currently available for booking.
    - status (upcoming/ongoing/completed/cancelled)
        - This attribute is changed only by explicit action from Trek Staff or Admin — it is never automatically computed from start_date/end_date. start_date/end_date act as guards on when a transition is *permitted*, not as triggers.
        - upcoming : the trek's initial status on creation. Can be changed to 'ongoing' (by Staff or Admin, once start_date has arrived) or 'cancelled' (by Admin only).
        - ongoing : set manually by Staff or Admin once the trek has actually started. Can be changed to 'completed' or 'cancelled' (Staff or Admin can complete; Staff can only cancel from this state, Admin can cancel from this or 'upcoming').
        - completed : set manually by Staff or Admin, only reachable from 'ongoing' (never directly from 'upcoming', for either role).
        - cancelled : set manually, either by Admin (from 'upcoming' or 'ongoing') or by Staff (from 'ongoing' only, since Staff's cancel power exists for ground emergencies that only arise once a trek is underway). Blocked entirely once today > end_date, regardless of who is attempting it.
    - start_date
    - end_date
    - amount (decimal value)
    - additional_info

3. Booking
    - id (primary key)
    - user_id (foreign key)
    - trek_id (foreign key)
    - booking_date
    - booking_status (pending/booked/cancelled/completed)
        - pending : trekker has completed payment, and the booking has been created, but admin has not approved it yet.
        - booked : admin has approved the booking.
        - cancelled : either the trekker cancelled the booking himself, or the admin/staff cancelled the associated trek, or admin rejected the pending booking.
        - completed : the associated trek has been marked completed, and this booking was 'booked' at that time.
    - payment_status (paid/refunded)
        - paid : payment has been made. Since booking and payment are a single combined step (a Booking row is only ever created after payment succeeds), every booking starts as 'paid' — there is no unpaid/pending payment state.
        - refunded : the booking was subsequently cancelled (by the trekker, or as part of a trek-cancellation cascade), and the payment was refunded.


### Relationships
1. Between User (Trekker) and Booking
    - One to many relationship (1:m).
    - One trekker can have multiple booking.
    - One booking belongs to only one trekker.

2. Between Trek and Booking
    - One to many relationship (1:m).
    - One trek can have multiple booking.
    - One booking belongs to only one trek.

3. Between User (Trek Staff) and Trek.
    - many to many relationship (m:n).
    - One trek staff can be assigned to more than one trek (provided that the duration doesn't overlap), and one trek can have multiple trek staffs assigned to it.
    - This relationship would be implemented by table StaffTrekAssignment in relational table.


### ER Diagram to Relational Table
1. User
    - id (primary key)
    - name 
    - password_hash
    - email (unique)
    - phone_number (unique)
    - role (admin/staff/trekker)
    - approval_status (null/pending/approved/rejected) //only meaningful when role=="staff", null for "admin" and "trekker"
    - is_blacklisted (true/false) //only meaningful when role=="staff" or role=="trekker", false for "admin"

2. Trek
    - id (primary key)
    - trekname
    - location 
    - difficulty (easy/moderate/hard)
    - total_slots
    - available_slots 
    - status (upcoming/ongoing/completed/cancelled)
    - start_date
    - end_date
    - amount
    - additional_info

3. Booking
    - id (primary key)
    - user_id (foreign key) //refers to id of User table, for user with role=="trekker"
    - trek_id (foreign key) //refers to id of Trek table
    - booking_date
    - booking_status (pending/booked/cancelled/completed)
    - payment_status (paid/refunded)

4. StaffTrekAssignment
    - user_id (foreign key) //refers to id of User table, for user with role=="staff"
    - trek_id (foreign key) //refers to id of Trek table
    - PRIMARY KEY : (user_id, trek_id) //composite