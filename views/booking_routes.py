from flask import Blueprint, render_template, jsonify, request
from models import db, Booking
from services.booking_service import create_booking, get_booking_details, get_patient_history

booking_bp = Blueprint('booking', __name__)

@booking_bp.route("/booking", methods=["GET"])
def BookingPage():
    return render_template("user/booking.html", title="Booking")

@booking_bp.route("/api/bookings", methods=["POST"])
def api_create_booking():
    data = request.get_json(silent=True)
    
    if data is None:
        return jsonify({"status": "error", "message": "ไม่สามารถอ่านข้อมูล JSON ได้ กรุณาตรวจสอบ Content-Type หรือรูปแบบ JSON"}), 400
    
    # รับค่าจาก Request
    slot_id = data.get('slot_id')
    user_id = data.get('id_users') # ในอนาคตควรดึงจาก Session หรือ Token
    detail = data.get('detail', '') # อาการเบื้องต้น (ถ้ามี)
    
    if not slot_id or not user_id:
        return jsonify({"status": "error", "message": "ข้อมูลไม่ครบถ้วน (ต้องการ slot_id และ id_users)"}), 400

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

@booking_bp.route("/api/history/<int:user_id>", methods=["GET"])
def api_get_history(user_id):
    # API เพิ่มเติมสำหรับดึงประวัติการจองของ User นำไปแสดงในหน้า history/mytickets
    result = get_patient_history(user_id=user_id)
    
    if result["success"]:
        return jsonify({
            "status": "success",
            "data": result["data"]
        }), 200
    else:
         return jsonify({"status": "error", "message": "ไม่สามารถดึงข้อมูลประวัติได้"}), 500
