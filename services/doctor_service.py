from models import db, Doctor, DoctorToDepartment, Department

def get_all_doctors():
    doctors = Doctor.query.all()
    result = []
    for doctor in doctors:
        # ดึงรายชื่อแผนกที่หมอคนนี้อยู่
        dept_names = db.session.query(Department.name).join(
            DoctorToDepartment, DoctorToDepartment.department_id == Department.department_id
        ).filter(DoctorToDepartment.doctor_id == doctor.id).all()
        
        departments = [d[0] for d in dept_names]
        
        result.append({
            "id": doctor.id,
            "firstname": doctor.firstname,
            "lastname": doctor.lastname,
            "doctor_id": doctor.doctor_id,
            "specialist": doctor.specialist,
            "status": doctor.status,
            "schedule": doctor.schedule,
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
    doctor = Doctor.query.get(doctor_db_id)
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
        DoctorToDepartment.query.filter_by(doctor_id=doctor_db_id).delete()
        # เพิ่มของใหม่
        for d_id in update_data['department_ids']:
            mapping = DoctorToDepartment(doctor_id=doctor_db_id, department_id=d_id)
            db.session.add(mapping)
        
    db.session.commit()
    return True

def remove_doctor(doctor_db_id):
    doctor = Doctor.query.get(doctor_db_id)
    if not doctor:
        return False
    
    db.session.delete(doctor)
    db.session.commit()
    return True
