# Project Decisions

## Decision 1 : Single `User` Table

### Info
- Date: June 26, 2026 to June 28, 2026
- Status : Current

### Context 
- The project document specifies three types of users based on role : `admin`, `staff` and `trekker`
- All the three types of users have almost the same attributes, leaving a few of them :
    - `staff` has two extra attributes : `is_blacklisted ` and `approval_status`.
    - `trekker` has one extra attributes : `is_blacklisted`.
- `staff` has one relationship to `Trek` to denote the trek assigned to it.  
- The project document suggests `StaffProfile` table to store the details about staff, and the treks assigned to them.

### Decision 
- A single `User` table will be used with a `role` attribute to distinguish between different user types.
- The two attributes `is_blacklisted ` and `approval_status` will be there in `User` table. For `admin`, `approval_status` will contain `null`, (by default) and `is_blacklisted` will contain `false` (by default). For `staff` and `trekker`, the value for both attribute will be according to the database schema.
- For `staff`, to capture the relationship about which trek has been assigned to it, we will use another table `StaffTrekAssignment` to store that (since it is a relationship).

### Reason 
- All the three types of users share the same basic attributes. 
- Creating separate table, for either `staff` or `trekker` or both, would introduce redundancy.

### Impact
- Simplifies the schema and avoid data duplication.
- Easier to write business logic.  

### Alternative to the Current Decision
- Separate table for `admin`, `trekker` and `staff`.
- In this approach too, we will still need another table `StaffTrekAssignment` to capture which staff has been assigned to which trek (This is because the relationship is many-to-many, so we can't store trek assigned to the `staff` table).

---

## Decision 2 : Avoiding Duplicate Booking only via Business Logic

### Info
- Date : June 26, 2026 to June 28, 2026
- Status : Current

### Context
- Here, each trek is an event, which has start date and end date. So even if there are two treks with everything same, but with different start date and end date, they will be two different treks.
- So a trekker cannot book the same trek twice (in `Booking` table)
- This duplicate booking can be avoided via :
    - Database `UNIQUE` constraint in `Booking` table.
    - Business logic
- The best practice is to avoid duplicate bookings using both `UNIQUE` constraints and Business logic.   

### Decision
- To avoid duplicate bookings only using Business logic.

### Reason
- For simplicity,

### Impact
- This will keep project simple.

### Alternatives to the current decision
- Avoid duplicate booking using both : `UNIQUE` constraints and Business logic.

---

## Decision 3 : Delete Cascade Operation only via Business Logic

### Info
- Date : June 26, 2026 to June 28, 2026
- Status : Current

### Context
- If a `trekker` entry in the `User` table is deleted, or a entry in `Trek` table is deleted, all the bookings in `Booking` table corresponding to that `trekker` or `trek` should be deleted.
- There are  two ways to implement this :
    - Using `cascade='all, delete-orphan` in db.relationship() in the database model.
    - Using Business logic.

### Decision
- To implement delete cascade operation only using Business Logic.

### Reason
- For simplicity

### Impact
- This will keep project simple.


### Alternatives to the Current Decision
- To implement delete cascade operation using both:
    - Using `cascade='all, delete-orphan` in db.relationship() in the database model.
    - Using Business logic.

---


## Decision 4 : How many slot a `trekker` can book?

### Info
- Date : June 26, 2026 to June 28, 2026
- Status : Current

### Context
- Can a `trekker` book only one slot?, or
- Can a `trekker` book more than one slot, for family members, friends, etc.?

### Decision
- A `trekker` can book only one slot.

### Reason
- For simplicity.

### Impact
- This will keep project simple.

### Alternatives to the Current Decision
- In general real live scenario, a `trekker` could have been able to book more than one slot.

---

## Decision 5 : `status` attribute in `Trek` table

### Info
- Date : June 26, 2026 to June 28, 2028

### Context
- The project docs suggested the following values for `status` attribute :
    - `pending`
    - `approved`
    - `open`
    - `closed`
    - `completed`
- Some clarification was needed. 
    - What does each value mean/denote?
    - If `admin` itself creates the trek, then who will approve it?
- Asked the project course team for clarification. They said :
    - We can keep reasonable values for `status` field ourselves.
    - If `admin` itself creates the trek, there is no need for approval.

### Decision
- The values in `status` field will be :
    - `upcoming` : A trek that has not been cancelled, and current date is less than start date.
    - `ongoing` : A trek that has not been cancelled, and the current date is between start date (included) and end date (included).
    - `completed` : A trek that has not been cancelled, and the current date is more than the end date.
    - `cancelled` : A trek that is cancelled, either before the start date, or between start date (included) and end date (included).

### Reason
- The original values for `status` did not have clear meaning of what they meant.
- `upcoming`, `ongoing` and `completed` are the obvious value for `status` attribute.
- `cancelled` is required, since a trek can be cancelled either in its `upcoming` phase or `ongoing` phase. So another value was needed to capture that situation.

### Impact
- This keeps the `status` of trek event unambiguous and clear. 

### Alternatives to the Current Decision
- No other alternatives were considered.

---

## Decision 6 : Booking and Payment Workflow

### Info
- Date : June 26, 2026 to June 28, 2026
- Status : **Superseded by Decision 25** (booking and payment merged 
  into a single step; `initiated` state removed; `payment_status` 
  simplified to `paid`/`refunded`). Kept below for historical record 
  of the original design.

### Context
- `Booking` table has the following two attributes with their values :
    - `booking_status` : `initiated`, ``pending`, `booked`, `cancelled`, and `completed`
    - `payment_status` : `pending`, `paid`, and `refunded`
- These are the following questions : 
    - What does each value denotes for these two attributes `booking_status` and `payment_status`?
    - What would be workflow for booking and payment.

### Decision
- `booking_status` :
    - `pending` : `trekker` has requested for the booking, and payment has been completed, but `admin` has not approved till now.
    - `booked` : `admin` has approved the requested booking.
    - `cancelled` : either `trekker` cancelled the booking himself, or the `admin` cancelled it.
    - `completed` : the trek has been completed by the `trekker`.
- `payment_status` :
    - `pending` : `trekker` has started the process for the booking, but payment has not been completed yet.
    - `paid` : `trekker` has paid the amount for the booking.
    - `refunded` : Either the trek was cancelled (by `admin`), or the booking was cancelled (either by `trekker` himself or by the `admin`).
- Workflow :
    - A `trekker` start the process of booking, fills the details and submit it. Payment is not made yet. (`booking_status` = `initiated`, `payment_status` = `pending`)
    - A `trekker` completes the payment process, but the booking request has not been approved by the `admin` (`booking_status` = `pending`, `payment_status` = `paid`)
    - `admin` approves the booking request. (`booking_status` = `booked`, `payment_status` = `paid`)
    - The  `trekker` completes the trek. (`booking_status` = `completed`, `payment_status` = `paid`)
    - The trek is cancelled by the `admin`, or the booking was cancelled by the `trekker` himself or by the `admin`, and `Trek.status == 'ongoing' or 'upcoming'`. (`booking_status` = `cancelled`, `payment_status` = `refunded`)    

### Reason
- `initiated` was introduced for `booking_status`, to denote the time period between booking process start and payment process completion.
- `pending` was introduced for `booking_status`, to denote the time period payment process completion and admin approval.
- `payment_status` attribute is not mentioned in the project doc, but was told by project course team to add on the discussion forum.
- All these values captures all the possible state of a booking.

### Impact
- This level of detailing removes any ambiguity.

### Alternatives to the Current Decision
- No other alternatives were considered.

---

## Decision 7: Adding `total_slots` attribute to `Trek` table

### Info
- Date : June 26, 2026 to June 28, 2026
- Status : Current

### Context
- `Trek` table has one attribute `available_slots` to store the number of slots that is available at present.
- With this design, there was no direct way to determine: 
    - Total capacity of a trek.
    - Number of bookings for a trek

### Decision
- A new attribute `total_slots` was added to the `Trek` table.

### Reason
- The new attribute `total_slots` makes the above information directly available:
    - Total capacity of a trek: `total_slots`
    - Number of bookings for a trek: `total_slots - available_slots`

### Alternatives Considered
1. Design 1
    - Store `total_slots` and `booked_slots`.
    - available slots can be derived by `total_slots` - `booked_slots`.
2. Design 2
    - Store only `available_slots` (initial design).

---

## Decision 8: Removing `duration` attribute from `Trek` table

### Info
- Date: June 28, 2026
- Status: Current

### Context
- The project document suggests a `duration` attribute for the `Trek` table.
- The `Trek` table already stores `start_date` and `end_date`.
- The duration of a trek can always be derived from these two attributes.

### Decision
- The `duration` attribute will be removed from the `Trek` table.

### Reason
- The duration of a trek can be calculated from `start_date` and `end_date` whenever required.
- Storing `duration` would introduce redundant data.
- The course team confirmed on the discussion forum that the `duration` attribute is optional because it can be computed from `start_date` and `end_date`.

### Impact
- removes redundant data in the database.
- Ensures that the duration of a trek is always consistent with its start and end dates.

### Alternatives Considered
- Store `duration` as a separate attribute in the `Trek` table (current design).    

---
## Decision 9 : Single Login Page for All User Roles

### Info
- Date : June 29, 2026
- Status : Current

### Context
- The application supports three user roles: `admin`, `staff`, and `trekker`.
- There were two possible approaches:
    - Separate login pages for each role.
    - A single login page for all users.

### Decision
- A single login page (/login) will be used for all users.
- The user role will not be provided during login.
- After successful authentication, the application will determine the user's role from the User table and redirect the user to the corresponding dashboard.

### Reason
- The role is already stored in the database, so asking the user to select a role during login is redundant.
- Since the username is unique across all users, there cannot be two users with same username but with different roles.
- Eliminates the possibility of selecting an incorrect role during login.

### Impact
- Simplifies the authentication flow.
- Provides a single entry point for all users.
- Keeps the database as the single source of truth for user roles.

### Alternatives Considered
1. Design 1 : Separate login pages for `admin`, `staff`, and `trekker`.
2. Design 2 : Passing the role as a query parameter during login.

---

## Decision 10 : Separate Registration Endpoints for Each User Role

### Info
- Date : June 29, 2026
- Status : Current

### Context
- Only `trekker` and `staff` are allowed to self-register.
- `admin` accounts are created manually and cannot be registered through the application.
- Two possible approaches were considered:
    - A single registration page with role selection.
    - Separate registration endpoints for each role.

### Decision
- Separate registration endpoints will be used:
    - `/register/trekker`
    - `/register/staff`

### Reason
- The role becomes implicit from the endpoint.
- Prevents users from attempting to register as an `admin`.
- Simplifies the registration logic by eliminating role validation during registration.

### Impact
- Cleaner registration workflow.
- Eliminates unnecessary role selection during registration.

### Alternatives Considered
- A single registration page with a role selector.

---

## Decision 11 : Staff Assignment Managed Through Trek

### Info
- Date : June 29, 2026
- Status : Current

### Context
- Staff assignment represents a many-to-many relationship between Staff and Trek.
- Two designs were considered:
    - A dedicated assignment module.
    - Managing assignments from the trek being administered.

### Decision
- Staff assignment will be managed from the trek itself.
    - `GET  /admin/treks/<trek_id>/assign`
    - `POST /admin/treks/<trek_id>/assign`
- The assignment page displays the current staff assigned to a trek and allows the administrator to update the complete assignment in a single operation.

### Reason
- Staff assignment is a part of managing a trek.
- The administrator naturally assigns staff while managing a trek.

### Impact
- Produces a simpler user interface.
- Avoids introducing a separate assignment module.
- Keeps trek-related operations grouped together.

### Alternatives Considered
- A separate assignment resource such as:
    - `/admin/assignments`
    - `/admin/assignments/create`

---

## Decision 12 : Searching and Filtering Using Query Parameters

### Info
- Date : June 29, 2026
- Status : Current

### Context
- Several pages support searching and filtering, such as:
    - Available treks.
    - Booking history.
    - Admin search.
- Two approaches were considered:
    - Separate routes for search and filtering.
    - Query parameters on the existing resource routes.

### Decision
- Searching and filtering will be implemented using query parameters on the existing resource routes.

### Reason
- Searching and filtering do not create new resources.
- Query parameters naturally represent different views of the same resource collection.
- Avoids creating unnecessary endpoints.

### Impact
- Produces a smaller and more consistent routing structure.
- Makes filtered URLs bookmarkable and shareable.
- Reduces the number of endpoints that need to be maintained.

### Alternatives Considered
- Separate endpoints such as:
    - `/trekker/treks/search`
    - `/trekker/treks/filter`
    - `/trekker/bookings/history`

## Decision 13: Generic Message Page

### Info
- Date : June 29, 2026 to June 30, 2026
- Status : Current

### Context
- Many operations require displaying a message to the user, such as "successful registration", "invalid credentials", "pending staff approval", "access denied", "booking confirmation", etc.
- Two approaches were considered:
    - Render the originating page again with an error/success message.
    - Render a generic message page and pass the required message through Jinja.

### Decision
- A single reusable message.html template will be used for displaying all informational, success, and error messages.
- Controllers will render message.html by passing the appropriate message (and optionally a title and navigation link).

### Reason
- Produces a simple and consistent flow throughout the application.

### Impact
- All user-facing messages follow a uniform presentation.
- Implementation becomes simple.

### Alternatives Considered
- Re-render the originating page with inline validation or status messages (the approach commonly used in production web applications).

---

## Decision 14: Common Layout for Role-Specific Pages

### Info
- Date : June 29, 2026 to June 30, 2026
- Status : Current

### Context
- Each role (`admin`, `staff`, and `trekker`) consists of multiple pages such as dashboard, management pages, forms, and detail pages.
- Two approaches were considered:
    - Each page has its own independent layout.
    - All pages belonging to the same role share a common layout, with only the main content changing.

### Decision
- All pages belonging to a particular role will use a common layout.
- The layout will contain:
    - Left Navigation Bar
    - Top Navigation Bar
    - Main Content Area
- Only the Main Content Area will differ between pages.

### Reason
- Provides a consistent user interface throughout the application.
- Clearly separates common UI components from page-specific content.

### Impact
- Every role will have a reusable base template (for example, `admin_base.html`, `staff_base.html`, and `trekker_base.html`).
- Eliminates duplication by reusing the same layout across multiple templates.
- Reduces maintenance effort and keeps the template structure organized.

### Alternatives Considered
1. Design 1
    - Create a separate layout for every page.
2. Design 2
    - Display navigation only on the dashboard and require navigation using browser history or
    page links.

---

## Decision 15: Replacing `username` with `name` in `User` table and Email-Based Authentication

### Info
- Date : June 29, 2026 to June 30, 2026
- Status : Current

### Context
- The `username` and `email` was kept unique and non-nullable, with the idea to use either of them or both for login.


### Decision
- `username` attribute will be removed, and `name` attribute will be added with non-nullable and non-unique constraints.
- Authentication will be performed using the `email` address only.

### Reason
- There may be multiple users with the same name.
- Having `username` and no `name` will prevent from getting the actual name of user.
- Email  are unique and natural way to authenticate.

### Impact
- Login page will ask for:
    - Email
    - Password
- Registration pages will ask for:
    - Name
    - Email
    - Password
    - Phone Number

### Alternatives Considered
- Use a unique `username` for authentication while storing `name` separately.
- Allow authentication using either `username` or `email` or both.

--- 

## Decision 16: Add `amount` attribute to `Trek` table.

### Info
- Date : June 29, 2026 to June 30, 2026
- Status : Current

### Context 
- The booking process asks `trekker` to make the payment, but there is no amount associated with trek till now.

### Decision
- The `Trek` table will contain a `amount` attribute representing the booking price of the trek.

### Reason
- The project team suggested the student to have `payment_status` in the `Booking` table.
- So there must be amount to pay for.

### Impact
- The application is now more closer to real-world scenario.

### Alternatives Considered
1. Does not store the `amount` in `Trek` table, and the `trekker` perform payment process as dummy process (Current Design).

--- 

## Decision 17 : Dummy Payment Workflow

### Info
- Date : June 29, 2026 to June 30, 2026
- Status : Current

### Context
- The project requires a booking workflow involving payment.

### Decision
- A dummy payment page will be implemented to demonstrate the payment flow.
- Clicking the "Pay Now" button will simulate a successful payment and continue the booking workflow.

### Reason
- Demonstrates the complete booking lifecycle.
- Avoids all the hassle of multiple condition and verification on input that is usually done in payment page.
- Integrating a real payment gateway is outside the scope of the project.

### Impact
- Keeps the implementation simple.

### Alternatives Considered
1. Design 1
    - Integrate a real payment gateway.
2. Design 2
    - Skip the payment step entirely.

---

## Decision 18 : Trek Dates Stored as `Date`, Not `DateTime`

### Info
- Date : July 5, 2026
- Status : Current

### Context
- `Trek.start_date` and `Trek.end_date` were originally defined using 
  `DateTime()`, which stores both a date and a time component.
- A trek's start and end are only ever meaningful as calendar dates; 
  no part of the application reads or uses a time-of-day component 
  for these fields.

### Decision
- `Trek.start_date` and `Trek.end_date` will use `Date()` instead of 
  `DateTime()`.

### Reason
- Matches the actual meaning of the data: a trek starts and ends on 
  a date, not at a specific moment in time.
- Avoids carrying an unused, always-midnight time component.
- Simplifies date comparisons (e.g. determining trek status) and form 
  handling, since HTML date inputs submit plain `YYYY-MM-DD` strings.

### Impact
- `Booking.booking_date` is unaffected and remains a `DateTime()`, 
  since a booking's exact timestamp is meaningful for ordering.

### Alternatives Considered
- Keep `DateTime()` and always store midnight as the time component 
  (original design).

--- 

## Decision 19 : Trek Status Recomputed on Fetch, Not Fixed at Creation

### Info
- Date : July 5, 2026
- Status : **Superseded by Decision 26** (trek status is now manually 
  controlled by Trek Staff, not auto-computed from dates). Kept below 
  for historical record of the original design.

### Context
- `Trek.status` should reflect `upcoming`, `ongoing`, or `completed` 
  automatically, based on the trek's dates relative to the current 
  date, except when a trek has been explicitly `cancelled`.
- Nothing in the application updates dates on its own; something has 
  to actively recompute status when it matters.

### Decision
- A shared function, `refresh_trek_status(trek)` (in `utilities.py`), 
  recalculates a trek's status from its `start_date`/`end_date` 
  whenever a trek is fetched for display or editing. It leaves the 
  status untouched if the trek is already `cancelled`. It does not 
  commit to the database itself; the calling route is responsible for 
  persisting the change.

### Reason
- The project has no background job/scheduler infrastructure, so 
  status cannot update automatically at midnight or on a schedule.
- Recomputing on every fetch is a reasonable middle ground: simple to 
  implement, and correct as long as a trek is viewed reasonably 
  regularly.

### Impact
- Every route that fetches a `Trek` for display (list, detail, edit) 
  must call `refresh_trek_status()` and commit, or the trek's status 
  may be stale until it is next viewed.

### Alternatives Considered
1. Design 1
   - Store status as a computed Python property on the `Trek` model, 
     never persisted as a column at all.
2. Design 2
   - Use a scheduled background task to update all trek statuses 
     periodically (rejected as unnecessary infrastructure for this 
     project's scope).

---
## Decision 20 : Trek Deletion Allowed Unless Active Bookings Exist

### Info
- Date : July 5, 2026
- Status : Current

### Context
- Deleting a `Trek` also affects related `Booking` and 
  `StaffTrekAssignment` records (per Decision 3, cascading is handled 
  in business logic, not the database).
- A trek that has been actually used will almost always have some 
  `completed` bookings, so blocking deletion whenever any booking 
  exists at all would make deletion effectively unusable for treks 
  that have already run.

### Decision
- Deleting a trek is blocked only if it has bookings with 
  `booking_status` in `initiated`, `pending`, or `booked` (i.e. an 
  active booking a trekker is currently relying on).
- If no active bookings exist, deleting the trek also deletes its 
  remaining (`completed`/`cancelled`) bookings and any 
  `StaffTrekAssignment` records, in that order.

### Reason
- Protects trekkers with a genuine, currently-relied-upon booking.
- Keeps trek deletion usable in practice, rather than being blocked 
  indefinitely by routine historical data.

### Impact
- A trekker's booking history for a deleted trek is not preserved 
  once the trek itself is deleted.

### Alternatives Considered
1. Design 1
   - Block deletion if any booking exists at all, regardless of 
     status (rejected: makes deletion impractical for used treks).
2. Design 2
   - Allow deletion unconditionally, cascading all related records 
     without checking booking status (rejected: could silently 
     remove a trekker's active, paid booking).

---
## Decision 21 : Deferred `joining_date` Attribute on `User` Table

### Info
- Date : July 6, 2026
- Status : Deferred

### Context
- Considered adding a `joining_date` attribute to the `User` table, 
  to record when a user (trekker or staff) originally registered.
- Registration, seeding, and several list/detail pages were already 
  built by this point without this field.

### Decision
- Not adding `joining_date` for now.

### Reason
- Adding it at this stage would require updating registration logic, 
  the seed script, and any user-facing pages that would display it, 
  for a field that isn't required by the project statement and isn't 
  blocking any core milestone.

### Impact
- None currently. If added later, existing users would need a 
  default/backfilled value, since the column would be new on an 
  already-populated table.

### Alternatives Considered
- Add `joining_date` now, accepting the rework needed across 
  registration, seeding, and templates (rejected for this stage).

---

## Decision 22 : Deferred Splitting `booking_status = 'cancelled'` 

### Info
- Date : July 6, 2026
- Status : Deferred

### Context
- A single 'cancelled' value in booking_status doesn't distinguish 
  why or by whom a booking was cancelled (trekker cancelling 
  themselves, admin rejecting a pending request, admin cancelling an 
  already-approved booking).
- Considered splitting this into 'admin_rejected', 'admin_cancelled', 
  and 'trekker_cancelled' for clearer history.

### Decision
- Not implementing this split for now.

### Reason
- The database design and most business logic were already 
  finalized by the time this was considered. The change would touch 
  the Enum definition, every route checking booking_status, the 
  status_order sorting logic on multiple pages, and the seed script — 
  a large, disruptive change for a refinement rather than a required 
  feature.

### Impact
- Cancelled bookings do not currently record who cancelled them or 
  why, beyond what's implied by which route was called at the time.

### Alternatives Considered
- Implement the three-value split now (rejected: too disruptive at 
  this stage).

  --- 

## Decision 23 : Trek Participants Shown on Trek Detail Page, Not a Separate Route

### Info
- Date : July 7, 2026
- Status : Current

### Context
- The routes doc originally specified a separate 
  `/staff/treks/<trek_id>/participants` route for staff to view 
  trekkers registered for their assigned trek.
- The Admin Trek Detail page already shows both assigned staff and 
  bookings for that trek on one page, without needing separate routes.

### Decision
- Trek participants for a staff member's assigned trek will be shown 
  directly on `staff_treks_view` (the trek detail page), not as a 
  separate route/page.

### Reason
- Consistent with the existing Admin Trek Detail pattern.
- Avoids an extra click for information a staff member would 
  naturally want to see alongside the trek's own details.
- The routes doc only specifies read-only viewing, with no indication 
  participants need their own filtering or actions that would justify 
  a separate page.

### Impact
- `GET /staff/treks/<trek_id>/participants` is dropped from 
  02-routes.md; no `staff_treks_trekkers` route/template needed.

### Alternatives Considered
- Keep the separate route and template as originally planned 
  (rejected: redundant given the merged detail-page pattern already 
  used elsewhere).

---

## Decision 24 : Added `'cancelled'` to `Booking.payment_status`

### Info
- Date : July 7, 2026
- Status : **Superseded by Decision 25** (booking and payment are now 
  merged into a single step, so a booking is never created before 
  payment succeeds — the "cancelled before any payment was made" case 
  this decision addressed can no longer occur, and `payment_status` 
  has been simplified back to two values: `paid`/`refunded`). Kept 
  below for historical record.

### Context
- A booking can be cancelled before any payment was made 
  (booking_status = 'initiated', payment_status = 'pending'). The 
  existing payment_status values ('pending', 'paid', 'refunded') have 
  no accurate value for this case — 'refunded' implies money was 
  returned, which is false if no payment was ever made.

### Decision
- Added 'cancelled' as a fourth value for payment_status, used 
  specifically when a booking is cancelled while payment_status was 
  still 'pending'.

### Reason
- 'refunded' would be factually incorrect for a booking that was 
  cancelled before any payment occurred.

### Impact
- payment_status is now: pending, paid, refunded, cancelled.
- trekker_treks_cancel sets payment_status = 'cancelled' if it was 
  'pending', or 'refunded' if it was 'paid'.

### Alternatives Considered
- Use 'refunded' for both cases regardless of whether payment was 
  actually made (rejected: factually inaccurate).

---

## Decision 25 : Booking and Payment Merged Into a Single Step; `initiated` State Removed

### Info
- Date : July 8, 2026
- Status : Current
- Supersedes: Decision 6, Decision 24.

### Context
- The original design (Decision 6) created a `Booking` row immediately 
  when a trekker clicked "Book Now", with `booking_status = 'initiated'` 
  and `payment_status = 'pending'`, then redirected to a separate 
  payment page. Only after payment did the row become 
  `booking_status = 'pending'`, `payment_status = 'paid'`.
- This caused real problems in practice:
  - An `'initiated'` booking already decremented `available_slots`, 
    even though no payment had been made — a trekker who abandoned 
    the payment step still occupied a slot.
  - Treks could show as unavailable (slots exhausted) despite no 
    actual payment ever being completed.
  - The `'initiated'` state existed purely to represent an incomplete 
    transaction, adding a state, a route, and a template for no 
    functional benefit.
  - Decision 24 (adding `payment_status = 'cancelled'`) existed only 
    to handle cancelling a booking in this incomplete `'initiated'` 
    state — once that state is removed, the problem it solved no 
    longer exists.

### Decision
- Booking and payment are merged into a single trekker-facing action.
- The trek booking form (`trekker_treks_book`, GET) directly collects 
  dummy card details alongside a summary of the trek — there is no 
  separate `trekker_treks_payment` route or page anymore.
- On successful form submission (`trekker_treks_book`, POST):
  - card fields are checked only for presence (dummy payment, per 
    Decision 17), not real validation,
  - a `Booking` row is created directly with `booking_status = 
    'pending'` and `payment_status = 'paid'`,
  - `available_slots` is decremented at this point, not earlier.
- No `Booking` row is ever created before payment succeeds. There is 
  no representation of an abandoned/incomplete booking attempt in the 
  database at all.
- `booking_status` is reduced to four values: `pending`, `booked`, 
  `completed`, `cancelled`. `'initiated'` is removed.
- `payment_status` is reduced to two values: `paid`, `refunded`. 
  `'pending'` and `'cancelled'` (from Decision 24) are removed, since 
  a booking is never created while payment is outstanding.

### Reason
- Every `Booking` row now represents a real, paid reservation — there 
  is no window where a slot is held without payment.
- Removes an entire state, its associated route/template, and the 
  bookkeeping needed to handle abandoned `'initiated'` rows.
- `admin_bookings_approve`/`reject` still operate on `'pending'` 
  bookings exactly as before (Decision 6's approval workflow, i.e. 
  `pending → booked`, is unchanged) — only the pre-payment part of 
  the lifecycle was removed.

### Impact
- `trekker_treks_payment` route and its template no longer exist.
- `models.py`: `Booking.booking_status` Enum is now 
  `('pending', 'booked', 'cancelled', 'completed')`; 
  `Booking.payment_status` Enum is now `('paid', 'refunded')`.
- `seed.py` updated to only generate bookings in these four/two 
  states, consistent with the new lifecycle.
- Any code that previously checked `booking_status == 'initiated'` or 
  `payment_status == 'pending'`/`'cancelled'` is dead logic and has 
  been removed.

### Alternatives Considered
1. Keep the two-step flow but auto-expire/clean up abandoned 
   `'initiated'` bookings after a timeout (rejected: needs background 
   job infrastructure the project doesn't otherwise use).
2. Keep the two-step flow, but don't decrement `available_slots` 
   until payment succeeds (rejected: still leaves an unnecessary 
   extra state and route for no real benefit, given this is a dummy 
   payment system with no real gateway latency to justify a separate 
   step).

---

## Decision 26 : Trek Status Manually Controlled by Trek Staff, Not Auto-Computed

### Info
- Date : July 8, 2026
- Status : Current
- Supersedes: Decision 19.

### Context
- Decision 19 recomputed `Trek.status` automatically from 
  `start_date`/`end_date` whenever a trek was fetched, with 
  `'cancelled'` as the only manually-set value.
- The Project Statement's Core Features section describes Trek Staff 
  as able to "mark trek as started/completed" — language that reads 
  as a deliberate staff action, not a background computation. The 
  Milestone doc separately lists "Update trek status (Open/Closed)" 
  and "Mark treks as started/ongoing/completed" the same way.
- Automatic recomputation also had a real weakness: status could go 
  stale until a trek happened to be fetched again, since the project 
  has no scheduler.

### Decision
- `upcoming`, `ongoing`, and `completed` are now all staff-triggered 
  actions, not automatic. `start_date`/`end_date` remain as *guards* 
  on when a transition is permitted, but nothing changes `Trek.status` 
  automatically anymore.
- Full transition table:

| From | To | Who | Guard |
|------------|-------------|----------------|--------------------------------------------|
| upcoming | ongoing | Staff | Blocked if `today < start_date` |
| ongoing | completed | Staff | none |
| ongoing | cancelled | Staff or Admin | Blocked if `today > end_date` |
| upcoming | cancelled | Admin only | none |
| upcoming | completed | — | Never allowed (must pass through `ongoing`) |
| any | cancelled | — | Blocked once `today > end_date`, regardless of who |

- `refresh_trek_status()` (introduced in Decision 19) is removed from 
  `utilities.py`, along with every call site.

### Reason
- Matches the project's own wording of staff "marking" a trek's phase, 
  rather than the system inferring it.
- Removes a real correctness gap (staleness) by removing the need for 
  automatic computation entirely, rather than trying to patch it with 
  scheduler infrastructure out of scope for this project.
- Admin retaining cancel power (in addition to staff) reflects that 
  cancellation is a policy-level decision (e.g. low bookings, permit 
  issues) that doesn't require physical presence at the trek, unlike 
  starting/completing a trek, which only staff on the ground can 
  meaningfully attest to.

### Impact
- `staff_treks_update` supports three transitions: `upcoming → 
  ongoing`, `ongoing → completed`, `ongoing → cancelled`.
- A new admin-only route is added for cancelling a trek from either 
  `upcoming` or `ongoing` (see Decision 27).
- `admin_treks_edit` gains a new restriction (see Decision 28).
- No safety net exists if staff is late to act — see Decision 29.

### Alternatives Considered
1. Keep automatic computation for `upcoming → ongoing`, and only add 
   manual staff control for `completed`/`cancelled` (rejected: still 
   doesn't match the "mark as started" wording, and keeps the 
   staleness weakness for the one transition being kept automatic).
2. Add a real scheduler/background job to keep automatic computation 
   accurate (rejected: infrastructure out of scope for this project).

---

## Decision 27 : Cancellation and Completion Cascades on Bookings

### Info
- Date : July 8, 2026
- Status : Current

### Context
- Under Decision 26, a trek's status can now be set to `cancelled` or 
  `completed` by staff (or, for cancellation, by admin). Existing 
  bookings on that trek need a consistent, defined outcome when this 
  happens.

### Decision
- **When a trek becomes `cancelled`** (by staff or admin, from either 
  `upcoming` or `ongoing`): every booking on that trek with 
  `booking_status` in (`pending`, `booked`) is set to 
  `booking_status = 'cancelled'`, `payment_status = 'refunded'` 
  (since, under Decision 25, every existing booking was already paid).
- **When a trek becomes `completed`** (staff only, from `ongoing`): 
  every booking with `booking_status == 'booked'` is set to 
  `booking_status = 'completed'`.
- A booking added a new admin-only route for cancelling a trek 
  directly (`POST /admin/treks/<trek_id>/cancel`), applying the same 
  cancellation cascade described above, and enforcing the same guard 
  as staff's cancel action (blocked once `today > end_date`).

### Reason
- Keeps `Booking.booking_status` synchronized with the trek's own 
  status change, rather than leaving stale `pending`/`booked` rows on 
  a trek that no longer exists in an active state.
- Refunding on cancellation is correct and unambiguous now that every 
  booking is guaranteed paid (Decision 25 removed the unpaid case 
  entirely).

### Impact
- `staff_treks_update` and the new admin cancel-trek route share this 
  cascade logic.
- `02-routes.md` needs the new admin cancel-trek route added.

### Alternatives Considered
- Leave existing bookings untouched when a trek's status changes, 
  requiring a separate manual step to resolve them (rejected: leaves 
  the database in an inconsistent state with no forcing function to 
  fix it).

---

## Decision 28 : Admin Cannot Edit a Trek Once It Leaves `'upcoming'`

### Info
- Date : July 8, 2026
- Status : Current

### Context
- `admin_treks_edit` previously had no restriction based on 
  `Trek.status` — only a guard preventing `total_slots` from being 
  reduced below the number of already-booked slots.
- Under Decision 26, `Trek.status` is now the authoritative signal for 
  what phase a trek is in.

### Decision
- `admin_treks_edit` (both the GET form and the POST submission) is 
  blocked entirely once `Trek.status != 'upcoming'`.

### Reason
- Once a trek is `ongoing`, `completed`, or `cancelled`, retroactively 
  changing its name, location, difficulty, dates, or amount would be 
  editing details trekkers already booked and paid against.
- Gating on `Trek.status` (rather than comparing `today` against 
  `start_date`) keeps a single, consistent source of truth for "what 
  phase is this trek in," matching Decision 26 and Decision 29 (no 
  date-based booking cutoff either) rather than introducing a second, 
  date-based rule just for this one route.

### Impact
- A trek can still be edited while `'upcoming'`, even past its actual 
  `start_date`, if staff hasn't yet clicked "Start Trek" — consistent 
  with treating `status`, not raw dates, as authoritative everywhere.

### Alternatives Considered
- Block editing based on `today >= start_date` instead of 
  `Trek.status` (rejected: introduces a second, inconsistent 
  authority for "has this trek started" alongside Decision 26's 
  status-based model).

---

## Decision 29 : No Date-Based Safety Net for Trekker Booking

### Info
- Date : July 8, 2026
- Status : Current

### Context
- Under Decision 26, `Trek.status` no longer changes automatically. If 
  Trek Staff is late to mark a trek `'ongoing'`, the trek could 
  technically remain `'upcoming'` past its real `start_date`.
- A question arose: should trekker booking additionally check 
  `today < start_date` as a safety net, blocking bookings on a trek 
  whose start date has passed even if staff hasn't updated its status 
  yet?

### Decision
- No additional date-based check is added. Trekker booking 
  (`trekker_treks_book`, and visibility on `trekker_treks_page`/
  `trekker_dashboard`) is gated purely on `Trek.status == 'upcoming'`.

### Reason
- Keeps a single, consistent authority (`Trek.status`) for "is this 
  trek bookable," matching Decision 26 and Decision 28, rather than 
  half-automating one specific path with a second, date-based rule.
- Trek Staff is assumed to act diligently and mark a trek `'ongoing'` 
  promptly once it starts.

### Impact
- Accepted, known risk: if staff is late to act, a trek could remain 
  bookable past its actual start date. This is a deliberate 
  simplification, not an oversight.

### Alternatives Considered
- Block booking once `today >= start_date`, regardless of 
  `Trek.status` (rejected: introduces a second, date-based authority 
  alongside `Trek.status`, contradicting Decision 26's single-source- 
  of-truth model).

---

## Decision 30 : Admin Given Full Trek-Status Power (Not Cancel-Only)

### Info
- Date : July 7-11, 2026
- Status : Current
- Supersedes: the earlier "admin: cancel only" scoping discussed
  during the trek-status-workflow redesign.

### Context
- When designing manual trek-status control (Decision 26), the
  initial plan was for Admin to hold cancel-only power, on the
  reasoning that starting/completing a trek are ground-truth facts
  only physically-present Trek Staff can honestly attest to.
- On reflection, this was reconsidered: the admin is the owner of the
  business, and structurally excluding them from any operational
  lever — even one they'd normally defer to staff for in practice —
  was judged too restrictive.

### Decision
- Admin now holds the full set of trek-status actions: mark
  `ongoing`, mark `completed`, and cancel — the same three actions
  Trek Staff has, each as its own dedicated POST route
  (`admin_treks_ongoing`, `admin_treks_completed`,
  `admin_treks_cancelled`), mirroring Staff's route shape exactly.
- All the same guards apply to Admin's routes as to Staff's: `ongoing`
  blocked if `today < start_date`; `completed` only reachable from
  `ongoing`; cancellation blocked once `today > end_date`.
- The one retained asymmetry: Admin's cancel scope is wider than
  Staff's — Admin can cancel from EITHER `upcoming` or `ongoing`,
  while Staff can only cancel from `ongoing` (see Decision 31).

### Reason
- An owner should not be structurally locked out of any lever, even
  if they would normally defer to on-ground staff in practice.
- This is purely additive — Trek Staff's own routes and powers are
  completely unchanged.

### Impact
- Three new admin routes added; no changes to Staff's existing
  routes.
- `invariants.md`'s Trek section updated to reflect Admin as a valid
  actor for all three status transitions, not just cancellation.

### Alternatives Considered
- Keep Admin cancel-only, as originally planned (rejected: judged
  overly restrictive for the actual business owner of the
  application).

---

## Decision 31 : Trek Staff's Cancel Power Restricted to `ongoing` Only

### Info
- Date : July 7-11, 2026
- Status : Current

### Context
- Following Decision 30, it was worth explicitly settling why Trek
  Staff's cancel scope should NOT also extend to `upcoming`, even
  though Admin's does.

### Decision
- Trek Staff can only cancel a trek while its status is `ongoing`.
  Staff cannot cancel an `upcoming` trek at all — that action belongs
  to Admin only.

### Reason
- Staff's cancel power exists specifically to handle ground
  emergencies (accidents, dangerous weather, unsafe terrain) — by
  definition, these only arise once a trek is actually underway.
- Cancelling a trek before it starts is a business/administrative
  decision (low bookings, permit denial, insufficient staff) that
  doesn't require ground presence, and is Admin's call, not Staff's.

### Impact
- `staff_treks_cancelled` explicitly rejects `trek.status ==
  'upcoming'` with an error, even though the trek-level invariant
  otherwise permits cancellation from either state depending on actor.

### Alternatives Considered
- Give Staff the same wide cancel scope as Admin (rejected: staff has
  no operational role at all before a trek starts, so pre-start
  cancellation power for staff would be functionally meaningless and
  inconsistent with why staff has cancel power in the first place).

---

## Decision 32 : Booking and Payment Merged Into a Single Step (Final)

### Info
- Date : July 7-11, 2026
- Status : Current
- Supersedes: the original two-step booking/payment design and any
  intermediate 4-value `payment_status` decisions made while that
  two-step design was still assumed.

### Context
- The original design created a `Booking` row immediately when a
  trekker clicked "Book Now" (`booking_status = 'initiated'`,
  `payment_status = 'pending'`), then redirected to a separate payment
  page. Only on successful payment did the row become `'pending'`/
  `'paid'`.
- This caused real problems: an `'initiated'` booking already
  decremented `available_slots`, even though no payment had been made
  — a trekker who abandoned the payment step still occupied a slot,
  and treks could appear unavailable despite no completed payment
  ever existing.

### Decision
- Booking and payment are merged into one trekker-facing action. The
  trek booking page (`trekker_treks_book`, GET) shows trek details
  alongside a dummy card-payment form on ONE page. POST checks card
  fields for presence only (dummy payment, no real gateway), then
  creates the `Booking` row directly with `booking_status = 'pending'`,
  `payment_status = 'paid'`, decrementing `available_slots` at this
  point.
- No `Booking` row is ever created before payment succeeds.
- `booking_status` is reduced to 4 values: `pending`, `booked`,
  `cancelled`, `completed`. `'initiated'` is removed.
- `payment_status` is reduced to 2 values: `paid`, `refunded`. Any
  earlier plan to add a `'pending'` or `'cancelled'` value to
  `payment_status` is moot, since a booking can no longer exist in an
  unpaid state at all.

### Reason
- Every `Booking` row now represents a real, paid reservation — no
  window exists where a slot is held without payment.
- Removes an entire state, its associated route (`trekker_treks_
  payment`), and its template, along with all the bookkeeping needed
  to handle abandoned `'initiated'` rows.
- The existing admin approval workflow (`pending → booked`) is
  completely unchanged — only the pre-payment part of the lifecycle
  was removed.

### Impact
- `trekker_treks_payment` route and template no longer exist.
- `models.py` updated: `Booking.booking_status` Enum is
  `('pending', 'booked', 'cancelled', 'completed')`;
  `Booking.payment_status` Enum is `('paid', 'refunded')`.
- `seed.py` updated to only generate bookings in these states.

### Alternatives Considered
- Keep the two-step flow but auto-expire abandoned `'initiated'`
  bookings after a timeout (rejected: needs background-job
  infrastructure out of scope for this project).
- Keep the two-step flow but delay decrementing `available_slots`
  until payment succeeds (rejected: still leaves an unnecessary extra
  state and route for a dummy payment system with no real gateway
  latency to justify a separate step).

---

## Decision 33 : Admin Search — Both a Dedicated Page AND Inline Filters

### Info
- Date : July 7-11, 2026
- Status : Current

### Context
- `02-routes.md` originally specified a single dedicated
  `GET /admin/search` page (with `type`/`field`/`q` query parameters)
  as the sole way to search treks/staff/trekkers by name or ID. It was
  worth reconsidering whether the four existing admin list pages
  (Treks/Staff/Trekkers/Bookings) should ALSO have their own inline
  filter forms, given the trekker side of the app already used inline
  query-parameter filtering on its own list pages.

### Decision
- Both were built: the single dedicated `/admin/search` page (matching
  the original route design, searching across all three entity types
  from one place), AND inline filter forms directly on each of the
  four admin list pages.

### Reason
- The dedicated search page matches the milestone requirement's
  phrasing ("search treks, staff, or users by name or ID") as one
  unified capability.
- Inline filters on each list page let admin narrow down what they're
  already looking at without navigating away, which the dedicated page
  alone doesn't offer.

### Impact
- No route conflicts — the dedicated search page and each list page's
  inline filters are independent, additive features.

### Alternatives Considered
- Only the dedicated search page (rejected: doesn't let admin filter
  a list page they're already viewing without navigating away).

---

## Decision 34 : Admin Summary Charts Built with Matplotlib, Saved as Plain Files

### Info
- Date : July 7-11, 2026
- Status : Current

### Context
- The Admin Summary/Analytics page needed charts. The Milestone doc
  names Chart.js as a suggested (optional) library, which would
  require JavaScript. Given the project's broader preference for
  avoiding JS wherever not strictly required, and the need to be able
  to explain every part of the implementation clearly in the viva, an
  alternative was chosen.

### Decision
- All 6 summary charts are generated server-side with matplotlib.
  Each chart-drawing function saves its output as a plain `.png` file
  to a fixed path inside `static/charts/` (e.g.
  `static/charts/top_treks.png`), overwriting the same file every time
  the summary page is loaded. The template displays each chart with a
  completely ordinary `<img src="{{ url_for('static', filename=
  'charts/top_treks.png') }}">` tag — no JavaScript, no base64
  encoding, no in-memory tricks.

### Reason
- This keeps the mechanism trivial to explain in a viva: "matplotlib
  draws the chart and saves it as a picture file; the page just shows
  that picture, and the file gets redrawn fresh every time the page
  loads."
- Avoids JS entirely, consistent with the project's broader
  preference for plain, well-understood HTML/CSS/Python wherever
  possible.

### Impact
- `application/charts.py` added, with one function per chart. Each
  uses `matplotlib.use("Agg")` (required — Flask has no display/GUI)
  and calls `plt.close(fig)` after saving, to avoid a memory leak
  across repeated page loads.
- `static/charts/` must exist (or be created) before first use.

### Alternatives Considered
- Chart.js (rejected: introduces JavaScript, and is harder to walk an
  examiner through live compared to "a Python function draws a picture
  and saves it").
- In-memory base64-encoded images, avoiding any file writes to disk
  (rejected after initial implementation: harder to explain in a viva
  than simply saving and referencing a plain image file).

---

## Decision 35 : `Booking.additional_info` removed

### Info
- Date : July 7-11, 2026
- Status : Current

### Context
- Earlier drafts of `models.py` during this project included a
  `Booking.additional_info` column. 
- The final schema reviewed at the end of this development phase does not include it.

### Decision
- `additional_info` column from `Booking` table have been removed.

### Reason
- No need of this attribute was felt during development of application.

### Impact
- `Booking` table does not have `additional_info` attribute in the final database schema.

---