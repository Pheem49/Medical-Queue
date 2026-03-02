from flask import Flask
from models import db, User

# Import Blueprints
from views.user_routes import user_bp
from views.admin_auth_routes import admin_auth_bp
from views.department_routes import department_bp
from views.doctor_routes import doctor_bp
from views.doctor_department_routes import doctor_department_bp
from views.slot_routes import slot_bp
from views.booking_routes import booking_bp
from views.booking_management_routes import booking_management_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Register Blueprints
app.register_blueprint(user_bp)
app.register_blueprint(admin_auth_bp)
app.register_blueprint(department_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(doctor_department_bp)
app.register_blueprint(slot_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(booking_management_bp)

if __name__ == "__main__":
    app.run(debug=True)