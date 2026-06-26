# Invariants
The rules that must remain true throughout the lifetime of the application.

### User 
1. Every user has exactly one role : Admin, Trek Staff or Trekker
2. The Admin must exist predefined in the database.
3. A Trek Staff cannot access the staff dashboard until approved by the Admin.
4. A blacklisted trekker or trek staff cannot access the application.

### Trek
1. Every trek has exactly one status at any point in time (Pending/Approved/Open/Closed/Completed).
2. Available slots can never be negative.
3. Only treks with status Open can be booked.

### Booking
1. Every booking belongs to exactly one Trekker.
2. Every booking belongs to exactly one Trek.
3. Every booking has exactly one booking status (Booked/Cancelled/Completed).
4. A trekker cannot have multiple active bookings for the same trek.
5. A booking can only be created for a trek with status Open.
6. A booking can only be created if the trek has available slots.

### Trek Staff Assignment
1. A trek may have one or more assigned staff members.
2. A Trek Staff member may be assigned to multiple treks, provided the trek durations do not overlap.
3. A Trek Staff member can only manage treks assigned to them.
4. Only approved Trek Staff can be assigned to a trek.