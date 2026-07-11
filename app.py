from flask import Flask 
from application.models import User
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os

load_dotenv() 

app = None 

from application.database import db

def create_app():
    app = Flask(__name__) 
    #creating object of Flask class
    # __name__ stores the name of the current file
    app.debug = True
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking-management.sqlite3'
    db.init_app(app)
    app.app_context().push()

    from application.controllers.auth import auth_bp
    from application.controllers.admin_bp import admin_bp
    from application.controllers import admin, admin_treks, admin_staff, admin_trekker, admin_bookings
    from application.controllers.staff_bp import staff_bp
    from application.controllers import staff, staff_profile, staff_bookings
    from application.controllers.trekker_bp import trekker_bp
    from application.controllers import trekker, trekker_bookings, trekker_profile

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(trekker_bp)


    return app 

app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role='admin').first()
        if admin is None:
            admin = User(name='Admin 123', email="admin123@gmail.com", password_hash=generate_password_hash('admin123'), phone_number="9100091000", role='admin')
            db.session.add(admin)
            db.session.commit()

        from application.seed import seed_dummy_data
        seed_dummy_data()

    app.run()