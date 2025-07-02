# This file defines the ReservationService class, which provides methods for managing reservations.
# It includes methods for creating, reading, updating, and deleting reservations.

from datetime import datetime, timezone
from typing import List
from extensions import db
from models.reservation import Reservation, ReservationStatus
from models.parking_slot import ParkingSlot
from sqlalchemy.orm import load_only
from sqlalchemy.exc import NoResultFound

class ReservationService:

    # ---------- HELPER ----------

    # Update slot status when called (same functionality with .utls.status_scheduler.py)
    @staticmethod
    def refresh_slot_statuses(slot_id: int) -> None:
        now = datetime.now(timezone.utc)

        booked   = (
            Reservation.query
            .filter(
                Reservation.slot_id == slot_id,
                Reservation.status == ReservationStatus.booked,
                Reservation.start_ts <= now,
            )
            .all()
        )
        finished = (
            Reservation.query
            .filter(
                Reservation.slot_id == slot_id,
                Reservation.status == ReservationStatus.ongoing,
                Reservation.end_ts <= now,
            )
            .all()
        )

        for r in booked:
            r.status = ReservationStatus.ongoing
        for r in finished:
            r.status = ReservationStatus.finished

        if booked or finished:
            db.session.commit()

    # ---------- CREATE ----------
    @staticmethod
    def create(**data) -> Reservation:
        # Slot must exist and be free
        slot = (
            ParkingSlot.query
            .options(load_only(ParkingSlot.id))
            .filter_by(id=data["slot_id"])
            .first()
        )
        if not slot:
            raise ValueError("Slot not found")

        # Make sure previous reservations are up‑to‑date
        ReservationService.refresh_slot_statuses(data["slot_id"])

        # No overlap with existing booked / ongoing
        overlap = (
            Reservation.query
            .filter(
                Reservation.slot_id == data["slot_id"],
                Reservation.status.in_(
                    [ReservationStatus.booked, ReservationStatus.ongoing]
                ),
                Reservation.start_ts < data["end_ts"],
                Reservation.end_ts   > data["start_ts"],
            )
            .first()
        )
        if overlap:
            raise ValueError("Slot already booked for this time")

        # Write to DB
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
        return (
            Reservation.query
            .filter_by(user_id=user_id)
            .order_by(Reservation.start_ts.desc())
            .all()
        )

    @staticmethod
    def list_by_status(status: ReservationStatus) -> List[Reservation]:
        return Reservation.query.filter_by(status=status).all()

    # ---------- UPDATE ----------
    @staticmethod
    def update(res: Reservation, **changes) -> Reservation:
        new_start = changes.get("start_ts", res.start_ts)
        new_end   = changes.get("end_ts",   res.end_ts)
        new_slot  = changes.get("slot_id",  res.slot_id)

        if new_start >= new_end:
            raise ValueError("Start time must be before end time")

        # Make sure reservations are in the right state
        ReservationService.refresh_slot_statuses(new_slot)

        overlap = (
            Reservation.query
            .filter(
                Reservation.id != res.id,
                Reservation.slot_id == new_slot,
                Reservation.status.in_(
                    [ReservationStatus.booked, ReservationStatus.ongoing]
                ),
                Reservation.start_ts < new_end,
                Reservation.end_ts   > new_start,
            )
            .first()
        )
        if overlap:
            raise ValueError("Slot already booked for this time")

        # Apply changes
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

    # ---------- FINISH ----------
    # Update ongoing reservation to finished and stamp the actual end time.
    @staticmethod
    def finish(res: Reservation) -> Reservation:

        ReservationService.refresh_slot_statuses(res.slot_id)

        if res.status != ReservationStatus.ongoing:
            raise ValueError("Only ongoing reservations can be finished")

        res.status = ReservationStatus.finished
        res.end_ts = datetime.now(timezone.utc)
        db.session.commit()
        return res
