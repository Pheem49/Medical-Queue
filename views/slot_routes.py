from flask import Blueprint, render_template, jsonify
from models import db, AppointmentSlot

slot_bp = Blueprint('slot', __name__)

@slot_bp.route("/staff/checkin", methods=["GET"])
def StaffCheckin():
    return render_template("admin/scanner.html", title="Staff Check-in")

@slot_bp.route("/api/admin/slots", methods=["POST"])
def api_admin_create_slot():
    return jsonify({"status": "success"})

@slot_bp.route("/api/admin/slots", methods=["GET"])
def api_admin_get_slots():
    return jsonify([])

@slot_bp.route("/api/admin/slots/<int:slot_id>/status", methods=["PUT"])
def api_admin_update_slot_status(slot_id):
    return jsonify({"status": "success"})
