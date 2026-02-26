from flask import Flask
from models import db, User

# Import Blueprints
from views.auth_views import auth_bp
from views.user_views import user_bp
from views.admin_views import admin_bp

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
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)