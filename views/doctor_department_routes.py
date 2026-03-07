# ==========================================
# คนที่ 5: ตาราง DoctorToDepartment (จัดการความเชี่ยวชาญ / การลิงค์แผนก)
# รับผิดชอบ: ตารางเชื่อมโยง Many-to-Many ว่าคุณหมอคนไหนอยู่แผนกอะไร
# ==========================================
from flask import Blueprint, jsonify, request
from services.doctor_department_service import (
    get_doctors_in_department,
    get_departments_for_doctor,
    assign_doctor_to_department,
    remove_doctor_from_department,
)

doctor_department_bp = Blueprint('doctor_department', __name__)

@doctor_department_bp.route("/api/department/<int:department_id>/doctors", methods=["GET"])
def api_get_doctors_by_department(department_id):
    try:
        doctors = get_doctors_in_department(department_id)
        return jsonify({"success": True, "doctors": doctors})
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404

@doctor_department_bp.route("/api/doctor/<int:doctor_id>/departments", methods=["GET"])
def api_get_departments_by_doctor(doctor_id):
    try:
        departments = get_departments_for_doctor(doctor_id)
        return jsonify({"success": True, "departments": departments})
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404

@doctor_department_bp.route("/api/admin/assign_doctor", methods=["POST"])
def api_admin_assign_doctor():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    doctor_id = data.get("doctor_id")
    department_id = data.get("department_id")
    if doctor_id is None or department_id is None:
        return jsonify({"success": False, "message": "doctor_id and department_id are required"}), 400

    try:
        mapping_id = assign_doctor_to_department(doctor_id, department_id)
        return jsonify({"success": True, "id": mapping_id}), 201
    except ValueError as e:
        message = str(e)
        status_code = 409 if "already assigned" in message else 404
        return jsonify({"success": False, "message": message}), status_code

@doctor_department_bp.route("/api/admin/remove_doctor_dept", methods=["DELETE"])
def api_admin_remove_doctor_dept():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    doctor_id = data.get("doctor_id")
    department_id = data.get("department_id")
    if doctor_id is None or department_id is None:
        return jsonify({"success": False, "message": "doctor_id and department_id are required"}), 400

    try:
        remove_doctor_from_department(doctor_id, department_id)
        return jsonify({"success": True})
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
