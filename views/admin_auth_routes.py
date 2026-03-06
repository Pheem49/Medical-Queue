# ==========================================
# คนที่ 2: ตาราง Admin (จัดการเจ้าหน้าที่)
# รับผิดชอบ: ข้อมูลสิทธิ์การเป็นแอดมินหรือพยาบาล
# ==========================================
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from models import db, Admin
from services.admin_auth_service import verify_admin_login

admin_auth_bp = Blueprint('admin_auth', __name__)

# FrontEND Route
@admin_auth_bp.route("/staff/login", methods=["GET"])
def StaffLogin():
    if 'admin_id' in session:
        return redirect(url_for('department.Home'))
    if 'user_id' in session:
        return redirect(url_for('department.Home'))
    return render_template("auth/staff_login.html", title="Staff Login")
@admin_auth_bp.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    data = request.get_json() if request.is_json else request.form
    
    login_id = data.get('username') or data.get('employee_id')
    password = data.get('password')
    
    if not login_id or not password:
        return jsonify({"status": "error", "message": "กรุณากรอกรหัสพนักงานและรหัสผ่าน"}), 400
        
    admin = verify_admin_login(login_id, password)
    
    if admin:
        session['admin_id'] = admin.id_admin
        session['admin_name'] = f"{admin.first_name} {admin.last_name}"
        session['role'] = 'admin'
        
        return jsonify({
            "status": "success", 
            "message": "เข้าสู่ระบบสำเร็จ",
            "redirect": "/staff/patients"
        }), 200
    else:
        return jsonify({"status": "error", "message": "รหัสพนักงานหรือรหัสผ่านไม่ถูกต้อง"}), 401

@admin_auth_bp.route("/api/logout", methods=["DELETE", "POST", "GET"])
def api_logout():
    session.clear()
    
    if request.method == "GET":
        return redirect(url_for('department.Home'))
        
    return jsonify({"status": "success", "message": "ออกจากระบบสำเร็จ"}), 200
