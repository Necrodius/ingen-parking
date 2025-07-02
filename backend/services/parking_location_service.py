# This file defines the ParkingLocationService class, which provides methods for managing parking locations in a parking system.
# It includes methods for creating, reading, updating, and deleting parking locations, 
# as well as counting available parking slots within a location.

from __future__ import annotations
from typing import List, Optional
from sqlalchemy.exc import IntegrityError, NoResultFound
from extensions import db
from models.parking_location import ParkingLocation
from models.parking_slot import ParkingSlot

class ParkingLocationService:
    # ---------- CREATE ----------
    @staticmethod
    def create_location(**attrs) -> ParkingLocation:
        existing = (
            ParkingLocation.query.filter_by(
                name=attrs.get("name"),
                address=attrs.get("address"),
                lat=attrs.get("lat"),
                lng =attrs.get("lng")
            )
            .first()
        )

        if existing:
            raise ValueError("location already exists")

        loc = ParkingLocation(**attrs)
        db.session.add(loc)
        try:
            db.session.commit()
            return loc
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("location already exists") from exc

    # ---------- READ ----------
    @staticmethod
    def list_locations() -> List[ParkingLocation]:
        return ParkingLocation.query.order_by(ParkingLocation.id).all()

    @staticmethod
    def get_location(location_id: int) -> Optional[ParkingLocation]:
        return ParkingLocation.query.get(location_id)

    @staticmethod
    def get_or_404(location_id: int) -> ParkingLocation:
        loc = ParkingLocationService.get_location(location_id)
        if not loc:
            raise NoResultFound(f"location {location_id} not found")
        return loc

    # ---------- UPDATE ----------
    @staticmethod
    def update_location(loc: ParkingLocation, **patch) -> ParkingLocation:
        for field, value in patch.items():
            setattr(loc, field, value)
        db.session.commit()
        return loc

    # ---------- DELETE ----------
    @staticmethod
    def delete_location(loc: ParkingLocation) -> None:

        # TO DO: guard if active reservations exist.

        db.session.delete(loc)
        db.session.commit()

    # ---------- UTILITY ----------
    @staticmethod
    def count_available_slots(loc: ParkingLocation) -> int:
        return (
            ParkingSlot.query.filter_by(location_id=loc.id)
            .count()
        )