from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from services.parking_slot_service import ParkingSlotService
from schemas.parking_slot_schema import (
    parking_slot_schema,
    parking_slots_schema,
)

parking_slot_bp = Blueprint("parking_slot_bp", __name__)

# ---------- CREATE ----------
@parking_slot_bp.post("/slots/")
def create_slot():
    try:
        data = parking_slot_schema.load(request.get_json())
        slot = ParkingSlotService.create_slot(**data)
        return jsonify({"slot": parking_slot_schema.dump(slot)}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

# ---------- READ ----------
@parking_slot_bp.get("/slots/<int:slot_id>")
def get_slot(slot_id):
    slot = ParkingSlotService.get_slot(slot_id)
    if not slot:
        return jsonify({"error": "Slot not found"}), 404
    return jsonify({"slot": parking_slot_schema.dump(slot)}), 200

@parking_slot_bp.get("/slots/")
def list_slots():
    slots = ParkingSlotService.list_slots()
    return jsonify({"slots": parking_slots_schema.dump(slots)}), 200

# ---------- UPDATE ----------
@parking_slot_bp.put("/slots/<int:slot_id>")
def update_slot(slot_id):
    slot = ParkingSlotService.get_slot(slot_id)
    if not slot:
        return jsonify({"error": "Slot not found"}), 404
    try:
        data = parking_slot_schema.load(request.get_json(), partial=True)
        slot = ParkingSlotService.update_slot(slot, **data)
        return jsonify({"slot": parking_slot_schema.dump(slot)}), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

# ---------- DELETE ----------
@parking_slot_bp.delete("/slots/<int:slot_id>")
def delete_slot(slot_id):
    slot = ParkingSlotService.get_slot(slot_id)
    if not slot:
        return jsonify({"error": "Slot not found"}), 404
    ParkingSlotService.delete_slot(slot)
    return jsonify({}), 204