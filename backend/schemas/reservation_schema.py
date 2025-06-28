from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.reservation import Reservation

class ReservationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Reservation
        load_instance = True
        include_fk = True
        ordered = True

reservation_schema   = ReservationSchema()
reservations_schema  = ReservationSchema(many=True)
