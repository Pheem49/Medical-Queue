from flask_sqlalchemy import SQLAlchemy
# อย่าลืม import date และ time ไว้ที่ด้านบนสุดของไฟล์ models.py ด้วยนะครับ
from datetime import date, time, datetime

# สร้างตัวแทนฐานข้อมูล (ยังไม่ผูกกับ app หลัก)
db = SQLAlchemy()


# --- user ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # ชื่อจริง - นามสกุล
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    
    # Email (ควรตั้งให้ห้ามซ้ำ)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # เลขบัตรประชาชน (13 หลัก และควรตั้งให้ห้ามซ้ำ)
    national_id = db.Column(db.String(13), unique=True, nullable=False)
    
    # วันเดือนปีเกิด (เก็บเป็น Date)
    date_of_birth = db.Column(db.Date, nullable=False) 
    
    # เบอร์โทรศัพท์
    phone_number = db.Column(db.String(15), nullable=False)
    
    # รหัสผ่าน (เผื่อความยาวไว้ 120 สำหรับการเข้ารหัสผ่านแบบ Hash ในอนาคต)
    password = db.Column(db.String(120), nullable=False)


class Admin(db.Model):
    id_admin = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)

    Employee_id = db.Column(db.String(20), unique=True, nullable=False)

    User_name = db.Column(db.String(50), unique=True , )

    hash_password = db.Column(db.String(255), nullable=False)


class Department(db.Model):
    # รหัสแผนก (Primary Key) auto - ใช้ db.Integer จะรันตัวเลขอัตโนมัติให้เอง
    department_id = db.Column(db.Integer, primary_key=True)
    
    # ชื่อแผนก - ใช้ db.String สำหรับข้อความ (เผื่อความยาวไว้ 100 ตัวอักษร)
    name = db.Column(db.String(100), nullable=False)


class Doctor(db.Model):
    # รหัสแพทย์ (Primary Key) auto
    id = db.Column(db.Integer, primary_key=True)
    
    # ชื่อจริง
    firstname = db.Column(db.String(80), nullable=False)
    
    # นามสกุล
    lastname = db.Column(db.String(80), nullable=False)
    
    # รหัสพนักงาน (เพิ่ม unique=True เพื่อไม่ให้รหัสพนักงานหมอซ้ำกันครับ)
    doctor_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # ความเชี่ยวชาญ
    specialist = db.Column(db.String(100), nullable=False)
    
    # สถานะแพทย์ (เช่น ว่างวันนี้/ว่างเช้า/ว่างบ่าย/เต็มวันนี
    status = db.Column(db.String(50), nullable=False)
    
    # ตารางแพทย์ (ใช้ db.JSON เพื่อเก็บข้อมูลรูปแบบ JSON ตามที่ออกแบบไว้)
    schedule = db.Column(db.JSON, nullable=True)


class DoctorToDepartment(db.Model):
    # กำหนดชื่อตารางในฐานข้อมูลให้ชัดเจน
    __tablename__ = 'doctor_to_department'
    
    # รหัสความสัมพันธ์ (Primary Key) auto
    id = db.Column(db.Integer, primary_key=True)
    
    # รหัสแพทย์ (Foreign Key) - เชื่อมกับช่อง id ของตาราง doctor
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    
    # รหัสแผนก (Foreign Key) - เชื่อมกับช่อง department_id ของตาราง department
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id'), nullable=False)


class AppointmentSlot(db.Model):
    # ตั้งชื่อตารางให้ตรงกับที่ออกแบบไว้
    __tablename__ = 'appointment_slots'
    
    # รหัสนัด (Primary Key) auto
    slot_id = db.Column(db.Integer, primary_key=True)
    
    # รหัสแพทย์ (Foreign Key) - เชื่อมกับตาราง doctor
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    
    # รหัสแผนก (Foreign Key) - เชื่อมกับตาราง department
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id'), nullable=False)
    
    # วันที่ในการจอง (เช่น 2026-10-10)
    slot_date = db.Column(db.Date, nullable=False)
    
    # เวลาที่เริ่มจอง (เช่น 09:00:00)
    start_time = db.Column(db.Time, nullable=False)
    
    # เวลาที่สิ้นสุดจากจอง (เช่น 09:29:00)
    end_time = db.Column(db.Time, nullable=False)
    
    # จำนวนคิวสูงสุดที่สามารถรับได้ใน Slot นี้
    max_capacity = db.Column(db.Integer, nullable=False)
    
    # จำนวนคิวปัจจุบัน (ใส่ค่าเริ่มต้น default=0 ไว้ เพราะตอนสร้าง Slot แรกๆ คิวจะยังเป็น 0 เสมอครับ)
    current_booking = db.Column(db.Integer, default=0, nullable=False)
    
    # สถานะของคิว (เช่น ว่าง/ไม่ว่าง/ไม่เปิดรับ)
    status = db.Column(db.String(50), nullable=False)


class Booking(db.Model):
    # กำหนดชื่อตาราง
    __tablename__ = 'booking'
    
    # รหัสการจองคิว (Primary Key) auto
    id = db.Column(db.Integer, primary_key=True)
    
    # รหัสนัด (Foreign Key) - เชื่อมกับตาราง appointment_slots
    slot_id = db.Column(db.Integer, db.ForeignKey('appointment_slots.slot_id'), nullable=False)
    
    # รหัสผู้ใช้ (Foreign Key) - เชื่อมกับตาราง user (สมมติว่าตารางคนไข้ชื่อ user)
    id_users = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # วันที่ทำการจองและเวลา (Timestamp)
    # ใช้ db.DateTime และให้ระบบตั้งค่าเวลาปัจจุบันตอนที่กดจองให้อัตโนมัติ (default=datetime.utcnow)
    booking_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # สถานะยืนยันการเข้ารับบริการ (เช่น รอรับบริการ/มารับบริการ/ยกเลิก)
    booking_Status = db.Column(db.String(50), default="รอรับบริการ", nullable=False)
    
    # อาการเบื้องต้น (ใช้ db.Text เพราะอาการคนไข้อาจจะพิมพ์ยาวกว่า 255 ตัวอักษร)
    detail = db.Column(db.Text, nullable=True)
    
    # คิวอาร์โค้ดการจอง (เก็บเป็นข้อความ/รหัสอ้างอิงของ QR Code)
    qr_code = db.Column(db.String(255), nullable=True)