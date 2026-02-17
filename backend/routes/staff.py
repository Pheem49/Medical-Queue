from flask import Blueprint, request, jsonify
from datetime import datetime
from database import get_db

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/api/admin/staff', methods=['GET'])
def list_staff():
    db = get_db()
    rows = db.execute('SELECT * FROM staff ORDER BY id_admin DESC').fetchall()
    return jsonify([dict(r) for r in rows])


@staff_bp.route('/api/admin/staff', methods=['POST'])
def create_staff():
    data = request.get_json() or {}
    db = get_db()
    
    # Handle splitting fullName if frontend still sends it, or expect firstname/lastname
    fname = data.get('firstname')
    lname = data.get('lastname')
    if not fname and data.get('fullName'):
        parts = data.get('fullName').split(' ', 1)
        fname = parts[0]
        lname = parts[1] if len(parts) > 1 else ''

    cur = db.execute(
        "INSERT INTO staff (firstname, lastname, employee_id, username, hash_password, contact, role, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (
            fname,
            lname,
            data.get('employee_id'),
            data.get('username'),
            data.get('password'), # assuming frontend sends 'password'
            data.get('contact'),
            data.get('role'),
            datetime.utcnow().isoformat(),
        ),
    )
    db.commit()
    row = db.execute('SELECT * FROM staff WHERE id_admin = ?', (cur.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201


@staff_bp.route('/api/admin/staff/<int:staff_id>', methods=['PUT'])
def update_staff(staff_id):
    data = request.get_json() or {}
    db = get_db()
    fields = {}
    
    # Map incoming JSON keys to DB columns if needed, or use direct keys
    # Assuming frontend might send: firstname, lastname, employee_id, username, password, contact, role
    
    if 'firstname' in data: fields['firstname'] = data['firstname']
    if 'lastname' in data: fields['lastname'] = data['lastname']
    if 'fullName' in data: # backward compat
        parts = data['fullName'].split(' ', 1)
        fields['firstname'] = parts[0]
        fields['lastname'] = parts[1] if len(parts) > 1 else ''
        
    for k in ('employee_id', 'username', 'contact', 'role'):
        if k in data:
            fields[k] = data[k]
            
    if 'password' in data:
        fields['hash_password'] = data['password']

    if not fields:
        return jsonify({'error': 'no fields to update'}), 400

    set_clause = ', '.join([f"{k} = ?" for k in fields.keys()])
    values = [fields[k] for k in fields.keys()]
    values.append(staff_id)

    cur = db.execute(f"UPDATE staff SET {set_clause} WHERE id_admin = ?", values)
    db.commit()
    if cur.rowcount == 0:
        return jsonify({'error': 'not found'}), 404
    row = db.execute('SELECT * FROM staff WHERE id_admin = ?', (staff_id,)).fetchone()
    return jsonify(dict(row)), 200


@staff_bp.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'missing credentials'}), 400
    db = get_db()
    row = db.execute('SELECT * FROM staff WHERE username = ? AND hash_password = ?', (username, password)).fetchone()
    if not row:
        return jsonify({'error': 'invalid credentials'}), 401
    
    # Return friendly structure
    user = dict(row)
    del user['hash_password']
    user['full_name'] = f"{user.get('firstname', '')} {user.get('lastname', '')}".strip()
    return jsonify(user), 200


@staff_bp.route('/api/admin/staff/<int:staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    db = get_db()
    cur = db.execute('DELETE FROM staff WHERE id_admin = ?', (staff_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'status': 'deleted'}), 200
