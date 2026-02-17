from flask import Blueprint, request, jsonify
from database import get_db

doctors_bp = Blueprint('doctors', __name__)

# --- Public Doctor API ---
@doctors_bp.route('/api/doctors', methods=['GET'])
def list_doctors():
    department = request.args.get('department')
    specialist = request.args.get('specialist')
    db = get_db()
    
    if department:
        rows = db.execute('SELECT * FROM doctors WHERE department = ?', (department,)).fetchall()
    elif specialist:
        rows = db.execute('SELECT * FROM doctors WHERE specialist = ?', (specialist,)).fetchall()
    else:
        rows = db.execute('SELECT * FROM doctors').fetchall()
    
    # Process rows to add 'name' field for frontend compatibility
    results = []
    for r in rows:
        d = dict(r)
        d['name'] = f"{d.get('firstname', '')} {d.get('lastname', '')}".strip()
        # map specialist -> specialty for frontend compatibility if needed
        d['specialty'] = d.get('specialist')
        
        results.append(d)
        
    return jsonify(results)


@doctors_bp.route('/api/departments', methods=['GET'])
def list_departments():
    db = get_db()
    rows = db.execute('SELECT * FROM departments').fetchall()
    return jsonify([dict(r) for r in rows])


# --- Admin Doctor Management Endpoints ---
@doctors_bp.route('/api/admin/doctors', methods=['POST'])
def create_doctor():
    data = request.get_json() or {}
    db = get_db()
    
    # Handle splitting name if still sent as one string
    fname = data.get('firstname')
    lname = data.get('lastname')
    if not fname and data.get('name'):
        parts = data.get('name').split(' ', 1)
        fname = parts[0]
        lname = parts[1] if len(parts) > 1 else ''

    cur = db.execute(
        "INSERT INTO doctors (firstname, lastname, doctor_id, department, specialist, status, schedule, image, status_color) VALUES (?,?,?,?,?,?,?,?,?)",
        (
            fname,
            lname,
            data.get('doctor_id'),
            data.get('department'),
            data.get('specialist'), 
            data.get('status', 'ว่างวันนี้'),
            data.get('schedule'),
            data.get('image'),
            data.get('status_color', 'text-green-600')
        )
    )
    db.commit()
    row = db.execute('SELECT * FROM doctors WHERE id_doctor = ?', (cur.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201

@doctors_bp.route('/api/admin/doctors/<int:doctor_id>', methods=['PUT'])
def update_doctor(doctor_id):
    data = request.get_json() or {}
    db = get_db()
    fields = {}
    
    # Map old names to new or split
    if 'name' in data:
         parts = data.get('name').split(' ', 1)
         fields['firstname'] = parts[0]
         fields['lastname'] = parts[1] if len(parts) > 1 else ''
    
    if 'department' in data: fields['specialist'] = data['department'] 
    if 'specialty' in data: fields['specialist'] = data['specialty']
         
    valid_fields = ('firstname', 'lastname', 'doctor_id', 'department', 'specialist', 'status', 'schedule', 'image', 'status_color')
    for k in valid_fields:
        if k in data:
            fields[k] = data[k]

    if not fields:
        return jsonify({'error': 'no fields to update'}), 400

    set_clause = ', '.join([f"{k} = ?" for k in fields.keys()])
    values = [fields[k] for k in fields.keys()]
    values.append(doctor_id)

    cur = db.execute(f"UPDATE doctors SET {set_clause} WHERE id_doctor = ?", values)
    db.commit()
    if cur.rowcount == 0:
        return jsonify({'error': 'not found'}), 404
    row = db.execute('SELECT * FROM doctors WHERE id_doctor = ?', (doctor_id,)).fetchone()
    return jsonify(dict(row)), 200

@doctors_bp.route('/api/admin/doctors/<int:doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    db = get_db()
    cur = db.execute('DELETE FROM doctors WHERE id_doctor = ?', (doctor_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'status': 'deleted'}), 200
