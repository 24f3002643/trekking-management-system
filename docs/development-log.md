# Development Log

## June 26, 2026 To June 28, 2026

### Work Completed
1. Finalized the database design.
2. Implemented the SQLAlchemy models for `User`, `Trek`, `Booking`, and `StaffTrekAssignment`.
3. Configured the Flask application.
4. Pre-seeded the admin in the database.


### Decisions Made
1. A single `User` table will be there for `admin`, `staff` and `trekker`.
2. Duplicate bookings in the `Booking` table will be avoided using Business logic, and not via `UNIQUE` constraints.
3. Delete cascade operation for `User` and `Trek` table will be implemented using business logic, and not using database.
4. Decided that a single `trekker` can book only one slot.
5. Changed the values of `status` attribute in `Trek` table from `['pending', 'approved', 'open', 'closed', 'completed']` to `['upcoming', 'ongoing', 'completed', 'cancelled']`.
6. Added `'initiated'` and `'pending'` as two new value for `booking_status` in `Booking` table.
7. Added `total_slots` attribute in `Trek` table.
8. Deleted `duration` attribute in `Trek` table.

### Next Step Decision
1. The database part is complete. The next step is `Authentication and Role Management` and `Creating views for admin, staff, and trekker`.

---

## June 29, 2026

### Work Decisions
1. `Authentication and Role Management` will be completed after completing models, views and controllers.
2. Before designing views, routes will be defined in `02-routes.md`

### Work Completed
1. Designed the public routes for home, login, registration, and dashboards.
2. Designed the routes for the `admin`, `staff` and `trekker`.

### Decisions Made
1. A single login page will be used for all user roles.
2. Separate registration endpoints will be used for `trekker` and `staff`.
3. Staff assignment will be managed from the corresponding trek instead of a separate assignment module.
4. Searching and filtering will be implemented using query parameters on the existing resource routes.

### Next Step
1. Design the views for `admin`, `staff` and `trekker`.

--- 

## June 29, 2026 to June 30, 2026

### Work Decisions
1. Before designing actual view, views and flows will be defined in `-3-views-and-flows.md` to get the idea of what views would be and what will the flow of views.

### Work Completed
1. Formalized the rough idea of views and flow in `03-views-and-flows.md`

### Decisions Made
1. Generic Message Page for displaying messages.
2. Common Layout for Role-Specific Pages.
3. Replacing `username` with `name` in `User` table and Email-Based Authentication.
4. Add `amount` attribute to `Trek` table.
5. Having a dummy payment workflow.


### Next Steps
1. Design the actual for `admin`, `staff` and `trekker`.

---
