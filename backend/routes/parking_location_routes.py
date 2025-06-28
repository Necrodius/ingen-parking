from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from services.parking_location_service import ParkingLocationService
from schemas.parking_location_schema import (
    parking_location_schema,
    parking_locations_schema,
)

parking_location_bp = Blueprint("parking_location_bp", __name__)

# ---------- CREATE ----------
@parking_location_bp.post("/locations/")
def create_location():
    try:
        data = parking_location_schema.load(request.get_json())
        loc = ParkingLocationService.create_location(**data)
        return jsonify({"location": parking_location_schema.dump(loc)}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

# ---------- READ ----------
@parking_location_bp.get("/locations/<int:loc_id>")
def get_location(loc_id: int):
    loc = ParkingLocationService.get_location(loc_id)
    if not loc:
        return jsonify({"error": "Location not found"}), 404
    data = parking_location_schema.dump(loc)
    data["available_slots"] = ParkingLocationService.count_available_slots(loc)
    return jsonify({"location": data}), 200

@parking_location_bp.get("/locations/")
def list_locations():
    locs = ParkingLocationService.list_locations()
    # example extra‑field: available slot count
    payload = [
        {
            **parking_location_schema.dump(l),
            "available_slots": ParkingLocationService.count_available_slots(l),
        }
        for l in locs
    ]
    return jsonify({"locations": payload}), 200

# ---------- UPDATE ----------
@parking_location_bp.put("/locations/<int:loc_id>")
def update_location(loc_id: int):
    loc = ParkingLocationService.get_location(loc_id)
    if not loc:
        return jsonify({"error": "Location not found"}), 404
    try:
        data = parking_location_schema.load(request.get_json(), partial=True)
        loc = ParkingLocationService.update_location(loc, **data)
        return jsonify({"location": parking_location_schema.dump(loc)}), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

# ---------- DELETE ----------
@parking_location_bp.delete("/locations/<int:loc_id>")
def delete_location(loc_id: int):
    loc = ParkingLocationService.get_location(loc_id)
    if not loc:
        return jsonify({"error": "Location not found"}), 404
    ParkingLocationService.delete_location(loc)
    return jsonify({}), 204