# ==========================================
# คนที่ 3: ตาราง Department (จัดการแผนกการเปิดบริการ)
# รับผิดชอบ: ลิสต์รายชื่อแผนก และหมวดหมู่การรักษา
# ==========================================
from flask import Blueprint, render_template, jsonify, request
from models import db, Department

department_bp = Blueprint('department', __name__)

@department_bp.route("/", methods=["GET"])
def Home():
    from flask import session
    from models import Booking
    has_active = False
    if 'user_id' in session:
        has_active = Booking.query.filter(
            Booking.id_users == session['user_id'],
            Booking.booking_Status == 'รอรับบริการ'
        ).first() is not None
    return render_template("user/home.html", title="Home", has_active_booking=has_active)

from services.department_service import get_all_departments, add_department, update_department

@department_bp.route("/api/departments", methods=["GET"])
def api_get_departments():
    departments = get_all_departments()
    return jsonify({"success": True, "departments": departments})

@department_bp.route("/api/admin/departments", methods=["POST"])
def api_admin_create_department():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({"success": False, "message": "Name is required"}), 400
    
    dept_id = add_department(data['name'])
    return jsonify({"success": True, "id": dept_id})

@department_bp.route("/api/admin/departments/<int:department_id>", methods=["PUT"])
def api_admin_update_department(department_id):
    data = request.json
    if not data or 'name' not in data:
        return jsonify({"success": False, "message": "Name is required"}), 400
        
    if update_department(department_id, data['name']):
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Department not found"}), 404
