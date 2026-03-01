from models import db, Admin
from werkzeug.security import check_password_hash, generate_password_hash

# API Logic
def verify_admin_login(login_id, password):
    admin = Admin.query.filter(
        (Admin.Employee_id == login_id) | (Admin.User_name == login_id)
    ).first()
    
    if admin and check_password_hash(admin.hash_password, password):
        return admin
    return None

def create_admin_staff(first_name, last_name, employee_id, user_name, password):
    hashed_pw = generate_password_hash(password)
    new_admin = Admin(
        first_name=first_name,
        last_name=last_name,
        Employee_id=employee_id,
        User_name=user_name,
        hash_password=hashed_pw
    )
    db.session.add(new_admin)
    db.session.commit()
    return new_admin
