from flask import Blueprint, render_template

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/staff/checkin")
def StaffCheckin():
    return render_template("admin/scanner.html", title="Staff Check-in")

@admin_bp.route("/staff/patients")
def StaffPatients():
    return render_template("admin/dashboard.html", title="Staff Patients")

@admin_bp.route("/staff/history")
def StaffHistory():
    return render_template("admin/history.html", title="Staff History")

@admin_bp.route("/staff/doctors")
def StaffDoctors():
    return render_template("admin/doctors.html", title="Staff Doctors")

# API Routes
@admin_bp.route("/api/admin/slots", methods=["GET"])
def api_admin_get_slots():
    pass

@admin_bp.route("/api/admin/slots", methods=["POST"])
def api_admin_create_slot():
    pass

@admin_bp.route("/api/admin/slots/<int:slot_id>", methods=["PUT"])
def api_admin_update_slot(slot_id):
    pass

@admin_bp.route("/api/admin/slots/<int:slot_id>", methods=["DELETE"])
def api_admin_delete_slot(slot_id):
    pass

@admin_bp.route("/api/admin/bookings", methods=["GET"])
def api_get_admin_bookings():
    pass

@admin_bp.route("/api/admin/booking/<int:booking_id>", methods=["GET"])
def api_get_admin_id_booking(booking_id):
    pass

@admin_bp.route("/api/admin/doctors", methods=["GET"])
def api_get_doctors_admin():
    pass

@admin_bp.route("/api/admin/doctors", methods=["POST"])
def api_admin_add_doctor():
    pass

@admin_bp.route("/api/admin/doctors/<int:doctor_id>", methods=["PUT"])
def api_admin_update_doctor(doctor_id):
    pass

@admin_bp.route("/api/admin/doctors/<int:doctor_id>", methods=["DELETE"])
def api_admin_delete_doctor(doctor_id):
    pass
