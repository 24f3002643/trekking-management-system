# Business Logics
This page contains all the business logics in plain language

## Public Routes
### `home`
0. The decorator checks if user is logged in or not, if they have the role which is required to login to the page or not
1. Get the role from session.
2. redirect to  the corresponding role dashboard.


### `login`
1. Check the http method
2. If method=="GET"
    3. Render the login page.
4. If method=="POST"
    5. Get the submitted email and password from the form.
    6. Look up for a user by submitted mail in database.
    7. If no user is found, then render "message.html" with message "Invalid Email or Password".
    8. If user is found, convert the submitted password to hash, and check it against password_hash in the database.
    9. If password does not matches, then render "message.html" with message "Invalid Email or Password. Try Again".
    10. If password matches, then check for user role. 
    11. If user.role == "admin", then redirect to admin dashboard.
    12. If user.role == "staff", then check for approval_status. 
        13. If user.approval_status == "pending", then render "message.html" with the message "Your registration as staff is still pending to be approved by admin. Try login in after some time".
        14. If user.approval_status == "rejected", then render "message.html" with the message "Your registration as staff is rejected by admin".
        15. If user.approval_status == "approved", then check for is_blacklisted.
            15. If is_blacklisted == "True", then render the "message.html" page with message "You have been blacklisted by the admin".
            16. If is_blacklisted == "False, then redirect to staff dashboard.
    17. If user.role == "trekker", check for is_blacklisted.
        18. If is_blacklisted == "True", then render the "message.html" page with message "You have been blacklisted by the admin".
        19. If is_blacklisted == "False", then redirect to trekker dashboard.

### `logout`
1. Clear the session
2. Redirect to login page.

### `staff_register`
1. Check the http method
2. If method == "GET"
    3. render the register_staff.html page.
4. If method == "POST"
    5. Get the submitted detail: name, email, password, phone_number
    6. set the role = "staff"
    7. Check if the user exists in the database by email.
    8. If yes, then render the message.html with message "User already exists".
    9. If No, 
        10. check whether phone_number exists in the database.
        11. If yes, then render the message.html with message "Phone Number is already registered. Try with another phone number".
        12. If no, then
            13. Add and commit  name, email, hashed password, phone_number, role, approval_status="pending", is_blacklisted=False to the database.
            14. Render the message.html with message "Registration request has been sent successfully to the admin. Try login in after some time'.


### `trekker_register`
1. Check the http method
2. If method == "GET"
    3. render the register_trekker.html page.
4. If method == "POST"
    5. Get the submitted detail: name, email, password, phone_number
    6. set the role = "trekker"
    7. Check if the user exists in the database by email.
    8. If yes, then render the message.html with message "User already exists".
    9. If No, 
        10. check whether phone_number exists in the database.
        11. If yes, then render the message.html with message "Phone Number is already registered. Try with another phone number".
        12. If no, then
            13. Add and commit  name, email, hashed password, phone_number, role, approval_status=null, is_blacklisted=False to the database.
            14. Render the message.html with message "Registration Successful. Login to access the application'.

### `home`
1. Check if user_id is in the session or not.
2. If not, then redirect to login page.
3. If yes, then check the role, and redirect to corresponding user role 's dashboard. 
    4. Also add last else in if-else ladder, and redirect to login page.

### `admin_dashboard`
1. Get the admin id from the session.
2. Fetch the details of the admin from the database.
3. Fetch all the bookings, sorted by the descending order of booking_date.
4. render the admin_dashboard.html by passing the admin details and all the bookings.

### `admin_treks_page`
1. Get the admin id from the session.
2. Fetch the details of the admin from the database.
3. Fetch all treks, grouped by status in this fixed priority order: 
   ongoing, upcoming, completed, cancelled. Within each status group, 
   sort by start_date ascending.
4. render the admin_treks.html by passing the admin details and all the treks

### `admin_treks_view`
1. Get the admin id from the session.
2. Fetch the details of the admin from the database.
3. Fetch the details of the given trek from its id from the database.
4. Fetch all bookings, grouped by status in this fixed priority order: 
   pending, booked, completed, initiated, cancelled. Within each status group, 
   sort by booking_date descending.
5. Also fetch the the staffs assigned on this treks.
6. render the admin_treks_details.html by passing admin object, booking object and staff object.

### admin_treks_create

**GET:**
1. Get the admin id from the session.
2. Fetch the admin's details from the database.
3. Render the trek creation form template, passing the admin's details.

**POST:**
1. Get submitted values from the form: trekname, location, difficulty, 
   total_slots, start_date, end_date, amount, additional_info.
2. Check if a trek with this trekname already exists.
   - If yes, show an error message: "A trek with this name already exists."
3. Convert start_date and end_date to actual date objects; convert 
   total_slots to an integer, amount to a decimal/float.
4. Check that start_date is strictly earlier than end_date.
   - If not, show an error message: "Start date must be before end date."
5. Set available_slots = total_slots (new trek, no bookings yet).
6. Create a new Trek object with all the above values, plus status 
   defaulting to 'upcoming' (via model default).
7. Add to database session and commit.
8. Redirect to the admin treks list page.

### admin_treks_edit

### admin_treks_edit

**GET:**
1. Get the admin id from the session.
2. Fetch the admin's details from the database.
3. Fetch the Trek object from the given trek_id.
4. If trek not found, show an error message.
5. Render the trek edit form template, passing the admin's details and the trek.

**POST:**
1. Fetch the Trek object from the given trek_id.
2. If trek not found, show an error message.
3. Get submitted values from the form: trekname, location, difficulty,
   total_slots, start_date, end_date, amount, additional_info.
4. Convert start_date and end_date to date objects; total_slots to an
   integer; amount to a Decimal.
5. Check if a DIFFERENT trek (id != this trek's id) already has this
   trekname. If yes, show an error: "A trek with this name already exists."
6. Check that start_date is strictly earlier than end_date. If not,
   show an error: "Start date must be before end date."
7. Calculate currently booked slots: booked = trek.total_slots - trek.available_slots.
8. Calculate new available_slots = total_slots - booked.
9. If new available_slots < 0, show an error: "Cannot reduce total slots 
   below the number of slots already booked."
10. Update the Trek object's fields: trekname, location, difficulty,
    total_slots, available_slots (the recalculated value), start_date,
    end_date, amount, additional_info.
11. Commit the changes.
12. Redirect to the admin treks list page.


### admin_treks_delete

**POST:**
1. Fetch the Trek object using the given trek_id from the database.
2. If no trek found, show an error message.
3. Check if any bookings for this trek have booking_status in 
   ('initiated', 'pending', 'booked') — i.e., any active booking.
4. If any active bookings exist, show an error message: "This trek has 
   active bookings. Cancel those bookings before deleting this trek."
5. If no active bookings exist, delete all StaffTrekAssignment records 
   for this trek.
6. Delete all remaining (completed/cancelled) Booking records for 
   this trek.
7. Delete the Trek object itself.
8. Commit to the database.
9. Show a success message.