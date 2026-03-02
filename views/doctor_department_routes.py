from flask import Blueprint, jsonify
from models import db, DoctorToDepartment

doctor_department_bp = Blueprint('doctor_department', __name__)

@doctor_department_bp.route("/api/department/<int:department_id>/doctors", methods=["GET"])
def api_get_doctors_by_department(department_id):
    return jsonify([])

@doctor_department_bp.route("/api/doctor/<int:doctor_id>/departments", methods=["GET"])
def api_get_departments_by_doctor(doctor_id):
    return jsonify([])

@doctor_department_bp.route("/api/admin/assign_doctor", methods=["POST"])
def api_admin_assign_doctor():
    return jsonify({"status": "success"})

@doctor_department_bp.route("/api/admin/remove_doctor_dept", methods=["DELETE"])
def api_admin_remove_doctor_dept():
    return jsonify({"status": "success"})
