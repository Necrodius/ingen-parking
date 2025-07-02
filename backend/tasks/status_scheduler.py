# tasks/status_scheduler.py
# Runs inside an app‑context (provided by app.py’s scheduler wrapper).

from datetime import datetime, timezone
from flask import current_app as app
from extensions import db
from models.reservation import Reservation, ReservationStatus


def update_reservation_statuses() -> None:
    """Promote booked→ongoing and ongoing→finished reservations."""
    now = datetime.now(timezone.utc)
    app.logger.info("🔄 Updating reservation statuses at %s", now.isoformat())

    # booked → ongoing
    booked_to_ongoing = (
        Reservation.query
        .filter(
            Reservation.status == ReservationStatus.booked,
            Reservation.start_ts <= now,
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
        app.logger.info("✅ %d updated: %d → ongoing, %d → finished",
                        len(booked_to_ongoing) + len(to_finished),
                        len(booked_to_ongoing), len(to_finished))
    else:
        app.logger.info("✅ No status changes needed.")
