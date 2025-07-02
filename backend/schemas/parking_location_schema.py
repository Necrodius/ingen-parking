# This file defines the schema for parking locations using Marshmallow and SQLAlchemy.
# It includes fields for both read-only and write operations, ensuring that sensitive information like timestamps is handled appropriately.
# It also uses SQLAlchemyAutoSchema to automatically generate fields based on the ParkingLocation model.

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.parking_location import ParkingLocation

class ParkingLocationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ParkingLocation
        load_instance = False
        include_fk = True
        ordered = True

    # ---------- READ-ONLY ----------
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # ---------- WRITE ----------
    name = fields.Str(required=True)
    address = fields.Str(required=True)

    # Automatically added in read responses
    available_slots = fields.Int(dump_only=True)

parking_location_schema = ParkingLocationSchema()
parking_locations_schema = ParkingLocationSchema(many=True)
