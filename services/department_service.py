from models import db, Department

def get_all_departments():
    departments = Department.query.all()
    return [{"department_id": d.department_id, "name": d.name} for d in departments]

def add_department(name):
    new_dept = Department(name=name)
    db.session.add(new_dept)
    db.session.commit()
    return new_dept.department_id

def update_department(department_id, new_name):
    dept = Department.query.get(department_id)
    if dept:
        dept.name = new_name
        db.session.commit()
        return True
    return False
