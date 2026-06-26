# Database Design

### Some Clarification
1. What does status in Trek entity denotes?
    - pending 
    - approved
    - open
    - closed
    - completed

## Key Terminologies
1. Admin: A user with the highest level of access who manages the entire trekking system.
2. Trek Staff: A staff member responsible for managing and coordinating assigned treks.
3. User (Trekker): A participant who books and participates in trekking activities.
4. Trek: A trekking event created and managed in the system.
5. Booking: A record of a user booking a trek.
6. Staff Profile: Details of a registered staff member.





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
    - phone_number (unique)
    - role (admin/staff/trekker)
    - approval_status (null/pending/approved/rejected) //only meaningful when role=="staff", null for "admin" and "trekker"
    - is_blacklisted (true/false) //only meaningful when role=="staff" or role=="trekker", false for "admin"

2. Trek
    - id (primary key)
    - name
    - location 
    - difficulty (easy/moderate/hard)
    - duration (in days)
    - available_slots 
    - status (pending/approved/open/closed/completed)
    - start_date
    - end_date
    - additional_info

3. Booking
    - id (primary key)
    - user_id (foreign key)
    - trek_id (foreign key)
    - booking_date
    - booking_status (booked/cancelled/completed)
    - payment_status (pending/paid/refunded)
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


### ER Diagram to Relational Table
1. User
    - id (primary key)
    - name
    - email (unique)
    - phone_number (unique)
    - role (admin/staff/trekker)
    - approval_status (null/pending/approved/rejected) //only meaningful when role=="staff", null for "admin" and "trekker"
    - is_blacklisted (true/false) //only meaningful when role=="staff" or role=="trekker", false for "admin"

2. Trek
    - id (primary key)
    - name
    - location 
    - difficulty (easy/moderate/hard)
    - duration (in days)
    - available_slots 
    - status (pending/approved/open/closed/completed)
    - start_date
    - end_date
    - additional_info

3. Booking
    - id (primary key)
    - user_id (foreign key) //refers to id of User table, for user with role=="trekker"
    - trek_id (foreign key) //refers to id of Trek table
    - booking_date
    - booking_status (booked/cancelled/completed)
    - payment_status (pending/paid/refunded)
    - additional_info

4. StaffTrekAssignment
    - user_id (foreign key) //refers to id of User table, for user with role=="staff"
    - trek_id (foreign key) //refers to id of Trek table
    - PRIMARY KEY : (user_id, trek_id) //composite