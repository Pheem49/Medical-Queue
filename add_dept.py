from app import app
from models import db, Department

def add_general_dept():
    with app.app_context():
        # Check if the department already exists
        dept = Department.query.filter_by(name="แผนกตรวจทั่วไป").first()
        if not dept:
            new_dept = Department(name="แผนกตรวจทั่วไป")
            db.session.add(new_dept)
            db.session.commit()
            print("Successfully added new department: แผนกตรวจทั่วไป")
        else:
            print("Department 'แผนกตรวจทั่วไป' already exists.")

if __name__ == "__main__":
    add_general_dept()
