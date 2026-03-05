from app import app, db
from services.admin_auth_service import create_admin_staff
from models import Admin
import sys

def seed_database():
    with app.app_context():
        print("--- ข้อมูล Admin ในระบบปัจจุบัน ---")
        admins = Admin.query.all()
        if not admins:
            print("ยังไม่มี Admin ในระบบเลย")
        for a in admins:
            print(f"- ID: {a.id_admin} | Username: {a.User_name} | Employee ID: {a.Employee_id}")
        
        print("\n--- กำลังสร้างบัญชีใหม่ ---")
        
        # คุณสามารถตั้งค่า username และรหัสที่ต้องการได้ที่นี่
        new_username = "admin2"
        new_employee_id = "EMP002"
        new_password = "password123"
        new_first_name = "Admin"
        new_last_name = "Two"
        
        existing_admin = Admin.query.filter_by(User_name=new_username).first()
        existing_emp = Admin.query.filter_by(Employee_id=new_employee_id).first()
        
        if existing_admin:
            print(f"❌ สร้างไม่ได้: มีชื่อผู้ใช้งาน '{new_username}' อยู่แล้ว")
        elif existing_emp:
            print(f"❌ สร้างไม่ได้: มีรหัสพนักงาน '{new_employee_id}' อยู่แล้ว")
        else:
            admin = create_admin_staff(
                first_name=new_first_name,
                last_name=new_last_name,
                employee_id=new_employee_id,
                user_name=new_username,
                password=new_password
            )
            print("🎉 สร้างบัญชีสำเร็จ!")
            print(f"👉 Employee ID: {admin.Employee_id}")
            print(f"👉 Username: {admin.User_name}")
            print(f"👉 Password: {new_password}")

if __name__ == "__main__":
    seed_database()
