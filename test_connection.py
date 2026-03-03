from app import app
from models import db, Doctor, Department, DoctorToDepartment
from services.doctor_service import get_all_doctors, add_doctor, update_doctor

def test_connection():
    with app.app_context():
        print("--- Testing Connection ---")
        
        # 1. สร้างแผนกจำลอง
        if not Department.query.filter_by(name="อายุรกรรม").first():
            d1 = Department(name="อายุรกรรม")
            d2 = Department(name="กุมารเวชกรรม")
            db.session.add_all([d1, d2])
            db.session.commit()
            print("Created dummy departments.")

        dept1 = Department.query.filter_by(name="อายุรกรรม").first()
        dept2 = Department.query.filter_by(name="กุมารเวชกรรม").first()

        # 2. ทดสอบเพิ่มหมอพร้อมแผนก
        new_id = add_doctor(
            firstname="สมพร",
            lastname="นอนน้อย",
            doctor_id_str="D888",
            specialist="อายุรกรรมทางเดินอาหาร",
            status="ว่างวันนี้",
            schedule_json={},
            department_ids=[dept1.department_id]
        )
        print(f"Added doctor with ID: {new_id} in {dept1.name}")

        # 3. ทดสอบดึงข้อมูลหมอทั้งหมด (ต้องมีรายชื่อแผนกติดมาด้วย)
        doctors = get_all_doctors()
        target = next((d for d in doctors if d['id'] == new_id), None)
        if target:
            print(f"Verified: {target['firstname']} is in departments: {target['departments']}")
            if dept1.name in target['departments']:
                print("SUCCESS: Department name included in response!")
            else:
                print("FAILED: Department name missing!")
        
        # 4. ทดสอบอัปเดตแผนก
        update_doctor(new_id, {"department_ids": [dept1.department_id, dept2.department_id]})
        doctors_updated = get_all_doctors()
        target_updated = next((d for d in doctors_updated if d['id'] == new_id), None)
        print(f"Verified Update: {target_updated['firstname']} is now in: {target_updated['departments']}")

if __name__ == "__main__":
    test_connection()
