from datetime import datetime, timedelta, timezone

from app import create_app
from extensions import db
from services.user_service import UserService
from services.parking_location_service import ParkingLocationService
from services.parking_slot_service import ParkingSlotService
from services.reservation_service import ReservationService
from models.user import UserRole
from models.reservation import ReservationStatus

# ───────────────────────────────────────────────────────────
# Config – tweak these numbers if you need a bigger dataset
# ───────────────────────────────────────────────────────────
DRIVER_COUNT_PER_LOCATION = 4   # 4×13 locations = 52 drivers
SLOTS_PER_LOCATION        = 20

# ───────────────────────────────────────────────────────────
def seed() -> None:
    app = create_app()
    with app.app_context():
        # -------- Reset schema --------
        db.drop_all()
        db.create_all()

        # -------- Admin users --------
        admin_1 = UserService.create_user(
            email="admin@sample.com",
            password="adminpw",
            first_name="Alice",
            last_name="Admin",
            role=UserRole.admin,
        )
        admin_2 = UserService.create_user(
            email="boss@sample.com",
            password="superpw",
            first_name="Carlos",
            last_name="Boss",
            role=UserRole.admin,
        )

        # -------- Parking locations --------
        davao_locs = [
            {
                "name": "Roxas Avenue Open Lot",
                "address": "Roxas Ave, Poblacion, Davao City",
                "lat": 7.0735,
                "lng": 125.6121,
            },
            {
                "name": "Abreeza Basement Parking",
                "address": "J.P. Laurel Ave, Bajada, Davao City",
                "lat": 7.0989,
                "lng": 125.6128,
            },
            {
                "name": "SM City Ecoland Multi‑level",
                "address": "Quimpo Blvd, Talomo, Davao City",
                "lat": 7.0639,
                "lng": 125.6082,
            },
            # ─────────── Added 10 more semi‑realistic locations ───────────
            {
                "name": "SM Lanang Premier Multi‑level",
                "address": "J.P. Laurel Ave, Lanang, Davao City",
                "lat": 7.1115,
                "lng": 125.6508,
            },
            {
                "name": "Gaisano Mall of Davao Open Lot",
                "address": "J.P. Laurel Ave, Bajada, Davao City",
                "lat": 7.0917,
                "lng": 125.6110,
            },
            {
                "name": "Victoria Plaza Car Park",
                "address": "J.P. Laurel Ave, Bajada, Davao City",
                "lat": 7.0919,
                "lng": 125.6131,
            },
            {
                "name": "People's Park Underground Parking",
                "address": "Camus St, Poblacion, Davao City",
                "lat": 7.0667,
                "lng": 125.6039,
            },
            {
                "name": "Ateneo Annex Covered Parking",
                "address": "C.M. Recto Ave, Poblacion, Davao City",
                "lat": 7.0729,
                "lng": 125.6135,
            },
            {
                "name": "Davao Doctors Hospital Garage",
                "address": "Quirino Ave, Poblacion, Davao City",
                "lat": 7.0642,
                "lng": 125.6089,
            },
            {
                "name": "NCCC Mall Buhangin Open Lot",
                "address": "Diversion Rd, Buhangin, Davao City",
                "lat": 7.1390,
                "lng": 125.6123,
            },
            {
                "name": "Gaisano Grand Citygate Parking",
                "address": "Buhangin, Davao City",
                "lat": 7.1500,
                "lng": 125.6135,
            },
            {
                "name": "Agdao Public Market Parking",
                "address": "Agdao, Davao City",
                "lat": 7.0945,
                "lng": 125.6312,
            },
            {
                "name": "Matina Town Square Open Lot",
                "address": "Matina, Davao City",
                "lat": 7.0655,
                "lng": 125.6087,
            },
        ]

        loc_objs = []
        for loc in davao_locs:
            loc_obj = ParkingLocationService.create_location(**loc)
            loc_objs.append(loc_obj)

        # -------- Parking slots --------
        slot_objs = []
        for loc in loc_objs:
            for i in range(1, SLOTS_PER_LOCATION + 1):
                label = f"{loc.name.split()[0][0]}{i:02d}"  # e.g. "R01"
                s = ParkingSlotService.create_slot(
                    slot_label=label,
                    location_id=loc.id
                )
                slot_objs.append(s)

        # -------- Driver users --------
        drivers = []
        driver_counter = 1
        for loc_idx, loc in enumerate(loc_objs):
            for _ in range(DRIVER_COUNT_PER_LOCATION):
                d = UserService.create_user(
                    email=f"driver{driver_counter}@example.com",
                    password="driverpw",
                    first_name=f"Driver{driver_counter}",
                    last_name="Davao",
                    role=UserRole.user,
                    is_active=(driver_counter % 5 != 0),  # every 5th is inactive
                )
                drivers.append(d)
                driver_counter += 1

        # -------- Reservations --------
        now = datetime.now(timezone.utc)

        # Helper to pick deterministic slots/drivers
        def slot_for(idx: int):
            return slot_objs[idx % len(slot_objs)].id

        def driver_for(idx: int):
            return drivers[idx % len(drivers)].id

        # ➊ Upcoming bookings (status=booked)
        for i in range(6):
            ReservationService.create(
                user_id=driver_for(i),
                slot_id=slot_for(i),
                start_ts=now + timedelta(hours=2 + i),
                end_ts=now   + timedelta(hours=4 + i),
                status=ReservationStatus.booked,
            )

        # ➋ Currently ongoing
        for i in range(6, 10):
            ReservationService.create(
                user_id=driver_for(i),
                slot_id=slot_for(i),
                start_ts=now - timedelta(hours=1),
                end_ts=now   + timedelta(hours=1 + (i - 6)),
                status=ReservationStatus.ongoing,
            )

        # ➌ Recently finished
        for i in range(10, 14):
            ReservationService.create(
                user_id=driver_for(i),
                slot_id=slot_for(i),
                start_ts=now - timedelta(hours=5),
                end_ts=now   - timedelta(hours=3),
                status=ReservationStatus.finished,
            )

        # ➍ Cancelled examples
        for i in range(14, 17):
            ReservationService.create(
                user_id=driver_for(i),
                slot_id=slot_for(i),
                start_ts=now + timedelta(days=1),
                end_ts=now   + timedelta(days=1, hours=2),
                status=ReservationStatus.cancelled,
            )

        print("Database reset and seeded with sample data.")


if __name__ == "__main__":
    seed()
