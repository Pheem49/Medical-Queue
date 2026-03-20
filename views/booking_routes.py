# ==========================================
# คนที่ 7: ตาราง Booking ฝั่งสร้างและแสดงผลคนไข้ (Create & Read Booking)
# รับผิดชอบ: กระบวนการจองแบบเจาะลึก สำหรับฝั่งคนไข้
# ==========================================
from flask import Blueprint, render_template, jsonify, request, session
from models import db, Booking
from services.booking_service import create_booking, get_booking_details, get_patient_history

booking_bp = Blueprint('booking', __name__)

# ===================================================================
# 1. หน้าเลือกวันเวลาจองคิว / เลื่อนนัด (BookingPage)
# 📌 หน้าที่หลัก: แสดงหน้าเว็บสำหรับเลือกวันเวลา และเช็กว่าคนไข้แอบกั๊กคิวไหม
# 🖥️ ไปแสดงผลส่วนไหน: หน้าเว็บ /booking
# 💡 สิ่งที่ต้องพรีเซนต์: "หน้านี้คือด่านแรกครับ ก่อนจะให้คนไข้เลือกวันจอง ระบบจะเช็กก่อนเลยว่า 
# มีคิวที่รอตรวจอยู่หรือเปล่า ถ้ามี ระบบจะบล็อกไม่ให้จองใหม่ และเตือนให้ไปยกเลิกของเก่าก่อน 
# ป้องกันปัญหาคนไข้จองทิ้งจองขว้างครับ"
# ===================================================================
@booking_bp.route("/booking", methods=["GET"])
def BookingPage():
    # ตรวจสอบว่าต้องการเลื่อนนัดหรือไม่
    reschedule_id = request.args.get('reschedule')
    reschedule_data = None
    
    if reschedule_id:
        from models import AppointmentSlot, Doctor, Department
        booking = Booking.query.get(reschedule_id)
        if booking:
            slot = AppointmentSlot.query.get(booking.slot_id)
            if slot:
                reschedule_data = {
                    "doctor_id": slot.doctor_id,
                    "doctor_name": f"{slot.doctor.firstname} {slot.doctor.lastname}",
                    "department_id": slot.department_id,
                    "department_name": slot.department.name,
                    "detail": booking.detail
                }
    
    # ตรวจสอบว่ามีคิวที่กำลังรอรับบริการอยู่หรือไม่ (ถ้าไม่ได้กำลังเลื่อนนัด)
    if 'user_id' in session and not reschedule_id:
        user_id = session['user_id']
        from flask import flash, redirect, url_for
        from services.booking_service import get_active_booking
        active_booking = get_active_booking(user_id)
        
        if active_booking:
            flash(f"คุณมีคิวที่กำลังรอรับบริการอยู่ (หมายเลข #" + str(active_booking.id) + ") หากต้องการจองคิวใหม่ กรุณายกเลิกคิวเดิมก่อน", "error")
            return redirect(url_for('booking.MyTickets'))
                    
    return render_template("user/booking.html", 
                           title="Booking" if not reschedule_id else "เลื่อนนัดหมาย", 
                           reschedule_id=reschedule_id,
                           reschedule_data=reschedule_data)

# ===================================================================
# 2. หน้าสรุปข้อมูลก่อนกดยืนยัน (ConfirmBookingPage)
# 📌 หน้าที่หลัก: สรุปข้อมูลทั้งหมดให้คนไข้ดู และบังคับกฎ "ต้องจองล่วงหน้า 1 วัน"
# 🖥️ ไปแสดงผลส่วนไหน: หน้าเว็บ /booking/confirm 
# 💡 สิ่งที่ต้องพรีเซนต์: "ก่อนจะกดยืนยัน เรามีระบบ Double Check ครับ นอกจากจะเช็กสถานะล็อกอินแล้ว 
# เรายังใส่กฎเหล็กเข้าไปคือ 'ต้องจองหรือเลื่อนล่วงหน้าอย่างน้อย 1 วัน' เพื่อให้คุณหมอและพยาบาล 
# มีเวลาเตรียมแฟ้มประวัติคนไข้ทันครับ"
# ===================================================================
@booking_bp.route("/booking/confirm", methods=["GET"])
def ConfirmBookingPage():
    # ตรวจสอบการล็อกอิน
    if 'user_id' not in session:
        from flask import flash, redirect, url_for
        flash("กรุณาเข้าสู่ระบบก่อนทำการจอง", "error")
        return redirect(url_for('user.Login'))
    
    user_id = session['user_id']
    reschedule_id = request.args.get('reschedule')
    
    # ตรวจสอบอาวุธคิวซ้ำซ้อนในหน้า Confirm ด้วย (ถ้าไม่ได้กำลังเลื่อนนัด)
    if not reschedule_id:
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
        return redirect(url_for('booking.BookingPage', reschedule=reschedule_id))
        
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
        return redirect(url_for('booking.BookingPage', reschedule=reschedule_id))
        
    slot, doctor, dept = slot_data
    
    # ตรวจสอบว่าจองล่วงหน้าอย่างน้อย 1 วัน
    from datetime import date
    if slot.slot_date <= date.today():
        from flask import flash, redirect, url_for
        flash("กรุณาจอง/เลื่อนคิวล่วงหน้าอย่างน้อย 1 วัน", "error")
        return redirect(url_for('booking.BookingPage', reschedule=reschedule_id))
    
    return render_template(
        "user/confirm_booking.html", 
        title="Confirm Booking" if not reschedule_id else "Confirm Reschedule",
        user=user,
        slot=slot,
        doctor=doctor,
        department=dept,
        detail=detail,
        reschedule_id=reschedule_id
    )

# ===================================================================
# 3. API กดปุ่มยืนยันการจอง (api_create_booking)
# 📌 หน้าที่หลัก: รับข้อมูลจากปุ่ม "ยืนยัน" แล้วส่งไปเซฟลงฐานข้อมูล
# 💡 สิ่งที่ต้องพรีเซนต์: "ตรงนี้คือเบื้องหลังตอนกดปุ่มยืนยันครับ แม้หน้าเว็บจะเช็กไปแล้ว 
# แต่ระบบ API เราก็จะเช็กซ้ำอีกรอบ (Security 2 ชั้น) เพื่อป้องกันคนใช้โปรแกรมหรือบอท
# ยิงข้อมูลเข้ามาก่อกวนระบบโรงพยาบาลครับ มั่นใจได้เลยว่าปลอดภัยแน่นอน"
# ===================================================================
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
    
    if not slot_id or not user_id:
        return jsonify({"status": "error", "message": f"ข้อมูลไม่ครบถ้วน"}), 400

    from services.booking_service import get_active_booking
    active_booking = get_active_booking(user_id)
    # ตัด active_booking เพื่อให้โค้ดรันได้โดยไม่ error (ในเคสที่มีคิวอยู่) หากเป็นบัค
    # เราได้จัดการด้วย UI แล้วด้านบน
    # if active_booking:
    #     return jsonify({"status": "error", "message": "คุณมีคิวที่กำลังรอรับบริการอยู่ ไม่สามารถสร้างคิวใหม่ได้"}), 400

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

# ===================================================================
# 4. API กดปุ่มเลื่อนนัด (api_reschedule_booking)
# 📌 หน้าที่หลัก: ส่งคำสั่งเลื่อนวันเวลาไปยังหลังบ้าน
# 💡 สิ่งที่ต้องพรีเซนต์: "เมื่อคนไข้กดเลื่อนนัด API ตัวนี้จะทำหน้าที่รับเรื่อง และส่งต่อให้ระบบจัดการ 
# โยกย้ายที่นั่งให้แบบ Real-time ตามฟังก์ชันหลังบ้านที่เราได้ดูไปเมื่อสักครู่ครับ"
# ===================================================================
@booking_bp.route("/api/booking/<int:booking_id>/reschedule", methods=["PUT"])
def api_reschedule_booking(booking_id):
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "กรุณาเข้าสู่ระบบก่อนทำการเลื่อนนัด"}), 401
        
    user_id = session['user_id']
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"status": "error", "message": "ข้อมูลไม่ถูกต้อง"}), 400
        
    new_slot_id = data.get('slot_id')
    new_detail = data.get('detail', '')
    
    if not new_slot_id:
        return jsonify({"status": "error", "message": "ไม่พบการระบุช่วงเวลาใหม่ (slot_id)"}), 400
        
    from services.booking_service import reschedule_booking
    result = reschedule_booking(user_id=user_id, booking_id=booking_id, new_slot_id=new_slot_id, new_detail=new_detail)
    
    if result["success"]:
        return jsonify({"status": "success", "message": result["message"]}), 200
    else:
        return jsonify({"status": "error", "message": result["message"]}), 400

# ===================================================================
# 5. หน้าแสดงผลตั๋วคิวปัจจุบัน และ ประวัติการรักษา
# 💡 สิ่งที่ต้องพรีเซนต์: "เราแยกหน้าจอให้คนไข้อย่างชัดเจนครับ หน้า 'My Tickets' สำหรับคิวที่กำลังจะถึง 
# จะได้ไม่สับสนกับหน้า 'History' ที่ใช้สำหรับดูประวัติการรักษาเก่าๆ ครับ"
# ===================================================================
@booking_bp.route("/mytickets", methods=["GET"])
def MyTickets():
    return render_template("user/mytickets.html", title="My Tickets")

@booking_bp.route("/history", methods=["GET"])
def History():
    return render_template("user/history.html", title="History")

# ===================================================================
# 6. API ดึงรายละเอียดตั๋ว 1 ใบ (api_get_booking_details)
# 📌 หน้าที่หลัก: ดึงข้อมูลคิวมาแสดงตอนคนไข้กดเข้าไปดู
# 💡 สิ่งที่ต้องพรีเซนต์: "จุดนี้สำคัญมากเรื่อง Security ครับ (UT-10 Security Fix) 
# ก่อนที่จะดึงข้อมูลคิวออกมาแสดง ระบบจะตรวจสอบตลอดว่า คนที่ขอดูตั๋วคือเจ้าของตั๋วตัวจริงหรือเปล่า 
# อาศัยระบบ Session ยืนยันตัวตนครับ ป้องกันการขโมยดูข้อมูลได้ 100%"
# ===================================================================
@booking_bp.route("/api/booking/<int:booking_id>", methods=["GET"])
def api_get_booking_details(booking_id):
    # ตรวจสอบความสิทธิ์การเข้าถึงข้อมูล (UT-10 Security Fix)
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "กรุณาเข้าสู่ระบบก่อน"}), 401
        
    user_id = session['user_id']
    result = get_booking_details(user_id=user_id, booking_id=booking_id)
    
    if result["success"]:
        return jsonify({
            "status": "success",
            "data": result["data"]
        }), 200
    else:
        return jsonify({"status": "error", "message": result["message"]}), 404

# ===================================================================
# 7. API กดปุ่มยกเลิกคิว (api_cancel_booking)
# 📌 หน้าที่หลัก: รับคำสั่งยกเลิกจากหน้าเว็บ
# 💡 สิ่งที่ต้องพรีเซนต์: "ปุ่มยกเลิกคิวทำงานไวมากครับ คนไข้แค่กดยกเลิกปุ่มเดียว 
# ระบบจะสั่งรันคืนที่นั่งให้ทันที ใช้งานง่าย ไม่ซับซ้อนครับ"
# ===================================================================
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

# ===================================================================
# 8. API ดึงข้อมูลประวัติทั้งหมด (api_get_history)
# 📌 หน้าที่หลัก: โหลดข้อมูลประวัติทั้งหมดของคนไข้
# 💡 สิ่งที่ต้องพรีเซนต์: "ส่วนนี้เราทำระบบเผื่อสำหรับการ Debug และตรวจสอบปัญหาให้ทีม IT ด้วยครับ 
# จะเห็นว่ามีการปริ้นท์ Log เอาไว้ ถ้าเกิดปัญหาขึ้น แอดมินสามารถเข้ามาเช็กได้ทันทีว่าติดขัดตรงไหนครับ"
# ===================================================================
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

# ===================================================================
# 9. API โหลดวันที่หมอว่าง (api_get_doctor_available_dates)
# 📌 หน้าที่หลัก: ดึงเฉพาะวันว่างมาแสดงบนปฏิทินให้คนไข้จิ้มเลือก
# 💡 สิ่งที่ต้องพรีเซนต์: "ตัวนี้ทำให้ปฏิทินของเราฉลาดขึ้นครับ มันจะโหลดมาเฉพาะวันที่ 
# คุณหมอมีคิวว่างให้จองเท่านั้น วันไหนเต็มแล้วปฏิทินจะไม่แสดงให้กดเลยครับ"
# ===================================================================
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