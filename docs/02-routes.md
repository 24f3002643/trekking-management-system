# Routes
This is the final list of routes

## Home Page Routes
GET /
    - If not logged in, then redirect to /login
    - If logged in, then redirect to user's dashboard

## Login Page Routes
GET /login
POST /login

- Single login page for all users.
- No role is passed as a query parameter.
- The role is determined from the database after successful authentication.

## Register Page Routes
GET /register/trekker
POST /register/trekker

GET /register/staff
POST /register/staff

- Only trekker and staff can register.
- Admin registration is not available.
- The role is inferred from the url.
- Taking role as a query parameter is avoided because the role is fixed by the endpoint and there is no possibility of someone attempting to register as an admin.


## Dashboard Routes
GET /admin
GET /staff
GET /trekker

- Each user role has its own dashboard.
- These routes display the dashboard corresponding to the authenticated user's role.
- Since these routes only retrieve and display data without modifying the application's state, they use the GET method.


## Admin Routes

### Admin can `view, add, edit or remove trek`
GET /admin/treks
    - to view all the existing treks.

GET /admin/treks/<trek_id>
    - to view the details of a particular trek.

GET /admin/treks/create
POST /admin/treks/create
    - to view and submit trek creation form.

GET /admin/treks/<trek_id>/edit
POST /admin/treks/<trek_id>/edit
    - to view and submit trek edit form.

POST /admin/treks/<trek_id>/delete
    - to submit the form/request to delete the trek.

### Admin can `view, approve and blacklist trek staff`
GET /admin/staff
    - To view all the existing staff.

GET /admin/staff/<staff_id>
    - To view the details of a particular staff.

GET /admin/staff/pending
    - To view all the staff with pending request for registration.

POST /admin/staff/<staff_id>/approve
POST /admin/staff/<staff_id>/reject
    - To submit the form to accept or reject the staff.

POST /admin/staff/<staff_id>/blacklist
POST /admin/staff/<staff_id>/unblacklist
    - To submit the form to either add to blacklist or remove from blacklist

### Admin can `view and blacklist trekker`
GET /admin/trekkers
    - To view all the existing trekker.

GET /admin/trekkers/<trekker_id>
    - To view the details of a particular trekker.

POST /admin/trekkers/<trekker_id>/blacklist
POST /admin/trekkers/<trekker_id>/unblacklist
    - To submit the form to either add to blacklist or remove from blacklist 


### Admin can `assign staff to a particular trek`

GET /admin/treks/<trek_id>/assign
POST /admin/treks/<trek_id>/assign
    - To view and update the staff (assign or unassign) to a trek


### Admin `search treks, staff, or users by name or ID`

GET /admin/search
    - Search  treks, staff and trekkers by name or ID.
    - It will have the following query parameters: 
        - type   -> trek | staff | trekker
        - field  -> id | name
        - q      -> search keyword


### Admin can `view and manage bookings`

GET /admin/bookings
    - To view all booking records.

GET /admin/bookings/<booking_id>
    - To view the details of a particular booking.

POST /admin/bookings/<booking_id>/approve
    - To approve a pending booking.

POST /admin/bookings/<booking_id>/cancel
    - To cancel a booking.


## Staff Routes 

### Staff can `view assigned treks by admin`
GET /staff/treks
    - To view the list of treks assigned to him by admin.

GET /staff/treks/<trek_id>
    - To view the details of a particular treks assigned to him by admin.

### Staff can `update trek details : 'available slots' and  'trek status'`
GET /staff/treks/<trek_id>/update
    - To view the form to update trek details.

POST /staff/treks/<trek_id>/update
    - To submit the form to updated trek details.

### Staff can `view list of trekkers registered for their treks`

GET /staff/treks/<trek_id>/participants
    - To view list of trekkers registered for the specific trek.


## Trekker Routes

### Trekker can `view, search and filter available treks`

GET /trekker/treks
    - To view all treks available for booking.
    - Supports filtering using query parameters.
    - Query Parameters :
        - difficulty -> easy | moderate | hard
        - location   -> trek location
        - q -> trek name

GET /trekker/treks/<trek_id>
    - To view the details of a particular trek.


### Trekker can `book treks and make payment`
POST /trekker/treks/<trek_id>/book
    - To submit form to book a trek.

POST /trekker/bookings/<booking_id>/cancel
    - To submit a request to cancel a booking.

GET /trekker/payment/<booking_id>
    - To view the form of payment.

POST /trekker/payment/<booking_id>
    - To submit the form of payment.


### Trekker can `view booking status and trekking history`

GET /trekker/bookings
    - To view all the bookings.
    - Supports filtering using query parameters.
    - Query Parameter :
        - status : pending | booked | completed | cancelled

GET /trekker/bookings/<booking_id>
    - To view the details of a particular booking.
    - Displays booking information such as booking status, payment status, trek details, trek status and other related information.

