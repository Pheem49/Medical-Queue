from app import app
from models import db, Doctor
import json

def seed_doctors():
    with app.app_context():
        # ข้อมูลจำลองของหมอ
        dummy_doctors = [
            {
                "firstname": "สมชาย",
                "lastname": "ใจดี",
                "doctor_id": "D001",
                "specialist": "อายุรกรรม",
                "status": "ว่าง",
                "schedule": {
                    "monday": ["09:00-12:00", "13:00-16:00"],
                    "wednesday": ["09:00-12:00"]
                }
            },
            {
                "firstname": "สมหญิง",
                "lastname": "รักเรียน",
                "doctor_id": "D002",
                "specialist": "กุมารเวชกรรม",
                "status": "ว่าง",
                "schedule": {
                    "tuesday": ["10:00-15:00"],
                    "thursday": ["10:00-15:00"]
                }
            },
            {
                "firstname": "วิชัย",
                "lastname": "กล้าหาญ",
                "doctor_id": "D003",
                "specialist": "ศัลยกรรม",
                "status": "ยุ่ง",
                "schedule": {
                    "friday": ["13:00-20:00"]
                }
            }
        ]

        for data in dummy_doctors:
            # ตรวจสอบว่ามีหมอรหัสนี้อยู่แล้วหรือยัง
            existing = Doctor.query.filter_by(doctor_id=data["doctor_id"]).first()
            if not existing:
                new_doctor = Doctor(
                    firstname=data["firstname"],
                    lastname=data["lastname"],
                    doctor_id=data["doctor_id"],
                    specialist=data["specialist"],
                    status=data["status"],
                    schedule=data["schedule"]
                )
                db.session.add(new_doctor)
                print(f"Added doctor: {data['firstname']} {data['lastname']}")
            else:
                print(f"Doctor {data['doctor_id']} already exists, skipping...")

        db.session.commit()
        print("Seeding completed!")

if __name__ == "__main__":
    seed_doctors()
