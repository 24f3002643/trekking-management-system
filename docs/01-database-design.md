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
    - username (unique)
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
        - upcoming : this will be status of trek, before the start date (if trek is not cancelled yet).
        - ongoing : this will be status of trek, from start date to end date (if trek is not cancelled yet).
        - completed : this will be status of trek, after the end date (if trek was not cancelled).
        - cancelled : this will be status of trek, if the trek is cancelled, either before the start date, between the start date (included) and end date (included), or after the end date.
    - start_date
    - end_date
    - additional_info

3. Booking
    - id (primary key)
    - user_id (foreign key)
    - trek_id (foreign key)
    - booking_date
    - booking_status (initiated/pending/booked/cancelled/completed)
        - initiated : trekker has started the booking process, but payment has not been completed yet.
        - pending : trekker has requested for the booking, and payment has been made, but admin has not approved the booking yet.
        - booked : admin has approved the booking.
        - cancelled : either trekker cancelled the booking himself, or the admin cancelled it.
        - completed : the trek has been completed by the trekker.
    - payment_status (pending/paid/refunded)
        - pending : trekker has started process for the booking, but payment has not been made yet.
        - paid : trekker has paid the amount for the booking.
        - refunded : Either the trek was cancelled (by admin), or the booking was cancelled (either by trekker himself or by the admin).
    - additional_info


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
    - username (unique)
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
    - additional_info

3. Booking
    - id (primary key)
    - user_id (foreign key) //refers to id of User table, for user with role=="trekker"
    - trek_id (foreign key) //refers to id of Trek table
    - booking_date
    - booking_status (initiated/pending/booked/cancelled/completed)
    - payment_status (pending/paid/refunded)
    - additional_info

4. StaffTrekAssignment
    - user_id (foreign key) //refers to id of User table, for user with role=="staff"
    - trek_id (foreign key) //refers to id of Trek table
    - PRIMARY KEY : (user_id, trek_id) //composite