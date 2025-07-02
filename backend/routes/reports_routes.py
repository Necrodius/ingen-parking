

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.user import UserRole
from services.analytics_service import AnalyticsService
from utils.security import role_required

reports_bp = Blueprint("reports_bp", __name__)

# Reservations created per day (last N days, default = 7)
@reports_bp.get("/reservations-per-day")
@jwt_required()
@role_required(UserRole.admin)
def reservations_per_day():
    try:
        days = int(request.args.get("days", 7))
        if days < 1 or days > 90:
            return jsonify({"error": "days must be between 1 and 90"}), 400

        data = AnalyticsService.reservations_per_day(days=days)
        return jsonify({"data": data}), 200
    except ValueError:
        return jsonify({"error": "days must be an integer"}), 400


# LIVE slot availability summary (total vs. free right now)
@reports_bp.get("/slot-summary")
@jwt_required()
@role_required(UserRole.admin)
def slot_summary():
    data = AnalyticsService.slots_available_per_location()
    return jsonify({"data": data}), 200

# Users who currently have active reservations
@reports_bp.get("/active-users")
@jwt_required()
@role_required(UserRole.admin)
def active_users():
    data = AnalyticsService.users_with_active_reservations()
    return jsonify({"data": data}), 200
