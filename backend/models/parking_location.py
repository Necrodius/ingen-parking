# It defines the Parking Location model for the application.

from app import db
from .mixins import TimestampMixin

class ParkingLocation(db.Model, TimestampMixin):
    __tablename__ = "parking_locations"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    address = db.Column(db.String(200), nullable=False)

    lat = db.Column(db.Float, nullable=False)

    lng = db.Column(db.Float, nullable=False)

    slots = db.relationship(
        "ParkingSlot", back_populates="location", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ParkingLocation {self.name} ({self.address})>"
