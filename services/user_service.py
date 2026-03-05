from models import db, User # นำเข้าออบเจกต์ฐานข้อมูล (db) และโมเดลตารางผู้ใช้ (User)
from werkzeug.security import generate_password_hash, check_password_hash # นำเข้าเครื่องมือสำหรับเข้ารหัสและตรวจสอบรหัสผ่าน
from datetime import datetime # นำเข้าเครื่องมือสำหรับจัดการวันที่และเวลา

def register_user(data): # ฟังก์ชันสำหรับลงทะเบียนผู้ใช้ใหม่
    if not data: # ถ้าไม่มีข้อมูลส่งมา
        return False, "No data provided" # ส่งสถานะเท็จพร้อมข้อความแจ้งเตือน

    # Check required fields # ตรวจสอบฟิลด์ที่จำเป็นต้องมี
    required_fields = ['first_name', 'last_name', 'email', 'national_id', 'date_of_birth', 'phone_number', 'password']
    for field in required_fields: # วนลูปเช็คทีละฟิลด์
        if field not in data or not data[field]: # ถ้าไม่มีฟิลด์นั้นหรือฟิลด์นั้นว่างเปล่า
            return False, f"Missing required field: {field}" # ส่งกลับว่าขาดข้อมูลฟิลด์ไหน

    # Check if email or national_id already exists # ตรวจสอบว่าอีเมลหรือเลขบัตรประชาชนซ้ำกับที่มีอยู่แล้วหรือไม่
    if User.query.filter_by(email=data['email']).first(): # ค้นหาอีเมลในฐานข้อมูล
        return False, "Email already exists" # ถ้าเจอ แสดงว่าซ้ำ
    
    if User.query.filter_by(national_id=data['national_id']).first(): # ค้นหาเลขบัตรประชาชนในฐานข้อมูล
        return False, "National ID already exists" # ถ้าเจอ แสดงว่าซ้ำ
    
    # Process date of birth # จัดการรูปแบบวันที่เกิด
    try:
        # แปลงข้อความวันที่ (เช่น 1990-01-01) ให้เป็นออบเจกต์วันที่ของ Python
        dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    except ValueError: # ถ้าแปลงไม่สำเร็จ (รูปแบบผิด)
        return False, "Invalid date format. Use YYYY-MM-DD" # แจ้งให้ใช้รูปแบบที่ถูกต้อง
    
    # เข้ารหัสผ่านก่อนบันทึกลงฐานข้อมูลเพื่อความปลอดภัย
    hashed_password = generate_password_hash(data['password'])
    
    # สร้างออบเจกต์ผู้ใช้ใหม่พร้อมข้อมูลที่ได้รับมา
    new_user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        national_id=data['national_id'],
        date_of_birth=dob,
        phone_number=data['phone_number'],
        password=hashed_password
    )
    
    try:
        db.session.add(new_user) # เตรียมเพิ่มข้อมูลผู้ใช้ใหม่เข้าสู่ Session ของฐานข้อมูล
        db.session.commit() # ยืนยันการบันทึกข้อมูลลงฐานข้อมูลจริง
        return True, "User registered successfully" # ส่งกลับว่าสำเร็จ
    except Exception as e: # ถ้าเกิดข้อผิดพลาดในการบันทึก
        db.session.rollback() # ยกเลิกการทำงานทั้งหมดของ Session นี้ (คืนค่าเดิม)
        return False, str(e) # ส่งกลับแจ้งความผิดพลาดที่เกิดขึ้น

def login_user(identifier, password): # ฟังก์ชันสำหรับตรวจสอบการเข้าสู่ระบบ
    if not identifier or not password: # ถ้าไม่มีข้อมูลการล็อกอินส่งมา
        return False, "Phone Number/National ID and password are required" # แจ้งว่าต้องระบุข้อมูล
        
    # Check both phone_number and national_id # ค้นหาผู้ใช้โดยใช้เบอร์โทรศัพท์ หรือ เลขบัตรประชาชน
    user = User.query.filter(
        (User.phone_number == identifier) | (User.national_id == identifier)
    ).first() # ดึงข้อมูลคนแรกที่เจอ
    
    # ตรวจสอบว่าเจอผู้ใช้ไหม และรหัสผ่านที่กรอกมาตรงกับที่เข้ารหัสไว้ในฐานข้อมูลหรือไม่
    if user and check_password_hash(user.password, password):
        return True, user # ถ้าถูกต้อง ส่งสถานะสำเร็จพร้อมข้อมูลผู้ใช้
    
    return False, "Invalid credentials" # ถ้าไม่ถูกต้อง ส่งสถานะล้มเหลว

def update_user_profile(user_id, update_data): # ฟังก์ชันสำหรับแก้ไขข้อมูลส่วนตัว
    user = User.query.get(user_id) # ค้นหาผู้ใช้จาก ID ที่ระบุ
    if not user: # ถ้าไม่เจอผู้ใช้
        return False, "User not found" # แจ้งว่าไม่พบผู้ใช้
    
    if not update_data: # ถ้าไม่มีข้อมูลที่จะแก้ไขส่งมา
        return False, "No update data provided" # แจ้งว่าไม่มีข้อมูล
    
    # We shouldn't allow updating email or national_id easily due to unique constraints
    # (เราจะไม่ยอมให้แก้ไขอีเมลหรือเลขบัตรผ่านทางนี้ง่ายๆ เพื่อป้องกันปัญหาเรื่องข้อมูลซ้ำ)
    
    if 'phone_number' in update_data: # ถ้ามีการขอแก้ไขเบอร์โทรศัพท์
        user.phone_number = update_data['phone_number'] # อัปเดตเบอร์โทรใหม่
    if 'first_name' in update_data: # ถ้ามีการขอแก้ไขชื่อจริง
        user.first_name = update_data['first_name'] # อัปเดตชื่อใหม่
    if 'last_name' in update_data: # ถ้ามีการขอแก้ไขนามสกุล
        user.last_name = update_data['last_name'] # อัปเดตนามสกุลใหม่
        
    try:
        db.session.commit() # ยืนยันการบันทึกการเปลี่ยนแปลงลงฐานข้อมูล
        return True, "Profile updated successfully" # แจ้งว่าอัปเดตสำเร็จ
    except Exception as e: # ถ้าบันทึกไม่สำเร็จ
        db.session.rollback() # คืนค่าเดิม
        return False, str(e) # แจ้งข้อผิดพลาด
