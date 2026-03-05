from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash # นำเข้าเครื่องมือต่างๆ จาก Flask เช่น Blueprint, render_template, session เป็นต้น
from services.user_service import register_user, login_user, update_user_profile # นำเข้าฟังก์ชันจัดการผู้ใช้ที่เขียนไว้ใน user_service

user_bp = Blueprint('user', __name__) # สร้าง Blueprint ชื่อ 'user' เพื่อจัดกลุ่มเส้นทาง (Routes) ที่เกี่ยวกับผู้ใช้

# --- Frontend Routes (GET) --- # ส่วนที่ใช้แสดงหน้าเว็บ (หน้าตา UI)

@user_bp.route("/login", methods=["GET"]) # กำหนดเส้นทาง URL /login สำหรับเปิดดูหน้าเข้าสู่ระบบ
def Login(): # ฟังก์ชันสำหรับจัดการหน้า Login
    return render_template("auth/login.html", title="Login") # ส่งไฟล์ HTML หน้า Login ไปแสดงผลที่ Browser

@user_bp.route("/register", methods=["GET"]) # กำหนดเส้นทาง URL /register สำหรับเปิดดูหน้าลงทะเบียน
def Register(): # ฟังก์ชันสำหรับจัดการหน้า Register
    return render_template("auth/register.html", title="Register") # ส่งไฟล์ HTML หน้าลงทะเบียนไปแสดงผล

@user_bp.route("/notification", methods=["GET"]) # กำหนดเส้นทาง URL /notification สำหรับหน้าแจ้งเตือน
def Notification(): # ฟังก์ชันสำหรับหน้าแจ้งเตือน
    return render_template("user/notification.html", title="Notifications") # แสดงหน้าแจ้งเตือน

@user_bp.route("/terms", methods=["GET"]) # กำหนดเส้นทาง URL /terms สำหรับหน้าเงื่อนไขการใช้งาน
def Terms(): # ฟังก์ชันสำหรับหน้า Terms
    return render_template("user/terms.html", title="Terms of Service") # แสดงหน้าเงื่อนไขการใช้งาน

@user_bp.route("/privacy", methods=["GET"]) # กำหนดเส้นทาง URL /privacy สำหรับหน้าสำรองข้อมูลส่วนบุคคล
def Privacy(): # ฟังก์ชันสำหรับหน้า Privacy
    return render_template("user/privacy.html", title="Privacy Policy") # แสดงหน้านโยบายความเป็นส่วนตัว

# --- API Routes (POST / PUT) --- # ส่วนที่ใช้จัดการข้อมูล (การส่งข้อมูลหลังบ้าน)

@user_bp.route("/api/register", methods=["POST"]) # เส้นทาง API สำหรับประมวลผลการลงทะเบียน
def api_register(): # ฟังก์ชันรับข้อมูลลงทะเบียน
    data = request.get_json() if request.is_json else request.form.to_dict() # ตรวจสอบวิธีส่งข้อมูลว่าเป็น JSON หรือส่งจาก Form ปกติ แล้วเก็บไว้ในตัวแปร data
    
    # Map frontend field names to backend model fields # แปลงชื่อฟิลด์จากหน้าเว็บให้ตรงกับชื่อที่ฐานข้อมูลใช้
    mapped_data = {
        'first_name': data.get('first_name'), # รับชื่อจริง
        'last_name': data.get('last_name'), # รับนามสกุล
        'email': data.get('email'), # รับอีเมล
        'national_id': data.get('idCard') or data.get('national_id'), # รับเลขบัตร (รองรับทั้งชื่อ idCard และ national_id)
        'date_of_birth': data.get('dob') or data.get('date_of_birth'), # รับวันเกิด (รองรับทั้ง dob และ date_of_birth)
        'phone_number': data.get('phone') or data.get('phone_number'), # รับเบอร์โทร (รองรับทั้ง phone และ phone_number)
        'password': data.get('password') # รับรหัสผ่าน
    }
    
    # Check password confirmation if available # ตรวจสอบการยืนยันรหัสผ่าน
    confirm_password = data.get('confirm_password') # รับรหัสผ่านที่กรอกยืนยัน
    if confirm_password and mapped_data['password'] != confirm_password: # ถ้ามีข้อมูลและรหัสไม่ตรงกัน
        message = "Passwords do not match" # ข้อความแจ้งเตือนว่ารหัสไม่ตรงกัน
        if request.is_json: # ถ้าส่งมาแบบ JSON
            return jsonify({"success": False, "message": message}), 400 # ส่ง JSON กลับไปบอกว่าผิดพลาด
        else: # ถ้าส่งมาจาก Form ปกติ
            flash(message, "error") # เก็บข้อความแจ้งเตือนไว้ในระบบ Flash Message
            return redirect(url_for('user.Register')) # ให้ Browser กลับไปหน้าลงทะเบียนใหม่

    success, message = register_user(mapped_data) # เรียกฟังก์ชัน register_user เพื่อบันทึกลงฐานข้อมูล
    
    if request.is_json: # ถ้าส่งมาแบบ JSON (เช่นใช้ JavaScript/Fetch)
        if success: # ถ้าบันทึกสำเร็จ
            return jsonify({"success": True, "message": message}), 201 # ส่งสถานะสำเร็จกลับไป
        else: # ถ้าบันทึกล้มเหลว
            return jsonify({"success": False, "message": message}), 400 # ส่งข้อความแจ้งสาเหตุที่ล้มเหลวกลับไป
    else: # ถ้าส่งมาจาก Form ปกติ (แบบกดปุ่มคลิก)
        if success: # ถ้าสำเร็จ
            flash(message, "success") # แจ้งข้อความสำเร็จ
            return redirect(url_for('user.Login')) # ส่งผู้ใช้ไปที่หน้า Login
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
    
    if success: # ถ้าเข้าสู่ระบบสำเร็จ
        # result is user object # ผลลัพธ์ที่ได้คือออบเจกต์ข้อมูลผู้ใช้
        user = result # เก็บข้อมูลผู้ใช้ไว้ในตัวแปร user
        # Store user info in session # เก็บข้อมูลที่จำเป็นไว้ในระบบ Session เพื่อให้คอมพิวเตอร์จำได้ว่าเราล็อกอินอยู่
        session['user_id'] = user.id # บันทึก ID ผู้ใช้
        session['user_name'] = f"{user.first_name} {user.last_name}" # บันทึกชื่อ-นามสกุล
        session['email'] = user.email # บันทึกอีเมล
        
        if request.is_json: # ถ้าส่งแบบ JSON
            return jsonify({ # ส่งข้อมูลผู้ใช้กลับไปในรูปแบบ JSON
                "success": True, 
                "message": "Login successful",
                "user": user.to_dict()
            }), 200
        else: # ถ้าส่งจาก Form ปกติ
            return redirect(url_for('department.Home')) # ส่งผู้ใช้ไปที่หน้าหลักของระบบ
    else: # ถ้าเข้าสู่ระบบไม่ได้
        # result is error message # ผลลัพธ์จะเป็นข้อความแจ้งว่าทำไมถึงผิด
        if request.is_json: # ถ้าส่งแบบ JSON
            return jsonify({"success": False, "message": result}), 401 # แจ้ง error กลับไป
        else: # ถ้าส่งจาก Form
            flash(result, "error") # เก็บข้อความแจ้งเตือน
            return redirect(url_for('user.Login')) # ให้กลับไปหน้าเข้าสู่ระบบใหม่
        
@user_bp.route("/api/logout", methods=["POST"]) # เส้นทาง API สำหรับการออกจากระบบ
def api_logout(): # ฟังก์ชันจัดการการ Logout
    session.clear() # ทำความสะอาดหรือลบข้อมูลทั้งหมดที่เคยจำไว้ใน Session
    return jsonify({"success": True, "message": "Logout successful"}), 200 # ส่งข้อความยืนยันการออกจากระบบสำเร็จ

@user_bp.route("/api/user/profile", methods=["PUT"]) # เส้นทาง API สำหรับแก้ไขข้อมูลโปรไฟล์
def api_update_profile(): # ฟังก์ชันแก้ไขข้อมูลส่วนตัว
    # Retrieve user_id from session or from request data # ดึง ID ผู้ใช้มาจากระบบ Session
    # Assuming user must be logged in to update profile # ตรวจสอบก่อนว่าผู้ใช้ได้ล็อกอินอยู่หรือไม่
    if 'user_id' not in session: # ถ้ายังไม่ล็อกอิน
        return jsonify({"success": False, "message": "Unauthorized"}), 401 # แจ้งว่าไม่มีสิทธิ์เข้าถึง
        
    user_id = session['user_id'] # เก็บ ID ผู้ใช้
    data = request.json # รับข้อมูลใหม่ที่จะแก้ไขในรูปแบบ JSON
    
    success, message = update_user_profile(user_id, data) # ส่งไปแก้ไขใน user_service
    
    if success: # ถ้าแก้ไขสำเร็จ
        # Update session name if changed # ถ้ามีการเปลี่ยนชื่อหรือนามสกุลจริง ให้ระบบจำชื่อใหม่ด้วย
        if 'first_name' in data or 'last_name' in data: # ตรวจสอบว่ามีฟิลด์ชื่อในข้อมูลส่งมาไหม
             from models import User # นำเข้าโมเดล User มาใช้ค้นหา
             user = User.query.get(user_id) # หาข้อมูลล่าสุดในฐานข้อมูล
             if user: # ถ้าเจอข้อมูล
                 session['user_name'] = f"{user.first_name} {user.last_name}" # อัปเดตชื่อใน Session ให้เป็นปัจจุบัน
        return jsonify({"success": True, "message": message}), 200 # แจ้งกลับไปว่าอัปเดตสำเร็จ
    else: # ถ้ามีปัญหาเกิดขึ้น
        return jsonify({"success": False, "message": message}), 400 # แจ้งสาเหตุที่ไม่สำเร็จ
