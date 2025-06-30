# This file seeds the database with sample users, parking locations, parking slots, and reservations.

from datetime import datetime, timedelta, timezone
from app import create_app
from extensions import db
from services.user_service import UserService
from services.parking_location_service import ParkingLocationService
from services.parking_slot_service import ParkingSlotService
from services.reservation_service import ReservationService
from models.user import UserRole
from models.reservation import ReservationStatus

def seed() -> None:
    app = create_app()
    with app.app_context():
        # -------- Reset schema --------
        db.drop_all()
        db.create_all()

        # -------- Users --------
        admin_1 = UserService.create_user(
            email="admin@sample.com",
            password="adminpw",
            first_name="Alice",
            last_name="Admin",
            role=UserRole.admin,
        )
        admin_2 = UserService.create_user(
            email="admin2@sample.com",
            password="adminpw2",
            first_name="Carlos",
            last_name="Super",
            role=UserRole.admin,
        )
        user_1 = UserService.create_user(
            email="davao.driver1@example.com",
            password="driver1",
            first_name="Daisy",
            last_name="Driver",
            role=UserRole.user,
        )
        user_2 = UserService.create_user(
            email="davao.driver2@example.com",
            password="driver2",
            first_name="Ernie",
            last_name="Driver",
            role=UserRole.user,
        )
        user_3 = UserService.create_user(
            email="davao.driver3@example.com",
            password="driver3",
            first_name="Felix",
            last_name="Driver",
            role=UserRole.user,
        )

        # -------- Parking locations --------
        roxas_lot = ParkingLocationService.create_location(
            name="Roxas Avenue Open Lot",
            address="Roxas Ave, Poblacion District, Davao City",
            lat=7.0735,
            lng=125.6121,
        )
        abreeza_garage = ParkingLocationService.create_location(
            name="Abreeza Basement Parking",
            address="J.P. Laurel Ave, Bajada, Davao City",
            lat=7.0989,
            lng=125.6128,
        )

        # -------- Parking slots --------
        slot_map = {}
        for label in ("A1", "A2", "A3", "A4"):
            s = ParkingSlotService.create_slot(slot_label=label, location_id=roxas_lot.id)
            slot_map[label] = s
        for label in ("B1", "B2", "B3", "B4"):
            s = ParkingSlotService.create_slot(slot_label=label, location_id=abreeza_garage.id)
            slot_map[label] = s

        # -------- Reservations --------
        now = datetime.now(timezone.utc)

        ReservationService.create(
            user_id=user_1.id,
            slot_id=slot_map["A1"].id,
            start_ts=now,
            end_ts=now + timedelta(hours=2),
            status=ReservationStatus.booked,
        )

        ReservationService.create(
            user_id=user_2.id,
            slot_id=slot_map["B2"].id,
            start_ts=now - timedelta(hours=1),
            end_ts=now + timedelta(hours=1),
            status=ReservationStatus.ongoing,
        )

        ReservationService.create(
            user_id=user_3.id,
            slot_id=slot_map["A3"].id,
            start_ts=now - timedelta(days=1, hours=3),
            end_ts=now - timedelta(days=1, hours=1),
            status=ReservationStatus.finished,
        )

        print("Database cleared and seeded with sample data.")

if __name__ == "__main__":
    seed()