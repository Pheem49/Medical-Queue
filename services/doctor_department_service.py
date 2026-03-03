from models import db, DoctorToDepartment, Doctor, Department

def get_doctors_in_department(department_id):
    department = Department.query.get(department_id)
    if not department:
        raise ValueError("Department not found")

    doctors = (
        db.session.query(Doctor)
        .join(DoctorToDepartment, DoctorToDepartment.doctor_id == Doctor.id)
        .filter(DoctorToDepartment.department_id == department_id)
        .order_by(Doctor.id.asc())
        .all()
    )

    return [
        {
            "id": doctor.id,
            "firstname": doctor.firstname,
            "lastname": doctor.lastname,
            "doctor_id": doctor.doctor_id,
            "specialist": doctor.specialist,
            "status": doctor.status,
            "schedule": doctor.schedule,
        }
        for doctor in doctors
    ]

def get_departments_for_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        raise ValueError("Doctor not found")

    departments = (
        db.session.query(Department)
        .join(DoctorToDepartment, DoctorToDepartment.department_id == Department.department_id)
        .filter(DoctorToDepartment.doctor_id == doctor_id)
        .order_by(Department.department_id.asc())
        .all()
    )

    return [
        {
            "department_id": department.department_id,
            "name": department.name,
        }
        for department in departments
    ]

def assign_doctor_to_department(doctor_id, department_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        raise ValueError("Doctor not found")

    department = Department.query.get(department_id)
    if not department:
        raise ValueError("Department not found")

    existing = DoctorToDepartment.query.filter_by(
        doctor_id=doctor_id,
        department_id=department_id
    ).first()
    if existing:
        raise ValueError("Doctor already assigned to this department")

    mapping = DoctorToDepartment(doctor_id=doctor_id, department_id=department_id)
    db.session.add(mapping)
    db.session.commit()
    return mapping.id

def remove_doctor_from_department(doctor_id, department_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        raise ValueError("Doctor not found")

    department = Department.query.get(department_id)
    if not department:
        raise ValueError("Department not found")

    mapping = DoctorToDepartment.query.filter_by(
        doctor_id=doctor_id,
        department_id=department_id
    ).first()
    if not mapping:
        raise ValueError("Doctor is not assigned to this department")

    db.session.delete(mapping)
    db.session.commit()
