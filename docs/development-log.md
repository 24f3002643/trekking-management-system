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

## July 6, 2026

### Work Decisions
1. ### Work Decisions
1. Decided to build Admin Staff, Trekker, and Bookings management 
   (in that order) before Search and Trek Staff Assignment — those 
   three are simpler CRUD + blacklist/action pages, while Search and 
   Staff Assignment need more involved logic.
2. Route-level guard clauses (e.g. "reject only valid while pending") 
   will be applied for state transitions with real alternative states 
   (approve/reject/pending), but skipped for simple boolean toggles 
   (blacklist/unblacklist), since setting an already-`True` boolean 
   to `True` again is harmless, unlike approving an already-rejected 
   registration.

### Work Completed
1. Admin Staff Management: list (grouped by 
   approval_status: pending, approved, rejected; sorted by name 
   within each group), detail (showing treks the staff member is 
   assigned to), pending-approvals queue, and 
   approve/reject/blacklist/unblacklist actions.
2. Admin Trekker Management: list (sorted by name), 
   detail (showing all bookings made by that trekker, sorted by 
   status priority then booking date), and blacklist/unblacklist 
   actions.
3. Every staff/trekker action route checks both that the target 
   `staff_id`/`trekker_id` exists AND that the matching `User` row's 
   `role` is actually `'staff'`/`'trekker'`, since the id comes 
   directly from the URL and could otherwise be pointed at an 
   unrelated user.
4. Added a reusable `.form-narrow` CSS class (`base_layout.html`) so 
   create/edit forms can opt into a narrower width without inline 
   styles or repeating the rule per page.
5. Fixed several bugs surfaced while building these pages:
   - Trek Detail's bookings table had `table-responsive`/
     `list-table-wrapper` applied to it, which collapsed its visible 
     height to zero on a page with multiple stacked sections; removed.
   - The Trek Create/Edit difficulty dropdown's "Moderate" option had 
     `value="medium"`, not matching the model's actual Enum value 
     `'moderate'`.
   - Leftover duplicate route stubs in the old, not-yet-fully-migrated 
     `admin.py`, still registering alongside the real implementation 
     in a newly split file (`admin_staff.py`, `admin_trekker.py`), 
     causing Flask to silently run the stale stub instead of the real 
     route..

### Decisions Made
1. Sidebar highlighting (`active_page`) is set only on a section's 
   list page, not on that section's create/edit/detail pages, so the 
   highlighted state specifically means "viewing the list."
2. Deferred adding a `joining_date` attribute to `User` (see 
   `project-decisions.md`).


### Next Step
1. Implement Admin Bookings (list, detail, approve/cancel).

---

## July 7, 2026 to July 11, 2026

### Work Decisions
1. Booking and payment, previously two separate steps (create booking
   as `initiated`/`pending`, then a separate payment page), were
   merged into a single combined step: the trek booking page shows
   trek details alongside a dummy card-payment form, and a `Booking`
   row is only ever created after that form is submitted. The
   `initiated` booking state was removed entirely, and
   `payment_status` was simplified from a planned 4-value enum back
   down to 2 values (`paid`/`refunded`).
2. Trek status (`upcoming`/`ongoing`/`completed`/`cancelled`) was
   changed from automatic, date-based computation
   (`refresh_trek_status()`) to fully manual control by Trek Staff and
   Admin. This reverses the earlier automatic-recomputation design,
   on the reasoning that the Project Statement's "mark trek as
   started/completed" language implies a deliberate staff action, not
   background computation, and automatic computation had a real
   staleness weakness (status could go stale until a trek happened to
   be re-fetched, since the project has no scheduler).
3. Admin was given the SAME status-change powers as Trek Staff
   (mark ongoing, mark completed, cancel) rather than cancel-only
   power, on the reasoning that the admin, as business owner, should
   not be structurally excluded from any operational lever — even
   though Trek Staff (being physically present) remains the more
   natural authority for confirming a trek has actually started or
   finished. The one retained asymmetry: Trek Staff can only cancel a
   trek while it is `ongoing` (ground emergencies only arise once a
   trek is underway), while Admin can cancel from either `upcoming` or
   `ongoing` (a policy-level decision that doesn't require ground
   presence).
4. No date-based safety net was added for trekker booking — booking
   remains gated purely on `Trek.status == 'upcoming'`, trusting Trek
   Staff to mark a trek `ongoing` promptly. This keeps `status` as the
   single source of truth throughout the system, rather than
   introducing a second, date-based check for one specific path.
5. Trek editing (`admin_treks_edit`) and staff assignment
   (`admin_treks_manage_staff`) were both restricted to only being
   permitted while a trek's status is `upcoming`, for the same
   single-source-of-truth reasoning.
6. Staff-editable slot capacity is `total_slots`, not
   `available_slots` (the latter is a derived bookkeeping value and
   should never be edited directly). The new value must not drop
   below the currently booked count; if it would, the request is
   rejected with a message suggesting cancellation instead of any
   automatic cascade.
7. Admin's Summary/Analytics page was built using matplotlib, saving
   each chart as a plain `.png` file into `static/charts/` (overwritten
   on every page load) rather than any base64/in-memory encoding
   approach, specifically so the mechanism stays simple enough to
   explain in the project viva.
8. Admin search was built as BOTH a single dedicated `/admin/search`
   page (matching the original `02-routes.md` design) AND inline
   filter forms directly on each of the Treks/Staff/Trekkers/Bookings
   list pages, rather than choosing one approach over the other.

### Work Completed
1. Reworked the entire trekker booking flow: `trekker_treks_book`
   (combined trek-details + dummy-payment form), removing the earlier
   separate `trekker_treks_payment` route/template entirely.
2. Split trekker's bookings view into two separate routes/templates:
   `trekker_bookings_page` (active — bookings on `upcoming`/`ongoing`
   treks) and `trekker_bookings_history` (past — bookings on
   `completed`/`cancelled` treks), each with its own filter form.
3. Added trekker profile view and update (`trekker_profile`,
   `trekker_profile_update`), including optional password change with
   current-password verification and new/confirm matching.
4. Implemented the full Trek Staff role from scratch:
   - Dashboard with assigned-treks table (including a per-trek
     registered-trekker count, defined strictly as
     `booking_status == 'booked'`), plus quick-stat cards.
   - Trek list and trek detail (participant list, same `'booked'`-only
     definition).
   - Three dedicated status-change routes (`..._ongoing`,
     `..._completed`, `..._cancelled`), each with its own guard
     conditions per the transition table in `invariants.md`.
   - `staff_treks_slots` for total_slots adjustment.
   - `staff_trekkers_page`, a cross-trek view of every trekker across
     all of a staff member's assigned treks.
   - Staff profile view and update, same shape as trekker's.
5. Implemented Admin's parallel status-change routes
   (`admin_treks_ongoing`, `admin_treks_completed`,
   `admin_treks_cancelled`), and the new `admin_treks_edit` status
   guard.
6. Implemented `admin_treks_manage_staff` (GET/POST): builds a
   three-state staff list (assigned / available / unavailable due to
   date overlap) per trek, with full server-side re-validation on
   POST and all-or-nothing rejection if any newly-added staff member
   fails validation.
7. Implemented `admin_search` and inline filter forms on the four
   admin list pages.
8. Implemented `admin_summary`: 4 stat cards + 6 matplotlib charts
   (Top 10 Popular Treks, Bookings in the Past 7 Days, Pending vs
   Booked, Staff Approval Status, Trekker Blacklist Split, Staff
   Blacklist Split), added `application/charts.py` to house the chart
   -generation functions.
9. Fixed numerous bugs surfaced during this phase across `staff.py`,
   `trekker.py`, `trekker_bookings.py`, and `admin_treks.py` — most
   commonly: `=` used instead of `==` inside `.filter()`/`.join()`
   calls (real Python syntax errors), `.filter_by()` misused with
   `.in_()`, missing `is None` checks before attribute access on a
   query result, duplicate route registrations on the same URL,
   string/int type mismatches on form field values, and missing
   de-duplication when counting distinct trekkers across a one-to-many
   join.
10. Updated `models.py`: `Booking.booking_status` reduced to
    `('pending', 'booked', 'cancelled', 'completed')`; 
    `Booking.payment_status` reduced to `('paid', 'refunded')`.
    `refresh_trek_status()` in `utilities.py` removed (or marked for
    removal), along with every call site.

### Decisions Made
1. `Booking.additional_info` — verify whether this column still
   exists in the current schema; some in-progress drafts included it,
   the final schema reviewed at the end of this phase did not. Needs
   an explicit final check before submission (see Next Steps).
2. Route naming for status-change actions was unified between Staff
   and Admin blueprints (`..._ongoing`, `..._completed`,
   `..._cancelled`), so the same action has matching route-name
   suffixes regardless of which role's blueprint it lives in.

### Next Step
1. Verify whether `/staff/treks/<trek_id>/update` (an older route,
   `staff_treks_update`) is still live/used alongside the newer
   `/staff/treks/<trek_id>/slots` — resolve or remove whichever is
   redundant.
2. Confirm `trekker_treks_book`'s POST explicitly sets
   `booking_status = 'pending'` rather than relying on any column
   default.
3. Final review pass: `03-views-and-flows.md` against the actual final
   templates; confirm `.gitignore` excludes `.venv/`, `instance/`,
   `__pycache__/`, `.env`; run through the manual testing checklist
   end-to-end; final commit and push.

---
