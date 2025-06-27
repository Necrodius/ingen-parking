# This file defines the Parking Location model for the application.

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from enum import Enum
from app import db
from .mixins import TimestampMixin

class ParkingLocation(db.Model, TimestampMixin):
    __tablename__ = "parking_locations"

    id = Column(Integer, primary_key=True)

    name = Column(String(120), nullable=True, server_default="Parking Location")

    address = Column(String(255), nullable=True, server_default="Unknown Address")

    lat = Column(Float, nullable=False)

    lng = Column(Float, nullable=False)

    slots = relationship("ParkingSlot", back_populates="location", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ParkingLocation {self.name} ({self.address})>"
