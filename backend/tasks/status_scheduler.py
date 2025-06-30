# tasks/status_scheduler.py
# Runs inside an app‑context (provided by app.py’s scheduler wrapper).

from datetime import datetime, timezone
from extensions import db
from models.reservation import Reservation, ReservationStatus


def update_reservation_statuses() -> None:
    """Promote booked→ongoing and ongoing→finished reservations."""
    now = datetime.now(timezone.utc)

    # booked → ongoing
    booked_to_ongoing = (
        Reservation.query
        .filter(
            Reservation.status == ReservationStatus.booked,
            Reservation.start_ts <= now,
            Reservation.end_ts   >  now,
        )
        .all()
    )

    # ongoing → finished
    to_finished = (
        Reservation.query
        .filter(
            Reservation.status == ReservationStatus.ongoing,
            Reservation.end_ts <= now,
        )
        .all()
    )

    for r in booked_to_ongoing:
        r.status = ReservationStatus.ongoing
    for r in to_finished:
        r.status = ReservationStatus.finished

    if booked_to_ongoing or to_finished:
        db.session.commit()
