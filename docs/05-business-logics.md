# Business Logics
Plain-English logic for every route in the application, matching
`02-routes.md` one-to-one.

---

## Auth Routes

### `home`
1. Get the user id from the session.
2. Fetch the user.
3. Redirect based on role: `admin` → admin dashboard, `staff` → staff
   dashboard, `trekker` → trekker dashboard.

### `login`
**GET:** Render the login form.

**POST:**
1. Read email and password from the form.
2. Fetch the User by email. If not found, or if the password doesn't
   match the stored hash, show an "invalid login" error.
3. If `role == 'staff'`:
   - If `approval_status == 'pending'`, show a "registration pending"
     message.
   - If `approval_status == 'rejected'`, show a "registration
     rejected" message.
   - If `approval_status == 'approved'` and `is_blacklisted`, show a
     "blacklisted" message.
   - Otherwise, log in and redirect to the staff dashboard.
4. If `role == 'trekker'`:
   - If `is_blacklisted`, show a "blacklisted" message.
   - Otherwise, log in and redirect to the trekker dashboard.
5. If `role == 'admin'`, log in and redirect to the admin dashboard
   (admin has no approval/blacklist checks — always allowed to log in
   if credentials match).
6. On successful login, store only `user_id` in the session (role and
   blacklist status are re-checked fresh from the database on every
   subsequent request, via the decorators, rather than trusted from
   the session).

### `logout`
1. Clear the session.
2. Redirect to `/login`.

### `register_trekker`
**GET:** Render the trekker registration form.

**POST:**
1. Read name, email, password, phone_number from the form.
2. If a user with this email already exists, show an error.
3. If a user with this phone_number already exists, show an error.
4. Hash the password. Create a new User with `role = 'trekker'`,
   `approval_status = NULL`, `is_blacklisted = False`.
5. Commit. Show a success message directing them to log in.

### `register_staff`
Same as `register_trekker`, except `role = 'staff'` and
`approval_status = 'pending'` (staff needs admin approval before they
can log in and access their dashboard).

---

## Admin Routes

### `admin_dashboard`
1. Fetch counts: total treks, total staff, total trekkers, total
   bookings.
2. Fetch recent bookings, ordered by status priority
   (pending → booked → completed → cancelled) then booking date
   descending, for the preview table.
3. Render the dashboard with these stats and the preview table.

### `admin_treks_page`
1. Fetch all treks, ordered by status priority
   (ongoing → upcoming → completed → cancelled) then start_date
   ascending.
2. Support inline filtering via query parameters (trekname, location,
   difficulty).
3. Render the list.

### `admin_treks_view`
1. Fetch the trek by id. Error if not found.
2. Fetch all bookings for this trek, ordered by status priority then
   booking date descending.
3. Fetch all staff currently assigned to this trek.
4. Render the detail page, including the Trek/Status Action button
   groups (view/edit/manage-staff conditionally on 'upcoming'; start/
   complete/cancel conditionally on current status — see the Trek
   Status section below).

### `admin_treks_create`
**GET:** Render the create form.

**POST:**
1. Read trekname, location, difficulty, total_slots, start_date,
   end_date, amount, additional_info from the form. Convert
   total_slots to int, dates to date objects, amount to Decimal — on
   any conversion failure, show a format error.
2. If a trek with this trekname already exists, show an error.
3. If start_date >= end_date, show an error.
4. Create the Trek with `available_slots = total_slots` and
   `status = 'upcoming'`. Commit.

### `admin_treks_edit`
**GET and POST, same guard:**
1. Fetch the trek. Error if not found.
2. If `trek.status != 'upcoming'`, error — editing is blocked once a
   trek has left 'upcoming' (see Trek Status Restrictions below).
3. **[POST]** Read and convert form fields as in create. Check
   trekname uniqueness excluding this trek's own id. Check
   start_date < end_date. Compute `booked = total_slots -
   available_slots` (old values); if the new total_slots would be
   less than `booked`, show an error. Otherwise update all fields,
   recompute `available_slots = new_total_slots - booked`. Commit.

### `admin_treks_delete`
1. Fetch the trek. Error if not found.
2. If any booking on this trek has `booking_status` in
   (`pending`, `booked`), show an error — active bookings must be
   resolved (cancelled) before deletion.
3. Otherwise, delete all StaffTrekAssignment rows for this trek,
   delete all Booking rows for this trek, delete the trek. Commit.

### `admin_treks_ongoing`
1. Fetch the trek. Error if not found.
2. If `trek.status != 'upcoming'`, error.
3. If `today < trek.start_date`, error.
4. Set `status = 'ongoing'`. Commit.

### `admin_treks_completed`
1. Fetch the trek. Error if not found.
2. If `trek.status != 'ongoing'`, error (can't complete an upcoming
   trek directly, and can't re-complete an already-completed/cancelled
   one).
3. Set `status = 'completed'`.
4. Cascade: bookings with `booking_status == 'booked'` become
   `'completed'`. Bookings still at `'pending'` become `'cancelled'`,
   `payment_status` set to `'refunded'` (that trekker never actually
   went on the trek).
5. Commit.

### `admin_treks_cancelled`
1. Fetch the trek. Error if not found.
2. If `trek.status` is already `'cancelled'` or `'completed'`, error.
3. If `today > trek.end_date`, error (too late to cancel — only
   'completed' remains reachable).
4. Set `status = 'cancelled'`.
5. Cascade: every booking with `booking_status` in
   (`pending`, `booked`) becomes `'cancelled'`, `payment_status`
   becomes `'refunded'`.
6. Commit.
(Admin can reach this from either `'upcoming'` or `'ongoing'` — wider
than Staff's equivalent route, see Staff Routes below.)

### `admin_treks_manage_staff`
**GET:**
1. Fetch the trek. Error if not found.
2. If `trek.status != 'upcoming'`, error.
3. Build the list of all staff with `role == 'staff'`,
   `approval_status == 'approved'`, `is_blacklisted == False`. For
   each: if already assigned to this trek, mark "assigned"; else check
   every other trek they're assigned to for a date overlap with this
   trek — if any overlap exists, mark "unavailable"; otherwise mark
   "available".
4. Render the page: one row per staff member, checkbox checked if
   "assigned", disabled if "unavailable".

**POST:**
1. Same trek fetch/status guard as GET.
2. Read the submitted list of staff ids.
3. Compute which ids are newly checked (`to_add`) and which were
   checked before but are now unchecked (`to_remove`), via set
   difference against the current assignment list.
4. For every id in `to_add`, re-validate from scratch: must exist,
   `role == 'staff'`, approved, not blacklisted, no date overlap with
   any other trek they're already assigned to.
5. If any id in `to_add` fails validation, reject the entire request
   — nothing is applied.
6. Otherwise, create `StaffTrekAssignment` rows for `to_add`, delete
   rows for `to_remove`. Commit.

### `admin_staff_page`
1. Fetch all staff (`role == 'staff'`), ordered by approval_status
   priority (pending → approved → rejected) then name ascending.
2. Support inline filtering via query parameters.
3. Render the list.

### `admin_staff_view`
1. Fetch the staff member by id. Error if not found or not
   `role == 'staff'`.
2. Fetch all treks this staff member is assigned to, ordered by
   status priority then start_date ascending.
3. Render the detail page.

### `admin_staff_pending`
1. Fetch all staff with `role == 'staff'` and
   `approval_status == 'pending'`.
2. Render the pending-approvals list.

### `admin_staff_approve` / `admin_staff_reject`
1. Fetch the staff member. Error if not found or not `role=='staff'`.
2. If `approval_status != 'pending'`, error (already resolved one way
   or another).
3. Set `approval_status` to `'approved'` or `'rejected'`. Commit.

### `admin_staff_blacklist` / `admin_staff_unblacklist`
1. Fetch the staff member. Error if not found or not `role=='staff'`.
2. Set `is_blacklisted = True` / `False`. Commit. (No status guard
   needed — setting an already-`True`/`False` boolean to the same
   value is harmless.)

### `admin_trekkers_page`
1. Fetch all trekkers (`role == 'trekker'`), ordered by name.
2. Support inline filtering.
3. Render the list.

### `admin_trekkers_view`
1. Fetch the trekker by id. Error if not found or not
   `role == 'trekker'`.
2. Fetch all bookings by this trekker, ordered by status priority then
   booking date descending.
3. Render the detail page.

### `admin_trekkers_blacklist` / `admin_trekkers_unblacklist`
Same pattern as staff blacklist/unblacklist above.

### `admin_search`
1. Read `type`, `field`, `q` from query parameters.
2. Based on `type` (trek/staff/trekker) and `field` (id/name), run the
   matching query — e.g. `type=trek, field=name` searches
   `Trek.trekname.ilike(f"%{q}%")`; `field=id` searches
   `Trek.id == q` (converted to int).
3. Render the results.

### `admin_bookings_page`
1. Fetch all bookings, ordered by status priority then booking date
   descending.
2. Support inline filtering.
3. Render the list.

### `admin_bookings_view`
1. Fetch the booking by id. Error if not found.
2. Render the detail page, including the related trekker and trek.

### `admin_bookings_pending`
1. Fetch all bookings with `booking_status == 'pending'`.
2. Render the pending-approvals list.

### `admin_bookings_approve`
1. Fetch the booking. Error if not found.
2. If `booking_status != 'pending'`, error.
3. Set `booking_status = 'booked'`. Commit.

### `admin_bookings_reject`
1. Same fetch/guard as approve.
2. Set `booking_status = 'cancelled'`. Commit. (No refund logic needed
   here specifically — payment_status handling for rejection should
   be verified: if a paid booking is rejected, should payment_status
   become 'refunded'? Confirm this is handled; if not currently, it's
   a gap worth closing before submission.)

### `admin_bookings_cancel`
1. Fetch the booking. Error if not found.
2. If `booking_status != 'booked'`, error (only a confirmed booking
   is cancelled this way — a still-pending one should be rejected
   instead, via the route above).
3. Set `booking_status = 'cancelled'`, `payment_status = 'refunded'`.
   Commit.

### `admin_summary`
1. Compute the 4 stat-card counts and the 6 charts' underlying data
   (see the Admin Summary Chart Data section at the end of this doc).
2. Generate each chart with matplotlib, saved as a `.png` file into
   `static/charts/`.
3. Render the page with the stat cards and chart image tags.

---

## Staff Routes

### `staff_dashboard`
1. Fetch all treks this staff member is assigned to (via
   `StaffTrekAssignment`), ordered by status priority then start_date.
2. Compute quick-stat counts: total assigned treks, total distinct
   participants (bookings with `booking_status == 'booked'` across
   all assigned treks, de-duplicated by trekker), count of currently
   `ongoing` assigned treks, count of currently `upcoming` assigned
   treks.
3. Compute a per-trek registered-trekker count (same `'booked'`-only
   definition), as a dict keyed by trek id, for the dashboard table.
4. Render the dashboard.

### `staff_treks_page`
1. Fetch all treks this staff member is assigned to, ordered by
   status priority then start_date.
2. Render the list.

### `staff_treks_view`
1. Fetch the trek by id. Confirm this staff member is assigned to it
   — error ("not assigned") if not.
2. Error if trek not found.
3. Fetch the participant list: trekkers with `booking_status ==
   'booked'` on this trek only (not pending, not cancelled).
4. Render the detail page.

### `staff_trekkers_page`
1. Fetch every trek this staff member is assigned to.
2. Fetch every booking (with `booking_status == 'booked'`) across all
   of those treks.
3. Build a de-duplicated list of distinct trekkers across all of them.
4. Render the cross-trek trekker list.

### `staff_treks_ongoing`
1. Fetch the trek. Confirm this staff member is assigned to it.
2. If `trek.status != 'upcoming'`, error.
3. If `today < trek.start_date`, error.
4. Set `status = 'ongoing'`. Commit.

### `staff_treks_completed`
1. Fetch the trek. Confirm assignment.
2. If `trek.status != 'ongoing'`, error.
3. Set `status = 'completed'`. Apply the same completion cascade as
   `admin_treks_completed` (booked → completed; pending → cancelled +
   refunded). Commit.

### `staff_treks_cancelled`
1. Fetch the trek. Confirm assignment.
2. If `trek.status != 'ongoing'`, error — staff can ONLY cancel from
   'ongoing', never from 'upcoming' (unlike admin — see Trek Status
   Restrictions below for why).
3. If `today > trek.end_date`, error.
4. Set `status = 'cancelled'`. Apply the same cancellation cascade as
   `admin_treks_cancelled`. Commit.

### `staff_treks_slots`
**GET and POST, same guard:**
1. Fetch the trek. Confirm assignment.
2. If `trek.status != 'upcoming'`, error (once 'ongoing', booking is
   already closed, so adjusting capacity has no purpose).
3. **[POST]** Read `new_total_slots`, convert to int. Compute
   `booked = trek.total_slots - trek.available_slots` (old values). If
   `new_total_slots < booked`, error suggesting cancellation instead.
   Otherwise, update `total_slots` and recompute `available_slots =
   new_total_slots - booked`. Commit.

### `staff_profile`
1. Fetch this staff member.
2. Render the profile view page.

### `staff_profile_update`
**GET:** Render the update form, pre-filled with current name and
phone_number (password fields blank).

**POST:**
1. Read name, phone_number from the form.
2. Check phone_number isn't used by a different user (excluding self).
   Error if it is.
3. Update name, phone_number.
4. If current_password/new_password/confirm_password are all blank,
   skip password change. If any is provided, all three are required:
   verify current_password against the stored hash; verify
   new_password == confirm_password; on success, hash and store the
   new password.
5. Commit. Show a success message.

---

## Trekker Routes

### `trekker_dashboard`
1. Fetch available treks: `status == 'upcoming'`,
   `available_slots > 0`, excluding treks this trekker has already
   booked (any non-cancelled booking).
2. Fetch this trekker's active bookings (treks with status
   'upcoming'/'ongoing').
3. Render the dashboard.

### `trekker_treks_page`
1. Same available-treks query as the dashboard, plus support for
   `difficulty`/`location`/`trekname` query-parameter filters.
2. Render the list.

### `trekker_treks_view`
1. Fetch the trek by id. Error if not found.
2. If `status != 'upcoming'` or `available_slots <= 0`, error ("not
   available for booking") — still viewable read-only in this case
   only if that's the intended UX; otherwise this may block viewing
   entirely, verify against actual behavior wanted.
3. Fetch staff assigned to this trek.
4. Check for an existing booking by this trekker on this trek (any
   status other than cancelled) — show "already booked" or "awaiting
   approval" instead of a plain view, if found.
5. Render the detail page.

### `trekker_treks_book`
**GET:**
1. Fetch the trek. Error if not found.
2. If `status != 'upcoming'` or `available_slots <= 0`, error.
3. Check for an existing active booking on this trek by this trekker
   — error if found.
4. Render the combined trek-details + dummy-payment form.

**POST:**
1. Repeat all the same fetch/guard checks as GET.
2. Read card fields (name, number, expiry, cvv) — check presence
   only, no real validation (dummy payment).
3. If any card field is missing, error.
4. Create the Booking: `user_id`, `trek_id`,
   `booking_status = 'pending'`, `payment_status = 'paid'`.
5. Decrement `trek.available_slots` by 1. Commit.
6. Show a success message: booking request sent, awaiting admin
   approval.

### `trekker_bookings_cancel`
1. Fetch the booking. Error if not found or doesn't belong to this
   trekker.
2. If `booking_status` in (`cancelled`, `completed`), error.
3. If `today >= trek.start_date`, error (too late to cancel).
4. Set `booking_status = 'cancelled'`. If `payment_status == 'paid'`,
   set it to `'refunded'`.
5. Increment `trek.available_slots` by 1. Commit.

### `trekker_bookings_page`
1. Fetch bookings by this trekker where the related trek's status is
   `'upcoming'` or `'ongoing'` — these are the "active" bookings.
2. Group/sort by booking_status priority (pending → booked), booking
   date descending within each group.
3. Render the active-bookings page (split into pending-request and
   confirmed sub-sections).

### `trekker_bookings_history`
1. Fetch bookings by this trekker where the related trek's status is
   `'completed'` or `'cancelled'`.
2. Support filtering by trekname/location/difficulty/trek-status query
   parameters.
3. Sort by trek start_date descending (latest trek first).
4. Render the history page.

### `trekker_bookings_view`
1. Fetch the booking. Error if not found or doesn't belong to this
   trekker.
2. Fetch the related trek and its assigned staff.
3. Render the detail page.

### `trekker_profile`
1. Fetch this trekker.
2. Render the profile view page.

### `trekker_profile_update`
Same shape as `staff_profile_update` above (name, phone_number
uniqueness check excluding self, optional password change).

---

## Trek Status Restrictions — Summary

Trek status is never automatically computed from dates — every
transition is an explicit action by Staff or Admin.

| From | To | Who | Guard |
|---|---|---|---|
| upcoming | ongoing | Staff or Admin | `today >= start_date` |
| ongoing | completed | Staff or Admin | none beyond being `ongoing` |
| ongoing | cancelled | Staff or Admin | `today <= end_date` |
| upcoming | cancelled | Admin only | none |
| upcoming | completed | — | never allowed for anyone |
| any → cancelled | — | — | blocked once `today > end_date` |

**Why Staff's cancel scope is narrower than Admin's:** Staff's cancel
power exists for ground emergencies (accidents, weather, unsafe
terrain), which by definition only arise once a trek is underway.
Cancelling before a trek starts is a business/policy decision
(insufficient bookings, permit issues) that Admin handles, not Staff.

**Why Admin has full status power, not just cancel:** the admin, as
business owner, should not be structurally excluded from any
operational lever, even though Staff (being physically present) is
the more natural authority for confirming a trek has actually started
or finished in practice.

**Trek editing and staff assignment are both restricted to
`status == 'upcoming'`** — once a trek leaves 'upcoming', its core
details and staff roster are locked in, since trekkers may already
have booked against them.

**No date-based safety net on trekker booking** — gated purely on
`status == 'upcoming'`, trusting Staff/Admin to transition the trek
promptly. A trek could technically remain bookable past its real
start date if nobody acts — a deliberately accepted simplification.

---

## Admin Summary — Chart Data

1. **Top 10 Popular Treks:** count bookings grouped by trek, order
   descending, limit 10. Horizontal bar chart.
2. **Bookings in the Past 7 Days:** count bookings per day for the
   last 7 calendar days including today. Vertical bar chart.
3. **Pending vs Booked:** count of `booking_status == 'pending'` vs
   `'booked'`. Pie chart.
4. **Staff Approval Status:** count of staff by `approval_status`
   (approved/pending/rejected). Pie chart, 3 slices.
5. **Trekkers Active vs Blacklisted:** count by `is_blacklisted`. Pie
   chart.
6. **Staff Active vs Blacklisted:** same as #5, for staff — kept
   separate so each role's ratio isn't diluted by combining two
   different populations into one chart.

Each chart function saves a `.png` file to `static/charts/` (fixed
filename, overwritten every page load) and returns `None` if there's
no data yet, in which case the template shows a "no data yet" message
instead of an image.