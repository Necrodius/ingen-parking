# This file defines the Parking Location model for the application.

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as PgEnum
from sqlalchemy.orm import relationship
from enum import Enum
from app import db
from .mixins import TimestampMixin

class ReservationStatus(str, Enum):
    BOOKED = "booked"
    ONGOING = "ongoing"
    FINISHED = "finished"
    CANCELLED = "cancelled"

class Reservation(db.Model, TimestampMixin):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    slot_id = Column(Integer, ForeignKey("parking_slots.id"), nullable=False, index=True)

    start_ts = Column(DateTime, nullable=False)

    end_ts = Column(DateTime, nullable=False)

    status = Column(PgEnum(ReservationStatus), nullable=False, default=ReservationStatus.BOOKED)

    user = relationship("User", back_populates="reservations")

    slot = relationship("ParkingSlot", back_populates="reservations")

    def __repr__(self) -> str:
        return (
            f"<Reservation {self.id} | {self.user.email} -> "
            f"{self.slot.slot_label} [{self.status}]>"
        )