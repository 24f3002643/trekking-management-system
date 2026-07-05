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
- Status : Current

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
- Status : Current

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