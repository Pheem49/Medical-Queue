from models import db, Booking, AppointmentSlot, Doctor, Department
import uuid

def create_booking(user_id, slot_id, detail):
    # ค้นหา Slot
    slot = AppointmentSlot.query.get(slot_id)
    if not slot:
        return {"success": False, "message": "ไม่พบเวลานัดหมายนี้"}
    
    # ตรวจสอบว่าคิวเต็มหรือยัง
    if slot.current_booking >= slot.max_capacity:
        return {"success": False, "message": "คิวนัดหมายนี้เต็มแล้ว"}
    
    # เพิ่มจำนวนคิวที่จองแล้ว (current_booking)
    slot.current_booking += 1
    
    # ถ้าคิวเต็มพอดี ให้อัปเดตสถานะ (ถ้าต้องการ) เช่น
    if slot.current_booking >= slot.max_capacity:
        slot.status = "เต็ม"

    # สร้างคิวอาร์โค้ด
    qr_code_ref = uuid.uuid4().hex

    # สร้างการจองใหม่
    new_booking = Booking(
        slot_id=slot.slot_id,
        id_users=user_id,
        detail=detail,
        qr_code=qr_code_ref
    )
    
    db.session.add(new_booking)
    
    try:
        db.session.commit()
        return {
            "success": True, 
            "message": "จองคิวสำเร็จ", 
            "booking_id": new_booking.id,
            "qr_code": qr_code_ref
        }
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}"}

def get_patient_history(user_id):
    # ดึงประวัติการจองทั้งหมดของคนไข้คนนี้
    # Join ข้อมูล Slot, Doctor, Department เพื่อให้ได้ข้อมูลครบถ้วนสำหรับแสดงผล
    history = db.session.query(
        Booking, AppointmentSlot, Doctor, Department
    ).join(
        AppointmentSlot, Booking.slot_id == AppointmentSlot.slot_id
    ).join(
        Doctor, AppointmentSlot.doctor_id == Doctor.id
    ).join(
        Department, AppointmentSlot.department_id == Department.department_id
    ).filter(
        Booking.id_users == user_id
    ).order_by(
        Booking.booking_at.desc()
    ).all()
    
    results = []
    for booking, slot, doctor, dept in history:
        results.append({
            "booking_id": booking.id,
            "booking_at": booking.booking_at.isoformat() if booking.booking_at else None,
            "status": booking.booking_Status,
            "detail": booking.detail,
            "qr_code": booking.qr_code,
            "slot_date": slot.slot_date.isoformat() if slot.slot_date else None,
            "start_time": slot.start_time.strftime('%H:%M') if slot.start_time else None,
            "end_time": slot.end_time.strftime('%H:%M') if slot.end_time else None,
            "doctor_name": f"{doctor.firstname} {doctor.lastname}",
            "department_name": dept.name
        })
        
    return {"success": True, "data": results}

def cancel_booking(user_id, booking_id):
    pass

def get_booking_details(user_id, booking_id):
    # ค้นหาการจองตาม ID และต้องเป็นของ user ที่ขอดู
    booking_data = db.session.query(
        Booking, AppointmentSlot, Doctor, Department
    ).join(
        AppointmentSlot, Booking.slot_id == AppointmentSlot.slot_id
    ).join(
        Doctor, AppointmentSlot.doctor_id == Doctor.id
    ).join(
        Department, AppointmentSlot.department_id == Department.department_id
    ).filter(
        Booking.id == booking_id,
        Booking.id_users == user_id
    ).first()

    if not booking_data:
        return {"success": False, "message": "ไม่พบข้อมูลการจอง หรือคุณไม่มีสิทธิ์เข้าถึง"}

    booking, slot, doctor, dept = booking_data

    return {
        "success": True,
        "data": {
            "booking_id": booking.id,
            "booking_at": booking.booking_at.isoformat() if booking.booking_at else None,
            "status": booking.booking_Status,
            "detail": booking.detail,
            "qr_code": booking.qr_code,
            "slot": {
                 "date": slot.slot_date.isoformat() if slot.slot_date else None,
                 "start_time": slot.start_time.strftime('%H:%M') if slot.start_time else None,
                 "end_time": slot.end_time.strftime('%H:%M') if slot.end_time else None,
            },
            "doctor": {
                "name": f"{doctor.firstname} {doctor.lastname}",
                "specialist": doctor.specialist
            },
            "department": {
                "name": dept.name
            }
        }
    }
