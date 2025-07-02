# Seed script for database

from datetime import datetime, timedelta, timezone
from app import create_app
from extensions import db
from services.user_service import UserService
from services.parking_location_service import ParkingLocationService
from services.parking_slot_service import ParkingSlotService
from services.reservation_service import ReservationService
from models.user import User, UserRole
from models.parking_location import ParkingLocation
from models.parking_slot import ParkingSlot
from models.reservation import Reservation, ReservationStatus

# Config  (tweak for a bigger/smaller demo dataset)
DRIVERS_PER_LOCATION = 4   # 4 × 13 locations = 52 drivers
SLOTS_PER_LOCATION   = 20

# Static demo data
ADMIN_USERS = [
    {"email": "admin@sample.com", "password": "adminpw", "first_name": "Alice",  "last_name": "Admin", "role": UserRole.admin},
    {"email": "boss@sample.com",  "password": "superpw", "first_name": "Carlos", "last_name": "Boss",  "role": UserRole.admin},
]

DAVAO_LOCS = [
    {"name": "Roxas Avenue Open Lot",            "address": "Roxas Ave, Poblacion, Davao City", "lat": 7.0735, "lng": 125.6121},
    {"name": "Abreeza Basement Parking",         "address": "J.P. Laurel Ave, Bajada, Davao City", "lat": 7.0989, "lng": 125.6128},
    {"name": "SM City Ecoland Multi‑level",      "address": "Quimpo Blvd, Talomo, Davao City", "lat": 7.0639, "lng": 125.6082},
    {"name": "SM Lanang Premier Multi‑level",    "address": "J.P. Laurel Ave, Lanang, Davao City", "lat": 7.1115, "lng": 125.6508},
    {"name": "Gaisano Mall of Davao Open Lot",   "address": "J.P. Laurel Ave, Bajada, Davao City", "lat": 7.0917, "lng": 125.6110},
    {"name": "Victoria Plaza Car Park",          "address": "J.P. Laurel Ave, Bajada, Davao City", "lat": 7.0919, "lng": 125.6131},
    {"name": "People's Park Underground",        "address": "Camus St, Poblacion, Davao City", "lat": 7.0667, "lng": 125.6039},
    {"name": "Ateneo Annex Covered Parking",     "address": "C.M. Recto Ave, Poblacion, Davao City", "lat": 7.0729, "lng": 125.6135},
    {"name": "Davao Doctors Hospital Garage",    "address": "Quirino Ave, Poblacion, Davao City", "lat": 7.0642, "lng": 125.6089},
    {"name": "NCCC Mall Buhangin Open Lot",      "address": "Diversion Rd, Buhangin, Davao City", "lat": 7.1390, "lng": 125.6123},
    {"name": "Gaisano Grand Citygate Parking",   "address": "Buhangin, Davao City", "lat": 7.1500, "lng": 125.6135},
    {"name": "Agdao Public Market Parking",      "address": "Agdao, Davao City", "lat": 7.0945, "lng": 125.6312},
    {"name": "Matina Town Square Open Lot",      "address": "Matina, Davao City", "lat": 7.0655, "lng": 125.6087},
]

# ---------- HELPERS ----------

# Create admin users if not present
def ensure_admins() -> None:
    for data in ADMIN_USERS:
        if not User.query.filter_by(email=data["email"]).first():
            UserService.create_user(**data)

# Create locations if not present then return all location objects
def ensure_locations() -> list[ParkingLocation]:
    locs: list[ParkingLocation] = []
    for loc_data in DAVAO_LOCS:
        loc = ParkingLocation.query.filter_by(name=loc_data["name"]).first()
        if not loc:
            try:
                loc = ParkingLocationService.create_location(**loc_data)
            except ValueError:
                loc = ParkingLocation.query.filter_by(name=loc_data["name"]).first()
        locs.append(loc)
    return locs

# Ensure each location has slots then return all slots
def ensure_slots(locs: list[ParkingLocation]) -> list[ParkingSlot]:
    all_slots: list[ParkingSlot] = []
    for loc in locs:
        existing_labels = {s.slot_label for s in loc.slots}
        for i in range(1, SLOTS_PER_LOCATION + 1):
            label = f"{loc.name.split()[0][0]}{i:02d}"
            if label not in existing_labels:
                ParkingSlotService.create_slot(slot_label=label, location_id=loc.id)
        db.session.refresh(loc)            # refresh relationship
        all_slots.extend(loc.slots)
    return all_slots

# Create drivers then return all drivers
def ensure_drivers(total_needed: int) -> list[User]:
    drivers: list[User] = list(User.query.filter_by(role=UserRole.user))
    next_idx = len(drivers) + 1
    while len(drivers) < total_needed:
        email = f"driver{next_idx}@example.com"
        driver = UserService.create_user(
            email=email,
            password="driverpw",
            first_name=f"Driver{next_idx}",
            last_name="Davao",
            role=UserRole.user,
            active=(next_idx % 5 != 0),
        )
        drivers.append(driver)
        next_idx += 1
    return drivers

# Insert reservations only if the table is empty
def seed_reservations(drivers: list[User], slots: list[ParkingSlot]) -> None:
    if db.session.query(Reservation).count() > 0:
        return

    now = datetime.now(timezone.utc)

    def slot_for(idx: int):   return slots[idx % len(slots)].id
    def driver_for(idx: int): return drivers[idx % len(drivers)].id

    # Upcoming (booked)
    for i in range(6):
        ReservationService.create(
            user_id=driver_for(i),
            slot_id=slot_for(i),
            start_ts=now + timedelta(hours=2 + i),
            end_ts  =now + timedelta(hours=4 + i),
            status  =ReservationStatus.booked,
        )
    # Ongoing
    for i in range(6, 10):
        ReservationService.create(
            user_id=driver_for(i),
            slot_id=slot_for(i),
            start_ts=now - timedelta(hours=1),
            end_ts  =now + timedelta(hours=1 + (i - 6)),
            status  =ReservationStatus.ongoing,
        )
    # Finished
    for i in range(10, 14):
        ReservationService.create(
            user_id=driver_for(i),
            slot_id=slot_for(i),
            start_ts=now - timedelta(hours=5),
            end_ts  =now - timedelta(hours=3),
            status  =ReservationStatus.finished,
        )
    # Cancelled
    for i in range(14, 17):
        ReservationService.create(
            user_id=driver_for(i),
            slot_id=slot_for(i),
            start_ts=now + timedelta(days=1),
            end_ts  =now + timedelta(days=1, hours=2),
            status  =ReservationStatus.cancelled,
        )

# ---------- MAIN ----------
def seed() -> None:
    app = create_app()
    with app.app_context():
        # Ensure schema exists
        db.create_all()

        # Seed core data
        ensure_admins()
        locations = ensure_locations()
        slots     = ensure_slots(locations)
        drivers   = ensure_drivers(DRIVERS_PER_LOCATION * len(locations))

        # Seed reservations
        seed_reservations(drivers, slots)

        print("Database idempotently seeded")

if __name__ == "__main__":
    seed()
