from flask import Blueprint, render_template, jsonify

user_bp = Blueprint('user', __name__)

@user_bp.route("/")
def Home():
    return render_template("user/home.html", title="Home")

@user_bp.route("/booking")
def Booking():
    return render_template("user/booking.html", title="Booking")

@user_bp.route("/mytickets")
def MyTickets():
    return render_template("user/mytickets.html", title="My Tickets")

@user_bp.route("/history")
def History():
    return render_template("user/history.html", title="History")

@user_bp.route("/notification")
def Notification():
    return render_template("user/notification.html", title="Notification")

@user_bp.route("/terms")
def Terms():
    return render_template("user/terms.html", title="Terms of Service")

@user_bp.route("/privacy")
def Privacy():
    return render_template("user/privacy.html", title="Privacy Policy")

# API Routes
@user_bp.route("/api/doctors", methods=["GET"])
def api_get_doctors():
    return jsonify([])

@user_bp.route("/api/departments", methods=["GET"])
def api_get_departments():
    return jsonify([])

@user_bp.route("/api/bookings", methods=["POST"])
def api_create_booking():
    return jsonify({"status": "success"})

@user_bp.route("/api/bookings", methods=["GET"])
def api_get_bookings():
    return jsonify([])

@user_bp.route("/api/booking/<int:booking_id>", methods=["GET"])
def api_get_booking_details(booking_id):
    return jsonify({})

@user_bp.route("/api/booking/<int:booking_id>", methods=["PUT"])
def api_update_booking(booking_id):
    return jsonify({"status": "success"})

@user_bp.route("/api/booking/<int:booking_id>", methods=["DELETE"])
def api_delete_booking(booking_id):
    return jsonify({"status": "success"})

@user_bp.route("/api/booking/<int:booking_id>/slot", methods=["GET"])
def api_get_booking_slot(booking_id):
    return jsonify({})

@user_bp.route("/api/notifications", methods=["GET"])
def api_get_notifications():
    return jsonify([])

