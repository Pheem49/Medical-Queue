from flask import Blueprint, jsonify
from datetime import datetime
from database import get_db

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    # In a real app, we would filter by logged in user ID from session/token
    # Here we expect frontend to filter, or we return global + user specific logic if we had auth middleware
    # For simplicity, we return ALL notifications logic, and frontend filters by patient name if matched
    # Or better: We fetch all bookings and compute notifications for them
    
    db = get_db()
    # Fetch all active bookings
    bookings = db.execute("SELECT * FROM bookings WHERE booking_Status NOT IN ('cancelled', 'completed', 'arrived')").fetchall()
    
    notifications = []
    now = datetime.now()
    
    for b in bookings:
        try:
            # Construct date/time. booking_at usually has "YYYY-MM-DD HH:MM"
            # But let's look at the data. 
            # If booking_at is missing, try to construct from date/time fields if we had them separate, 
            # but schema stores them in booking_at or detail.
            booking_dt = datetime.strptime(b['booking_at'], "%Y-%m-%d %H:%M")
        except:
             # Try other formats or skip
             continue
            
        diff = booking_dt - now
        days = diff.days
        
        # We need patient_name. It's in detail JSON or we can try to join users table if we had a proper join.
        # But `bookings` has `detail` with patientName.
        import json
        patient_name = "Unknown"
        try:
            details = json.loads(b['detail'])
            patient_name = details.get('patientName', 'Unknown')
        except:
            pass

        # New Booking Notification (created within last 24 hours)
        # We don't have a reliable 'created_at' in bookings table in the new schema text, 
        # unless we added it. The snippet I saw earlier didn't have it explicitly in the CREATE TABLE for bookings 
        # in the *new* schema (only id, slot_id, id_users, booking_at, booking_Status, detail, qr_code).
        # So this logic might fail if we don't have it.
        # However, let's assume valid data or just skip "New Booking" check if we can't find it.
        # Actually, let's just show upcoming appointments.
        
        # Reminder Logic
        if 0 <= days <= 1:
            if days == 0:
                msg = "ถึงวันนัดหมายแล้ว! กรุณาเตรียมตัวให้พร้อม"
                title = "ถึงวันนัดหมาย"
                urgent = True
            else:
                msg = f"อีก {days} วัน จะถึงวันนัดหมายของคุณ" # Actually if days=1 it means tomorrow
                title = "แจ้งเตือนใกล้ถึงวันนัด"
                urgent = False
                
            notifications.append({
                'type': 'reminder',
                'title': title,
                'message': msg,
                'date': b['booking_at'].split(' ')[0],
                'time': b['booking_at'].split(' ')[1] if ' ' in b['booking_at'] else '',
                'patient_name': patient_name,
                'urgent': urgent,
                'meta': 'เหลืออีก ' + (f"{int(diff.total_seconds()/3600)} ชม." if days==0 else f"{days} วัน")
            })
            
    # Add a system notification for everyone
    notifications.append({
        'type': 'system',
        'title': 'ยินดีต้อนรับสู่ Medical Queue',
        'message': 'ระบบจองคิวออนไลน์พร้อมให้บริการตลอด 24 ชม.',
        'meta': 'ข่าวสารระบบ',
        'patient_name': None # For everyone
    })
            
    return jsonify(notifications)
