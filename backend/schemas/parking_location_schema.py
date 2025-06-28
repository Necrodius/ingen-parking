from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.parking_location import ParkingLocation

class ParkingLocationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ParkingLocation
        load_instance = True
        include_fk = True
        ordered = True

parking_location_schema   = ParkingLocationSchema()
parking_locations_schema  = ParkingLocationSchema(many=True)
