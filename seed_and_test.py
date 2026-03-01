import os
from datetime import date, time
from app import app
from models import db, User, Doctor, Department, AppointmentSlot, Booking
from services.booking_service import create_booking, get_booking_details, get_patient_history

def seed_db_and_test():
    with app.app_context():
        # 1. ลบข้อมูลเก่าและสร้างตารางใหม่ทั้งหมด (สำหรับการทดสอบเท่านั้น)
        db.drop_all()
        db.create_all()

        print("--- สร้างข้อมูลจำลอง (Mock Data) ---")
        # สร้างแผนก
        dept = Department(name="แผนกอายุรกรรมทั่วไป")
        db.session.add(dept)
        db.session.commit()

        # สร้างแพทย์
        doc = Doctor(
            firstname="สมชาย",
            lastname="ใจดี",
            doctor_id="DOC001",
            specialist="อายุรกรรม",
            status="ว่าง"
        )
        db.session.add(doc)
        db.session.commit()

        # สร้างคนไข้
        patient = User(
            first_name="สมปอง",
            last_name="รักดี",
            email="sompong@test.com",
            national_id="1234567890123",
            date_of_birth=date(1990, 1, 1),
            phone_number="0801234567",
            password="hashedpassword123"
        )
        db.session.add(patient)
        db.session.commit()

        # สร้าง Slot การจอง
        slot = AppointmentSlot(
            doctor_id=doc.id,
            department_id=dept.department_id,
            slot_date=date(2026, 12, 1),
            start_time=time(9, 0),
            end_time=time(9, 30),
            max_capacity=5,
            current_booking=0,
            status="ว่าง"
        )
        db.session.add(slot)
        db.session.commit()

        print(f"เพิ่มข้อมูลสำเร็จ! \nUser ID: {patient.id} \nSlot ID: {slot.slot_id}")
        
        print("\n--- เริ่มทดสอบระบบการจอง (Booking Service) ---")
        
        # 2. ทดสอบจองคิว
        print(">> ทดสอบฟังก์ชัน create_booking()...")
        result = create_booking(user_id=patient.id, slot_id=slot.slot_id, detail="มีอาการไข้สูง ปวดหัว")
        
        if result["success"]:
            print(f"✅ จองสำเร็จ! Booking ID ที่ได้คือ: {result['booking_id']}")
            print(f"✅ QR Code ของคุณคือ: {result['qr_code']}")
            booking_id = result['booking_id']
        else:
            print(f"❌ จองไม่สำเร็จ: {result['message']}")
            return

        # 3. ทดสอบการดึงข้อมูลการจอง
        print("\n>> ทดสอบฟังก์ชัน get_booking_details()...")
        details = get_booking_details(user_id=patient.id, booking_id=booking_id)
        if details["success"]:
            print("✅ ดึงข้อมูลสำเร็จ รายละเอียดที่ได้:")
            data = details["data"]
            print(f"   - อาการ: {data['detail']}")
            print(f"   - ชื่อแพทย์: {data['doctor']['name']}")
            print(f"   - แผนก: {data['department']['name']}")
            print(f"   - เวลา: {data['slot']['date']} {data['slot']['start_time']}")
        else:
            print(f"❌ ดึงข้อมูลไม่สำเร็จ: {details['message']}")

        # 4. ทดสอบดึงประวัติ
        print("\n>> ทดสอบฟังก์ชัน get_patient_history()...")
        history = get_patient_history(user_id=patient.id)
        if history["success"]:
            print(f"✅ ดึงประวัติสำเร็จ พบการจองทั้งหมด {len(history['data'])} รายการ")
        else:
            print("❌ ดึงประวัติไม่สำเร็จ")

if __name__ == "__main__":
    seed_db_and_test()
