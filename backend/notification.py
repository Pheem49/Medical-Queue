from flask import request, jsonify
from app import app,get_db
from datetime import datetime

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    # In a real app, we would filter by logged in user ID from session/token
    # Here we expect frontend to filter, or we return global + user specific logic if we had auth middleware
    # For simplicity, we return ALL notifications logic, and frontend filters by patient name if matched
    # Or better: We fetch all bookings and compute notifications for them

    db = get_db()
    # Fetch all active bookings
    bookings = db.execute("SELECT * FROM bookings WHERE status NOT IN ('cancelled', 'completed', 'arrived')").fetchall()

    notifications = []
    now = datetime.now()

    for b in bookings:
        try:
            booking_dt = datetime.strptime(f"{b['date']} {b['time']}", "%Y-%m-%d %H:%M")
        except:
            continue

        diff = booking_dt - now
        days = diff.days

        # New Booking Notification (created within last 24 hours)
        try:
             created_at = datetime.strptime(b['created_at'], "%Y-%m-%dT%H:%M:%S.%f")
        except:
             try: created_at = datetime.strptime(b['created_at'], "%Y-%m-%dT%H:%M:%S")
             except: created_at = now # fallback

        if (now - created_at).total_seconds() < 86400: # 24 hours
             notifications.append({
                 'type': 'appointment',
                 'title': 'การจองสำเร็จ',
                 'message': f"คุณได้จองคิว {b['department_name']} วันที่ {b['date']}",
                 'date': b['date'],
                 'time': b['time'],
                 'patient_name': b['patient_name'],
                 'is_new': True,
                 'meta': 'จองเมื่อเร็วๆ นี้'
             })

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
                'date': b['date'],
                'time': b['time'],
                'patient_name': b['patient_name'],
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