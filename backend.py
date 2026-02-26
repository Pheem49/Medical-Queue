from flask import Blueprint, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Doctor, Department, DoctorToDepartment
from datetime import datetime

# สร้าง Blueprint ชื่อ 'api' โดยไม่มี prefix 
api_bp = Blueprint('api', __name__)

#---------- ### -- Backend routes -- ### ---------->>>

# แป้ง
# หน้า login ลงทะเบียน login admin logout
@api_bp.route("/api/register", methods=["POST"]) # หน้าลงทะเบียนผู้ป่วยใหม่ (Registration Page)
def api_register():
    pass

@api_bp.route("/api/login", methods=["POST"])# หน้าเข้าสู่ระบบ (Login Page)
def api_login():
    pass

@api_bp.route("/api/logout", methods=["DELETE"])# ลบ session ของผู้ใช้ที่ล็อกอินอยู่ (Logout)
def api_logout():
    pass


# -------------------------------------------------


# บอล
# ดึงข้อมูลแพทย์ทั้งหมด ดึงข้อมูลแผนกทั้งหมด สร้างการจองคิวใหม่ ดึงรายละเอียดการจองคิวตาม ID
# ดึงข้อมูลจาก docter และ department มาแสดงในหน้า booking
@api_bp.route("/api/doctors", methods=["GET"])# เลือกแพทย์
def api_get_doctors():
    pass

@api_bp.route("/api/departments", methods=["GET"])# เลือกแผนก
def api_get_departments_ball():
    try:
        departments = Department.query.all()
        return jsonify({
            "success": True, 
            "departments": [{"department_id": d.department_id, "name": d.name} for d in departments]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api_bp.route("/api/bookings", methods=["POST"])# หน้าหน้าตรวจสอบและยืนยันข้อมูลการจอง ไม่ได้ทำ Booking Details
def api_create_booking():
    pass

@api_bp.route("/api/booking/<int:booking_id>", methods=["DELETE"])# การยกเลิกการจอง
def api_deletet_booking():
    pass


# -------------------------------------------------

# คิม
# เลือกวันที่และเวลาที่ต้องการจองคิว ดึงข้อมูลแพทย์ทั้งหมด ดึงข้อมูลแผนกทั้งหมดตาม ID
@api_bp.route("/api/departments/status", methods=["GET"])# สถานะคิวปัจจุบัน แผนก
def api_get_departments():
    pass

@api_bp.route("/api/admin/login", methods=["POST"])# หน้าเข้าสู่ระบบของเจ้าหน้าที่ (Admin Login)
def api_admin_login():
    pass

@api_bp.route("/api/booking/<int:booking_id>/slot", methods=["GET"])# ทำสี slot ต่างๆ ตามสถานะคิว (เช่น ว่าง/เต็ม/ไม่ว่าง)
def api_get_booking(booking_id):
    pass


# -------------------------------------------------

# ปอน 
# ดูรายละเอียดการจองคิวของผู้ใช้ เลื่อนวันจองคิวของผู้ใช้ ยกเลิกการจองคิวของผู้ใช้

@api_bp.route("/api/admin/slots", methods=["GET"])# ดึงข้อมูลสล็อตเวลาที่มีอยู่ทั้งหมด (เช่น วันที่และเวลาที่เปิดให้จองคิว) เพื่อแสดงในหน้า Admin Home
def api_admin_get_slots():
    pass

@api_bp.route("/api/booking/<int:booking_id>", methods=["PUT"])#  เลือกวันและเวลาเพื่อเลื่อนการจองคิวของผู้ใช้ (Reschedule Booking)
def api_update_booking(booking_id):
    pass

@api_bp.route("/api/booking/<int:booking_id>", methods=["GET"])# ดูรายละเอียดการจองคิวของผู้ใช้ (Booking Details)/QR code
def api_get_booking_details(booking_id):
    pass

# -------------------------------------------------

# ฟิล์ม นายพงศกร กอคูณ
# ดึงมาจาก Booking_ID ดูรายละเอียดการจองคิว และอัพเดตสถานะการจองคิว (เช่น ยืนยัน/ยกเลิก)
@api_bp.route("/api/admin/bookings", methods=["GET"])# ดูรายการจองทั้งหมด admin (All Bookings)
def api_get_admin_bookings():
    pass
@api_bp.route("/api/admin/booking/<int:booking_id>", methods=["GET"])#  ตรวจสอบรายชื่อการจอง admin(Check Booking List)
def api_get_admin_id_booking(booking_id):
    pass
# -------------------------------------------------

# ชันเด นายวุฒิภัทร วิริยเสนกุล

# ดึงการแจ้งเตือนทั้งหมดของผู้ใช้ที่ล็อกอินอยู่ และดึงการจองคิวทั้งหมดของผู้ใช้ที่ล็อกอินอยู่
@api_bp.route("/api/notifications", methods=["GET"])# ดึงการแจ้งเตือนทั้งหมดของผู้ใช้ที่ล็อกอินอยู่
def api_get_notifications():
    pass

@api_bp.route("/api/bookings", methods=["GET"])# ดึงการจองคิวทั้งหมดของผู้ใช้ที่ล็อกอินอยู่
def api_get_bookings_sunday():
    pass

@api_bp.route("/api/booking/<int:booking_id>", methods=["GET"])# ระบบตัดคิวอัตโนมัติเมื่อถึงเวลานัดหมาย ถ้าเกินเวลานัดหมายแล้วผู้ใช้ยังไม่มาถึง ระบบจะยกเลิกการจองคิวของผู้ใช้โดยอัตโนมัติ (เช่น อัปเดตสถานะการจองคิวเป็น "No Show")
def api_system_get_booking(booking_id):
    pass

# -------------------------------------------------

# แฟรงค์ นายรัชชานนท์ อรรถพันธ์
# ตรวจสอบรายชื่อเข้าตรวจ, ดูประวัติการจองทั้งหมด, จัดการสล็อตเวลา (Manage Slots)

@api_bp.route("/api/admin/slots", methods=["POST"]) # สร้างสล็อตเวลาที่เปิดให้จองคิว
def api_admin_create_slot():
    pass

@api_bp.route("/api/admin/slots/<int:slot_id>", methods=["PUT"]) # แก้ไขข้อมูลสล็อตเวลาที่มีอยู่
def api_admin_update_slot(slot_id):
    pass

@api_bp.route("/api/admin/slots/<int:slot_id>", methods=["DELETE"]) # ลบสล็อตเวลาที่มีอยู่
def api_admin_delete_slot(slot_id):
    pass


# --------------------------------------------------

# ภีม นายอภิสิทธิ์ พรหมมา
# จัดการรายชื่อแพทย์ (Manage Doctors สร้าง/อัปเดต/ลบ) และ Admin Home
@api_bp.route("/api/admin/doctors", methods=["GET"])# ดึงข้อมูลแพทย์ทั้งหมดสำหรับ Admin (Admin Home)
def api_get_doctors_admin():
    try:
        doctors = Doctor.query.all()
        results = []
        for doc in doctors:
            doc_deps = DoctorToDepartment.query.filter_by(doctor_id=doc.id).all()
            dep_names = []
            for dd in doc_deps:
                dep = Department.query.get(dd.department_id)
                if dep:
                    dep_names.append(dep.name)
            results.append({
                "id": doc.id,
                "doctor_id": doc.doctor_id,
                "firstname": doc.firstname,
                "lastname": doc.lastname,
                "specialist": doc.specialist,
                "status": doc.status,
                "schedule": doc.schedule,
                "departments": dep_names
            })
        return jsonify({"success": True, "doctors": results}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api_bp.route("/api/admin/doctors", methods=["POST"])# สร้างแพทย์ใหม่ (Create Doctor)
def api_admin_add_doctor():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    try:
        new_doc = Doctor(
            firstname=data.get('firstname'),
            lastname=data.get('lastname'),
            doctor_id=data.get('doctor_id'),
            specialist=data.get('specialist'),
            status=data.get('status', 'ว่างวันนี้'),
            schedule=data.get('schedule', {})
        )
        db.session.add(new_doc)
        db.session.flush() # To get the new_doc.id
        
        department_ids = data.get('department_ids', [])
        for dep_id in department_ids:
            new_rel = DoctorToDepartment(doctor_id=new_doc.id, department_id=dep_id)
            db.session.add(new_rel)
            
        db.session.commit()
        return jsonify({"success": True, "message": "Doctor added successfully", "id": new_doc.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@api_bp.route("/api/admin/doctors/<int:doctor_id>", methods=["PUT"])# แกไขข้อมูลแพทย์ที่มีอยู่ (Update Doctor)
def api_admin_update_doctor(doctor_id):
    doc = Doctor.query.get(doctor_id)
    if not doc:
        return jsonify({"success": False, "message": "Doctor not found"}), 404
        
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
        
    try:
        doc.firstname = data.get('firstname', doc.firstname)
        doc.lastname = data.get('lastname', doc.lastname)
        doc.doctor_id = data.get('doctor_id', doc.doctor_id)
        doc.specialist = data.get('specialist', doc.specialist)
        doc.status = data.get('status', doc.status)
        doc.schedule = data.get('schedule', doc.schedule)
        
        # Update departments if provided (replace all)
        if 'department_ids' in data:
            DoctorToDepartment.query.filter_by(doctor_id=doc.id).delete()
            for dep_id in data['department_ids']:
                new_rel = DoctorToDepartment(doctor_id=doc.id, department_id=dep_id)
                db.session.add(new_rel)
                
        db.session.commit()
        return jsonify({"success": True, "message": "Doctor updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@api_bp.route("/api/admin/doctors/<int:doctor_id>", methods=["DELETE"])# ลบแพทย์ที่มีอยู่ (Delete Doctor)
def api_admin_delete_doctor(doctor_id):
    doc = Doctor.query.get(doctor_id)
    if not doc:
        return jsonify({"success": False, "message": "Doctor not found"}), 404
        
    try:
        # Delete relationships in doctor_to_department
        DoctorToDepartment.query.filter_by(doctor_id=doc.id).delete()
        db.session.delete(doc)
        db.session.commit()
        return jsonify({"success": True, "message": "Doctor deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# -------------------------------------------------