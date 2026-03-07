# ==========================================
# คนที่ 4: ตาราง Doctor (จัดการประวัติคุณหมอ)
# รับผิดชอบ: ฐานข้อมูลแพทย์รายบุคคล (เพิ่ม/ลบแพทย์)
# ==========================================
from flask import Blueprint, render_template, jsonify, request
from services.doctor_service import get_all_doctors, get_all_doctors_admin, add_doctor, update_doctor, remove_doctor

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route("/staff/doctors", methods=["GET"])
def StaffDoctors():
    return render_template("admin/doctors.html", title="Staff Doctors")

# เส้นสำหรับดึงข้อมูลหมอ (ใช้ร่วมกันทั้งหน้าบ้านและหลังบ้าน)
@doctor_bp.route("/api/doctors", methods=["GET"])
def api_get_all_doctors():
    doctors = get_all_doctors()
    return jsonify({"success": True, "doctors": doctors})

@doctor_bp.route("/api/admin/doctors", methods=["GET"])
def api_admin_get_all_doctors():
    doctors = get_all_doctors_admin()
    return jsonify({"success": True, "doctors": doctors})

@doctor_bp.route("/api/admin/doctors", methods=["POST"])
def api_admin_add_doctor():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
        
    try:
        doctor_id = add_doctor(
            firstname=data.get('firstname'),
            lastname=data.get('lastname'),
            doctor_id_str=data.get('doctor_id'),
            specialist=data.get('specialist'),
            status=data.get('status'),
            schedule_json=data.get('schedule'),
            department_ids=data.get('department_ids')
        )
        return jsonify({"success": True, "id": doctor_id}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@doctor_bp.route("/api/admin/doctors/<int:doctor_id>", methods=["PUT"])
def api_admin_update_doctor(doctor_id):
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
        
    try:
        success = update_doctor(doctor_id, data)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Doctor not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@doctor_bp.route("/api/admin/doctors/<int:doctor_id>", methods=["DELETE"])
def api_admin_delete_doctor(doctor_id):
    try:
        success = remove_doctor(doctor_id)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Doctor not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
