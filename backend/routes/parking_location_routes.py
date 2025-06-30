from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy.exc import NoResultFound
from models.user import UserRole
from services.parking_location_service import ParkingLocationService
from schemas.parking_location_schema import (
    parking_location_schema,
    parking_locations_schema,
)
from utils.security import role_required

parking_location_bp = Blueprint("parking_location_bp", __name__)

# ---------- CREATE ----------
@parking_location_bp.post("/locations")
@jwt_required()
@role_required(UserRole.admin)
def create_location():
    try:
        data = parking_location_schema.load(request.get_json())
        loc = ParkingLocationService.create_location(**data)
        return jsonify({"location": parking_location_schema.dump(loc)}), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except ValueError as dup:
        return jsonify({"error": str(dup)}), 409

# ---------- READ ----------
@parking_location_bp.get("/locations")
def list_locations():
    locations = ParkingLocationService.list_locations()
    enriched = [
        {
            **parking_location_schema.dump(loc),
            "available_slots": ParkingLocationService.count_available_slots(loc),
        }
        for loc in locations
    ]
    return jsonify({"locations": enriched}), 200

@parking_location_bp.get("/locations/<int:loc_id>")
def get_location(loc_id: int):
    try:
        loc = ParkingLocationService.get_or_404(loc_id)
        payload = {
            **parking_location_schema.dump(loc),
            "available_slots": ParkingLocationService.count_available_slots(loc),
        }
        return jsonify({"location": payload}), 200
    except NoResultFound:
        return jsonify({"error": "Location not found"}), 404


# ---------- UPDATE ----------
@parking_location_bp.put("/locations/<int:loc_id>")
@jwt_required()
@role_required(UserRole.admin)
def update_location(loc_id: int):
    try:
        loc = ParkingLocationService.get_or_404(loc_id)
        patch = parking_location_schema.load(request.get_json(), partial=True)
        loc = ParkingLocationService.update_location(loc, **patch)
        return jsonify({"location": parking_location_schema.dump(loc)}), 200

    except NoResultFound:
        return jsonify({"error": "Location not found"}), 404
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400


# ---------- DELETE ----------
@parking_location_bp.delete("/locations/<int:loc_id>")
@jwt_required()
@role_required(UserRole.admin)
def delete_location(loc_id: int):
    try:
        loc = ParkingLocationService.get_or_404(loc_id)
        ParkingLocationService.delete_location(loc)
        return jsonify({}), 204
    except NoResultFound:
        return jsonify({"error": "Location not found"}), 404
