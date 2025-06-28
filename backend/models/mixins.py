# This file defines a class that adds creation and last update timestamps.
# They automatically set to the current time when a record is created (in DB) or updated (in backend).

from sqlalchemy import Column, DateTime, func
from extensions import db

class TimestampMixin:
    created_at  = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)