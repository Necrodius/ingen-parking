# This file seeds the database with sample users, parking locations, parking slots, and reservations.

from datetime import datetime, timedelta, UTC

from app import create_app, db
from models import User, UserRole, ParkingLocation, ParkingSlot, Reservation, ReservationStatus

def hash_password(raw: str) -> str:
    # Temporary dummy hash
    return f"hashed-{raw}"

def seed() -> None:
    app = create_app()
    with app.app_context():
        # ---------- clear & recreate schema ----------
        db.drop_all()
        db.create_all()

        # ---------- USERS ----------
        admin_1 = User(
            email="admin@sample.com",
            password_hash=hash_password("adminpw"),
            first_name="Alice",
            last_name="Admin",
            role=UserRole.admin,
        )

        admin_2 = User(
            email="admin2@sample.com",
            password_hash=hash_password("adminpw2"),
            first_name="Carlos",
            last_name="Super",
            role=UserRole.admin,
        )

        user_1 = User(
            email="davao.driver1@example.com",
            password_hash=hash_password("driver1"),
            first_name="Daisy",
            last_name="Driver",
            role=UserRole.user,
        )

        user_2 = User(
            email="davao.driver2@example.com",
            password_hash=hash_password("driver2"),
            first_name="Ernie",
            last_name="Driver",
            role=UserRole.user,
        )

        user_3 = User(
            email="davao.driver3@example.com",
            password_hash=hash_password("driver3"),
            first_name="Felix",
            last_name="Driver",
            role=UserRole.user,
        )

        db.session.add_all([admin_1, admin_2, user_1, user_2, user_3])
        db.session.flush()

        # ---------- PARKING LOCATIONS ----------
        roxas_lot = ParkingLocation(
            name="Roxas Avenue Open Lot",
            address="Roxas Ave, Poblacion District, Davao City",
            lat=7.0735,
            lng=125.6121,
        )

        abreeza_garage = ParkingLocation(
            name="Abreeza Basement Parking",
            address="J.P. Laurel Ave, Bajada, Davao City",
            lat=7.0989,
            lng=125.6128,
        )

        db.session.add_all([roxas_lot, abreeza_garage])
        db.session.flush()

        # ---------- PARKING SLOTS ----------
        slots = []
        for label in ("A1", "A2", "A3", "A4"):
            slots.append(ParkingSlot(slot_label=label, location_id=roxas_lot.id))
        for label in ("B1", "B2", "B3", "B4"):
            slots.append(ParkingSlot(slot_label=label, location_id=abreeza_garage.id))

        db.session.add_all(slots)
        db.session.flush()
        slot_map = {s.slot_label: s for s in slots}

        # ---------- RESERVATIONS ----------
        now = datetime.now(UTC)
        res_1 = Reservation(
            user_id=user_1.id,
            slot_id=slot_map["A1"].id,
            start_ts=now,
            end_ts=now + timedelta(hours=2),
            status=ReservationStatus.booked,
        )

        res_2 = Reservation(
            user_id=user_2.id,
            slot_id=slot_map["B2"].id,
            start_ts=now - timedelta(hours=1),
            end_ts=now + timedelta(hours=1),
            status=ReservationStatus.ongoing,
        )

        res_3 = Reservation(
            user_id=user_3.id,
            slot_id=slot_map["A3"].id,
            start_ts=now - timedelta(days=1, hours=3),
            end_ts=now - timedelta(days=1, hours=1),
            status=ReservationStatus.finished,
        )

        db.session.add_all([res_1, res_2, res_3])

        # ---------- COMMIT ----------
        db.session.commit()
        print("Database cleared and seeded with sample data.")

if __name__ == "__main__":
    seed()