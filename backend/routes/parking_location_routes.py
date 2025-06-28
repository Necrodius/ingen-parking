from flask import Blueprint, request, jsonify
from extensions import db
from models.parking_location import ParkingLocation
from schemas.parking_location_schema import ParkingLocationSchema
from marshmallow import ValidationError

parking_location_bp = Blueprint("parking_location_bp", __name__)
location_schema = ParkingLocationSchema()
locations_schema = ParkingLocationSchema(many=True)

@parking_location_bp.route("/locations/", methods=["GET"])
def list_locations():
    try:
        locations = ParkingLocation.query.all()
        return jsonify({"locations": locations_schema.dump(locations)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@parking_location_bp.route("/locations/", methods=["POST"])
def create_location():
    try:
        data = request.get_json()
        loc = location_schema.load(data)
        db.session.add(loc)
        db.session.commit()
        return jsonify({"location": location_schema.dump(loc)}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
