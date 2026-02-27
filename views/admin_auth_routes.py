from flask import Blueprint, render_template, jsonify
from models import db, Admin

admin_auth_bp = Blueprint('admin_auth', __name__)

@admin_auth_bp.route("/staff/login")
def StaffLogin():
    return render_template("auth/staff_login.html", title="Staff Login")

@admin_auth_bp.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    return jsonify({"status": "success"})

@admin_auth_bp.route("/api/logout", methods=["DELETE"])
def api_logout():
    return jsonify({"status": "success"})
