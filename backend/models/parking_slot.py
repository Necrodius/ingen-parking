# This file defines the Parking Location model for the application.

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, text
from sqlalchemy.orm import relationship
from extensions import db
from .mixins import TimestampMixin

class ParkingSlot(db.Model, TimestampMixin):
    __tablename__ = "parking_slots"

    id              = Column(Integer, primary_key=True)
    slot_label      = Column(String(20), server_default="Slot")
    location_id     = Column(Integer, ForeignKey("parking_locations.id"), nullable=False)
    location        = relationship("ParkingLocation", back_populates="slots")
    reservations    = relationship("Reservation", back_populates="slot", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Slot {self.slot_label} @ location {self.location_id}>"
