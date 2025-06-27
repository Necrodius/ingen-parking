# It defines the Parking Location model for the application.

from app import db
from .mixins import TimestampMixin
from enum import Enum

class ReservationStatus(str, Enum):
    BOOKED = "booked"
    ONGOING = "ongoing"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class Reservation(db.Model, TimestampMixin):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )

    slot_id = db.Column(
        db.Integer, db.ForeignKey("parking_slots.id"), nullable=False, index=True
    )

    start_ts = db.Column(db.DateTime, nullable=False)

    end_ts = db.Column(db.DateTime, nullable=False)

    status = db.Column(
        db.Enum(ReservationStatus),
        nullable=False,
        default=ReservationStatus.BOOKED,
    )

    user = db.relationship("User", back_populates="reservations")

    slot = db.relationship("ParkingSlot", back_populates="reservations")

    def __repr__(self) -> str:
        return (
            f"<Reservation {self.id} | {self.user.email} -> "
            f"{self.slot.slot_label} [{self.status}]>"
        )