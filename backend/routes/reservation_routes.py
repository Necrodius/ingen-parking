from flask import Blueprint, request, jsonify
from extensions import db
from models.reservation import Reservation
from schemas.reservation_schema import ReservationSchema
from marshmallow import ValidationError

reservation_bp = Blueprint("reservation_bp", __name__)
reservation_schema = ReservationSchema()
reservations_schema = ReservationSchema(many=True)

@reservation_bp.route("/reservations/", methods=["GET"])
def get_reservations():
    try:
        reservations = Reservation.query.all()
        return jsonify({"reservations": reservations_schema.dump(reservations)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reservation_bp.route("/reservations/", methods=["POST"])
def create_reservation():
    try:
        data = request.get_json()
        reservation = reservation_schema.load(data)
        db.session.add(reservation)
        db.session.commit()
        return jsonify({"reservation": reservation_schema.dump(reservation)}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
