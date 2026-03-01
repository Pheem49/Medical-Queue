from flask import Blueprint, render_template, jsonify
from models import db, Doctor

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route("/staff/doctors", methods=["GET"])
def StaffDoctors():
    return render_template("admin/doctors.html", title="Staff Doctors")

@doctor_bp.route("/api/doctors", methods=["GET"])
def api_get_doctors():
    return jsonify([])

@doctor_bp.route("/api/admin/doctors", methods=["POST"])
def api_admin_add_doctor():
    return jsonify({"status": "success"})

@doctor_bp.route("/api/admin/doctors/<int:doctor_id>", methods=["PUT"])
def api_admin_update_doctor(doctor_id):
    return jsonify({"status": "success"})

@doctor_bp.route("/api/admin/doctors/<int:doctor_id>", methods=["DELETE"])
def api_admin_delete_doctor(doctor_id):
    return jsonify({"status": "success"})
