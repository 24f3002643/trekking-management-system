# Trekking Management System
A role-based web application that enables administrators, trek staff, and trekkers (users) to efficiently manage trekking activities, bookings, staff assignments, and trek operations.

## Tech Stack
- **Backend:** Flask
- **Frontend:** HTML, CSS, Bootstrap 5, Jinja2
- **Database:** SQLite
- **ORM:** Flask-SQLAlchemy
- **Visualization:** Matplotlib

## Features
### Authentication
- Admin login
- Staff registration and login
- Trekker registration and login
- Session-based authentication (using Flask-Session)
- Role-based access control

### Admin
- Create, edit and delete treks.
- Update trek status (ongoing/completed/cancelled).
- Approve or reject staff registration.
- Blacklist or un-blacklist staff and trekkers.
- Manage (assign/un-assign) staff on treks.
- Approve or reject booking requests.
- Cancel approved bookings with automatic refund.
- Search treks, trekkers and staff by name or ID.
- Summary dashboard with analytics and charts.

### Trek Staff
- Register and log in (requires admin approval before accessing dashboard).
- View treks assigned by admin.
- Mark an assigned trek as ongoing, completed or cancelled.
- Update the total slots of the assigned trek.
- View the trekkers registered for their treks.
- View and update their own profile.

### Trekker
- Register and log in.
- Browse and search available treks (filter by difficulty, location).
- Book a trek (with a simulated payment step).
- View active bookings and full booking history.
- Cancel a booking (before the trek starts).
- View and update their own profile.

## Project Structure
```bash
trekking-management-system/
├── app.py                      # Flask app factory, DB init, seeding
├── application/
│   ├── models.py                # SQLAlchemy models
│   ├── database.py, decorators.py, seed.py charts.py
│   └── controllers/             # Routes, split by role (Flask Blueprints)
├── docs/                        # Design docs, decisions, business logic
├── static/                      # CSS, generated chart images
└── templates/                   # Jinja2 templates, split by role
```

## Future Enhancements 
1. REST/JSON API endpoints.
2. Frontend form validation using HTML5/JavaScript.
3. Styling using Bootstrap and UI responsiveness for mobile/tablet/PC.
4. Integration of Flask-Login or Flask-Security.
5. Adding Chart.js based analytics.

## Local Setup
1. Clone the repository
```bash
git clone <your-repo-url>
cd trekking-management-system
```
2. Create and activate a virtual environment
```bash
python3 -m venv .venv

# On Linux / macOS
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Set up environment variables
Create a `.env` file in the project root:
```
SECRET_KEY=any-random-secret-string-here
```
5. Run the application
```bash
python3 app.py
```
The app will be available at `http://localhost:5000`

On first run, the database is created automatically
(`trekking-management.sqlite3`), the Admin account is pre-seeded, and
dummy trekkers, staff, treks, are generated for local
testing/demo purposes.

## Login Credentials
### Admin (pre-seeded, no registration available for this role)
```
Email:    admin123@gmail.com
Password: admin123
```
### Staff
```
Email:    staff1@example.com, staff2@example.com,...., staff10@example.com
Password: password
```
### Trekker
```
Email:    trekker1@example.com, trekker2@example.com,...., trekker10@example.com
Password: password
```

## Academic Project
This project was developed as part of the **Modern Application Development I (MAD-1)** course in the **BS Degree in Data Science and Applications** offered by **IIT Madras**.
