from flask import Blueprint, request, jsonify
from database import get_db
import json

history_bp = Blueprint('history', __name__)

@history_bp.route('/api/user/history', methods=['GET'])
def get_user_history():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400

    db = get_db()
    # Fetch bookings for the user
    # Note: frontend expects specific format, similar to list_bookings but filtered
    rows = db.execute('SELECT * FROM bookings WHERE id_users = ? ORDER BY id DESC', (user_id,)).fetchall()
    
    results = []
    for r in rows:
        d = dict(r)
        # compatibility mapping
        d['status'] = d.get('booking_Status')
        d['symptoms'] = d.get('detail') # fallback if not parsed
        
        # separate date/time from booking_at if needed
        if d.get('booking_at'):
             try:
                 parts = d['booking_at'].split(' ')
                 d['date'] = parts[0]
                 d['time'] = parts[1] if len(parts) > 1 else ''
             except: pass
             
        # unpack detail json
        try:
            details = json.loads(d['detail'])
            if isinstance(details, dict):
                 # merge
                 d['doctor_name'] = details.get('doctorName')
                 d['department_name'] = details.get('departmentName')
                 d['patient_name'] = details.get('patientName')
                 d['symptoms'] = details.get('symptoms')
        except:
            pass # keep raw detail as symptoms
            
        results.append(d)

    return jsonify(results), 200
