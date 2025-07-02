# This file defines the schema for reservation data using Marshmallow.
# It specifies how reservation data should be serialized and deserialized,
# including validation rules for the fields.

from marshmallow import fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.reservation import Reservation, ReservationStatus

class ReservationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Reservation
        load_instance = False
        include_fk = True
        ordered = True

    # ---------- READ‑ONLY FIELDS ----------
    id         = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    status = fields.String(
        dump_only=True,
        validate=validate.OneOf([s.value for s in ReservationStatus])
    )

    # ---------- INPUT FIELDS ----------
    start_ts = fields.DateTime(required=True)      # ISO 8601 string
    end_ts   = fields.DateTime(required=True)      # ISO 8601 string
    slot_id  = fields.Integer(required=True)
    user_id  = fields.Integer(dump_only=True)      # set server‑side

# Single + many helpers (same pattern as other schemas)
reservation_schema  = ReservationSchema()
reservations_schema = ReservationSchema(many=True)
