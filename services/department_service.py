from models import db, Department

def get_all_departments():
    try:
        departments = Department.query.all()
        # ใช้ to_dict() ตามที่กำหนดไว้ใน models.py เพื่อไม่ให้ hard code
        return [d.to_dict() for d in departments]
    except Exception as e:
        print(f"Error fetching departments: {e}")
        return []

def add_department(name):
    try:
        new_dept = Department(name=name)
        db.session.add(new_dept)
        db.session.commit()
        return new_dept.department_id
    except Exception as e:
        db.session.rollback()
        print(f"Error adding department: {e}")
        return None

def update_department(department_id, new_name):
    try:
        dept = Department.query.get(department_id)
        if dept:
            dept.name = new_name
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error updating department: {e}")
        return False
