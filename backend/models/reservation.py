# This file defines the Parking Location model for the application.

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as PgEnum, text
from sqlalchemy.orm import relationship
from extensions import db
from .mixins import TimestampMixin
from enum import Enum

class ReservationStatus(str, Enum):
    booked    = "booked"
    ongoing   = "ongoing"
    finished  = "finished"
    cancelled = "cancelled"

class Reservation(db.Model, TimestampMixin):
    __tablename__ = "reservations"

    id        = Column(Integer, primary_key=True)
    user_id   = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    slot_id   = Column(Integer, ForeignKey("parking_slots.id"), nullable=False, index=True)
    start_ts  = Column(DateTime, nullable=False)
    end_ts    = Column(DateTime, nullable=False)
    status    = Column(PgEnum(ReservationStatus, name="reservation_status"), nullable=False, server_default=text("'booked'"))

    user      = relationship("User", back_populates="reservations")
    slot      = relationship("ParkingSlot", back_populates="reservations")

    def __repr__(self):
        return f"<Reservation {self.id} [{self.status}]>"
