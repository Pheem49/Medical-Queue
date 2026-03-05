from flask import Blueprint, render_template, jsonify, request
from models import db, AppointmentSlot
from services.slot_service import create_appointment_slot, update_slot_status, get_slots_by_doctor_date

slot_bp = Blueprint('slot', __name__)

@slot_bp.route("/staff/checkin", methods=["GET"])
def StaffCheckin():
    return render_template("admin/scanner.html", title="Staff Check-in")

@slot_bp.route("/api/admin/slots", methods=["POST"])
def api_admin_create_slot():
    try:
        data = request.json
        doctor_id = data.get('doctor_id')
        department_id = data.get('department_id')
        slot_date = data.get('slot_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        max_capacity = data.get('max_capacity')
        
        create_appointment_slot(doctor_id, department_id, slot_date, start_time, end_time, max_capacity)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@slot_bp.route("/api/admin/slots", methods=["GET"])
def api_admin_get_slots():
    doctor_id = request.args.get('doctor_id')
    date_str = request.args.get('date')
    if not doctor_id or not date_str:
        return jsonify([])
        
    slots = get_slots_by_doctor_date(doctor_id, date_str)
    return jsonify(slots)

@slot_bp.route("/api/admin/slots/<int:slot_id>/status", methods=["PUT"])
def api_admin_update_slot_status(slot_id):
    data = request.json
    new_status = data.get('status')
    if update_slot_status(slot_id, new_status):
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Slot not found"}), 404

@slot_bp.route("/api/admin/slots/<int:slot_id>", methods=["DELETE"])
def api_admin_delete_slot(slot_id):
    from services.slot_service import delete_appointment_slot
    if delete_appointment_slot(slot_id):
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Cannot delete slot because it might be booked or not found"}), 400