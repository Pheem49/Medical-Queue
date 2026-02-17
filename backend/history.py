from flask import request, jsonify
from app import app, get_db

@app.route('/api/user/history', methods=['GET'])
def get_user_history():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user_id'}), 400
    
    db = get_db()
    bookings = db.execute('''
        SELECT b.id, b.slot_id, b.booking_at, b.booking_Status, b.detail, b.qr_code,
               d.firstname as doctor_firstname, d.lastname as doctor_lastname, d.specialist, d.department
        FROM bookings b
        JOIN doctors d ON b.slot_id = d.id_doctor
        WHERE b.id_users = ?
        ORDER BY b.booking_at DESC
    ''', (user_id,)).fetchall()
    
    result = [dict(row) for row in bookings]
    return jsonify(result), 200