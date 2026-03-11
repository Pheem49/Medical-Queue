import os
from datetime import date, time, datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Admin, Department, Doctor, DoctorToDepartment, AppointmentSlot, Booking
from services.booking_service import encrypt_national_id

def seed_database():
    with app.app_context():
        print("Cleaning up database...")
        db.drop_all()
        db.create_all()

        password_plain = "password123"
        hashed_pw = generate_password_hash(password_plain)

        # 1. สร้าง Admin (คนที่ 2)
        print("Creating Admin...")
        admin = Admin(
            first_name="Admin",
            last_name="System",
            Employee_id="EMP001",
            User_name="admin01",
            hash_password=hashed_pw
        )
        db.session.add(admin)

        # 2. สร้าง User (คนที่ 1)
        print("Creating User...")
        user_national_id = "1234567890123"
        user = User(
            first_name="สมชาย",
            last_name="สายเสมอ",
            email="somchai@example.com",
            national_id=user_national_id,
            date_of_birth=date(1990, 5, 20),
            phone_number="0812345678",
            password=hashed_pw
        )
        db.session.add(user)
        db.session.flush() # เพื่อเอา user.id มาใช้ต่อ

        # 3. สร้างแผนก (คนที่ 3)
        print("Creating Departments...")
        dept1 = Department(name="แผนกอายุรกรรม (Internal Medicine)")
        dept2 = Department(name="แผนกศัลยกรรม (Surgery)")
        dept3 = Department(name="แผนกกุมารเวชกรรม (Pediatrics)")
        db.session.add_all([dept1, dept2, dept3])
        db.session.flush()

        # 4. สร้างหมอ (คนที่ 4)
        # status: ว่าง ว่างเช้า ว่างบ่าย คิวเต็มวันนี้
        print("Creating Doctors...")
        doc1 = Doctor(
            firstname="ประวัติ",
            lastname="ดีเด่น",
            doctor_id="DOC001",
            specialist="อายุรแพทย์",
            status="ว่าง",
            schedule={"mon": "09:00-16:00", "wed": "09:00-16:00"}
        )
        doc2 = Doctor(
            firstname="วิภา",
            lastname="รักษาสุข",
            doctor_id="DOC002",
            specialist="ศัลยแพทย์",
            status="ว่าง",
            schedule={"tue": "10:00-18:00", "thu": "10:00-18:00"}
        )
        db.session.add_all([doc1, doc2])
        db.session.flush()

        # 5. เชื่อมหมอกับแผนก (คนที่ 5)
        print("Linking Doctors to Departments...")
        link1 = DoctorToDepartment(doctor_id=doc1.id, department_id=dept1.department_id)
        link2 = DoctorToDepartment(doctor_id=doc2.id, department_id=dept2.department_id)
        db.session.add_all([link1, link2])

        # 6. สร้าง Slot เวลา (คนที่ 6)
        print("Creating Appointment Slots...")
        # สร้าง Slot สำหรับวันนี้และพรุ่งนี้
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        slot1 = AppointmentSlot(
            doctor_id=doc1.id,
            department_id=dept1.department_id,
            slot_date=today,
            start_time=time(9, 0),
            end_time=time(10, 0),
            max_capacity=10,
            current_booking=1, # เดี๋ยวจะสร้าง Booking ให้ 1 อัน
            status="active"
        )
        
        slot2 = AppointmentSlot(
            doctor_id=doc1.id,
            department_id=dept1.department_id,
            slot_date=tomorrow,
            start_time=time(10, 0),
            end_time=time(11, 0),
            max_capacity=5,
            current_booking=0,
            status="active"
        )
        db.session.add_all([slot1, slot2])
        db.session.flush()

        # 7. สร้าง Booking (คนที่ 7 & 8)
        print("Creating Sample Bookings...")
        # สร้าง QR Code ที่เข้ารหัสจาก National ID
        # booking_Statu: เสร็จสิ้น รอรับบริการ ยกเลิก
        qr_token = encrypt_national_id(user_national_id)
        
        booking = Booking(
            slot_id=slot1.slot_id,
            id_users=user.id,
            booking_at=datetime.utcnow(),
            booking_Status="รอรับบริการ",
            detail="ปวดท้องเล็กน้อย",
            qr_code=qr_token
        )
        db.session.add(booking)

        # เพิ่มประวัติที่จบไปแล้ว (History)
        old_booking = Booking(
            slot_id=slot1.slot_id,
            id_users=user.id,
            booking_at=datetime.utcnow() - timedelta(days=7),
            booking_Status="เสร็จสิ้น",
            detail="ตรวจร่างกายประจำปี",
            qr_code=encrypt_national_id(user_national_id)
        )
        db.session.add(old_booking)

        db.session.commit()
        print("Successfully seeded the database!")

if __name__ == "__main__":
    seed_database()
