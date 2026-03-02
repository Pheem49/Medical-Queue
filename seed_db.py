from app import app
from models import db, User, Admin, Department, Doctor, AppointmentSlot, Booking
from datetime import date, time, datetime, timedelta
import random

def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("Creating Departments...")
        dep1 = Department(name="อายุรกรรม (Internal Medicine)")
        dep2 = Department(name="กุมารเวชกรรม (Pediatrics)")
        db.session.add_all([dep1, dep2])
        db.session.commit()

        print("Creating Doctors...")
        doc1 = Doctor(
            firstname="สมชาย",
            lastname="ใจดี",
            doctor_id="DOC001",
            specialist="โรคหัวใจ",
            status="ว่าง",
            schedule={"mon": "09:00-12:00", "wed": "13:00-16:00"}
        )
        doc2 = Doctor(
            firstname="สมหญิง",
            lastname="รักเรียน",
            doctor_id="DOC002",
            specialist="โรคเด็ก",
            status="ว่าง",
            schedule={"tue": "09:00-12:00", "thu": "09:00-12:00"}
        )
        db.session.add_all([doc1, doc2])
        db.session.commit()

        print("Creating Slots...")
        today = date.today()
        slots = []
        # Create slots for doc 1
        for i in range(3):
            slot = AppointmentSlot(
                doctor_id=doc1.id,
                department_id=dep1.department_id,
                slot_date=today,
                start_time=time(9 + i, 0),
                end_time=time(9 + i, 30),
                max_capacity=5,
                current_booking=0,
                status="ว่าง"
            )
            slots.append(slot)
        
        # Create slots for doc 2
        for i in range(2):
            slot = AppointmentSlot(
                doctor_id=doc2.id,
                department_id=dep2.department_id,
                slot_date=today,
                start_time=time(14 + i, 0),
                end_time=time(14 + i, 30),
                max_capacity=5,
                current_booking=0,
                status="ว่าง"
            )
            slots.append(slot)
        
        db.session.add_all(slots)
        db.session.commit()

        print("Creating Users...")
        users = []
        for i in range(5):
            user = User(
                first_name=f"Patient{i}",
                last_name=f"Test{i}",
                email=f"patient{i}@example.com",
                national_id=f"123456789000{i}",
                date_of_birth=date(1990, 1, 1),
                phone_number=f"081234567{i}",
                password="password123"
            )
            users.append(user)
        db.session.add_all(users)
        db.session.commit()

        print("Creating Bookings...")
        bookings = []
        for i in range(5):
            # Book first 5 patients into first 5 slots
            slot = slots[i]
            user = users[i]
            booking = Booking(
                slot_id=slot.slot_id,
                id_users=user.id,
                booking_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
                booking_Status="รอรับบริการ",
                detail=f"มีอาการปวดหัวตัวร้อน รายการที่ {i+1}",
                qr_code=f"QR_CODE_DATA_{i+1}"
            )
            slot.current_booking += 1
            bookings.append(booking)
        
        db.session.add_all(bookings)
        db.session.commit()

        print("Creating Admin...")
        admin = Admin(
            first_name="Admin",
            last_name="System",
            Employee_id="ADM001",
            User_name="admin",
            hash_password="hashed_password_here"
        )
        db.session.add(admin)
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()
