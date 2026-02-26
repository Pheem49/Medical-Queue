from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login")
def Login():
    if 'user_id' in session:
        return redirect(url_for('user.Home'))
    return render_template("auth/login.html", title="Login")

@auth_bp.route("/register")
def Register():
    if 'user_id' in session:
        return redirect(url_for('user.Home'))
    return render_template("auth/register.html", title="Register")

@auth_bp.route("/staff/login")
def StaffLogin():
    return render_template("auth/staff_login.html", title="Staff Login")

@auth_bp.route("/api/register", methods=["POST"])
def api_register():
    return jsonify({"status": "success"})

@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    return jsonify({"status": "success"})

@auth_bp.route("/api/logout", methods=["DELETE"])
def api_logout():
    return jsonify({"status": "success"})

@auth_bp.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    return jsonify({"status": "success"})
