from flask import Blueprint, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
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
    pass

@api_bp.route("/api/bookings", methods=["POST"])# หน้าหน้าตรวจสอบและยืนยันข้อมูลการจอง ไม่ได้ทำ Booking Details
def api_create_booking():
    pass

@api_bp.route("/api/booking/<int:booking_id>", methods=["DELETE"])# การยกเลิกการจอง
def api_deletet_booking():
    pass


# -------------------------------------------------

# คิม
# เลือกวันที่และเวลาที่ต้องการจองคิว ดึงข้อมูลแพทย์ทั้งหมด ดึงข้อมูลแผนกทั้งหมดตาม ID
@api_bp.route("/api/departments", methods=["GET"])# สถานะคิวปัจจุบัน แผนก
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

@api_bp.route("/api/admin/slots", methods=["POST"])# 
def api_admin_get_slots_frank():
    pass

@api_bp.route("/api/admin/slots", methods=["PUT"])# 
def api_admin_get_all_bookings():
    pass

@api_bp.route("/api/admin/slots", methods=["DELETE"])# 
def api_admin_update_booking_status(booking_id):
    pass

# --------------------------------------------------

# ภีม นายอภิสิทธิ์ พรหมมา
# จัดการรายชื่อแพทย์ (Manage Doctors สร้าง/อัปเดต/ลบ) และ Admin Home
@api_bp.route("/api/doctors", methods=["GET"])
def api_get_doctors_admin():
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

# -------------------------------------------------