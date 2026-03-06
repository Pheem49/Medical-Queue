from flask import Blueprint, render_template, jsonify, request, session
from models import db, Booking
from services.booking_service import create_booking, get_booking_details, get_patient_history

booking_bp = Blueprint('booking', __name__)

@booking_bp.route("/booking", methods=["GET"])
def BookingPage():
    return render_template("user/booking.html", title="Booking")

@booking_bp.route("/booking/confirm", methods=["GET"])
def ConfirmBookingPage():
    # ตรวจสอบการล็อกอิน
    if 'user_id' not in session:
        return render_template("user/error.html", message="กรุณาเข้าสู่ระบบก่อนทำการจอง"), 401
    
    user_id = session['user_id']
    slot_id = request.args.get('slot_id')
    detail = request.args.get('detail', '')
    
    if not slot_id:
        return render_template("user/error.html", message="ข้อมูลการจองไม่ครบถ้วน กรุณากลับไปเลือกเวลาใหม่"), 400
        
    from models import User, AppointmentSlot, Doctor, Department
    
    user = User.query.get(user_id)
    slot_data = db.session.query(
        AppointmentSlot, Doctor, Department
    ).join(
        Doctor, AppointmentSlot.doctor_id == Doctor.id
    ).join(
        Department, AppointmentSlot.department_id == Department.department_id
    ).filter(
        AppointmentSlot.slot_id == slot_id
    ).first()
    
    if not slot_data or not user:
        return render_template("user/error.html", message="ไม่พบข้อมูลการจองที่ระบุ"), 404
        
    slot, doctor, dept = slot_data
    
    return render_template(
        "user/confirm_booking.html", 
        title="Confirm Booking",
        user=user,
        slot=slot,
        doctor=doctor,
        department=dept,
        detail=detail
    )

@booking_bp.route("/api/bookings", methods=["POST"])
def api_create_booking():
    data = request.get_json(silent=True)
    
    if data is None:
        return jsonify({"status": "error", "message": "ไม่สามารถอ่านข้อมูล JSON ได้ กรุณาตรวจสอบ Content-Type หรือรูปแบบ JSON"}), 400
    
    # รับค่าจาก Request
    slot_id = data.get('slot_id')
    
    # ดึง User ID จาก Session
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "กรุณาเข้าสู่ระบบก่อนทำการจอง"}), 401
    
    user_id = session['user_id']
    detail = data.get('detail', '') # อาการเบื้องต้น (ถ้ามี)
    
    print(f"DEBUG - slot_id from request: {slot_id} (type: {type(slot_id)})")
    print(f"DEBUG - user_id from session: {user_id} (type: {type(user_id)})")
    
    if not slot_id or not user_id:
        return jsonify({"status": "error", "message": f"ข้อมูลไม่ครบถ้วน (ต้องการ slot_id: {slot_id} และ id_users: {user_id})"}), 400

    # เรียกใช้ Service ทำการจอง
    result = create_booking(user_id=user_id, slot_id=slot_id, detail=detail)
    
    if result["success"]:
        return jsonify({
            "status": "success", 
            "message": result["message"],
            "booking_id": result["booking_id"],
            "qr_code": result["qr_code"]
        }), 201
    else:
        return jsonify({"status": "error", "message": result["message"]}), 400

@booking_bp.route("/mytickets", methods=["GET"])
def MyTickets():
    return render_template("user/mytickets.html", title="My Tickets")

@booking_bp.route("/history", methods=["GET"])
def History():
    return render_template("user/history.html", title="History")

@booking_bp.route("/api/booking/<int:booking_id>", methods=["GET"])
def api_get_booking_details(booking_id):
    # สมมติชั่วคราวว่า user_id = 1 (ในระบบจริงควรดึงจาก session ของการ Login)
    # เพื่อให้สามารถทดสอบฟังก์ชัน get_booking_details ที่มีการเช็คสิทธิ์ได้
    user_id = request.args.get('user_id', 1, type=int) 
    
    result = get_booking_details(user_id=user_id, booking_id=booking_id)
    
    if result["success"]:
        return jsonify({
            "status": "success",
            "data": result["data"]
        }), 200
    else:
        return jsonify({"status": "error", "message": result["message"]}), 404

@booking_bp.route("/api/history", methods=["GET"])
def api_get_history():
    # API เพิ่มเติมสำหรับดึงประวัติการจองของ User นำไปแสดงในหน้า history/mytickets
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "กรุณาเข้าสู่ระบบก่อน"}), 401
        
    user_id = session['user_id']
    print(f"DEBUG api_get_history - session user_id: {user_id}")
    result = get_patient_history(user_id=user_id)
    print(f"DEBUG api_get_history - returned result: {result}")
    
    if result["success"]:
        return jsonify({
            "status": "success",
            "data": result["data"]
        }), 200
    else:
         return jsonify({"status": "error", "message": "ไม่สามารถดึงข้อมูลประวัติได้"}), 500

@booking_bp.route("/api/scan/decrypt", methods=["POST"])
def api_decrypt_qr():
    """
    API สำหรับพนักงานโรงพยาบาล ใช้ถอดรหัส QR Code token กลับเป็นเลขบัตรประชาชน
    เรียกได้เฉพาะ Staff session เท่านั้น (เพื่อความปลอดภัย)
    Request body: { "token": "<encrypted_qr_code>" }
    Response: { "status": "success", "national_id": "1234567890123" }
    """
    # ตรวจสอบว่าเป็น Staff
    if 'staff_id' not in session:
        return jsonify({"status": "error", "message": "สำหรับเจ้าหน้าที่เท่านั้น"}), 403
    
    data = request.get_json(silent=True)
    if not data or 'token' not in data:
        return jsonify({"status": "error", "message": "ไม่พบข้อมูล token"}), 400
    
    from services.booking_service import decrypt_national_id
    
    token = data['token']
    national_id = decrypt_national_id(token)
    
    if national_id is None:
        return jsonify({"status": "error", "message": "QR Code ไม่ถูกต้องหรือหมดอายุ"}), 400
    
    # ค้นหาข้อมูลคนไข้จากเลขบัตรประชาชน
    from models import User
    user = User.query.filter_by(national_id=national_id).first()
    
    if not user:
        return jsonify({"status": "error", "message": "ไม่พบข้อมูลผู้ป่วยในระบบ"}), 404
    
    return jsonify({
        "status": "success",
        "national_id": national_id,
        "patient_name": f"{user.first_name} {user.last_name}"
    }), 200
