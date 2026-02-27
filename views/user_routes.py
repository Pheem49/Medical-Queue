from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models import db, User

user_bp = Blueprint('user', __name__)

@user_bp.route("/login", methods=["GET"])
def Login():
    if 'user_id' in session:
        return redirect(url_for('department.Home'))
    return render_template("auth/login.html", title="Login")

@user_bp.route("/register", methods=["GET"])
def Register():
    if 'user_id' in session:
        return redirect(url_for('department.Home'))
    return render_template("auth/register.html", title="Register")

@user_bp.route("/api/register", methods=["POST"])
def api_register():
    return jsonify({"status": "success"})

@user_bp.route("/api/login", methods=["POST"])
def api_login():
    return jsonify({"status": "success"})

@user_bp.route("/api/user/profile", methods=["PUT"])
def api_update_profile():
    return jsonify({"status": "success"})
