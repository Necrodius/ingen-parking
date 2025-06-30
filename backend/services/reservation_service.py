from typing import List, Optional
from extensions import db
from models.reservation import Reservation, ReservationStatus
from models.parking_slot import ParkingSlot
from sqlalchemy.orm import load_only
from sqlalchemy.exc import NoResultFound

class ReservationService:

    # ---------- CREATE ----------
    @staticmethod
    def create(**data) -> Reservation:
        # Validate slot exists
        slot = ParkingSlot.query.options(load_only(ParkingSlot.id, ParkingSlot.is_available)) \
            .filter_by(id=data["slot_id"]).first()

        if not slot:
            raise ValueError("Slot not found")
        if not slot.is_available:
            raise ValueError("Slot is already occupied")

        # Prevent overlapping reservation times
        overlapping = Reservation.query.filter(
            Reservation.slot_id == data["slot_id"],
            Reservation.status == ReservationStatus.booked or Reservation.status == ReservationStatus.ongoing,
            Reservation.start_ts < data["end_ts"],
            Reservation.end_ts > data["start_ts"],
        ).first()

        if overlapping:
            raise ValueError("Slot already booked for this time")

        # Save reservation
        res = Reservation(**data)
        db.session.add(res)
        db.session.commit()
        return res

    # ---------- READ ----------
    @staticmethod
    def list_all() -> List[Reservation]:
        return Reservation.query.order_by(Reservation.start_ts.desc()).all()

    @staticmethod
    def get(reservation_id: int) -> Reservation:
        res = Reservation.query.get(reservation_id)
        if not res:
            raise NoResultFound("Reservation not found")
        return res

    @staticmethod
    def list_by_user(user_id: int) -> List[Reservation]:
        return Reservation.query.filter_by(user_id=user_id).order_by(Reservation.start_ts.desc()).all()

    @staticmethod
    def list_by_status(status: ReservationStatus) -> List[Reservation]:
        return Reservation.query.filter_by(status=status).all()

    # ---------- UPDATE ----------
    @staticmethod
    def update(res: Reservation, **changes) -> Reservation:
        new_start = changes.get("start_ts", res.start_ts)
        new_end   = changes.get("end_ts", res.end_ts)
        new_slot  = changes.get("slot_id", res.slot_id)

        if new_start >= new_end:
            raise ValueError("start_ts must be before end_ts")

        overlap = (
            Reservation.query
            .filter(
                Reservation.id != res.id,
                Reservation.slot_id == new_slot,
                Reservation.status == ReservationStatus.booked,
                Reservation.start_ts < new_end,
                Reservation.end_ts   > new_start,
            )
            .first()
        )
        if overlap:
            raise ValueError("slot already booked for this time")

        for k, v in changes.items():
            setattr(res, k, v)
        db.session.commit()
        return res

    # ---------- DELETE ----------
    @staticmethod
    def delete(res: Reservation) -> None:
        db.session.delete(res)
        db.session.commit()

    # ---------- CANCEL ----------
    @staticmethod
    def cancel(res: Reservation) -> Reservation:
        if res.status != ReservationStatus.booked:
            raise ValueError("Only booked reservations can be cancelled")

        res.status = ReservationStatus.cancelled
        db.session.commit()
        return res
