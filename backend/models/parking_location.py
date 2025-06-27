# It defines the Parking Location model for the application.

from app import db 

class User(db.Model):
    __tablename__ = "parking_locations"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    address = db.Column(db.String(120), nullable=False)

    lat = db.Column(db.String(120), nullable=False)

    long = db.Column(db.String(120), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
