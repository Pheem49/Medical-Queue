from models import db, Booking, AppointmentSlot, User, Doctor
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from datetime import datetime

def get_all_bookings_for_admin(date_filter=None):
    """
    ดึงข้อมูลการจองทั้งหมดสำหรับแอดมิน สามารถกรองตามวันที่ได้
    """
    try:
        query = Booking.query.options(
            joinedload(Booking.user),
            joinedload(Booking.slot).joinedload(AppointmentSlot.doctor)
        ).order_by(Booking.booking_at.desc())

        if date_filter:
            # แปลง string 'YYYY-MM-DD' เป็น date object
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            # กรองข้อมูลโดยใช้ slot_date ของตาราง AppointmentSlot
            query = query.join(AppointmentSlot).filter(AppointmentSlot.slot_date == filter_date)

        bookings = query.all()
        return [booking.to_dict(include_user=True, include_slot=True) for booking in bookings]
    except Exception as e:
        # ใน Production ควรใช้ logging แทน print
        print(f"Error in get_all_bookings_for_admin: {e}")
        return None

def update_booking_status(booking_id, new_status):
    """
    อัปเดตสถานะของการจอง (เช่น 'completed', 'skipped')
    """
    booking = Booking.query.get(booking_id)
    if not booking:
        return None, "Booking not found"

    booking.booking_Status = new_status
    db.session.commit()
    return booking.to_dict(), None

def get_booking_full_info(booking_id):
    """
    ดึงข้อมูลการจองแบบละเอียด 1 รายการ
    """
    booking = Booking.query.options(
        joinedload(Booking.user),
        joinedload(Booking.slot).joinedload(AppointmentSlot.doctor)
    ).get(booking_id)
    
    return booking

def delete_booking_and_update_slot(booking_id):
    """
    ลบการจองและลดจำนวน current_booking ใน AppointmentSlot ที่เกี่ยวข้อง
    """
    booking = Booking.query.get(booking_id)
    if not booking:
        return False, "Booking not found"

    slot = booking.slot
    if slot and slot.current_booking > 0:
        slot.current_booking -= 1

    db.session.delete(booking)
    db.session.commit()
    return True, "Booking deleted successfully"
