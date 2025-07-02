# This file defines the ParkingSlotService class, which provides methods for managing parking slots in a parking system.
# It includes methods for creating, reading, updating, and deleting parking slots.

from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from sqlalchemy import exists, and_
from sqlalchemy.exc import NoResultFound
from extensions import db
from models.parking_slot import ParkingSlot
from models.reservation import Reservation
from models.reservation import Reservation, ReservationStatus

class ParkingSlotService:
    # ---------- CREATE ----------
    @staticmethod
    def create_slot(**slot_dict) -> ParkingSlot:
        slot = ParkingSlot(**slot_dict)
        db.session.add(slot)
        db.session.commit()
        return slot

    # ---------- READ ----------
    @staticmethod
    def list_slots() -> List[ParkingSlot]:
        return ParkingSlot.query.order_by(ParkingSlot.id).all()

    @staticmethod
    def get_slot(slot_id: int) -> Optional[ParkingSlot]:
        return ParkingSlot.query.get(slot_id)

    @staticmethod
    def get_or_404(slot_id: int) -> ParkingSlot:
        slot = ParkingSlot.query.get(slot_id)
        if not slot:
            raise NoResultFound("Parking slot not found")
        return slot

    @staticmethod
    def get_by_location(location_id: int) -> List[ParkingSlot]:
        return (
            ParkingSlot.query
            .filter_by(location_id=location_id)
            .order_by(ParkingSlot.id)
            .all()
        )

    @staticmethod
    def get_available_slots(
        location_id: int,
        start_ts: datetime,
        end_ts: datetime,
    ) -> List[ParkingSlot]:

        # conflicting reservations (booked OR ongoing only)
        conflicting_q = (
            db.session.query(Reservation.slot_id)
            .filter(
                Reservation.location_id == location_id,
                Reservation.status.in_(
                    [ReservationStatus.booked, ReservationStatus.ongoing]
                ),
                Reservation.start_ts < end_ts,
                Reservation.end_ts   > start_ts,
            )
        ).subquery()

        # every slot not conflicting
        return (
            db.session
            .query(ParkingSlot)
            .filter(
                ParkingSlot.location_id == location_id,
                ~exists(conflicting_q.where(conflicting_q.c.slot_id == ParkingSlot.id)),
            )
            .order_by(ParkingSlot.id)
            .all()
        )

    # ---------- UPDATE ----------
    @staticmethod
    def update_slot(slot: ParkingSlot, **changes) -> ParkingSlot:
        for field, value in changes.items():
            setattr(slot, field, value)
        db.session.commit()
        return slot

    # ---------- DELETE ----------
    @staticmethod
    def delete_slot(slot: ParkingSlot) -> None:
        db.session.delete(slot)
        db.session.commit()
