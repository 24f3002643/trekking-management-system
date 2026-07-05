# Views and Flows
This file contains final list of all the views and flows.

## Public Pages
### Login Page
1. Will serve as a home page, if not logded in.
2. Input Field :
    - username
    - email
    - password
3. submit button
4. On clicking submit button :
    - if details correct , then will redirect to corresponding user dashboard
    - if details correct, but the role is staff and the admin has not approved, a new page with message of awaiting admin approval will be displayed. This page will contain the link to login page.
    - if details incorrect, a new page with message of incorrect credentials will be displayed. The page will contain the link to login page.
5. Links:
    - Register as Trekker
    - Register as Staff
### Staff Register Page
1. Input field :
    - username
    - email
    - password
    - phone number
2. submit button
3. Links :
    - Login
4. On clicking submit button,
    - if no such entry is found in the database, :
        - details will be added to database.
        - request for approval will be sent to admin.
        - a new page with message that "request for appproval has been sent to admin and login after some time" will be displayed.There will a link to login page.
    - if a user with the same username, email, or phone number already exists :
        - it will display the message that "staff already exists. Login to access the dashboard"
### Trekker Register Page
1. Input field :
    - username
    - email
    - password
    - phone number
2. submit button
3. Links :
    - Login
4. On clicking submit button,
    - if no such entry is found in the database, :
        - details will be added to database.
        - a new page with message that "registration successful. Login to access the dashboard" will be displayed.There will a link to login page.
    - if a user with the same username, email, or phone number already exists :
        - it will display the message that "trekker already exists. Login to access the dashboard"

## Admin Views

### Admin Dashboard
1. Navigation bar on left side :
    - Dashboard : redirect to admin dashboard
    - Treks : redirect to admin trek management page
    - Staffs : redirect to admin staff management page
    - Trekkers : redirect to admin trekker management page
    - Bookings : redirect to admin booking management page
    - Summary : redirect to admin summary page
2. Top Navigation bar :
    - search : redirect to admin search page  
    - logout : logout the admin, and redirect to login page.
3. Main Screen : Divided into two parts (Top Section and Main Section)
    - Top Section (small rectangle area) : Shows the following information in card formats
        - Total treks with number
        - Total staff with number
        - Total trekkers with number
        - Total bookings with number
    - Main Section (big rectangle down) : Contain a list of all the recent bookings . 
        - The columns of list will be :
            - Booking ID (clickable link, will redirect to this particular booking details)
            - Trekker
            - Trek 
            - Booking Date
            - Booking Status
            - Payment Status
            - Action : 
                - Approve (if booking status is pending): Approves the booking request.
                - Cancel (if booking status is pending or booked): Cancels the booking.
                - View (if booking status is completed or cancelled): Displays the booking details.
        - The list will be scrollable, and only 4 enteries will be shown at once.
        - At the end of list, there will be link to "See all bookings", which will redirect to admin booking management page.

### Admin Trek Management Page
1. Same Navigation bar as admin dashboard : Left Navigation bar and top navigation bar
2. Main page shows a list of all the treks.
    - The columns would be :
        - ID (clickable link to view the details of that trek)
        - Trek Name
        - Duration as (Start Date - End Date)
        - Slots (Available / Total)
        - Status
        - Action 
            - view : to view the details of that trek
            - assign staff : redirect to the trek staff assignment page
            - edit : redirect to trek edit page
            - delete : delete the trek 
    - The list will be scrollable.
3. At the top-right corner, there will be an "Add Trek" button that redirects to the trek creation page.

### Trek Creation Page
1. Form asking for the following details
    - Trek Name
    - Location
    - Difficulty
    - Total slots
    - Start date
    - End date
    - Additional Info
2. No asking for the following details :
    - status : this would be determined based on dates, and by business logic
    - available slot : same as total slot initially, but will change as booking starts.
3. Submit button, which triggers the endpoint for creating the trek. On successful creation, redirect to the Admin Trek Management Page.
4. Same Navigation bar as admin dashboard : Left Navigation bar and top navigation bar

### Trek Staff Assignment Page
1. Displays  the details of trek (Which are autofilled and non editable)
2. There is form containing the checkbox list of all staffs.
    - Approved staff already assigned to this trek are checked and editable.
    - Approved staff not assigned to any overlapping trek are unchecked and editable.
    - Approved staff assigned to another overlapping trek are disabled.
    - Pending, rejected, or blacklisted staff are not displayed.
3. Submit button, which triggers the endpoint for assigning staffs to treks. On successful submission, redirects to the Admin Trek Management 
4. Same Navigation bar as admin dashboard : Left Navigation bar and top navigation bar


### Admin Trek Detail Page
1. Same Navigation bar as admin dashboard : Left Navigation bar and top navigation bar
2. Contains all the details of the trek
3. There would be buttons for under action : 
        - assign staff : redirect to the trek staff assignment page
        - edit : redirect to trek edit page
        - delete : delete the trek 
4. At last, there will be link to return to Admin Trek Management Page


### Admin Staff Management Page
1. Same Navigation bar as admin dashboard : Left Navigation bar and top navigation bar.
2. Contains two list :
    - new registration of staffs awaiting for approval
    - approved staff
3. New registration staff list :
    - scrollable list, showing 4 enteries at a time.
    - there will be following columns :
        - id (clickable link, on clicking displays all the details about this staff)
        - name
        - email
        - phone number
        - action :
            - approve : will trigger end point to approve the staff, and will redirect to admin staff management page
            - reject : will trigger end point to deny the staff approval, and will redirect to admin staff management page
4. Approved staff list :
    - displays the following columns:
        - id (clickable link, on clicking displays all the details about this staff)
        - name
        - email
        - phone number
        - blacklist status

        - action :
            - Add to blacklist (if not blacklisted) : on clicking, add to blacklist and redirect to current page
            - Remove from blacklist (if blacklisted) :on clicking, remove from blacklist and redirect to current page

### Admin Staff Detail Page
1. Same Navigation bar as admin dashboard : Left Navigation bar and top navigation bar
2. Contains all the details of the staff
3. There would be buttons for under action : 
        - action :
            - Add to blacklist (if not blacklisted) : on clicking, add to blacklist and redirect to current page
            - Remove from blacklist (if blacklisted) :on clicking, remove from blacklist and redirect to current page
4. Displays the treks assigned to the staff. To remove the this staff from trek assigned, go to trek management page.        
5. At last, there will be link to return to Admin Staff Management Page



### Admin Trekker Management Page
1. Same Navigation bar as admin dashboard : Left Navigation bar and top navigation bar.
2. Contains the list showing all the users :
    - scrollable list, showing 4-6 enteries at a time.
    - there will be following columns :
        - id (clickable link, on clicking displays all the details about this trekker)
        - name
        - email
        - phone number
        - Blacklist status
        - action :
            - Add to blacklist (if not blacklisted) : on clicking, add to blacklist and redirect to current page
            - Remove from blacklist (if blacklisted) :on clicking, remove from blacklist and redirect to current page

### Admin Trekker Detail Page
1. Same Navigation bar as admin dashboard : Left Navigation bar and top navigation bar
2. Contains all the details of the trekker
3. There would be buttons for under action : 
        - action :
            - Add to blacklist (if not blacklisted) : on clicking, add to blacklist and redirect to current page
            - Remove from blacklist (if blacklisted) :on clicking, remove from blacklist and redirect to current page
4. Displays all the booking made by the trekker. 
    The columns of list will be :
            - Booking ID (clickable link, will redirect to this particular booking details)
            - Trek 
            - Booking Date
            - Booking Status
            - Action : 
                - Approve (if booking status is pending): Approves the booking request.
                - Cancel (if booking status is pending or booked): Cancels the booking.
                - View (if booking status is completed or cancelled): Displays the booking details.
        - The list will be scrollable, and only 4 enteries will be shown at once.        
5. At last, there will be link to return to Admin Trekker Management Page



### Admin Booking Management Page
1. Same Navigation bar as admin dashboard : Left Navigation bar and top navigation bar.
2. Contains the list showing all the bookings :
    - scrollable list, showing 4-6 enteries at a time.
        - The columns of list will be :
            - Booking ID (clickable link, will redirect to this particular booking details)
            - Trekker
            - Trek 
            - Booking Date
            - Booking Status
            - Payment Status
            - Action : 
                - Approve (if booking status is pending): Approves the booking request.
                - Cancel (if booking status is pending or booked): Cancels the booking.
                - View (if booking status is completed or cancelled): Displays the booking details.

### Admin Booking Detail Page
1. Same Navigation bar as admin dashboard : Left Navigation bar and top navigation bar
2. Contains all the details of the booking
    - The columns of list will be :
        - Booking ID 
        - Trekker
        - Trek 
        - Booking Date
        - Booking Status
        - Payment Status
        - Action : 
            - Approve (if booking status is pending): Approves the booking request.
            - Cancel (if booking status is pending or booked): Cancels the booking. 
5. At last, there will be link to return to Admin Booking Management Page

### Admin Search Page
1. Same Navigation bar as Admin Dashboard:
    - Left Navigation Bar
    - Top Navigation Bar
2. Search Section:
    - Search input field
    - Search button
3. Search Results:
    - Displays matching records from:
        - Treks
        - Staff
        - Trekkers
        - Bookings
4. Search results are grouped by category.
5. Trek Results:
    - Trek ID (clickable, redirects to Trek Detail Page)
    - Trek Name
    - Status
6. Staff Results:
    - Staff ID (clickable, redirects to Staff Detail Page)
    - Name
    - Email

7. Trekker Results:
    - Trekker ID (clickable, redirects to Trekker Detail Page)
    - Name
    - Email

8. Booking Results:
    - Booking ID (clickable, redirects to Booking Detail Page)
    - Trek
    - Trekker
    - Booking Status

9. If no matching records are found, display:
    - "No matching records found."



## Trekker Views 



### Trekker Dashboard
1. Navigation bar on left side :
    - Dashboard : redirect to trekker dashboard
    - Browse Treks : redirect to trekker Trek Browse Page
    - My Bookings : redirect to the trekker Trek Booking Page
    - History : redirect To User trekker Booking History Page
    - My Profile : redirect to trekker profile page
    - logout : logout the trekker and redirect to login page
2. Top Navigation bar :
    - search : redirect to trekker search page  
    - logout : logout the trekker, and redirect to login page.
3. Main Screen : Divided into two parts (Top Section and Bottom Section)
    - Top Section  : Shows the list of available treks with following columns
        - ID (clickable, on clicking redirect to trekker trek details page)
        - Trek name
        - Location
        - Difficulty
        - duration (in format of start date - end date)
        - Available slots
        - Action
            - Book Now : on clicking, trigger the end point to create the booking and will redirect to payment page.
        - The list will be scrollable, and only 4 enteries will be shown at once.
        - At the end of list, there will be link to "See all available treks", which will redirect to trekker Trek Browse Page.
    - Main Section (big rectangle down) : Contain a list of all the current bookings of the user . 
        - The columns of list will be :
            - Booking ID (clickable link, will redirect to this particular booking details)
            - Trek 
            - Booking Date
            - Booking Status
            - Payment Status
            - Action : 
                - Cancel (if booking status is pending or booked): Cancels the booking.
                - View (if booking status is completed or cancelled): Displays the booking details.
        - The list will be scrollable, and only 4 enteries will be shown at once.
        - At the end of list, there will be link to "See all bookings", which will redirect to trekker booking page.


### Trekker Browse Trek Page
1. Same navigation as trekker dashboard : left side navigation and top navigation.
2. Shows the list of available treks with following columns
    - Top Section  : Shows the list of available treks with following columns
        - ID (clickable, on clicking redirect to trekker trek details page)
        - Trek name
        - Location
        - Difficulty
        - duration (in format of start date - end date)
        -  slots (available/total)
        - Action
            - Book Now : on clicking, trigger the end point to create the booking and will redirect to payement page
        - At the end of list, there will be link to return to trekker dashboard.

### Trekker Trek Detail Page
1. Same navigation as trekker dashboard : left side navigation and top navigation.
2. It will contain all the details of the trek.
3. Action
    - Book Now : on clicking, trigger the end point to create the booking, and will redirect to payement page
4. At the end, there will be link to return to trekker browse trek page.


### Trekker Trek Payement Page
1. Shows the amount details and the trek name for which payemnt is being made
2. Option to select the payment method.
3. Pay now button.
4. It will be dummy button, since we are just demostrating the flow.
5. On Selecting pay now button, it would trigger the endpoint to create the booking and  it will redirect to Trekker Booking Page.
6. Same navigation as trekker dashboard : left side navigation and top navigation.

### Trekker Booking Page
1. Contain a list of all the current bookings of the user .
    - The columns of list will be :
        - Booking ID (clickable link, will redirect to this particular booking details)
        - Trek 
        - Booking Date
        - Booking Status
        - Payment Status
        - Action : 
            - Cancel (if booking status is pending or booked): Cancels the booking.
            - View (if booking status is completed or cancelled): Displays the booking details.
2. At the end of list, there will be link to return to trekker dashboard.
3. Same navigation as trekker dashboard : left side navigation and top navigation.

### Trekker Booking Detail Page
1. Same navigation as trekker dashboard : left side navigation and top navigation.
2. It will contain all the current details of the booking.
3. Action
    - Cancel (if booking status is pending or booked): Cancels the booking.
4. At the end of list, there will be link to return to trekker booking page.

### Trekker History Page
1. Contain a list of all the  bookings of the user that have been cancelled or completed .
    - The columns of list will be :
        - Booking ID (clickable link, will redirect to this particular booking details)
        - Trek 
        - Booking Date
        - Booking Status
        - Payment Status
        - Action
            - View (if booking status is completed or cancelled): Displays the booking details.
2. At the end of list, there will be link to return to trekker dashboard.
3. Same navigation as trekker dashboard : left side navigation and top navigation.

### Trekker Profile Page
1. Contain the form to update the trekker details autofilled with current details
    - name (changeable)
    - email (non-editable)
    - phone number (changeable)
    - New Password
2. At last, submit button which would update trigger a end point which will update the user details.
    - the controller will verfiy the user does not change email.
    - it would redirect to profile page again.
3. At last, there would be link to return to trekker dashboard.





## Staff Views

### Staff Dashboard
1. Navigation bar on left side :
    - Dashboard : redirect to staff dashboard
    - My Treks : redirect to staff trek  page
    - Participants : redirect to staff participants page.
    - Profile : redirect to staff profile page
    - Logout : logout the admin and redirects to login page
2. Top Navigation bar :
    - logout : logout the admin, and redirect to login page.
3. Main Screen : Divided into two parts (Top Section and Main Section)
    - First  Section (small rectangle area) : Shows the following information in card formats
        - Assigned treks with number
        - Total Participants registered with the treks assigned with number
        - Total upcoming, ongoing, completed and cancelled treks assigned to him with number
    - Main Section (big rectangle down) : Contain a list of all the assigned treks.
        - The columns of list will be :
            -  ID (clickable link, will redirect to this particular trek details)
            - Trek Name
            - Participants
            - Slots (available/total)
            - Status
            - Amount
            - Action : 
                - Update :; redirect to staff trek update page
                - View : Displays the details of a particular trek.
        - The list will be scrollable, and only 4 enteries will be shown at once.


### Staff Trek Page
1. Same navigation as staff dashboard
2. Contain a list of all the assigned treks.
    - The columns of list will be :
        -  ID (clickable link, will redirect to this particular trek details)
        - Trek Name
        - Participants
        - Slots (available/total)
        - Status
        - Amount
        - Action : 
            - Update :; redirect to staff trek update page.
            - View : Displays the details of a particular trek.
    - At the end of list, there will be link to return to staff dashboard.

### Staff Trek Detail Page
1. Same navigation as staff dashboard
2. Contains all the details of a particular trek.
    -  ID (clickable link, will redirect to this particular trek details)
    - Trek Name
    - Participants
    - Slots (available/total)
    - Status
    - Amount
    - Action : 
        - Update :; redirect to staff trek update page.
3. At the end, there will be link to return to Staff Trek Page

### Staff Trek Update Page
1. Same navigation as staff dashboard
2. Shows all the details of a particular trek, with Available slots and status as editable. rest field will be pre filled but disabled.

### Staff Participants Page
1. Same Navigation as staff dashboard
2. Shows a list of all the participants assigned with the trek assigned to it.
    - ID
    - Name
    - Trek
    - Email
    - Phone Number
3. At the end, there is a link to return to Staff Dashboard

### Staff Profile Page
1. Contain the form to update the trekker details autofilled with current details
    - name (changeable)
    - email (non-editable)
    - phone number (changeable)
    - New Password
2. At last, submit button which would update trigger a end point which will update the staff details.
    - the controller will verfiy the user does not change email.
    - it would redirect to profile page again.
3. At last, there would be link to return to staff dashboard.