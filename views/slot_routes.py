from flask import Blueprint, render_template, jsonify
from models import db, AppointmentSlot

slot_bp = Blueprint('slot', __name__)

@slot_bp.route("/staff/checkin")
def StaffCheckin():
    return render_template("admin/scanner.html", title="Staff Check-in")

@slot_bp.route("/api/admin/slots", methods=["GET"])
def api_admin_get_slots():
    return jsonify([])

@slot_bp.route("/api/admin/slots", methods=["POST"])
def api_admin_create_slot():
    return jsonify({"status": "success"})

@slot_bp.route("/api/admin/slots/<int:slot_id>", methods=["PUT"])
def api_admin_update_slot(slot_id):
    return jsonify({"status": "success"})

@slot_bp.route("/api/admin/slots/<int:slot_id>", methods=["DELETE"])
def api_admin_delete_slot(slot_id):
    return jsonify({"status": "success"})
