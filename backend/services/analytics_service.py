# This file contains the AnalyticsService class which provides methods for generating various analytics reports related to parking reservations, slot availability, and active users.

from datetime import date, datetime, timedelta
from typing import List, Dict
from sqlalchemy import func, cast, Date
from extensions import db
from models.reservation import Reservation, ReservationStatus
from models.parking_location import ParkingLocation
from models.parking_slot import ParkingSlot
from models.user import User

class AnalyticsService:
    # Reservations per calendar day (last N days, default = 7)
    @staticmethod
    def reservations_per_day(days: int = 7) -> List[Dict]:
        today = date.today()
        start = today - timedelta(days=days - 1)

        rows = (
            db.session.query(
                cast(Reservation.start_ts, Date).label("day"),
                func.count().label("count"),
            )
            .filter(Reservation.start_ts >= start)
            .group_by("day")
            .order_by("day")
            .all()
        )

        # ensure all days appear even if count = 0
        counts = {r.day: r.count for r in rows}
        return [
            {"day": (start + timedelta(d)).isoformat(), "count": counts.get(start + timedelta(d), 0)}
            for d in range(days)
        ]

    # Slot availability summary per location
    @staticmethod
    def slots_available_per_location() -> List[Dict]:
        sub_total = (
            db.session.query(
                ParkingSlot.location_id,
                func.count().label("total")
            )
            .group_by(ParkingSlot.location_id)
            .subquery()
        )

        sub_free = (
            db.session.query(
                ParkingSlot.location_id,
                func.count().label("available")
            )
            .filter(ParkingSlot.is_available.is_(True))
            .group_by(ParkingSlot.location_id)
            .subquery()
        )

        rows = (
            db.session.query(
                ParkingLocation.id,
                ParkingLocation.name,
                sub_total.c.total,
                func.coalesce(sub_free.c.available, 0).label("available"),
            )
            .join(sub_total, sub_total.c.location_id == ParkingLocation.id)
            .outerjoin(sub_free, sub_free.c.location_id == ParkingLocation.id)
            .order_by(ParkingLocation.name)
            .all()
        )

        return [
            {
                "location_id": r.id,
                "location_name": r.name,
                "total": r.total,
                "available": r.available,
            }
            for r in rows
        ]

    # Users with current reservations (booked or ongoing "now")
    @staticmethod
    def users_with_active_reservations() -> List[Dict]:
        now = func.now()

        rows = (
            db.session.query(User)
            .join(Reservation)
            .filter(
                Reservation.status.in_(
                    [ReservationStatus.booked, ReservationStatus.ongoing]
                ),
                Reservation.start_ts <= now,
                Reservation.end_ts >= now,
            )
            .distinct()
            .all()
        )

        result: List[Dict] = []
        for u in rows:
            active_res = [
                {
                    "id": r.id,
                    "slot_id": r.slot_id,
                    "status": r.status.value,
                    "start_ts": r.start_ts.isoformat(),
                    "end_ts": r.end_ts.isoformat(),
                }
                for r in u.reservations
                if r.status in (ReservationStatus.booked, ReservationStatus.ongoing)
                and r.start_ts <= datetime.now()
                and r.end_ts >= datetime.now()
            ]
            result.append(
                {
                    "user_id": u.id,
                    "email": u.email,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "reservations": active_res,
                }
            )
        return result
