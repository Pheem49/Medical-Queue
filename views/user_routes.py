from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from models import db, User

user_bp = Blueprint('user', __name__)

@user_bp.route("/login")
def Login():
    if 'user_id' in session:
        return redirect(url_for('user.Home'))
    return render_template("auth/login.html", title="Login")

@user_bp.route("/register")
def Register():
    if 'user_id' in session:
        return redirect(url_for('user.Home'))
    return render_template("auth/register.html", title="Register")

@user_bp.route("/api/register", methods=["POST"])
def api_register():
    return jsonify({"status": "success"})

@user_bp.route("/api/login", methods=["POST"])
def api_login():
    return jsonify({"status": "success"})
