# Development Roadmap

## Core-Requirements

### Step-1: Requirement Analysis
- Study the project statements 
- Identify actors, functional requirements and business rules.
- Define invariants and constraints
- Define how to document the project

### Step-2: Domain Modelling
- Identify entities, their attributes and relationship between them.
- Draw the ER diagram.
- Finalize the database design.
- Convert the ER diagram into relational tables.

### Step-3: Project Structure Setup 
- Create the folder structure according to MVC architecture.
- Set up the virtual environment and install required libraries.
- Configure the Flask application.

### Step-4: Define Models
- Create the SQLAlchemy models.
- Define relationships between models.
- Initialize the database.
- Seed the predefined Admin user.

### Step-5: Authentication and Role Management 
- Implement user registration (Trekkers and Trek Staffs).
- Implement user login and logout.
- Implement session management.
- Implement role-based access control.
- Implement staff approval workflow.

### Step-6: Setup Admin Views
- Create views (html pages) for admin.
- Implement the admin dashboard.

### Step-7: Setup Trek Staff Views
- Create views (html pages) for trek staff.
- Implement the trek staff dashboard.

### Step-8: Setup Trekker Views
- Create views (html pages) for trekker.
- Implement the trekker dashboard.

### Step-9: Implement Controllers and Business Logic
- Define controllers and routes.
- Write business logic in controllers.
- Implement Admin functionalities.
- Implement Trek Staff functionalities.
- Implement Trekker functionalities.

## Additional Features

### Step-10: Create Charts and Analytics
- Create summary and analytics using charts.

### Step-11: Develop REST-APIs
- Develop JSON APIs for users, treks, staff, and bookings.
- Implement proper business errors and HTTP status codes.

### Step-12: Frontend and Backend Validation
- Add form validation using HTML5/JavaScript.
- Add backend validation in Flask routes/controllers.
- Prevent invalid trek bookings and duplicate entries through validation 

### Step-13: Responsive UI and Styling
- Add styling using Bootstrap.
- Ensure mobile/tablet/PC responsiveness.
- Improve dashboard layouts and user experience.

### Step-14: Flask-Login Integration and Security
- Integrate Flask-Login or Flask-Security.
- Restrict routes based on roles.
- Protect sessions and unauthorized access.
