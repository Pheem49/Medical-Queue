from app import app, db
from models import Admin
with app.app_context():
    admins = Admin.query.all()
    for a in admins:
        print(f"ID: {a.id_admin}, Username: {a.User_name}, EmployeeID: {a.Employee_id}")
