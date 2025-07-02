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
    #  Reservations per calendar day (last N days, default = 7)
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

        # ensure every day appears, even if the count is zero
        counts = {r.day: r.count for r in rows}
        return [
            {
                "day": (start + timedelta(offset)).isoformat(),
                "count": counts.get(start + timedelta(offset), 0),
            }
            for offset in range(days)
        ]

    #  Slot availability summary per location (LIVE, right now)
    @staticmethod
    def slots_available_per_location() -> List[Dict]:
        now = func.now()

        # Total slots per location 
        sub_total = (
            db.session.query(
                ParkingSlot.location_id.label("loc_id"),
                func.count(ParkingSlot.id).label("total"),
            )
            .group_by(ParkingSlot.location_id)
            .subquery()
        )

        # Reserved slots per location (distinct slot IDs)
        sub_reserved = (
            db.session.query(
                ParkingSlot.location_id.label("loc_id"),
                func.count(func.distinct(Reservation.slot_id)).label("reserved"),
            )
            .join(Reservation, Reservation.slot_id == ParkingSlot.id)
            .filter(
                Reservation.status.in_(
                    [ReservationStatus.booked, ReservationStatus.ongoing]
                ),
                Reservation.start_ts <= now,
                Reservation.end_ts >= now,
            )
            .group_by(ParkingSlot.location_id)
            .subquery()
        )

        # Combine and compute available = total − reserved
        rows = (
            db.session.query(
                ParkingLocation.id,
                ParkingLocation.name,
                sub_total.c.total,
                (sub_total.c.total - func.coalesce(sub_reserved.c.reserved, 0)).label(
                    "available"
                ),
            )
            .join(sub_total, sub_total.c.loc_id == ParkingLocation.id)
            .outerjoin(sub_reserved, sub_reserved.c.loc_id == ParkingLocation.id)
            .order_by(ParkingLocation.name)
            .all()
        )

        # convert to plain dicts for JSON
        return [
            {
                "location_id": r.id,
                "location_name": r.name,
                "total": r.total,
                "available": r.available,
            }
            for r in rows
        ]

    #  Users with currently active reservations
    @staticmethod
    def users_with_active_reservations() -> List[Dict]:
        now = func.now()

        users = (
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
        for u in users:
            active_res = [
                {
                    "id": r.id,
                    "slot_id": r.slot_id,
                    "status": r.status.value,
                    "start_ts": r.start_ts.isoformat(),
                    "end_ts": r.end_ts.isoformat(),
                }
                for r in u.reservations
                if r.status
                in (
                    ReservationStatus.booked,
                    ReservationStatus.ongoing,
                )
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

