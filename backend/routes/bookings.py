from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import random
import string
from database import get_db

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.get_json() or {}
    # accept partial data; store what's provided
    db = get_db()

    doctor_name = data.get('doctorName')
    booking_date = data.get('date')
    booking_time = data.get('time')
    
    # Enforce Single Active Ticket: Cancel previous active bookings
    # Need userId. 
    user_id = data.get('userId')
    if user_id:
        db.execute(
            "UPDATE bookings SET booking_Status = 'ยกเลิก' WHERE id_users = ? AND booking_Status IN ('รอรับบริการ', 'booked')",
            (user_id,)
        )

    # Generate QR Code
    qr_code = ''.join(random.choices(string.digits, k=10))
    
    # Combine date/time for booking_at
    booking_at = f"{booking_date} {booking_time}"
    
    # Detail: combine symptoms + doctor info for now since we restricted columns
    detail_obj = {
        'symptoms': data.get('symptoms'),
        'doctorName': data.get('doctorName'),
        'departmentName': data.get('departmentName'),
        'departmentValue': data.get('departmentValue'),
        'patientName': data.get('patientName')
    }
    detail_json = json.dumps(detail_obj, ensure_ascii=False)
    
    cur = db.execute(
        "INSERT INTO bookings (id_users, slot_id, booking_at, booking_Status, detail, qr_code) VALUES (?,?,?,?,?,?)",
        (
            user_id,
            0, # slot_id
            booking_at,
            'รอรับบริการ', # booking_Status
            detail_json, # detail (JSON)
            qr_code
        ),
    )
    db.commit()
    booking_id = cur.lastrowid
    
    # Return legacy format for frontend
    return jsonify({
        'id': booking_id,
        'status': 'booked', # legacy
        'booking_Status': 'รอรับบริการ',
        'qr_code': qr_code,
        'date': booking_date,
        'time': booking_time,
        'doctor_name': doctor_name,
        'department_name': data.get('departmentName'),
        'symptoms': data.get('symptoms')
    }), 201

@bookings_bp.route('/api/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    db = get_db()
    row = db.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,)).fetchone()
    if not row:
        return jsonify({'error': 'not found'}), 404
    d = dict(row)
    # unpack details
    try:
        details = json.loads(d['detail'])
        if isinstance(details, dict):
            d.update(details) # flatten (keeps CamelCase)
            # map to snake_case for frontend
            d['patient_name'] = details.get('patientName')
            d['doctor_name'] = details.get('doctorName')
            d['department_name'] = details.get('departmentName')
            d['department_value'] = details.get('departmentValue')
            d['symptoms'] = details.get('symptoms')
    except:
        d['symptoms'] = d['detail'] # fallback

    # split booking_at to date/time
    if d.get('booking_at'):
         try:
             parts = d['booking_at'].split(' ')
             d['date'] = parts[0]
             d['time'] = parts[1] if len(parts) > 1 else ''
         except: pass

    d['status'] = d.get('booking_Status')
    return jsonify(d)


@bookings_bp.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    db = get_db()
    cur = db.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'status': 'deleted'}), 200


@bookings_bp.route('/api/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    data = request.get_json() or {}
    db = get_db()
    # only allow updating certain fields (date, time, department_name, doctor_name, symptoms, status)
    fields = {}
    for k in ('date', 'time', 'departmentName', 'doctorName', 'symptoms', 'departmentValue', 'status'):
        if k in data:
            fields[k] = data[k]

    if not fields:
        return jsonify({'error': 'no fields to update'}), 400

    # Fetch current booking
    current = db.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,)).fetchone()
    if not current:
        return jsonify({'error': 'not found'}), 404
    
    current_dict = dict(current)
    # unpack existing details
    try:
        current_details = json.loads(current_dict['detail'])
    except:
        current_details = {}

    # Update logic
    updated_details = current_details.copy()
    
    # 1. Update Detail Fields
    for k in ('departmentName', 'doctorName', 'symptoms', 'departmentValue', 'patientName'):
        if k in data:
            updated_details[k] = data[k]
    
    # 2. Update Date/Time -> booking_at
    # need current date/time if only one changed
    current_booking_at = current_dict.get('booking_at', '')
    try:
        parts = current_booking_at.split(' ')
        c_date = parts[0]
        c_time = parts[1] if len(parts) > 1 else ''
    except:
        c_date = ''
        c_time = ''
        
    new_date = data.get('date', c_date)
    new_time = data.get('time', c_time)
    new_booking_at = f"{new_date} {new_time}"
    
    # 3. Update Status
    new_status = data.get('status') # 'booked', 'arrived', etc.
    # map confirm status back to booking_Status if needed
    if new_status == 'booked': new_status_val = 'รอรับบริการ'
    elif new_status == 'arrived': new_status_val = 'arrived' # keep as is or map? Frontend expects 'arrived' in response?
    # actually frontend sends 'arrived'.
    else: new_status_val = new_status
    
    # If explicit new status provided, use it, else keep old
    if not new_status:
        new_status_val = current_dict['booking_Status']

    # Execute Update
    new_detail_json = json.dumps(updated_details, ensure_ascii=False)
    
    db.execute(
        "UPDATE bookings SET detail = ?, booking_at = ?, booking_Status = ? WHERE id = ?",
        (new_detail_json, new_booking_at, new_status_val, booking_id)
    )
    db.commit()

    row = db.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,)).fetchone()
    d = dict(row)
    # unpack details
    try:
        details = json.loads(d['detail'])
        if isinstance(details, dict):
            d.update(details) # flatten
            d['patient_name'] = details.get('patientName')
            d['doctor_name'] = details.get('doctorName')
            d['department_name'] = details.get('departmentName')
            d['department_value'] = details.get('departmentValue')
            d['symptoms'] = details.get('symptoms')
    except:
        d['symptoms'] = d['detail'] # fallback

    # split booking_at to date/time
    if d.get('booking_at'):
         try:
             parts = d['booking_at'].split(' ')
             d['date'] = parts[0]
             d['time'] = parts[1] if len(parts) > 1 else ''
         except: pass

    d['status'] = d.get('booking_Status')
    return jsonify(d)

@bookings_bp.route('/api/bookings', methods=['GET'])
def list_bookings():
    db = get_db()
    # map new schema to old fields for frontend
    rows = db.execute('SELECT * FROM bookings ORDER BY id DESC').fetchall()
    results = []
    for r in rows:
        d = dict(r)
        # compatibility mapping
        d['status'] = d.get('booking_Status')
        d['symptoms'] = d.get('detail')
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
    return jsonify(results)
