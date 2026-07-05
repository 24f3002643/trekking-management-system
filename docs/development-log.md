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

## July 1, 2026 to July 5, 2026

### Work Decisions
1. The base layout (top navigation, left navigation, main section, 
   bottom navigation) would be designed first as plain CSS flexbox, 
   not Bootstrap's grid system, since the grid system fought against 
   a fixed-region, single-scrollable-area layout.
2. Authentication and Role Management would be implemented before 
   continuing with admin views and business logic, since almost every 
   subsequent route depends on knowing who is logged in and what role 
   they have.
3. Controllers would be split by role, and further split per-domain 
   within admin (treks, staff, trekkers, bookings, search, summary), 
   using Flask Blueprints, to keep route files manageable as the 
   number of routes grew.
4. Templates would be organized into role-specific subfolders 
   (`templates/admin/`, `templates/staff/`, `templates/trekker/`), 
   mirroring the controller structure, so templates belonging to a 
   role are easy to locate as the number of pages grows. Shared 
   templates (`base.html`, `base_layout.html`, `base_auth.html`, 
   login/register pages) remain at the top level of `templates/`.
5. For each page, the template would be designed first (with dummy 
   data), followed immediately by its real business logic, rather 
   than batching all templates first or all business logic first.

### Work Completed
1. Designed and implemented `base_layout.html`: a flexbox skeleton 
   with fixed-height top navigation and bottom navigation, a 
   fixed-width sidebar, and a scrollable main content area.
2. Designed `base_admin.html`, extending `base_layout.html`, 
   containing the sidebar links and top navigation links common to 
   every admin page.
3. Implemented plain Flask session-based authentication: `login()`, 
   `logout()`, `register_trekker()`, and `register_staff()`, using 
   `werkzeug.security` for password hashing.
4. Implemented two reusable access-control decorators in 
   `decorators.py`:
   - `login_required`, which checks for a valid, non-blacklisted 
     session, used only by `home()`.
   - `role_required(role)`, which additionally checks the logged-in 
     user's role, used by every role-specific route.
5. Migrated all routes from a single flat `controllers.py` file to 
   Flask Blueprints, split across `application/controllers/`, one 
   file per role (`auth.py`, `staff.py`, `trekker.py`) and further 
   split per-domain within admin (`admin.py`, `admin_treks.py`, 
   `admin_bp.py`).
6. Implemented the Admin Dashboard: summary stat cards (total treks, 
   staff, trekkers, bookings) and a scrollable preview of recent 
   bookings with approve/cancel actions.
7. Implemented full CRUD for Treks (Admin): list, view details, 
   create, edit, and delete, including:
   - A shared `refresh_trek_status()` utility that recalculates a 
     trek's status from its start/end dates, leaving cancelled treks 
     untouched.
   - Validation on create/edit: trek name uniqueness, start date 
     before end date, and available slots never going negative when 
     total slots is reduced.
   - Deletion blocked if the trek has any active (initiated, pending, 
     or booked) bookings; otherwise, historical bookings and staff 
     assignments are cleaned up alongside the trek.
8. Added two reusable Jinja macros in `_macros.html`:
   - `stat_card(title, value, icon)`, for the summary cards used on 
     dashboard-style pages.
   - `detail_item(label, value)`, for the labeled key-value rows used 
     on detail pages (e.g. Trek Detail).
9. Added a seed script (`seed.py`) to generate dummy trekkers, staff, 
   treks, and bookings, plus realistic staff-to-trek assignments 
   respecting the no-overlapping-treks invariant, for local testing.
10. Added routes for `POST /logout` and `GET /admin/summary` to 
    `02-routes.md`, and added Staff page details to `03-views-and-flows.md`.

### Decisions Made
1. `Trek.start_date` and `Trek.end_date` changed from `DateTime()` to 
   `Date()`, since these fields only ever represent a calendar date.
2. Session data stores only `user_id`; role and blacklist status are 
   re-fetched from the database on every request (via the decorators) 
   rather than trusted from a stale session value, so a mid-session 
   blacklist takes effect immediately.
3. `SECRET_KEY` is loaded from a `.env` file via `python-dotenv`, kept 
   out of version control.
4. List pages (e.g. all treks) use their own reusable CSS pattern 
   (`.list-page-wrapper` / `.list-table-wrapper`) so the table fills 
   whatever space is available, rather than a fixed pixel height; 
   detail pages, which have several distinct sections, do not use 
   this pattern and instead rely on the page's own natural scroll.

### Next Step
1. Continue building out Admin Staff, Trekkers, Bookings, Search, and 
   Summary pages, following the same template-then-logic pattern.

---
