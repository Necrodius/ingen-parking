from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.parking_slot import ParkingSlot

class ParkingSlotSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ParkingSlot
        load_instance = True
        include_fk = True
        ordered = True

slot_schema   = ParkingSlotSchema()
slots_schema  = ParkingSlotSchema(many=True)
