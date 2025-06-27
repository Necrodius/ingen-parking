# It defines the Parking Location model for the application.

from app import db
from .mixins import TimestampMixin

class ParkingSlot(db.Model, TimestampMixin):
    __tablename__ = "parking_slots"

    id = db.Column(db.Integer, primary_key=True)

    slot_label = db.Column(db.String(20), nullable=False)

    is_active = db.Column(db.Boolean, nullable=False, default=True)

    location_id = db.Column(
        db.Integer, db.ForeignKey("parking_locations.id"), nullable=False
    )

    location = db.relationship("ParkingLocation", back_populates="slots")

    reservations = db.relationship(
        "Reservation", back_populates="slot", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Slot {self.slot_label} @ {self.location.name}>"
