from flask import Blueprint, render_template, jsonify, request
from models import db, Department
from services.department_service import get_all_departments, add_department, update_department

department_bp = Blueprint('department', __name__)

@department_bp.route("/", methods=["GET"])
def Home():
    # หน้า Home ที่แสดงผลหน้าแรกของเว็บ
    return render_template("user/home.html", title="Home")

@department_bp.route("/api/departments", methods=["GET"])
def api_get_departments():
    # SELECT ดึงรายชื่อแผนกทั้งหมดให้หน้าเว็บ
    departments = get_all_departments()
    return jsonify({
        "success": True,
        "departments": departments,
        "message": "ดึงข้อมูลแผนกสำเร็จ"
    }), 200

@department_bp.route("/api/admin/departments", methods=["POST"])
def api_admin_create_department():
    # แอดมินเพิ่มแผนกใหม่ เช่น เปิดแผนกตา
    data = request.json
    if not data or not data.get('name') or str(data.get('name')).strip() == '':
        return jsonify({"success": False, "message": "กรุณาระบุชื่อแผนก"}), 400
    
    dept_id = add_department(data['name'].strip())
    if dept_id:
        return jsonify({"success": True, "id": dept_id, "message": "เพิ่มแผนกสำเร็จ"}), 201
    else:
        return jsonify({"success": False, "message": "ไม่สามารถเพิ่มแผนกได้"}), 500

@department_bp.route("/api/admin/departments/<int:department_id>", methods=["PUT"])
def api_admin_update_department(department_id):
    # แก้ไขชื่อแผนก
    data = request.json
    if not data or not data.get('name') or str(data.get('name')).strip() == '':
        return jsonify({"success": False, "message": "กรุณาระบุชื่อแผนกใหม่"}), 400
        
    from services.department_service import update_department
    result = update_department(department_id, data['name'].strip())
    if result:
        return jsonify({"success": True, "message": "อัปเดตชื่อแผนกสำเร็จ"}), 200
    
    return jsonify({"success": False, "message": "ไม่พบแผนกดังกล่าวหรืออัปเดตล้มเหลว"}), 404


