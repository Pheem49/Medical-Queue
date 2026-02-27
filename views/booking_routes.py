from flask import Blueprint, render_template, jsonify
from models import db, Booking

booking_bp = Blueprint('booking', __name__)

@booking_bp.route("/booking")
def BookingPage():
    return render_template("user/booking.html", title="Booking")

@booking_bp.route("/mytickets")
def MyTickets():
    return render_template("user/mytickets.html", title="My Tickets")

@booking_bp.route("/history")
def History():
    return render_template("user/history.html", title="History")

@booking_bp.route("/notification")
def Notification():
    return render_template("user/notification.html", title="Notification")

@booking_bp.route("/terms")
def Terms():
    return render_template("user/terms.html", title="Terms of Service")

@booking_bp.route("/privacy")
def Privacy():
    return render_template("user/privacy.html", title="Privacy Policy")

@booking_bp.route("/api/bookings", methods=["POST"])
def api_create_booking():
    return jsonify({"status": "success"})

@booking_bp.route("/api/bookings", methods=["GET"])
def api_get_bookings():
    return jsonify([])

@booking_bp.route("/api/booking/<int:booking_id>", methods=["GET"])
def api_get_booking_details(booking_id):
    return jsonify({})

@booking_bp.route("/api/booking/<int:booking_id>", methods=["PUT"])
def api_update_booking(booking_id):
    return jsonify({"status": "success"})

@booking_bp.route("/api/booking/<int:booking_id>", methods=["DELETE"])
def api_delete_booking(booking_id):
    return jsonify({"status": "success"})

@booking_bp.route("/api/booking/<int:booking_id>/slot", methods=["GET"])
def api_get_booking_slot(booking_id):
    return jsonify({})

@booking_bp.route("/api/notifications", methods=["GET"])
def api_get_notifications():
    return jsonify([])
