from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.parking_location import ParkingLocation

class ParkingLocationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ParkingLocation
        load_instance = True
        include_fk = True
        ordered = True

location_schema   = ParkingLocationSchema()
locations_schema  = ParkingLocationSchema(many=True)
