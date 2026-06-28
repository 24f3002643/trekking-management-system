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

### Impact
- removes redundant data in the database.
- Ensures that the duration of a trek is always consistent with its start and end dates.

### Alternatives Considered
- Store `duration` as a separate attribute in the `Trek` table (current design).    

---