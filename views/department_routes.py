from flask import Blueprint, render_template, jsonify
from models import db, Department

department_bp = Blueprint('department', __name__)

@department_bp.route("/", methods=["GET"])
def Home():
    return render_template("user/home.html", title="Home")

@department_bp.route("/api/departments", methods=["GET"])
def api_get_departments():
    return jsonify([])

@department_bp.route("/api/admin/departments", methods=["POST"])
def api_admin_create_department():
    return jsonify({"status": "success"})

@department_bp.route("/api/admin/departments/<int:department_id>", methods=["PUT"])
def api_admin_update_department(department_id):
    return jsonify({"status": "success"})
