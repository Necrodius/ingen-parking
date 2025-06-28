from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from extensions import db
from models.reservation import Reservation
from schemas.reservation_schema import ReservationSchema
from services.reservation_service import ReservationService

reservation_bp = Blueprint("reservation_bp", __name__)
reservation_schema = ReservationSchema()
reservations_schema = ReservationSchema(many=True)

# ---------- CREATE ----------
@reservation_bp.route("/reservations/", methods=["POST"])
def create_reservation():
    try:
        data = request.get_json()
        validated_data = reservation_schema.load(data)
        reservation = ReservationService.create(**validated_data)
        return jsonify({"reservation": reservation_schema.dump(reservation)}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- READ ----------
@reservation_bp.route("/reservations/", methods=["GET"])
def list_reservations():
    try:
        reservations = ReservationService.list_all()
        return jsonify({"reservations": reservations_schema.dump(reservations)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reservation_bp.route("/reservations/<int:reservation_id>/", methods=["GET"])
def get_reservation(reservation_id):
    try:
        reservation = ReservationService.get(reservation_id)
        if not reservation:
            return jsonify({"error": "Reservation not found"}), 404
        return jsonify({"reservation": reservation_schema.dump(reservation)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- UPDATE ----------
@reservation_bp.route("/reservations/<int:reservation_id>/", methods=["PUT"])
def update_reservation(reservation_id):
    try:
        reservation = ReservationService.get(reservation_id)
        if not reservation:
            return jsonify({"error": "Reservation not found"}), 404

        data = request.get_json()
        validated_data = reservation_schema.load(data, partial=True)
        updated = ReservationService.update(reservation, **validated_data)
        return jsonify({"reservation": reservation_schema.dump(updated)}), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- DELETE ----------
@reservation_bp.route("/reservations/<int:reservation_id>/", methods=["DELETE"])
def delete_reservation(reservation_id):
    try:
        reservation = ReservationService.get(reservation_id)
        if not reservation:
            return jsonify({"error": "Reservation not found"}), 404

        ReservationService.delete(reservation)
        return jsonify({"message": "Reservation deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- CANCEL ----------
@reservation_bp.route("/reservations/<int:reservation_id>/cancel/", methods=["POST"])
def cancel_reservation(reservation_id):
    try:
        reservation = ReservationService.get(reservation_id)
        if not reservation:
            return jsonify({"error": "Reservation not found"}), 404

        cancelled = ReservationService.cancel(reservation)
        return jsonify({"reservation": reservation_schema.dump(cancelled)}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500