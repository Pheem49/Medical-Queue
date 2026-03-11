from models import db, Booking, AppointmentSlot, Doctor, Department
import os
from cryptography.fernet import Fernet

# ===================================================================
# !! สำคัญมาก !!
# กุญแจลับนี้ต้องเก็บเป็นความลับและไม่เปลี่ยนแปลง
# ถ้าเปลี่ยน KEY รหัสเก่าทั้งหมดจะถอดรหัสไม่ได้!
# ===================================================================
_FERNET_KEY = os.environ.get("QR_FERNET_KEY", "aGB7sxb5xIQAAF_Nte9hBrvMLYlnEWhRO5GYZUCbit4=")
_fernet = Fernet(_FERNET_KEY.encode())

def encrypt_national_id(national_id: str) -> str:
    """เข้ารหัสเลขบัตรประชาชนเป็น token ที่ถอดรหัสกลับได้"""
    if not national_id:
        return ""
    return _fernet.encrypt(national_id.encode("utf-8")).decode("utf-8")

def decrypt_national_id(token: str) -> str:
    """ถอดรหัส token กลับเป็นเลขบัตรประชาชน (returns None ถ้า token ไม่ถูกต้อง)"""
    if not token:
        return None
    try:
        return _fernet.decrypt(token.encode("utf-8")).decode("utf-8")
    except Exception:
        return None

def get_active_booking(user_id):
    """
    ดึงข้อมูลคิวที่ active อยู่ และถ้าเวลาเลยปลายทางของ slot ไปแล้ว ให้ยกเลิกอัตโนมัติ
    """
    from datetime import datetime
    active_booking = Booking.query.filter(
        Booking.id_users == user_id,
        Booking.booking_Status == 'รอรับบริการ'
    ).first()

    if active_booking:
        slot = AppointmentSlot.query.get(active_booking.slot_id)
        if slot:
            slot_end_datetime = datetime.combine(slot.slot_date, slot.end_time)
            if datetime.now() > slot_end_datetime:
                # ยกเลิกคิวอัตโนมัติ
                active_booking.booking_Status = "ยกเลิก"
                if slot.current_booking > 0:
                    slot.current_booking -= 1
                if slot.status in ["เต็ม", "Full"]:
                    slot.status = "active"
                db.session.commit()
                return None
    return active_booking

def create_booking(user_id, slot_id, detail):
    """
    สร้างการจองใหม่:
    - ตรวจสอบว่าผู้ใช้มีคิวที่ยัง active (รอรับบริการ/กำลังตรวจ) อยู่หรือไม่
    - ถ้ามีแล้ว จะไม่อนุญาตให้จองเพิ่มจนกว่าจะเสร็จสิ้นหรือยกเลิกคิวเดิม
    """
    # 1. ตรวจสอบคิวที่ยัง Active อยู่ของผู้ใช้คนนี้
    active_booking = get_active_booking(user_id)
    
    if active_booking:
        return {
            "success": False, 
            "message": "คุณมีคิวที่กำลังรอรับบริการอยู่ (หมายเลขคิว #" + str(active_booking.id) + ") หากต้องการจองคิวใหม่ กรุณายกเลิกคิวเดิมก่อนที่หน้า 'บัตรคิวของฉัน'"
        }

    # ค้นหา Slot
    slot = AppointmentSlot.query.get(slot_id)
    if not slot:
        return {"success": False, "message": "ไม่พบเวลานัดหมายนี้"}
    
    # ตรวจสอบว่าคิวเต็มหรือยัง
    if slot.current_booking >= slot.max_capacity:
        return {"success": False, "message": "คิวนัดหมายนี้เต็มแล้ว"}
    
    # ดึงข้อมูลผู้ใช้เพื่อเอา national_id มาทำเป็น qr_code
    from models import User
    user = User.query.get(user_id)
    if not user:
        return {"success": False, "message": "ไม่พบข้อมูลผู้ใช้"}
    
    # เพิ่มจำนวนคิวที่จองแล้ว (current_booking)
    slot.current_booking += 1
    
    # ถ้าคิวเต็มพอดี ให้อัปเดตสถานะ
    if slot.current_booking >= slot.max_capacity:
        slot.status = "เต็ม"

    # เข้ารหัสเลขบัตรประชาชนด้วย Fernet (AES) ก่อนเซฟ
    # ระบบสามารถถอดรหัสกลับได้ แต่คนภายนอกสแกน QR จะอ่านเลข 13 หลักไม่ออก
    qr_code_ref = encrypt_national_id(user.national_id)

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
    # ค้นหาข้อมูลการจอง
    booking = Booking.query.filter_by(id=booking_id, id_users=user_id).first()
    
    if not booking:
        return {"success": False, "message": "ไม่พบข้อมูลการจอง หรือคุณไม่มีสิทธิ์ยกเลิกคิวนี้"}
        
    if booking.booking_Status in ['ยกเลิก', 'เสร็จสิ้น']:
        return {"success": False, "message": f"ไม่สามารถยกเลิกคิวได้เนื่องจากสถานะปัจจุบันคือ '{booking.booking_Status}'"}
        
    try:
        # เปลี่ยนสถานะการจองเป็นยกเลิก
        booking.booking_Status = "ยกเลิก"
        
        # คืนจำนวนคิวที่ยังว่างอยู่ให้กับ slot
        slot = AppointmentSlot.query.get(booking.slot_id)
        if slot and slot.current_booking > 0:
            slot.current_booking -= 1
            # ถ้าก่อนหน้านี้เต็ม ให้เปลี่ยนเป็นสถานะปกติ (active)
            if slot.status == "เต็ม" or slot.status == "Full":
                slot.status = "active"
                
        db.session.commit()
        return {"success": True, "message": "ยกเลิกคิวสำเร็จ"}
        
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"เกิดข้อผิดพลาดในการยกเลิกคิว: {str(e)}"}

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

def get_available_dates(doctor_id):
    """
    ดึงรายการวันที่แพทย์คนนี้มี Slot ที่ยังว่างและเป็นสถานะ 'active'
    """
    from sqlalchemy import func
    from datetime import date
    
    # หาวันที่ที่มี Slot ที่ยังไม่เต็ม และสถานะเป็น active และต้องเป็นวันนี้หรืออนาคต
    slots = db.session.query(
        AppointmentSlot.slot_date
    ).filter(
        AppointmentSlot.doctor_id == doctor_id,
        AppointmentSlot.status == 'active',
        AppointmentSlot.current_booking < AppointmentSlot.max_capacity,
        AppointmentSlot.slot_date > date.today()
    ).group_by(
        AppointmentSlot.slot_date
    ).all()
    
    return [slot.slot_date.isoformat() for slot in slots]
