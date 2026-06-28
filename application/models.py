from .database import db 


class User(db.Model):
    __tablename__ = 'user' # it explicitly sets the name of the database table that the model maps to.

    id = db.Column(db.Integer(), primary_key=True) #when primary_key=True, then autoincrement=True by default
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), unique=True) 
    # phone_number is kept string, since phone_number can have leading zeros, country code, dashes, etc.
    role = db.Column(db.Enum('admin', 'staff', 'trekker'), nullable=False, default='trekker')
    approval_status = db.Column(db.Enum('pending', 'approved', 'rejected')) 
    # by default nullable=True, and default=None
    is_blacklisted = db.Column(db.Boolean(), nullable=False, default=False)
    bookings = db.relationship('Booking', back_populates='trekker')
    assignments = db.relationship('StaffTrekAssignment', back_populates='staff')



class Trek(db.Model):
    __tablename__ = 'trek'

    id = db.Column(db.Integer(), primary_key=True)
    trekname = db.Column(db.String(50), unique=True, nullable=False)
    location = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.Enum('easy', 'moderate', 'hard'), nullable=False)
    total_slots = db.Column(db.Integer(), nullable=False)
    available_slots = db.Column(db.Integer(), nullable=False)
    status = db.Column(db.Enum('upcoming', 'ongoing', 'completed', 'cancelled'), nullable=False, default='upcoming')
    start_date = db.Column(db.DateTime(), nullable=False)
    end_date = db.Column(db.DateTime(), nullable=False)
    additional_info = db.Column(db.String(250))
    bookings = db.relationship('Booking', back_populates='trek')
    assignments = db.relationship('StaffTrekAssignment', back_populates='trek')


class Booking(db.Model):
    __tablename__ = 'booking'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    trek_id = db.Column(db.Integer(), db.ForeignKey('trek.id'), nullable=False)
    booking_date = db.Column(db.DateTime(), nullable=False, default=db.func.now()) 
    #db.func.now() calls the database NOW() function to get the current timestamp.
    booking_status = db.Column(db.Enum('initiated', 'pending', 'booked', 'cancelled', 'completed'), nullable=False, default='initiated')
    payment_status = db.Column(db.Enum('pending', 'paid', 'refunded'), nullable=False, default='pending')
    additional_info = db.Column(db.String(250))
    trekker = db.relationship('User', back_populates='bookings')
    trek = db.relationship('Trek', back_populates='bookings')


class StaffTrekAssignment(db.Model):
    __tablename__ = 'staff_trek_assignment'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'), primary_key=True)

    staff = db.relationship('User', back_populates='assignments')
    trek = db.relationship('Trek', back_populates='assignments')

    
