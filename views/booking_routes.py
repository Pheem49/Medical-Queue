# ==========================================
# คนที่ 7: ตาราง Booking ฝั่งสร้างและแสดงผลคนไข้ (Create & Read Booking)
# รับผิดชอบ: กระบวนการจองแบบเจาะลึก สำหรับฝั่งคนไข้
# ==========================================
from flask import Blueprint, render_template, jsonify, request, session
from models import db, Booking
from services.booking_service import create_booking, get_booking_details, get_patient_history

booking_bp = Blueprint('booking', __name__)

@booking_bp.route("/booking", methods=["GET"])
def BookingPage():
    # ตรวจสอบว่ามีคิวที่กำลังรอรับบริการอยู่หรือไม่
    if 'user_id' in session:
        user_id = session['user_id']
        from flask import flash, redirect, url_for
        from services.booking_service import get_active_booking
        active_booking = get_active_booking(user_id)
        
        if active_booking:
            flash(f"คุณมีคิวที่กำลังรอรับบริการอยู่ (หมายเลข #" + str(active_booking.id) + ") หากต้องการจองคิวใหม่ กรุณายกเลิกคิวเดิมก่อน", "error")
            return redirect(url_for('booking.MyTickets'))
                    
    return render_template("user/booking.html", title="Booking")

@booking_bp.route("/booking/confirm", methods=["GET"])
def ConfirmBookingPage():
    # ตรวจสอบการล็อกอิน
    if 'user_id' not in session:
        from flask import flash, redirect, url_for
        flash("กรุณาเข้าสู่ระบบก่อนทำการจอง", "error")
        return redirect(url_for('user.Login'))
    
    user_id = session['user_id']
    
    # ตรวจสอบอาวุธคิวซ้ำซ้อนในหน้า Confirm ด้วย
    from services.booking_service import get_active_booking
    active_booking = get_active_booking(user_id)
    
    if active_booking:
        from flask import flash, redirect, url_for
        flash(f"คุณมีคิวที่กำลังรอรับบริการอยู่ ไม่สามารถดำเนินการจองใหม่ได้", "error")
        return redirect(url_for('booking.MyTickets'))

    slot_id = request.args.get('slot_id')
    detail = request.args.get('detail', '')
    
    if not slot_id:
        from flask import flash, redirect, url_for
        flash("ข้อมูลการจองไม่ครบถ้วน กรุณากลับไปเลือกเวลาใหม่", "error")
        return redirect(url_for('booking.BookingPage'))
        
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
        from flask import flash, redirect, url_for
        flash("ไม่พบข้อมูลการจองที่ระบุ", "error")
        return redirect(url_for('booking.BookingPage'))
        
    slot, doctor, dept = slot_data
    
    # ตรวจสอบว่าจองล่วงหน้าอย่างน้อย 1 วัน
    from datetime import date
    if slot.slot_date <= date.today():
        from flask import flash, redirect, url_for
        flash("กรุณาจองคิวล่วงหน้าอย่างน้อย 1 วัน", "error")
        return redirect(url_for('booking.BookingPage'))
    
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

@booking_bp.route("/api/booking/<int:booking_id>/cancel", methods=["POST"])
def api_cancel_booking(booking_id):
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "กรุณาเข้าสู่ระบบก่อน"}), 401
        
    user_id = session['user_id']
    from services.booking_service import cancel_booking
    result = cancel_booking(user_id=user_id, booking_id=booking_id)
    
    if result["success"]:
        return jsonify({"status": "success", "message": result["message"]}), 200
    else:
        return jsonify({"status": "error", "message": result["message"]}), 400

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


@booking_bp.route("/api/doctor/<int:doctor_id>/available-dates", methods=["GET"])
def api_get_doctor_available_dates(doctor_id):
    """
    API สำหรับดึงรายการวันที่แพทย์คนนี้มีคิวว่าง
    """
    from services.booking_service import get_available_dates
    dates = get_available_dates(doctor_id)
    return jsonify({
        "status": "success",
        "dates": dates
    }), 200
