# This file defines a class that adds creation and last update timestamps.
# They automatically set to the current time when a record is created (in DB) or updated (in backend).


from datetime import datetime
from app import db

class TimestampMixin:
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )