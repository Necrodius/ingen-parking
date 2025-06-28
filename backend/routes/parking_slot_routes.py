from flask import Blueprint, request, jsonify
from extensions import db
from models.parking_slot import ParkingSlot
from schemas.parking_slot_schema import ParkingSlotSchema
from marshmallow import ValidationError

parking_slot_bp = Blueprint("parking_slot_bp", __name__)
slot_schema = ParkingSlotSchema()
slots_schema = ParkingSlotSchema(many=True)

@parking_slot_bp.route("/slots/", methods=["GET"])
def list_slots():
    try:
        slots = ParkingSlot.query.all()
        return jsonify({"slots": slots_schema.dump(slots)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@parking_slot_bp.route("/slots/", methods=["POST"])
def create_slot():
    try:
        data = request.get_json()
        slot = slot_schema.load(data)
        db.session.add(slot)
        db.session.commit()
        return jsonify({"slot": slot_schema.dump(slot)}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
