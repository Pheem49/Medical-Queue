from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def register_user(data): 
    if not data: 
        return False, "No data provided" 

    # Check required fields # ตรวจสอบฟิลด์ที่จำเป็นต้องมี
    required_fields = ['first_name', 'last_name', 'email', 'national_id', 'date_of_birth', 'phone_number', 'password']
    for field in required_fields: 
        value = data.get(field)
        if not value or (isinstance(value, str) and not value.strip()):
            return False, f"Missing required field: {field}" 

    # Check if email or national_id already exists # ตรวจสอบว่าอีเมลหรือเลขบัตรประชาชนซ้ำกับที่มีอยู่แล้วหรือไม่
    if User.query.filter_by(email=data['email']).first(): 
        return False, "Email already exists"
    
    if User.query.filter_by(national_id=data['national_id']).first():
        return False, "National ID already exists"
    
    # Process date of birth # จัดการรูปแบบวันที่เกิด
    try:
       
        dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    except ValueError: 
        return False, "Invalid date format. Use YYYY-MM-DD" 
    
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
        db.session.add(new_user)
        db.session.commit() 
        return True, "User registered successfully"
    except Exception as e: 
        db.session.rollback() 
        return False, str(e) 

def login_user(identifier, password): # ฟังก์ชันสำหรับตรวจสอบการเข้าสู่ระบบ
    if not identifier or not password: 
        return False, "Phone Number/National ID and password are required" 
        
    # Check both phone_number and national_id # ค้นหาผู้ใช้โดยใช้เบอร์โทรศัพท์ หรือ เลขบัตรประชาชน
    user = User.query.filter(
        (User.phone_number == identifier) | (User.national_id == identifier)
    ).first() 
    
    # ตรวจสอบว่าเจอผู้ใช้ไหม และรหัสผ่านที่กรอกมาตรงกับที่เข้ารหัสไว้ในฐานข้อมูลหรือไม่
    if user and check_password_hash(user.password, password):
        return True, user 
    
    return False, "Invalid credentials" 

def update_user_profile(user_id, update_data): 
    user = User.query.get(user_id) 
    if not user: 
        return False, "User not found" 
    
    if not update_data: 
        return False, "No update data provided" 
    
    # ม่ยอมให้แก้ไขอีเมลหรือเลขบัตรผ่านทางนี้ง่ายๆ เพื่อป้องกันปัญหาเรื่องข้อมูลซ้ำ
    
    if 'phone_number' in update_data: # ถ้ามีการขอแก้ไขเบอร์โทรศัพท์
        user.phone_number = update_data['phone_number'] # อัปเดตเบอร์โทรใหม่
    if 'first_name' in update_data: # ถ้ามีการขอแก้ไขชื่อจริง
        user.first_name = update_data['first_name'] # อัปเดตชื่อใหม่
    if 'last_name' in update_data: # ถ้ามีการขอแก้ไขนามสกุล
        user.last_name = update_data['last_name'] # อัปเดตนามสกุลใหม่
        
    try:
        db.session.commit() # ยืนยันการบันทึกการเปลี่ยนแปลงลงฐานข้อมูล
        return True, "Profile updated successfully" 
    except Exception as e: # ถ้าบันทึกไม่สำเร็จ
        db.session.rollback() # คืนค่าเดิม
        return False, str(e)
