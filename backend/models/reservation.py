# It defines the Parking Location model for the application.

from app import db
from sqlalchemy import Enum
import enum

class ReservationStatus(enum.Enum):
    FINISHED = "finished"
    ONGOING = "ongoing"
    CANCELLED = "cancelled"
    BOOKED = "booked" 

class User(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    slot_id = db.Column(db.Integer, nullable=False)

    start_date_time = db.Column(db.DateTime)

    end_date_time = db.Column(db.DateTime)

    role = db.Column(db.Enum(ReservationStatus), nullable=False, default=ReservationStatus.BOOKED)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
