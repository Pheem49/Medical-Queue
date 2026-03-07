from models import db, Doctor, DoctorToDepartment, Department, AppointmentSlot, Booking
from datetime import datetime, timedelta, timezone

# กำหนด Timezone ไทย (UTC+7) แบบมาตรฐาน ไม่ต้องใช้ pytz
THAILAND_TZ = timezone(timedelta(hours=7))

def get_all_doctors():
    """
    ดึงข้อมูลแพทย์ทั้งหมด พร้อมขยับขยายระบบ:
    - ระบบ Auto-Hiding: แพทย์ที่ไม่มีตารางตรวจในวันนี้หรืออนาคต จะไม่ถูกดึงมาแสดงผลในหน้าจัดการ (แต่ข้อมูลใน DB ยังอยู่เพื่อให้หน้า History แสดงผลได้)
    - ตามคำสั่งผู้ใช้: "ถ้าเลยวันเวลามาแล้วให้ลบข้อมูลแพทย์ออกเลย" (ในมุมมอง Staff จะหายไปจากลิสต์)
    - แต่ต้องเห็นของวันเก่าด้วยในหน้า /staff/history ดังนั้นเราจะไม่กด Delete จริงใต DB อัตโนมัติ
    """
    today = datetime.now(THAILAND_TZ).date()
    
    # ดึงหมอทั้งหมด
    all_docs = Doctor.query.all()
    result = []
    for doc in all_docs:
        # เช็คว่ามี Slot ในวันนี้หรืออนาคตไหม
        has_future_slots = AppointmentSlot.query.filter(
            AppointmentSlot.doctor_id == doc.id,
            AppointmentSlot.slot_date >= today
        ).first() is not None
        
        # ถ้าไม่มีตารางเหลือแล้ว (เป็นหมอที่คิวหมดอายุแล้ว) -> ข้ามไป ไม่ต้องแสดงในหน้า Doctors
        if not has_future_slots:
            continue

        # ดึงรายชื่อแผนกที่หมอคนนี้อยู่
        dept_names = db.session.query(Department.name).join(
            DoctorToDepartment, DoctorToDepartment.department_id == Department.department_id
        ).filter(DoctorToDepartment.doctor_id == doc.id).all()
        
        departments = [d[0] for d in dept_names]
        
        result.append({
            "id": doc.id,
            "firstname": doc.firstname,
            "lastname": doc.lastname,
            "doctor_id": doc.doctor_id,
            "specialist": doc.specialist,
            "status": doc.status,
            "schedule": doc.schedule,
            "departments": departments
        })
    return result

def add_doctor(firstname, lastname, doctor_id_str, specialist, status, schedule_json, department_ids=None):
    new_doctor = Doctor(
        firstname=firstname,
        lastname=lastname,
        doctor_id=doctor_id_str,
        specialist=specialist,
        status=status,
        schedule=schedule_json
    )
    db.session.add(new_doctor)
    db.session.flush() # เพื่อเอา id มาใช้ต่อ
    
    if department_ids:
        for d_id in department_ids:
            mapping = DoctorToDepartment(doctor_id=new_doctor.id, department_id=d_id)
            db.session.add(mapping)
            
    db.session.commit()
    return new_doctor.id

def update_doctor(doctor_db_id, update_data):
    # ใช้ db.session.get แทน Doctor.query.get เพื่อความเสถียร
    doctor = db.session.get(Doctor, doctor_db_id)
    if not doctor:
        return False
    
    if 'firstname' in update_data:
        doctor.firstname = update_data['firstname']
    if 'lastname' in update_data:
        doctor.lastname = update_data['lastname']
    if 'doctor_id' in update_data:
        doctor.doctor_id = update_data['doctor_id']
    if 'specialist' in update_data:
        doctor.specialist = update_data['specialist']
    if 'status' in update_data:
        doctor.status = update_data['status']
    if 'schedule' in update_data:
        doctor.schedule = update_data['schedule']
    
    # อัปเดตแผนก
    if 'department_ids' in update_data:
        # ลบของเก่าออกก่อน
        db.session.query(DoctorToDepartment).filter_by(doctor_id=doctor_db_id).delete()
        # เพิ่มของใหม่
        for d_id in update_data['department_ids']:
            mapping = DoctorToDepartment(doctor_id=doctor_db_id, department_id=d_id)
            db.session.add(mapping)
        
    db.session.commit()
    return True

def remove_doctor(doctor_db_id):
    """
    ลบข้อมูลแพทย์และข้อมูลที่เกี่ยวข้องทั้งหมด (Mappings, Slots, Bookings)
    (ใช้วิธีลบแบบ Hard Delete เมื่อผู้ใช้กดลบเองด้วยมือเท่านั้น)
    """
    try:
        doctor = db.session.get(Doctor, doctor_db_id)
        if not doctor:
            return False
            
        # 1. ลบความสัมพันธ์หมอกับแผนก
        db.session.query(DoctorToDepartment).filter(DoctorToDepartment.doctor_id == doctor_db_id).delete(synchronize_session=False)
        
        # 2. หา Slots และลบ Bookings ที่เกี่ยวข้อง
        slots = db.session.query(AppointmentSlot).filter(AppointmentSlot.doctor_id == doctor_db_id).all()
        slot_ids = [s.slot_id for s in slots]
        
        if slot_ids:
            # ลบการจองที่ผูกกับ Slots ของหมอท่านนี้
            db.session.query(Booking).filter(Booking.slot_id.in_(slot_ids)).delete(synchronize_session=False)
            
        # 3. ลบ Slots ทั้งหมดของหมอ
        db.session.query(AppointmentSlot).filter(AppointmentSlot.doctor_id == doctor_db_id).delete(synchronize_session=False)
        
        # 4. ลบข้อมูลแพทย์ออกจากตารางหลัก
        db.session.delete(doctor)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error removing doctor: {e}")
        return False
