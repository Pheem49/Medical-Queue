from flask import Flask
from flask_cors import CORS
import os
from database import init_db, close_db, DB_PATH

# Import Blueprints
from routes.auth import auth_bp
from routes.bookings import bookings_bp
from routes.doctors import doctors_bp
from routes.staff import staff_bp
from routes.notifications import notifications_bp
from routes.pages import pages_bp

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(bookings_bp)
app.register_blueprint(doctors_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(pages_bp)

# DB Teardown
@app.teardown_appcontext
def shutdown_session(exception=None):
    close_db(exception)

if __name__ == '__main__':
    # create DB file if not exists
    if not os.path.exists(DB_PATH):
        open(DB_PATH, 'a').close()
    
    # Initialize DB (using the logic from database.py)
    with app.app_context():
        init_db()

    app.run(host='0.0.0.0', port=5000, debug=True)
