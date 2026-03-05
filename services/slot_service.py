from models import db, AppointmentSlot, Doctor, Department
from datetime import datetime, date, time

def get_slots_for_date(target_date):
    pass

def get_slots_by_doctor_date(doctor_id, target_date_str):
    try:
        if isinstance(target_date_str, date):
            t_date = target_date_str
        else:
            t_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    except ValueError:
        return []
        
    slots = AppointmentSlot.query.filter_by(doctor_id=doctor_id, slot_date=t_date).all()
    res = []
    for s in slots:
        department_name = s.department.name if s.department else None
        res.append({
            "id": s.slot_id,
            "date": s.slot_date.isoformat(),
            "start_time": s.start_time.strftime("%H:%M") if hasattr(s.start_time, 'strftime') else str(s.start_time),
            "end_time": s.end_time.strftime("%H:%M") if hasattr(s.end_time, 'strftime') else str(s.end_time),
            "department_name": department_name,
            "max_capacity": s.max_capacity,
            "current_bookings": s.current_booking,
            "status": s.status
        })
    return res

def create_appointment_slot(doctor_id, department_id, slot_date, start_time, end_time, max_capacity):
    if isinstance(start_time, str):
        # Allow handling "HH:MM"
        if len(start_time.split(':')) == 2:
            start_time += ":00"
        start_time = datetime.strptime(start_time, "%H:%M:%S").time()
    if isinstance(end_time, str):
        if len(end_time.split(':')) == 2:
            end_time += ":00"
        end_time = datetime.strptime(end_time, "%H:%M:%S").time()
    if isinstance(slot_date, str):
        slot_date = datetime.strptime(slot_date, "%Y-%m-%d").date()

    new_slot = AppointmentSlot(
        doctor_id=doctor_id,
        department_id=department_id,
        slot_date=slot_date,
        start_time=start_time,
        end_time=end_time,
        max_capacity=max_capacity,
        current_booking=0,
        status="active"
    )
    db.session.add(new_slot)
    db.session.commit()
    return new_slot

def update_slot_status(slot_id, new_status):
    slot = AppointmentSlot.query.get(slot_id)
    if not slot:
        return False
    slot.status = new_status
    db.session.commit()
    return True

def change_slot_time(slot_id, start_time, end_time):
    pass

def delete_appointment_slot(slot_id):
    slot = AppointmentSlot.query.get(slot_id)
    if not slot:
        return False
    if slot.current_booking > 0:
        return False # can't delete if booked
    db.session.delete(slot)
    db.session.commit()
    return True
