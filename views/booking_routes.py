from flask import Blueprint, render_template, jsonify
from models import db, Booking

booking_bp = Blueprint('booking', __name__)

@booking_bp.route("/booking", methods=["GET"])
def BookingPage():
    return render_template("user/booking.html", title="Booking")

@booking_bp.route("/api/bookings", methods=["POST"])
def api_create_booking():
    return jsonify({"status": "success"})

@booking_bp.route("/mytickets", methods=["GET"])
def MyTickets():
    return render_template("user/mytickets.html", title="My Tickets")

@booking_bp.route("/history", methods=["GET"])
def History():
    return render_template("user/history.html", title="History")

@booking_bp.route("/api/booking/<int:booking_id>", methods=["GET"])
def api_get_booking_details(booking_id):
    return jsonify({})
