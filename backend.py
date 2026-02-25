from flask import Blueprint, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from datetime import datetime

# สร้าง Blueprint ชื่อ 'api' โดยไม่มี prefix 
api_bp = Blueprint('api', __name__)

#---------- ### -- Backend routes -- ### ---------->>>

# แป้ง
@api_bp.route("/api/register", methods=["POST"])
def api_register():
    pass

@api_bp.route("/api/login", methods=["POST"])
def api_login():
    pass

@api_bp.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    pass

@api_bp.route("/api/logout")
def api_logout():
    pass

# หน้า login ลงทะเบียน login admin logout

# -------------------------------------------------


# บอล
@api_bp.route("/api/doctors", methods=["GET"])
def api_get_doctors():
    pass

@api_bp.route("/api/departments", methods=["GET"])
def api_get_departments():
    pass

@api_bp.route("/api/bookings", methods=["POST"])
def api_create_booking():
    pass

@api_bp.route("/api/booking/<int:booking_id>", methods=["GET"])
def api_get_booking(booking_id):
    pass

# ดึงข้อมูลแพทย์ทั้งหมด ดึงข้อมูลแผนกทั้งหมด สร้างการจองคิวใหม่ ดึงรายละเอียดการจองคิวตาม ID
# ดึงข้อมูลจาก docter และ department มาแสดงในหน้า booking

# -------------------------------------------------

# คิม
@api_bp.route("/api/doctors", methods=["GET"])
def api_get_doctors():
    pass

@api_bp.route("/api/departments", methods=["GET"])
def api_get_departments():
    pass

@api_bp.route("/api/bookings", methods=["GET"])
def api_get_bookings():
    pass

@api_bp.route("/api/booking/<int:booking_id>", methods=["GET"])
def api_get_booking(booking_id):
    pass

# เลือกวันที่และเวลาที่ต้องการจองคิว ดึงข้อมูลแพทย์ทั้งหมด ดึงข้อมูลแผนกทั้งหมดตาม ID

# -------------------------------------------------

# ปอน 

@api_bp.route("/api/admin/slots", methods=["GET"])
def api_admin_get_slots():
    pass

@api_bp.route("/api/booking/<int:booking_id>", methods=["PUT"])
def api_update_booking(booking_id):
    pass

@api_bp.route("/api/booking/<int:booking_id>", methods=["DELETE"])
def api_delete_booking(booking_id):
    pass
# ดูรายละเอียดการจองคิวของผู้ใช้ เลื่อนวันจองคิวของผู้ใช้ ยกเลิกการจองคิวของผู้ใช้

# -------------------------------------------------

# ฟิล์ม นายพงศกร กอคูณ
@api_bp.route("/api/bookings", methods=["GET"])
def api_get_bookings():
    pass
@api_bp.route("/api/booking/<int:booking_id>", methods=["PUT"])
def api_update_booking(booking_id):
    pass
# ดึงมาจาก Booking_ID ดูรายละเอียดการจองคิว และอัพเดตสถานะการจองคิว (เช่น ยืนยัน/ยกเลิก)

# -------------------------------------------------

# ชันเด นายวุฒิภัทร วิริยเสนกุล

@api_bp.route("/api/notifications", methods=["GET"])
def api_get_notifications():
    pass


@api_bp.route("/api/bookings", methods=["GET"])
def api_get_bookings():
    pass
# ดึงการแจ้งเตือนทั้งหมดของผู้ใช้ที่ล็อกอินอยู่ และดึงการจองคิวทั้งหมดของผู้ใช้ที่ล็อกอินอยู่

# -------------------------------------------------

# แฟรงค์ นายรัชชานนท์ อรรถพันธ์

@api_bp.route("/api/admin/slots", methods=["GET"])
def api_admin_get_slots():
    pass

@api_bp.route("/api/admin/bookings", methods=["GET"])
def api_admin_get_all_bookings():
    pass

@api_bp.route("/api/admin/bookings/<int:booking_id>", methods=["POST"])
def api_admin_update_booking_status(booking_id):
    pass
# ตรวจสอบรายชื่อเข้าตรวจ, ดูประวัติการจองทั้งหมด, จัดการสล็อตเวลา (Manage Slots)

# --------------------------------------------------

# ภีม นายอภิสิทธิ์ พรหมมา
@api_bp.route("/api/doctors", methods=["GET"])
def api_get_doctors():
    pass

@api_bp.route("/api/admin/doctors", methods=["POST"])
def api_admin_add_doctor():
    pass

@api_bp.route("/api/admin/doctors/<int:doctor_id>", methods=["PUT"])
def api_admin_update_doctor(doctor_id):
    pass

@api_bp.route("/api/admin/doctors/<int:doctor_id>", methods=["DELETE"])
def api_admin_delete_doctor(doctor_id):
    pass

# จัดการรายชื่อแพทย์ (Manage Doctors สร้าง/อัปเดต/ลบ) และ Admin Home
# -------------------------------------------------