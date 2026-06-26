from flask import Flask 
from werkzeug.security import generate_password_hash
app = None 

from application.database import db

def create_app():
    app = Flask(__name__) 
    #creating object of Flask class
    # __name__ stores the name of the current file
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking-management.sqlite3'
    db.init_app(app)
    app.app_context().push()
    return app 

app = create_app()

from application.controllers import *

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role='admin').first()
        if admin is None:
            admin = User(username='admin123', email="admin123@gmail.com", password_hash=generate_password_hash('admin123'), phone_number="9100091000", role='admin')
            db.session.add(admin)
            db.session.commit()
    app.run()