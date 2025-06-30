from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy.exc import NoResultFound
from services.parking_slot_service import ParkingSlotService
from schemas.parking_slot_schema import parking_slot_schema, parking_slots_schema
from utils.security import role_required
from models.user import UserRole

parking_slot_bp = Blueprint("parking_slot_bp", __name__)

# ---------- CREATE ----------
@parking_slot_bp.post("/slots")
@jwt_required()
@role_required(UserRole.admin)
def create_slot():
    try:
        data = parking_slot_schema.load(request.get_json())
        slot = ParkingSlotService.create_slot(**data)
        return jsonify({"slot": parking_slot_schema.dump(slot)}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

# ---------- READ ----------
@parking_slot_bp.get("/slots")
def list_slots():
    location_id = request.args.get("location_id", type=int)

    if location_id:
        slots = ParkingSlotService.get_by_location(location_id)
    else:
        slots = ParkingSlotService.list_slots()

    return jsonify({"slots": parking_slots_schema.dump(slots)}), 200

@parking_slot_bp.get("/slots/<int:slot_id>")
def get_slot(slot_id):
    try:
        slot = ParkingSlotService.get_or_404(slot_id)
        return jsonify({"slot": parking_slot_schema.dump(slot)}), 200
    except NoResultFound:
        return jsonify({"error": "Slot not found"}), 404

# ---------- UPDATE ----------
@parking_slot_bp.put("/slots/<int:slot_id>")
@jwt_required()
@role_required(UserRole.admin)
def update_slot(slot_id):
    try:
        slot = ParkingSlotService.get_or_404(slot_id)
        data = parking_slot_schema.load(request.get_json(), partial=True)
        slot = ParkingSlotService.update_slot(slot, **data)
        return jsonify({"slot": parking_slot_schema.dump(slot)}), 200
    except NoResultFound:
        return jsonify({"error": "Slot not found"}), 404
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

# ---------- DELETE ----------
@parking_slot_bp.delete("/slots/<int:slot_id>")
@jwt_required()
@role_required(UserRole.admin)
def delete_slot(slot_id):
    try:
        slot = ParkingSlotService.get_or_404(slot_id)
        ParkingSlotService.delete_slot(slot)
        return jsonify({}), 204
    except NoResultFound:
        return jsonify({"error": "Slot not found"}), 404
