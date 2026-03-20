from models import db, Booking, AppointmentSlot, Doctor, Department
from sqlalchemy import func
import os
from cryptography.fernet import Fernet

# ===================================================================
# 📌 ส่วนนี้คือ "กุญแจเข้ารหัส" (Secret Key)
# 💡 สิ่งที่ต้องพรีเซนต์: "เพื่อความปลอดภัยสูงสุดของข้อมูลคนไข้ เรามีกุญแจเข้ารหัสระดับสูง 
# ป้องกันไม่ให้ใครมาแอบอ่านข้อมูลสำคัญในฐานข้อมูลได้ครับ"
# ===================================================================
_FERNET_KEY = os.environ.get("QR_FERNET_KEY", "aGB7sxb5xIQAAF_Nte9hBrvMLYlnEWhRO5GYZUCbit4=")
_fernet = Fernet(_FERNET_KEY.encode())

# ===================================================================
# 1. ฟังก์ชันเข้ารหัสและถอดรหัสข้อมูลบัตรประชาชน
# 📌 หน้าที่หลัก: แปลงเลขบัตร 13 หลักให้เป็นข้อความที่อ่านไม่ออก ก่อนนำไปทำ QR Code
# 🖥️ ไปแสดงผลส่วนไหน: อยู่เบื้องหลังการสร้าง QR Code บนหน้าบัตรคิว
# 💡 สิ่งที่ต้องพรีเซนต์: "ระบบเราให้ความสำคัญกับ PDPA ครับ เราไม่เอาเลขบัตรประชาชนมาสร้าง QR Code ตรงๆ 
# แต่เราจะเข้ารหัสไว้ คนนอกสแกนไปก็อ่านไม่ออก ป้องกันข้อมูลคนไข้รั่วไหลครับ"
# ===================================================================
def encrypt_national_id(national_id: str) -> str:
    """เข้ารหัสเลขบัตรประชาชนเป็น token ที่ถอดรหัสกลับได้"""
    if not national_id:
        return ""
    return _fernet.encrypt(national_id.encode("utf-8")).decode("utf-8")

def decrypt_national_id(token: str) -> str:
    """ถอดรหัส token กลับเป็นเลขบัตรประชาชน"""
    if not token:
        return None
    try:
        return _fernet.decrypt(token.encode("utf-8")).decode("utf-8")
    except Exception:
        return None


# ===================================================================
# 2. ฟังก์ชันตรวจสอบคิวปัจจุบัน และยกเลิกคิวอัตโนมัติ (get_active_booking)
# 📌 หน้าที่หลัก: เช็กว่าคนไข้มีคิวที่รอตรวจอยู่ไหม และถ้าคนไข้มาสายเกินเวลา ระบบจะยกเลิกคิวให้ทันที
# 🖥️ ไปแสดงผลส่วนไหน: หน้า "ตั๋วคิวของฉัน" และทำงานอยู่เบื้องหลังตลอดเวลา
# 💡 สิ่งที่ต้องพรีเซนต์: "จุดเด่นของระบบเราคือ 'การจัดการคิวผี' ครับ ถ้าระบบพบว่าเลยเวลานัดแล้วคนไข้ไม่มา 
# ระบบจะทำการยกเลิกคิวให้อัตโนมัติ และคืนที่นั่งให้คนอื่นจองต่อได้ทันที หมอจะไม่เสียโอกาสครับ"
# ===================================================================
def get_active_booking(user_id):
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


# ===================================================================
# 3. ฟังก์ชันสร้างการจองคิวใหม่ (create_booking) *** พระเอกของระบบ ***
# 📌 หน้าที่หลัก: จัดการตอนคนไข้กดจอง (เช็กคิวซ้ำ -> เช็กคิวเต็ม -> หักที่นั่ง -> รันเลขคิว -> สร้าง QR)
# 🖥️ ไปแสดงผลส่วนไหน: ทำงานเมื่อกดปุ่ม "ยืนยันการจอง" และพาไปหน้า "บัตรคิวที่จองสำเร็จ"
# 💡 สิ่งที่ต้องพรีเซนต์: "นี่คือหัวใจหลักครับ ระบบจะป้องกันคนไข้กดจองซ้ำซ้อนเพื่อกั๊กคิว 
# มีการเช็กจำนวนที่นั่งแบบ Real-time และระบบจะคำนวณรันเลขคิว (เช่น คิวที่ 1, 2, 3) 
# แยกตามแผนกและวันให้อัตโนมัติ ทำให้เลขคิวไม่ชนกันแน่นอนครับ"
# ===================================================================
def create_booking(user_id, slot_id, detail):
    # ตรวจสอบคิวที่ยัง Active อยู่
    active_booking = get_active_booking(user_id)
    if active_booking:
        return {
            "success": False, 
            "message": "คุณมีคิวที่กำลังรอรับบริการอยู่ (หมายเลขคิว #" + str(active_booking.id) + ") หากต้องการจองคิวใหม่ กรุณายกเลิกคิวเดิมก่อนที่หน้า 'บัตรคิวของฉัน'"
        }

    slot = AppointmentSlot.query.get(slot_id)
    if not slot:
        return {"success": False, "message": "ไม่พบเวลานัดหมายนี้"}
    
    if slot.current_booking >= slot.max_capacity:
        return {"success": False, "message": "คิวนัดหมายนี้เต็มแล้ว"}
    
    from models import User
    user = User.query.get(user_id)
    if not user:
        return {"success": False, "message": "ไม่พบข้อมูลผู้ใช้"}
    
    # หักโควต้าที่นั่งหมอ
    slot.current_booking += 1
    if slot.current_booking >= slot.max_capacity:
        slot.status = "เต็ม"

    # เข้ารหัสบัตรประชาชนทำ QR Code
    qr_code_ref = encrypt_national_id(user.national_id)

    # รันเลขคิวอัตโนมัติ
    max_queue = db.session.query(func.max(Booking.queue_number))\
        .join(AppointmentSlot)\
        .filter(
            AppointmentSlot.department_id == slot.department_id,
            AppointmentSlot.slot_date == slot.slot_date
        ).scalar()
    
    new_queue_number = (max_queue or 0) + 1

    new_booking = Booking(
        slot_id=slot.slot_id,
        id_users=user_id,
        detail=detail,
        qr_code=qr_code_ref,
        queue_number=new_queue_number
    )
    
    db.session.add(new_booking)
    try:
        db.session.commit()
        return {
            "success": True, 
            "message": "จองคิวสำเร็จ", 
            "booking_id": new_booking.id,
            "queue_number": new_booking.queue_number,
            "qr_code": qr_code_ref
        }
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}"}


# ===================================================================
# 4. ฟังก์ชันดูประวัติการจองทั้งหมด (get_patient_history)
# 📌 หน้าที่หลัก: ดึงข้อมูลการหาหมอทั้งหมดในอดีตมาแสดง (ดึงชื่อหมอ, แผนก, เวลา มาครบในรอบเดียว)
# 🖥️ ไปแสดงผลส่วนไหน: หน้า "ประวัติการจอง" (History) ของคนไข้
# 💡 สิ่งที่ต้องพรีเซนต์: "ส่วนนี้เราออกแบบให้ดึงข้อมูลทั้งหมดมาครบจบในรอบเดียวครับ 
# ทำให้แอปทำงานได้รวดเร็ว หน้าประวัติจะแสดงข้อมูลครบถ้วนให้คนไข้ดูย้อนหลังได้สบายๆ ครับ"
# ===================================================================
def get_patient_history(user_id):
    history = db.session.query(
        Booking, AppointmentSlot, Doctor, Department
    ).join(AppointmentSlot, Booking.slot_id == AppointmentSlot.slot_id)\
     .join(Doctor, AppointmentSlot.doctor_id == Doctor.id)\
     .join(Department, AppointmentSlot.department_id == Department.department_id)\
     .filter(Booking.id_users == user_id)\
     .order_by(Booking.booking_at.desc())\
     .all()
    
    results = []
    for booking, slot, doctor, dept in history:
        results.append({
            "booking_id": booking.id,
            "booking_at": booking.booking_at.isoformat() if booking.booking_at else None,
            "status": booking.booking_Status,
            "detail": booking.detail,
            "qr_code": booking.qr_code,
            "queue_number": booking.queue_number,
            "slot_date": slot.slot_date.isoformat() if slot.slot_date else None,
            "start_time": slot.start_time.strftime('%H:%M') if slot.start_time else None,
            "end_time": slot.end_time.strftime('%H:%M') if slot.end_time else None,
            "doctor_name": f"{doctor.firstname} {doctor.lastname}",
            "department_name": dept.name
        })
        
    return {"success": True, "data": results}


# ===================================================================
# 5. ฟังก์ชันยกเลิกคิว (cancel_booking)
# 📌 หน้าที่หลัก: เปลี่ยนสถานะเป็น "ยกเลิก" และที่สำคัญคือ "คืนโควต้าที่นั่ง" กลับเข้าระบบ
# 🖥️ ไปแสดงผลส่วนไหน: ทำงานเมื่อคนไข้กดปุ่ม "ยกเลิกการจอง"
# 💡 สิ่งที่ต้องพรีเซนต์: "ระบบเราไม่เพียงแค่ยกเลิกคิวครับ แต่จะทำการ 'คืน Slot เวลากลับเข้าระบบแบบ Real-time' 
# ถ้ายกเลิกปุ๊บ คิวที่เคยเต็มจะกลับมาว่างทันที คนอื่นที่รออยู่สามารถกดจองเสียบแทนได้เลยครับ"
# ===================================================================
def cancel_booking(user_id, booking_id):
    booking = Booking.query.filter_by(id=booking_id, id_users=user_id).first()
    if not booking:
        return {"success": False, "message": "ไม่พบข้อมูลการจอง หรือคุณไม่มีสิทธิ์ยกเลิกคิวนี้"}
        
    if booking.booking_Status in ['ยกเลิก', 'เสร็จสิ้น']:
        return {"success": False, "message": f"ไม่สามารถยกเลิกคิวได้เนื่องจากสถานะปัจจุบันคือ '{booking.booking_Status}'"}
        
    try:
        booking.booking_Status = "ยกเลิก"
        
        # คืนจำนวนคิวที่ยังว่างอยู่ให้กับหมอ
        slot = AppointmentSlot.query.get(booking.slot_id)
        if slot and slot.current_booking > 0:
            slot.current_booking -= 1
            if slot.status == "เต็ม" or slot.status == "Full":
                slot.status = "active"
                
        db.session.commit()
        return {"success": True, "message": "ยกเลิกคิวสำเร็จ"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"เกิดข้อผิดพลาดในการยกเลิกคิว: {str(e)}"}


# ===================================================================
# 6. ฟังก์ชันดูรายละเอียดตั๋วคิว 1 ใบ (get_booking_details)
# 📌 หน้าที่หลัก: ดึงข้อมูลเฉพาะคิวที่เลือก และตรวจสอบความปลอดภัยว่าใช่เจ้าของคิวจริงๆ ไหม
# 🖥️ ไปแสดงผลส่วนไหน: หน้า "รายละเอียดคิวนัดหมาย" (ตอนกดดูตั๋ว 1 ใบ)
# 💡 สิ่งที่ต้องพรีเซนต์: "เรามีระบบตรวจสอบสิทธิ์ก่อนแสดงข้อมูลครับ (Security Check) 
# คนไข้จะดูได้เฉพาะตั๋วคิวของตัวเองเท่านั้น คนอื่นจะแอบเนียนเอาไอดีมาดึงข้อมูลคิวเราไม่ได้ครับ"
# ===================================================================
def get_booking_details(user_id, booking_id):
    booking_data = db.session.query(
        Booking, AppointmentSlot, Doctor, Department
    ).join(AppointmentSlot, Booking.slot_id == AppointmentSlot.slot_id)\
     .join(Doctor, AppointmentSlot.doctor_id == Doctor.id)\
     .join(Department, AppointmentSlot.department_id == Department.department_id)\
     .filter(Booking.id == booking_id, Booking.id_users == user_id)\
     .first()

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
            "queue_number": booking.queue_number,
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


# ===================================================================
# 7. ฟังก์ชันค้นหาวันที่หมอว่าง (get_available_dates)
# 📌 หน้าที่หลัก: กรองเอาเฉพาะวันที่ "ยังไม่เต็ม" และ "เป็นวันในอนาคต" มาแสดงบนปฏิทิน
# 🖥️ ไปแสดงผลส่วนไหน: หน้า "ปฏิทินเลือกวันจองคิว" 
# 💡 สิ่งที่ต้องพรีเซนต์: "เพื่อประสบการณ์ใช้งานที่ดีเยี่ยม ระบบเราจะกรองวันที่เต็มแล้ว 
# หรือวันที่ผ่านมาแล้วออกให้อัตโนมัติครับ คนไข้จะเห็นเฉพาะวันและเวลาที่กดจองได้จริงเท่านั้น"
# ===================================================================
def get_available_dates(doctor_id):
    from sqlalchemy import func
    from datetime import date
    
    slots = db.session.query(AppointmentSlot.slot_date).filter(
        AppointmentSlot.doctor_id == doctor_id,
        AppointmentSlot.status == 'active',
        AppointmentSlot.current_booking < AppointmentSlot.max_capacity,
        AppointmentSlot.slot_date > date.today()
    ).group_by(AppointmentSlot.slot_date).all()
    
    return [slot.slot_date.isoformat() for slot in slots]


# ===================================================================
# 8. ฟังก์ชันเลื่อนนัด (reschedule_booking) *** ฟีเจอร์ที่ช่วยลดงานแอดมิน ***
# 📌 หน้าที่หลัก: ย้ายคิวไปวันใหม่ (คืนที่นั่งวันเก่า -> ย้ายไปวันใหม่ -> รันเลขคิวใหม่ให้)
# 🖥️ ไปแสดงผลส่วนไหน: ทำงานเมื่อกดปุ่ม "เลื่อนนัด" (Reschedule)
# 💡 สิ่งที่ต้องพรีเซนต์: "แทนที่จะให้คนไข้กดยกเลิกแล้วไปเริ่มจองใหม่ตั้งแต่ต้นให้หงุดหงิด 
# เราทำปุ่ม 'เลื่อนนัด' ให้เลยครับ ระบบจะจัดการคืนสิทธิ์วันเก่าและย้ายไปจองวันใหม่ให้แบบไร้รอยต่อ 
# และที่สำคัญ บังคับว่าต้องเลื่อนล่วงหน้าอย่างน้อย 1 วัน เพื่อให้โรงพยาบาลเตรียมตัวทันครับ"
# ===================================================================
def reschedule_booking(user_id, booking_id, new_slot_id, new_detail):
    booking = Booking.query.filter_by(id=booking_id, id_users=user_id).first()
    if not booking:
        return {"success": False, "message": "ไม่พบข้อมูลการจอง หรือคุณไม่มีสิทธิ์เลื่อนคิวนี้"}
        
    if booking.booking_Status in ['ยกเลิก', 'เสร็จสิ้น']:
        return {"success": False, "message": f"ไม่สามารถเลื่อนคิวได้เนื่องจากสถานะปัจจุบันคือ '{booking.booking_Status}'"}

    if str(booking.slot_id) == str(new_slot_id):
        return {"success": False, "message": "กรุณาเลือกช่วงเวลาใหม่ที่แตกต่างจากคิวเดิม"}

    new_slot = AppointmentSlot.query.get(new_slot_id)
    if not new_slot:
        return {"success": False, "message": "ไม่พบช่วงเวลาใหม่ที่ระบุ"}
        
    if new_slot.status != "active" or new_slot.current_booking >= new_slot.max_capacity:
        return {"success": False, "message": "ช่วงเวลาใหม่ที่คุณเลือกเต็มหรือถูกยกเลิกไปแล้ว"}

    from datetime import date
    if new_slot.slot_date <= date.today():
         return {"success": False, "message": "กรุณาเลื่อนคิวไปล่วงหน้าอย่างน้อย 1 วัน"}

    try:
        # คืนที่นั่งให้ Slot เดิม
        old_slot = AppointmentSlot.query.get(booking.slot_id)
        if old_slot and old_slot.current_booking > 0:
            old_slot.current_booking -= 1
            if old_slot.status in ["เต็ม", "Full"]:
                old_slot.status = "active"

        # หักที่นั่ง Slot ใหม่
        new_slot.current_booking += 1
        if new_slot.current_booking >= new_slot.max_capacity:
             new_slot.status = "เต็ม"
             
        # คำนวณเลขคิวใหม่
        max_queue = db.session.query(func.max(Booking.queue_number))\
            .join(AppointmentSlot)\
            .filter(
                AppointmentSlot.department_id == new_slot.department_id,
                AppointmentSlot.slot_date == new_slot.slot_date
            ).scalar()
        
        new_queue_number = (max_queue or 0) + 1
        
        # อัปเดตข้อมูลลงฐานข้อมูล
        booking.slot_id = new_slot.slot_id
        booking.detail = new_detail if new_detail else booking.detail
        booking.queue_number = new_queue_number
        
        db.session.commit()
        return {
            "success": True, 
            "message": "เลื่อนนัดสำเร็จ!",
            "booking_id": booking.id,
            "queue_number": new_queue_number
        }
        
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"เกิดข้อผิดพลาดในการเลื่อนคิว: {str(e)}"}