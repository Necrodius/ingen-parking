# This file defines the schema for the ParkingSlot model using Marshmallow and SQLAlchemy.
# It includes fields for both read-only and write operations, ensuring that sensitive information like timestamps is handled appropriately.
# It also uses SQLAlchemyAutoSchema to automatically generate fields based on the ParkingSlot model.

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.parking_slot import ParkingSlot

class ParkingSlotSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ParkingSlot
        load_instance = False
        include_fk = True
        ordered = True

    # ---------- READ ----------
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # ---------- WRITE ----------
    slot_number = fields.Str(required=True)
    is_available = fields.Bool(required=False)

    # ---------- FOREIGN KEY ----------
    location_id = fields.Int(required=True)

parking_slot_schema = ParkingSlotSchema()
parking_slots_schema = ParkingSlotSchema(many=True)
