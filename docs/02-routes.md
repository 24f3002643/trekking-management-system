# Routes
This is the final list of routes, verified directly against the live
Flask app's `url_map` (see project-decisions.md / development-log.md
for the date this was last confirmed).

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

## Logout Route
POST /logout
    - Logs out the currently authenticated user by clearing the session.
    - Redirects to /login after logging out.
    - Accessible to all authenticated roles (admin, staff, trekker).
    - Uses POST (not GET) since logout changes application state (destroys the session).

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
    - Only allowed while trek.status == 'upcoming'. Blocked (both GET
      and POST) once the trek has left 'upcoming', since trekkers may
      already have booked against its current details.

POST /admin/treks/<trek_id>/delete
    - to submit the form/request to delete the trek.
    - Blocked if the trek has any active (pending/booked) bookings.

### Admin can `change a trek's status`
POST /admin/treks/<trek_id>/ongoing
    - Marks the trek 'ongoing'. Only valid from 'upcoming'. Blocked
      if today < trek.start_date.

POST /admin/treks/<trek_id>/completed
    - Marks the trek 'completed'. Only valid from 'ongoing'.
    - Cascades: bookings with booking_status == 'booked' become
      'completed'; bookings still at 'pending' become 'cancelled'
      (+ payment_status = 'refunded'), since that trekker never
      actually went on the trek.

POST /admin/treks/<trek_id>/cancelled
    - Marks the trek 'cancelled'. Valid from 'upcoming' OR 'ongoing'.
      Blocked once today > trek.end_date.
    - Cascades: every booking with booking_status in
      (pending, booked) becomes 'cancelled', payment_status becomes
      'refunded' (every existing booking is guaranteed already paid).

- Admin holds the SAME status-change powers as Trek Staff (ongoing,
  completed, cancelled) — this was a deliberate design choice: the
  admin is the business owner and should not be structurally excluded
  from any operational lever, even though Trek Staff (being physically
  present) is the more natural authority for "has this trek actually
  started/finished."
- The one asymmetry: Trek Staff can only cancel a trek from 'ongoing'
  (see Staff Routes below), while Admin can cancel from EITHER
  'upcoming' or 'ongoing' — since admin's cancel power is a
  policy-level decision (low bookings, permit issues) that doesn't
  require ground presence, unlike staff's cancel power, which exists
  specifically for ground emergencies that only arise once a trek is
  underway.

### Admin can `manage staff assignment to a trek`
GET /admin/treks/<trek_id>/manage
POST /admin/treks/<trek_id>/manage
    - To view and update the staff (assign or unassign) for a trek.
    - Only allowed while trek.status == 'upcoming' (assignment is a
      planning-time decision, same restriction as edit above).
    - Eligible staff = role == 'staff', approval_status == 'approved',
      is_blacklisted == False, and no date-overlapping assignment on
      another trek.
    - The page shows every relevant staff member with a checkbox in
      one of three states: already-assigned (checked), available
      (unchecked, clickable), or conflicting (unchecked, disabled).
    - POST re-validates every newly-added staff id from scratch
      server-side; if ANY addition fails validation, the entire
      request is rejected (nothing partial is applied), since a
      failure here likely means the disabled-checkbox UI was bypassed.

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


### Admin `search treks, staff, or users by name or ID`

GET /admin/search
    - Search treks, staff and trekkers by name or ID.
    - Query parameters:
        - type   -> trek | staff | trekker
        - field  -> id | name
        - q      -> search keyword
    - In addition to this dedicated search page, each of the Treks,
      Staff, Trekkers, and Bookings list pages ALSO has its own inline
      filter form directly on the page (both were built, not one
      instead of the other).


### Admin can `view and manage bookings`

GET /admin/bookings
    - To view all booking records.

GET /admin/bookings/<booking_id>
    - To view the details of a particular booking.

GET /admin/bookings/pending
    - To view all bookings with status == 'pending', awaiting admin approval.

POST /admin/bookings/<booking_id>/approve
    - To approve a pending booking. booking_status: pending -> booked.

POST /admin/bookings/<booking_id>/reject
    - To reject a pending booking. booking_status: pending -> cancelled.

POST /admin/bookings/<booking_id>/cancel
    - To cancel a booked booking. booking_status: booked -> cancelled,
      payment_status -> refunded.

### Admin can `view summary/analytics`

GET /admin/summary
    - Displays 4 quick-stat cards (total treks/staff/trekkers/bookings)
      and 6 matplotlib-generated charts:
      1. Top 10 Popular Treks (horizontal bar, by booking count)
      2. Bookings in the Past 7 Days (vertical bar, one bar per day)
      3. Bookings: Pending vs Booked (pie)
      4. Staff Approval Status (pie, 3 slices)
      5. Trekkers: Active vs Blacklisted (pie)
      6. Staff: Active vs Blacklisted (pie, kept separate from #5 so
         each role's ratio stays honest rather than being diluted by
         combining two different populations)
    - Charts are generated with matplotlib and saved as plain .png
      files into static/charts/, overwritten on every page load — no
      base64 encoding, no JS.


## Staff Routes 

### Staff can `view assigned treks and trekkers`
GET /staff/treks
    - To view the list of treks assigned to him by admin.

GET /staff/treks/<trek_id>
    - To view the details of a particular trek assigned to him,
      including its participant list (bookings with
      booking_status == 'booked' only — this is the confirmed
      definition of "registered trekker").

GET /staff/trekkers
    - To view all trekkers across every trek assigned to this staff
      member (a cross-trek view, distinct from a single trek's
      participant list above).

### Staff can `change a trek's status`
POST /staff/treks/<trek_id>/ongoing
    - Marks the trek 'ongoing'. Only valid from 'upcoming'. Blocked
      if today < trek.start_date.

POST /staff/treks/<trek_id>/completed
    - Marks the trek 'completed'. Only valid from 'ongoing'.
    - Same cascade as Admin's completed route above.

POST /staff/treks/<trek_id>/cancelled
    - Marks the trek 'cancelled'. ONLY valid from 'ongoing' (unlike
      Admin, staff cannot cancel a trek that hasn't started yet —
      staff's cancel power exists specifically for ground emergencies,
      which by definition only arise once a trek is underway).
      Blocked once today > trek.end_date.
    - Same cascade as Admin's cancelled route above.

### Staff can `update a trek's total_slots`
GET /staff/treks/<trek_id>/slots
POST /staff/treks/<trek_id>/slots
    - To view and submit the form to update total_slots.
    - Only allowed while trek.status == 'upcoming' (once a trek is
      'ongoing', booking is already closed, so adjusting capacity has
      no purpose).
    - New total_slots must be >= currently booked count (total_slots
      - available_slots, using the CURRENT/old total_slots). If the
      new value would be lower, the request is rejected with a message
      suggesting cancellation instead — no automatic cascade.

(The earlier `/staff/treks/<trek_id>/update` route, `staff_treks_
update`, was an earlier, superseded route for the same purpose and
has been removed. `/staff/treks/<trek_id>/slots` is the sole route
for this now.)

### Staff can `view and update profile`
GET /staff/profile
GET /staff/profile/update
POST /staff/profile/update
    - Same shape as trekker profile update: name, phone_number
      (uniqueness checked excluding self), and optional password
      change (current password verified, new/confirm must match).


## Trekker Routes

### Trekker can `view, search and filter available treks`

GET /trekker/treks
    - To view all treks available for booking (status == 'upcoming',
      available_slots > 0, excluding treks this trekker has already
      booked).
    - Supports filtering using query parameters:
        - difficulty -> easy | moderate | hard
        - location   -> trek location
        - trekname   -> trek name

GET /trekker/treks/<trek_id>
    - To view the details of a particular trek, including assigned
      staff and this trekker's existing booking status on it, if any.


### Trekker can `book and cancel treks`
GET /trekker/treks/<trek_id>/book
POST /trekker/treks/<trek_id>/book
    - GET shows the trek's details alongside a dummy card-payment
      form, on ONE combined page (booking and payment are a single
      step, not two separate ones — see project-decisions.md).
    - POST checks card fields for presence only (dummy payment, no
      real validation), then creates the Booking directly with
      booking_status = 'pending', payment_status = 'paid', and
      decrements trek.available_slots. No booking ever exists in an
      unpaid state.

POST /trekker/bookings/<booking_id>/cancel
    - To cancel an existing booking. Blocked if already
      cancelled/completed, or if today >= trek.start_date.
    - If payment_status == 'paid', sets it to 'refunded'.
    - Increments trek.available_slots back.


### Trekker can `view booking status and trekking history`

GET /trekker/bookings
    - Active bookings: bookings whose TREK status is 'upcoming' or
      'ongoing'. Split into "pending requests" and "confirmed"
      sub-sections on the page.

GET /trekker/bookings/history
    - Past bookings: bookings whose TREK status is 'completed' or
      'cancelled'. A separate route and template from the Active page
      above, with its own filter form (trekname/location/difficulty/
      trek-status).

GET /trekker/bookings/<booking_id>
    - To view the details of a particular booking, including its
      related trek and assigned staff.


### Trekker can `view and update profile`
GET /trekker/profile
GET /trekker/profile/update
POST /trekker/profile/update
    - name, phone_number (uniqueness excluding self), optional
      password change (current password verified, new/confirm match).