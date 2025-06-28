from typing import List, Optional
from extensions import db
from models.parking_location import ParkingLocation
from models.parking_slot import ParkingSlot

class ParkingLocationService:
    
    # ---------- Create ----------
    @staticmethod
    def create_location(**loc_dict) -> ParkingLocation:
        loc = ParkingLocation(**loc_dict)
        db.session.add(loc)
        db.session.commit()
        return loc
    
    # ---------- Read ----------
    @staticmethod
    def list_locations() -> List[ParkingLocation]:
        return ParkingLocation.query.all()

    @staticmethod
    def get_location(location_id: int) -> Optional[ParkingLocation]:
        return ParkingLocation.query.get(location_id)

    # ---------- Update ----------
    @staticmethod
    def update_location(loc: ParkingLocation, **changes) -> ParkingLocation:
        for field, value in changes.items():
            setattr(loc, field, value)
        db.session.commit()
        return loc

    # ---------- Delete ----------
    @staticmethod
    def delete_location(loc: ParkingLocation) -> None:
        db.session.delete(loc)
        db.session.commit()

    # ---------- Utility ----------
    @staticmethod
    def count_available_slots(loc: ParkingLocation) -> int:
        return (
            ParkingSlot.query.filter_by(location_id=loc.id, is_available=True)
            .count()
        )