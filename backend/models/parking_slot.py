# It defines the Parking Location model for the application.

from app import db 

class User(db.Model):
    __tablename__ = "parking_slots"

    id = db.Column(db.Integer, primary_key=True)

    slot_name = db.Column(db.Integer, nullable=False)

    location = db.Column(db.String(120), nullable=False)

    is_available = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
