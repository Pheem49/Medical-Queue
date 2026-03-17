# ==========================================
# คนที่ 8: ตาราง Booking ฝั่งควบคุมและอัปเดต (Admin Booking Management)
# รับผิดชอบ: หลังบ้านคิวทั้งหมด การเรียกคิว และเปลี่ยนแปลงสถานะคิว
# ==========================================
from flask import Blueprint, jsonify, request, session, render_template, redirect, url_for
from models import db, Booking
from services import booking_management_service

booking_management_bp = Blueprint('booking_management', __name__)

@booking_management_bp.route("/staff/patients", methods=["GET"])
def StaffPatients():
    """หน้าของเจ้าหน้าที่ (Admin) สำหรับดูผู้ป่วยของวันนี้"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_auth.StaffLogin'))
    return render_template("admin/dashboard.html", title="Today's Patients")

@booking_management_bp.route("/staff/history", methods=["GET"])
def StaffHistory():
    """หน้าของเจ้าหน้าที่ (Admin) สำหรับดูประวัติการจองทั้งหมด"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_auth.StaffLogin'))
    return render_template("admin/history.html", title="ประวัติการรับบริการ")

# ====== API Routes ======
@booking_management_bp.route("/api/admin/bookings", methods=["GET"])
def api_get_admin_bookings():
    date_filter = request.args.get('date') # รับค่า 'date' จาก query string (e.g., ?date=2023-10-27)
    bookings = booking_management_service.get_all_bookings_for_admin(date_filter)
    if bookings is None:
        return jsonify({"error": "Failed to retrieve bookings"}), 500
    return jsonify(bookings)

@booking_management_bp.route("/api/admin/bookings/<int:booking_id>/status", methods=["PUT"])
def api_update_admin_booking_status(booking_id):
    data = request.get_json()
    new_status = data.get('status')

    if not new_status:
        return jsonify({"error": "Missing status"}), 400

    updated_booking, error = booking_management_service.update_booking_status(booking_id, new_status)

    if error:
        return jsonify({"error": error}), 404

    return jsonify(updated_booking)

@booking_management_bp.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
def api_delete_booking(booking_id):
    """
    Endpoint สำหรับลบการจอง ซึ่งอาจถูกเรียกโดยคนไข้หรือเจ้าหน้าที่
    """
    success, message = booking_management_service.delete_booking_and_update_slot(booking_id)

    if not success:
        return jsonify({"error": message}), 404

    return jsonify({"status": "success", "message": message})

@booking_management_bp.route("/api/admin/bookings/<int:booking_id>", methods=["GET"])
def api_get_admin_booking_details(booking_id):
    """
    Endpoint สำหรับดึงข้อมูลการจองด้วย Booking ID สำหรับเจ้าหน้าที่ (ใช้ในหน้า Scanner)
    """
    # ดึงข้อมูลโดยไม่ต้องตรวจ user_id ของคนไข้
    from models import Doctor, Department, AppointmentSlot, User
    
    booking_data = db.session.query(
        Booking, AppointmentSlot, Doctor, Department, User
    ).join(
        AppointmentSlot, Booking.slot_id == AppointmentSlot.slot_id
    ).join(
        Doctor, AppointmentSlot.doctor_id == Doctor.id
    ).join(
        Department, AppointmentSlot.department_id == Department.department_id
    ).join(
        User, Booking.id_users == User.id
    ).filter(
        Booking.id == booking_id
    ).first()

    if not booking_data:
        return jsonify({"status": "error", "message": "ไม่พบข้อมูลการจอง"}), 404

    booking, slot, doctor, dept, user = booking_data

    # ปรับ format ให้ตรงกับที่ Dashboard นำไปใช้
    return jsonify({
        "status": "success",
        "data": {
            "booking_id": booking.id,
            "status": booking.booking_Status,
            "patient_name": f"{user.first_name} {user.last_name}",
            "detail": booking.detail,
            "slot_date": slot.slot_date.isoformat() if slot.slot_date else None,
            "start_time": slot.start_time.strftime('%H:%M') if slot.start_time else None,
            "end_time": slot.end_time.strftime('%H:%M') if slot.end_time else None,
            "queue_number": booking.queue_number,
            "doctor_name": f"{doctor.firstname} {doctor.lastname}",
            "department_name": dept.name
        }
    }), 200

@booking_management_bp.route("/api/admin/history", methods=["GET"])
def api_get_admin_history():
    """
    Endpoint สำหรับดึงข้อมูลประวัติการจองทั้งหมดสำหรับเจ้าหน้าที่
    """
    if 'admin_id' not in session:
        return jsonify({"status": "error", "message": "สำหรับเจ้าหน้าที่เท่านั้น"}), 403

    from models import Doctor, Department, AppointmentSlot, User
    from sqlalchemy import desc

    # ดึงข้อมูลการจองทั้งหมด และเรียงตามวันที่จองล่าสุด
    history_data = db.session.query(
        Booking, AppointmentSlot, Doctor, Department, User
    ).join(
        AppointmentSlot, Booking.slot_id == AppointmentSlot.slot_id
    ).join(
        Doctor, AppointmentSlot.doctor_id == Doctor.id
    ).join(
        Department, AppointmentSlot.department_id == Department.department_id
    ).join(
        User, Booking.id_users == User.id
    ).order_by(desc(Booking.id)).all()

    results = []
    for booking, slot, doctor, dept, user in history_data:
        results.append({
            "booking_id": booking.id,
            "status": booking.booking_Status,
            "patient_name": f"{user.first_name} {user.last_name}",
            "national_id": user.national_id,
            "phone_number": user.phone_number,
            "detail": booking.detail,
            "queue_number": booking.queue_number,
            "slot": {
                "department_id": slot.department_id,
                "department_name": dept.name
            },
            "slot_date": slot.slot_date.isoformat() if slot.slot_date else None,
            "start_time": slot.start_time.strftime('%H:%M') if slot.start_time else None,
            "end_time": slot.end_time.strftime('%H:%M') if slot.end_time else None,
            "doctor_name": f"{doctor.firstname} {doctor.lastname}",
            "department_name": dept.name
        })

    return jsonify({
        "status": "success",
        "data": results
    }), 200
