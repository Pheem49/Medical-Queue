# ==========================================
# คนที่ 1: ตาราง User (จัดการคนไข้)
# รับผิดชอบ: ข้อมูลผู้สมัคร / ผู้ป่วยทั่วไปทั้งหมด
# ==========================================
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from services.user_service import register_user, login_user, update_user_profile 

user_bp = Blueprint('user', __name__) # สร้าง Blueprint ชื่อ 'user' เพื่อจัดกลุ่มเส้นทาง (Routes) ที่เกี่ยวกับผู้ใช้

# --- Frontend Routes (GET) --- # ส่วนที่ใช้แสดงหน้าเว็บ (หน้าตา UI)

@user_bp.route("/login", methods=["GET"]) # กำหนดเส้นทาง URL /login สำหรับเปิดดูหน้าเข้าสู่ระบบ
def Login():
    return render_template("auth/login.html", title="Login") # ส่งไฟล์ HTML หน้า Login ไปแสดงผลที่ Browser

@user_bp.route("/register", methods=["GET"]) # กำหนดเส้นทาง URL /register สำหรับเปิดดูหน้าลงทะเบียน
def Register():
    return render_template("auth/register.html", title="Register") # ส่งไฟล์ HTML หน้าลงทะเบียนไปแสดงผล

@user_bp.route("/notification", methods=["GET"]) # กำหนดเส้นทาง URL /notification สำหรับหน้าแจ้งเตือน
def Notification():
    if 'user_id' not in session:
        return redirect(url_for('user.Login'))
    
    from models import Booking, AppointmentSlot, Department, Doctor
    # ดึงข้อมูลการจอง 5 รายการล่าสุดเพื่อทำเป็น Notification Feed
    notifications = Booking.query.filter_by(id_users=session['user_id'])\
        .join(AppointmentSlot, Booking.slot_id == AppointmentSlot.slot_id)\
        .join(Department, AppointmentSlot.department_id == Department.department_id)\
        .join(Doctor, AppointmentSlot.doctor_id == Doctor.id)\
        .order_by(Booking.id.desc()).limit(5).all()
        
    return render_template("user/notification.html", title="Notifications", notifications=notifications)

@user_bp.route("/terms", methods=["GET"]) # กำหนดเส้นทาง URL /terms สำหรับหน้าเงื่อนไขการใช้งาน
def Terms():
    return render_template("user/terms.html", title="Terms of Service") # แสดงหน้าเงื่อนไขการใช้งาน

@user_bp.route("/privacy", methods=["GET"]) # กำหนดเส้นทาง URL /privacy สำหรับหน้าสำรองข้อมูลส่วนบุคคล
def Privacy():
    return render_template("user/privacy.html", title="Privacy Policy") # แสดงหน้านโยบายความเป็นส่วนตัว

# --- API Routes (POST / PUT) --- # ส่วนที่ใช้จัดการข้อมูล (การส่งข้อมูลหลังบ้าน)

@user_bp.route("/api/register", methods=["POST"]) # เส้นทาง API สำหรับประมวลผลการลงทะเบียน
def api_register():
    data = request.get_json() if request.is_json else request.form.to_dict() # ตรวจสอบวิธีส่งข้อมูลว่าเป็น JSON หรือส่งจาก Form ปกติ แล้วเก็บไว้ในตัวแปร data
    
    # Map frontend field names to backend model fields # แปลงชื่อฟิลด์จากหน้าเว็บให้ตรงกับชื่อที่ฐานข้อมูลใช้
    mapped_data = {
        'first_name': data.get('first_name'), 
        'last_name': data.get('last_name'), 
        'email': data.get('email'), 
        'national_id': data.get('idCard') or data.get('national_id'), 
        'date_of_birth': data.get('dob') or data.get('date_of_birth'), 
        'phone_number': data.get('phone') or data.get('phone_number'), 
        'password': data.get('password') 
    }
    
    # Check password confirmation if available # ตรวจสอบการยืนยันรหัสผ่าน
    confirm_password = data.get('confirm_password') 
    if confirm_password and mapped_data['password'] != confirm_password: 
        message = "Passwords do not match" 
        if request.is_json: 
            return jsonify({"success": False, "message": message}), 400 
        else: 
            flash(message, "error") 
            return redirect(url_for('user.Register')) 

    success, message = register_user(mapped_data) 
    
    if request.is_json: # ถ้าส่งมาแบบ JSON (เช่นใช้ JavaScript/Fetch)
        if success: 
            return jsonify({"success": True, "message": message}), 201 
        else: # ถ้าบันทึกล้มเหลว
            return jsonify({"success": False, "message": message}), 400 
    else: 
        if success: 
            flash(message, "success") 
            return redirect(url_for('user.Login')) 
        else: # ถ้าไม่สำเร็จ
            flash(message, "error") # แจ้งข้อความที่ผิดพลาด
            return redirect(url_for('user.Register')) # ให้กลับไปหน้าลงทะเบียนอีกครั้ง

@user_bp.route("/api/login", methods=["POST"]) # เส้นทาง API สำหรับการเข้าสู่ระบบ
def api_login(): # ฟังก์ชันจัดการการ Login
    data = request.get_json() if request.is_json else request.form.to_dict() # รับข้อมูลได้ทั้งแบบ JSON และ Form
    
    if not data: # ถ้าไม่มีข้อมูลส่งมาเลย
         return jsonify({"success": False, "message": "No data provided"}), 400 # ส่งข้อความเตือนกลับไป
         
    identifier = data.get("identifier") or data.get("email") # รับค่าชื่อล็อกอิน (อาจเป็นเบอร์โทรหรือเลขบัตร)
    password = data.get("password") # รับรหัสผ่าน
    
    success, result = login_user(identifier, password) # ส่งไปให้ user_service ตรวจสอบความถูกต้อง
    
    if success: 
        
        user = result 
        
        session['user_id'] = user.id 
        session['user_name'] = f"{user.first_name} {user.last_name}" 
        session['email'] = user.email 
        
        if request.is_json: 
            return jsonify({ 
                "success": True, 
                "message": "Login successful",
                "user": user.to_dict()
            }), 200
        else: 
            return redirect(url_for('department.Home')) # ส่งผู้ใช้ไปที่หน้าหลักของระบบ
    else: # ถ้าเข้าสู่ระบบไม่ได้
        # result is error message # ผลลัพธ์จะเป็นข้อความแจ้งว่าทำไมถึงผิด
        if request.is_json: # ถ้าส่งแบบ JSON
            return jsonify({"success": False, "message": result}), 401 # แจ้ง error กลับไป
        else: # ถ้าส่งจาก Form
            flash(result, "error") # เก็บข้อความแจ้งเตือน
            return redirect(url_for('user.Login')) # ให้กลับไปหน้าเข้าสู่ระบบใหม่
        

@user_bp.route("/api/user/profile", methods=["PUT"]) 
def api_update_profile(): 
 
    if 'user_id' not in session: # ถ้ายังไม่ล็อกอิน
        return jsonify({"success": False, "message": "Unauthorized"}), 401 
    user_id = session['user_id'] 
    data = request.json 
    
    success, message = update_user_profile(user_id, data) 
    
    if success: 

        if 'first_name' in data or 'last_name' in data: 
             from models import User 
             user = User.query.get(user_id) 
             if user: # ถ้าเจอข้อมูล
                 session['user_name'] = f"{user.first_name} {user.last_name}" 
        return jsonify({"success": True, "message": message}), 200 
    else: # ถ้ามีปัญหาเกิดขึ้น
        return jsonify({"success": False, "message": message}), 400 
