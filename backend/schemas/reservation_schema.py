# This file defines the ReservationSchema for serializing and deserializing Reservation objects using Marshmallow.
# It includes fields for both read-only and write operations, ensuring that sensitive information like timestamps is handled appropriately.
# It also uses SQLAlchemyAutoSchema to automatically generate fields based on the Reservation model.

from marshmallow import fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.reservation import Reservation, ReservationStatus

class ReservationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Reservation
        load_instance = True
        include_fk = True
        ordered = True

    # Explicit field overrides
    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # ---------- READ-ONLY ----------
    status = fields.String(
        dump_only=True,
        validate=validate.OneOf([s.value for s in ReservationStatus])
    )

    # Expect ISO date strings for datetime fields
    start_time = fields.DateTime(required=True)
    end_time   = fields.DateTime(required=True)

    # ---------- FOREIGN KEYS ----------
    user_id = fields.Integer(required=True)
    slot_id = fields.Integer(required=True)

reservation_schema = ReservationSchema()
reservations_schema = ReservationSchema(many=True)
