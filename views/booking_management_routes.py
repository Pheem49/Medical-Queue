from flask import Blueprint, render_template, jsonify, request
from models import db, Booking
from services import booking_management_service

booking_management_bp = Blueprint('booking_management', __name__)

@booking_management_bp.route("/staff/patients", methods=["GET"])
def StaffPatients():
    return render_template("admin/dashboard.html", title="Staff Patients")

@booking_management_bp.route("/staff/history", methods=["GET"])
def StaffHistory():
    return render_template("admin/history.html", title="Staff History")

@booking_management_bp.route("/api/admin/bookings", methods=["GET"])
def api_get_admin_bookings():
    date_filter = request.args.get('date') # รับค่า 'date' จาก query string (e.g., ?date=2023-10-27)
    bookings = booking_management_service.get_all_bookings_for_admin(date_filter)
    if bookings is None:
        return jsonify({"error": "Failed to retrieve bookings"}), 500
    return jsonify(bookings)

@booking_management_bp.route("/api/admin/bookings/<int:booking_id>/status", methods=["PUT"])
def api_update_admin_booking_status(booking_id):
    data = request.get_json()
    new_status = data.get('status')

    if not new_status:
        return jsonify({"error": "Missing status"}), 400

    updated_booking, error = booking_management_service.update_booking_status(booking_id, new_status)

    if error:
        return jsonify({"error": error}), 404

    return jsonify(updated_booking)

@booking_management_bp.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
def api_delete_booking(booking_id):
    """
    Endpoint สำหรับลบการจอง ซึ่งอาจถูกเรียกโดยคนไข้หรือเจ้าหน้าที่
    """
    success, message = booking_management_service.delete_booking_and_update_slot(booking_id)

    if not success:
        return jsonify({"error": message}), 404

    return jsonify({"status": "success", "message": message})
