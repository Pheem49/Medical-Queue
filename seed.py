import os
from datetime import date, time, datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Admin, Department, Doctor, DoctorToDepartment, AppointmentSlot, Booking
from services.booking_service import encrypt_national_id

def seed_database():
    with app.app_context():
        print("Starting expanded seed process...")
        
        # 1. Cleanup transient data (preserving User and Admin)
        print("Cleaning up Bookings, Slots, and Profiles...")
        db.session.query(Booking).delete()
        db.session.query(AppointmentSlot).delete()
        db.session.query(DoctorToDepartment).delete()
        db.session.query(Doctor).delete()
        db.session.query(Department).delete()
        db.session.commit()

        # Generate shared hash
        password_plain = "password123"
        hashed_pw = generate_password_hash(password_plain)

        # 2. Handle Admin
        admin = Admin.query.filter_by(Employee_id="EMP001").first()
        if not admin:
            print("Creating Admin...")
            admin = Admin(
                first_name="Admin",
                last_name="System",
                Employee_id="EMP001",
                User_name="admin01",
                hash_password=hashed_pw
            )
            db.session.add(admin)
        
        # 3. Handle Users (เพิ่มข้อมูลผู้ป่วยหลายคน)
        print("Checking/Creating Users...")
        users_data = [
            ("1234567890123", "สมชาย", "สายเสมอ", "somchai@example.com", "0812345678"),
            ("1234567890124", "สมหญิง", "จริงใจ", "somying@example.com", "0812345679"),
            ("1234567890125", "สมปอง", "น้องพี่", "sompong@example.com", "0812345680")
        ]
        created_users = []
        for nat_id, fname, lname, email, phone in users_data:
            user = User.query.filter_by(national_id=nat_id).first()
            if not user:
                user = User(
                    first_name=fname,
                    last_name=lname,
                    email=email,
                    national_id=nat_id,
                    date_of_birth=date(1990, 5, 20),
                    phone_number=phone,
                    password=hashed_pw
                )
                db.session.add(user)
                db.session.flush()
            created_users.append(user)


        # 4. Departments (Expanded)
        print("Creating Departments...")
        depts = [
            Department(name="แผนกอายุรกรรม (Internal Medicine)"),
            Department(name="แผนกศัลยกรรม (Surgery)"),
            Department(name="แผนกกุมารเวชกรรม (Pediatrics)"),
            Department(name="แผนกทันตกรรม (Dental)"),
            Department(name="แผนกจักษุ (Ophthalmology)")
        ]
        db.session.add_all(depts)
        db.session.flush()

        # 5. Doctors (Expanded)
        # Doctor Status: ว่าง, ว่างเช้า, ว่างบ่าย, คิวเต็มวันนี้
        print("Creating Doctors...")
        doctors = [
            Doctor(firstname="ประวัติ", lastname="ดีเด่น", doctor_id="DOC001", specialist="อายุรแพทย์", status="ว่าง", schedule={"mon": "09:00-16:00"}),
            Doctor(firstname="วิภา", lastname="รักษาสุข", doctor_id="DOC002", specialist="ศัลยแพทย์", status="ว่าง", schedule={"tue": "10:00-18:00"}),
            Doctor(firstname="มานะ", lastname="พากเพียร", doctor_id="DOC003", specialist="กุมารแพทย์", status="ว่าง", schedule={"wed": "09:00-12:00"}),
            Doctor(firstname="สมศรี", lastname="ดีงาม", doctor_id="DOC004", specialist="ทันตแพทย์", status="ว่าง", schedule={"thu": "09:00-16:00"}),
            Doctor(firstname="เก่งกาจ", lastname="สามารถ", doctor_id="DOC005", specialist="จักษุแพทย์", status="ว่าง", schedule={"fri": "13:00-17:00"})
        ]
        db.session.add_all(doctors)
        db.session.flush()

        # 6. Linking Doctors to Departments
        print("Linking Doctors to Departments...")
        for i in range(5):
            db.session.add(DoctorToDepartment(doctor_id=doctors[i].id, department_id=depts[i].department_id))

        # 7. Slots (Expanded: Past 7 days and future 4 days)
        # Slot Status: active, เต็ม, ไม่เปิดรับ
        print("Creating Appointment Slots (7 past days + 4 forward days)...")
        today = date.today()
        # เปลี่ยน Loop เป็นย้อนหลัง 7 วัน ถึงล่วงหน้า 3 วัน (-7 to 3)
        for i in range(-7, 4):
            slot_date = today + timedelta(days=i)
            for doc_idx, doc in enumerate(doctors):
                # สร้าง 2 slot ต่อวัน ต่อหมอ
                s1 = AppointmentSlot(
                    doctor_id=doc.id,
                    department_id=depts[doc_idx].department_id,
                    slot_date=slot_date,
                    start_time=time(9, 0) if i % 2 == 0 else time(13, 0),
                    end_time=time(10, 0) if i % 2 == 0 else time(14, 0),
                    max_capacity=10,
                    current_booking=0, # ตั้งเป็น 0 เพื่อให้กดลบเล่นได้
                    status="active"
                )
                s2 = AppointmentSlot(
                    doctor_id=doc.id,
                    department_id=depts[doc_idx].department_id,
                    slot_date=slot_date,
                    start_time=time(10, 0) if i % 2 == 0 else time(14, 0),
                    end_time=time(11, 0) if i % 2 == 0 else time(15, 0),
                    max_capacity=10,
                    current_booking=0,
                    status="active"
                )
                db.session.add_all([s1, s2])

        # 8. Sample Bookings (เพิ่มคิวข้อมูลย้อนหลังเยอะๆ)
        # Booking Status ที่ต้องการ: เสร็จสิ้น, ยกเลิก
        print("Creating Historical Bookings (เสร็จสิ้น, ยกเลิก)...")
        
        # ดึง Slot ทั้งหมดที่เป็นของอดีต (ก่อนวันนี้)
        past_slots = AppointmentSlot.query.filter(AppointmentSlot.slot_date < today).all()
        
        historical_bookings = []
        user_count = len(created_users)
        # ตัวนับคิวแยกตามแผนกและวันที่
        queue_counters = {}
        
        for idx, slot in enumerate(past_slots):
            # สลับสถานะ เสร็จสิ้น (80%) และ ยกเลิก (20%)
            status = "เสร็จสิ้น" if idx % 5 != 0 else "ยกเลิก"
            # กระจายคนไข้
            assigned_user = created_users[idx % user_count]
            
            # จำลองเวลาจองให้เป็นช่วงเวลาก่อนหน้าของ slot นั้นๆ เล็กน้อย
            # ใช้ datetime.now(datetime.UTC) หรือแค่ .now() ทั่วไปก็ได้ แต่ให้แน่ใจว่าค่าถูกต้อง
            booking_time = datetime.combine(slot.slot_date, slot.start_time) - timedelta(minutes=30)

            # คำนวณเลขคิวรายวันแยกตามแผนก
            key = (slot.department_id, slot.slot_date)
            queue_counters[key] = queue_counters.get(key, 0) + 1
            current_q = queue_counters[key]
            
            bk = Booking(
                slot_id=slot.slot_id,
                id_users=assigned_user.id,
                booking_at=booking_time,
                booking_Status=status,
                queue_number=current_q,
                detail=f"อาการปวดคิวที่ {current_q}",
                qr_code=encrypt_national_id(assigned_user.national_id)
            )
            historical_bookings.append(bk)
            
            # อัปเดต current_booking สำหรับ "เสร็จสิ้น" 
            # (ยกเลิก อาจจะไม่นับเป็น current_booking แต่ขึ้นอยู่กับ logic ของระบบคุณ 
            # ถ้าอยากให้ช่องนั้นเคยเต็มก็บวก 1 ได้เลย)
            slot.current_booking += 1

        if historical_bookings:
            db.session.add_all(historical_bookings)
        
        # คิวสำหรับ "วันนี้" (ถ้าต้องการให้มีโชว์หน้าระบบปัจจุบัน) 
        # ให้เป็น "เสร็จสิ้น" และ "ยกเลิก" ตามคำขอเท่านั้น
        print("Creating Today Bookings (เสร็จสิ้น, ยกเลิก)...")
        today_slot_doc1 = AppointmentSlot.query.filter_by(doctor_id=doctors[0].id, slot_date=today).first()
        today_slot_doc2 = AppointmentSlot.query.filter_by(doctor_id=doctors[1].id, slot_date=today).first()

        if today_slot_doc1 and len(created_users) >= 2:
            key1 = (today_slot_doc1.department_id, today)
            q1 = queue_counters.get(key1, 0) + 1
            queue_counters[key1] = q1
            b1 = Booking(
                slot_id=today_slot_doc1.slot_id,
                id_users=created_users[0].id,
                booking_at=datetime.combine(today, time(8, 30)),
                booking_Status="เสร็จสิ้น",
                queue_number=q1,
                detail="ปวดหัว มีไข้สูง",
                qr_code=encrypt_national_id(created_users[0].national_id)
            )

            q2 = queue_counters[key1] + 1
            queue_counters[key1] = q2
            b2 = Booking(
                slot_id=today_slot_doc1.slot_id,
                id_users=created_users[1].id,
                booking_at=datetime.combine(today, time(9, 30)),
                booking_Status="ยกเลิก",
                queue_number=q2,
                detail="ทดสอบตรวจเสร็จสิ้น อาการปกติ",
                qr_code=encrypt_national_id(created_users[1].national_id)
            )
            db.session.add_all([b1, b2])
            today_slot_doc1.current_booking += 2

        if today_slot_doc2 and len(created_users) >= 3:
            key2 = (today_slot_doc2.department_id, today)
            q3 = queue_counters.get(key2, 0) + 1
            queue_counters[key2] = q3
            b3 = Booking(
                slot_id=today_slot_doc2.slot_id,
                id_users=created_users[2].id,
                booking_at=datetime.combine(today, time(8, 0)),
                booking_Status="เสร็จสิ้น",
                queue_number=q3,
                detail="ปวดท้องเรื้อรัง",
                qr_code=encrypt_national_id(created_users[2].national_id)
            )
            db.session.add(b3)
            today_slot_doc2.current_booking += 1

        db.session.commit()
        print("\nSuccessfully seeded the database with expanded data!")
        print(f"Added: {len(depts)} Departments, {len(doctors)} Doctors, and dozens of Slots.")
        print("All slots have current_booking=0 for immediate deletion testing.")

if __name__ == "__main__":
    seed_database()
