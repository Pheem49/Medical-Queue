from flask import Blueprint, render_template, jsonify
from models import db, Booking

booking_management_bp = Blueprint('booking_management', __name__)

@booking_management_bp.route("/staff/patients", methods=["GET"])
def StaffPatients():
    return render_template("admin/dashboard.html", title="Staff Patients")

@booking_management_bp.route("/staff/history", methods=["GET"])
def StaffHistory():
    return render_template("admin/history.html", title="Staff History")

@booking_management_bp.route("/api/admin/bookings", methods=["GET"])
def api_get_admin_bookings():
    return jsonify([])

@booking_management_bp.route("/api/admin/bookings/<int:booking_id>/status", methods=["PUT"])
def api_update_admin_booking_status(booking_id):
    return jsonify({"status": "success"})

@booking_management_bp.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
def api_delete_booking(booking_id):
    return jsonify({"status": "success"})
