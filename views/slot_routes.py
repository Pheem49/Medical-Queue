# ==========================================
# คนที่ 6: ตาราง AppointmentSlot (ตารางเวลาการเปิดเปิดคิว)
# รับผิดชอบ: เวลาแต่ละสล็อตที่พยาบาลหรือหมอเปิดรับคนไข้ และระบบ Scanner
# ==========================================
from flask import Blueprint, render_template, jsonify, request
from models import db, AppointmentSlot
from services.slot_service import create_appointment_slot, update_slot_status, get_slots_by_doctor_date

slot_bp = Blueprint('slot', __name__)

@slot_bp.route("/staff/checkin", methods=["GET"])
def StaffCheckin():
    return render_template("admin/scanner.html", title="Staff Check-in")

@slot_bp.route("/api/admin/slots", methods=["POST"])
def api_admin_create_slot():
    try:
        data = request.json
        doctor_id = data.get('doctor_id')
        department_id = data.get('department_id')
        slot_date = data.get('slot_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        max_capacity = data.get('max_capacity')
        
        create_appointment_slot(doctor_id, department_id, slot_date, start_time, end_time, max_capacity)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@slot_bp.route("/api/admin/slots", methods=["GET"])
def api_admin_get_slots():
    doctor_id = request.args.get('doctor_id')
    date_str = request.args.get('date')
    if not doctor_id or not date_str:
        return jsonify([])
        
    slots = get_slots_by_doctor_date(doctor_id, date_str)
    return jsonify(slots)

@slot_bp.route("/api/admin/slots/<int:slot_id>/status", methods=["PUT"])
def api_admin_update_slot_status(slot_id):
    data = request.json
    new_status = data.get('status')
    if update_slot_status(slot_id, new_status):
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Slot not found"}), 404

@slot_bp.route("/api/admin/slots/<int:slot_id>", methods=["DELETE"])
def api_admin_delete_slot(slot_id):
    from services.slot_service import delete_appointment_slot
    if delete_appointment_slot(slot_id):
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Cannot delete slot because it might be booked or not found"}), 400

@slot_bp.route("/api/scan/decrypt", methods=["POST"])
def api_decrypt_qr():
    """
    API สำหรับพนักงานโรงพยาบาล ใช้ถอดรหัส QR Code token กลับเป็นเลขบัตรประชาชน
    เรียกได้เฉพาะ Staff session เท่านั้น (เพื่อความปลอดภัย)
    """
    from flask import session
    # ตรวจสอบว่าเป็น Staff
    if 'admin_id' not in session:
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
    from models import User, Booking, AppointmentSlot, Doctor, Department
    user = User.query.filter_by(national_id=national_id).first()
    
    if not user:
        return jsonify({"status": "error", "message": "ไม่พบข้อมูลผู้ป่วยในระบบ"}), 404
    
    # ดึงคิวของคนไข้คนนี้ ที่มีสถานะ รอรับบริการ หรืออื่นๆ แบบล่าสุด
    from sqlalchemy import desc
    active_booking_data = db.session.query(
        Booking, AppointmentSlot, Doctor, Department
    ).join(
        AppointmentSlot, Booking.slot_id == AppointmentSlot.slot_id
    ).join(
        Doctor, AppointmentSlot.doctor_id == Doctor.id
    ).join(
        Department, AppointmentSlot.department_id == Department.department_id
    ).filter(
        Booking.id_users == user.id,
        Booking.booking_Status == 'รอรับบริการ'
    ).order_by(desc(Booking.id)).first()

    if not active_booking_data:
         return jsonify({
             "status": "error", 
             "message": f"ผู้ป่วย {user.first_name} {user.last_name} ไม่มีคิวที่กำลังรอรับบริการในขณะนี้"
         }), 404
         
    booking, slot, doctor, dept = active_booking_data
    
    return jsonify({
        "status": "success",
        "data": {
            "booking_id": booking.id,
            "national_id": national_id,
            "patient_name": f"{user.first_name} {user.last_name}",
            "status": booking.booking_Status,
            "detail": booking.detail,
            "slot_date": slot.slot_date.isoformat() if slot.slot_date else None,
            "start_time": slot.start_time.strftime('%H:%M') if slot.start_time else None,
            "end_time": slot.end_time.strftime('%H:%M') if slot.end_time else None,
            "doctor_name": f"{doctor.firstname} {doctor.lastname}",
            "department_name": dept.name
        }
    }), 200
