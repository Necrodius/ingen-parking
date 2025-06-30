from datetime import datetime, timezone
from typing import List
from extensions import db
from models.reservation import Reservation, ReservationStatus
from models.parking_slot import ParkingSlot
from sqlalchemy.orm import load_only
from sqlalchemy.exc import NoResultFound


class ReservationService:

    # ---------- HELPER: Update status of related reservations ----------
    @staticmethod
    def refresh_slot_statuses(slot_id: int) -> None:
        """Update all reservations for this slot: booked → ongoing, ongoing/booked → completed."""
        now = datetime.now(timezone.utc)

        # booked → ongoing
        booked = Reservation.query.filter(
            Reservation.slot_id == slot_id,
            Reservation.status == ReservationStatus.booked,
            Reservation.start_ts <= now,
            Reservation.end_ts > now,
        ).all()

        # booked/ongoing → completed
        finished = Reservation.query.filter(
            Reservation.slot_id == slot_id,
            Reservation.status.in_([ReservationStatus.booked, ReservationStatus.ongoing]),
            Reservation.end_ts <= now,
        ).all()

        for r in booked:
            r.status = ReservationStatus.ongoing
        for r in finished:
            r.status = ReservationStatus.completed

        if booked or finished:
            db.session.commit()

    # ---------- CREATE ----------
    @staticmethod
    def create(**data) -> Reservation:
        # Validate slot exists
        slot = ParkingSlot.query.options(load_only(ParkingSlot.id, ParkingSlot.is_available)) \
            .filter_by(id=data["slot_id"]).first()

        if not slot:
            raise ValueError("Slot not found")
        if not slot.is_available:
            raise ValueError("Slot is already marked occupied")

        # ⬇️ Make sure statuses are up to date before overlap check
        ReservationService.refresh_slot_statuses(data["slot_id"])

        # Prevent overlapping reservation times
        overlapping = Reservation.query.filter(
            Reservation.slot_id == data["slot_id"],
            Reservation.status.in_([ReservationStatus.booked, ReservationStatus.ongoing]),
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
        new_end = changes.get("end_ts", res.end_ts)
        new_slot = changes.get("slot_id", res.slot_id)

        if new_start >= new_end:
            raise ValueError("start_ts must be before end_ts")

        # Refresh statuses before overlap check
        ReservationService.refresh_slot_statuses(new_slot)

        overlap = (
            Reservation.query
            .filter(
                Reservation.id != res.id,
                Reservation.slot_id == new_slot,
                Reservation.status.in_([ReservationStatus.booked, ReservationStatus.ongoing]),
                Reservation.start_ts < new_end,
                Reservation.end_ts > new_start,
            )
            .first()
        )
        if overlap:
            raise ValueError("Slot already booked for this time")

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