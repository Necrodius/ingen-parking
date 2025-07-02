# tasks/status_scheduler.py
# Runs inside an app‑context (provided by app.py’s scheduler wrapper).

from datetime import datetime, timezone
from flask import current_app as app
from extensions import db
from models.reservation import Reservation, ReservationStatus

# Update reservation status
def update_reservation_statuses() -> None:
    
    now = datetime.now(timezone.utc)

    # Booked reservation where start date is after now
    booked_to_ongoing = (
        Reservation.query
        .filter(
            Reservation.status == ReservationStatus.booked,
            Reservation.start_ts <= now,
        )
        .all()
    )

    # Ongoing reservations where end date is before now
    to_finished = (
        Reservation.query
        .filter(
            Reservation.status == ReservationStatus.ongoing,
            Reservation.end_ts <= now,
        )
        .all()
    )

    # Booked to ongoing
    for r in booked_to_ongoing:
        r.status = ReservationStatus.ongoing
    
    # Ongoing to finished
    for r in to_finished:
        r.status = ReservationStatus.finished

    # Commit changes to DB only if there are
    if booked_to_ongoing or to_finished:
        db.session.commit()
