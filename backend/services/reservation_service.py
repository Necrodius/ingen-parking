from typing import List, Optional
from datetime import datetime
from extensions import db
from models.reservation import Reservation, ReservationStatus

class ReservationService:

    # ---------- CREATE ----------
    @staticmethod
    def create(**data) -> Reservation:
        # Optional: Check for overlapping reservations here
        new_res = Reservation(**data)
        db.session.add(new_res)
        db.session.commit()
        return new_res

    # ---------- READ ----------
    @staticmethod
    def list_all() -> List[Reservation]:
        return Reservation.query.all()

    @staticmethod
    def get(reservation_id: int) -> Optional[Reservation]:
        return Reservation.query.get(reservation_id)

    @staticmethod
    def list_by_user(user_id: int) -> List[Reservation]:
        return Reservation.query.filter_by(user_id=user_id).all()

    # ---------- UPDATE ----------
    @staticmethod
    def update(reservation: Reservation, **changes) -> Reservation:
        for field, value in changes.items():
            setattr(reservation, field, value)
        db.session.commit()
        return reservation
    
    # ---------- DELETE ----------
    @staticmethod
    def delete(reservation: Reservation) -> None:
        db.session.delete(reservation)
        db.session.commit()

    # ---------- CANCEL ----------
    @staticmethod
    def cancel(reservation: Reservation) -> Reservation:
        if reservation.status != ReservationStatus.booked:
            raise ValueError("Only 'booked' reservations can be cancelled")
        reservation.status = ReservationStatus.cancelled
        db.session.commit()
        return reservation

