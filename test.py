from flask import Blueprint, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Doctor, Department, Booking, Slot, Notification # สมมติว่ามี Model เหล่านี้นะครับ
from datetime import datetime

api_bp = Blueprint('api', __name__)

# ==========================================
# 1. ระบบยืนยันตัวตน (Authentication) - [แป้ง/คิม]
# ==========================================

@api_bp.route("/api/register", methods=["POST"])#แป้ง
def api_register():
    # หน้าลงทะเบียนผู้ป่วยใหม่
    pass

@api_bp.route("/api/login", methods=["POST"])#แป้ง
def api_login():
    # หน้าเข้าสู่ระบบผู้ใช้งานทั่วไป
    pass

@api_bp.route("/api/admin/login", methods=["POST"])#คิม
def api_admin_login():
    # หน้าเข้าสู่ระบบของเจ้าหน้าที่ (Admin)
    pass

@api_bp.route("/api/logout", methods=["DELETE"])#แป้ง
def api_logout():
    # ลบ session ของผู้ใช้
    pass


# ==========================================
# 2. หน้า home แสดงสถานะคิว (Departments) - [บอล/คิม/ภีม]
# ==========================================

@api_bp.route("/api/doctors", methods=["GET"])# บอล 
def api_get_doctors_list():
    # ดึงข้อมูลแพทย์ทั้งหมด (สำหรับหน้าแรก หรือหน้าจอง)
    pass

@api_bp.route("/api/departments", methods=["GET"])# คิม
def api_get_departments_list():
    # ดึงข้อมูลแผนกทั้งหมด
    pass

@api_bp.route("/api/departments/<int:dept_id>/doctors", methods=["GET"])
def api_get_doctors_by_department(dept_id):
    # ดึงรายชื่อแพทย์แยกตามแผนก
    pass


# ==========================================
# 3. ระบบการจองสำหรับผู้ใช้ (User Bookings) - [บอล/ปอน/ชันเด]
# ==========================================

@api_bp.route("/api/bookings", methods=["POST"])
def api_create_booking():
    # สร้างการจองคิวใหม่
    pass

@api_bp.route("/api/my-bookings", methods=["GET"])
def api_get_user_bookings():
    # ดูประวัติการจองทั้งหมดของผู้ใช้ที่ Login อยู่
    pass

@api_bp.route("/api/booking/<int:booking_id>", methods=["GET"])
def api_get_booking_by_id(booking_id):
    # ดูรายละเอียดการจองคิวรายบุคคล / QR Code
    pass

@api_bp.route("/api/booking/<int:booking_id>", methods=["PUT"])
def api_reschedule_booking(booking_id):
    # เลื่อนวันนัดหมาย (Update Booking)
    pass

@api_bp.route("/api/booking/<int:booking_id>", methods=["DELETE"])
def api_cancel_booking(booking_id):
    # ยกเลิกการจอง
    pass

@api_bp.route("/api/notifications", methods=["GET"])
def api_get_notifications():
    # ดึงการแจ้งเตือนของผู้ใช้
    pass


# ==========================================
# 4. ระบบจัดการสำหรับ Admin (Admin Panel) - [ฟิล์ม/แฟรงค์/ภีม/ปอน]
# ==========================================

# --- จัดการคิวการจอง (Booking Management) ---
@api_bp.route("/api/admin/bookings", methods=["GET"])
def api_admin_get_all_bookings():
    # ดูรายการจองทั้งหมดในระบบ
    pass

@api_bp.route("/api/admin/booking/<int:booking_id>", methods=["PATCH"])
def api_admin_update_booking_status(booking_id):
    # อัปเดตสถานะ เช่น ยืนยัน / ไม่มาตามนัด (No Show)
    pass

# --- จัดการสล็อตเวลา (Slot Management) ---
@api_bp.route("/api/admin/slots", methods=["GET", "POST"])# ปอนดูสล็อกเวลา , แฟรงค์สร้างสล็อกใหม่
def api_admin_manage_slots():
    # GET: ดูสล็อตเวลาทั้งหมด, POST: สร้างสล็อตใหม่
    pass

@api_bp.route("/api/admin/slots/<int:slot_id>", methods=["PUT", "DELETE"])# แฟรงค์
def api_admin_edit_slot(slot_id):
    # แก้ไขหรือลบสล็อตเวลา
    pass

# --- จัดการข้อมูลแพทย์ (Doctor Management) ---
@api_bp.route("/api/doctors", methods=["GET"])# ภีม 
def api_get_doctors_list():
    # ดึงข้อมูลแพทย์ทั้งหมด (สำหรับหน้าแรก หรือหน้าจอง)
    pass

@api_bp.route("/api/admin/doctors", methods=["POST"])# ภีม
def api_admin_add_doctor():
    # เพิ่มแพทย์ใหม่
    pass

@api_bp.route("/api/admin/doctors/<int:doctor_id>", methods=["PUT", "DELETE"])# ภีม
def api_admin_modify_doctor(doctor_id):
    # แก้ไขหรือลบข้อมูลแพทย์
    pass