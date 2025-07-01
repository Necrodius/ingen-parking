"""
Idempotent database seeder for Ingenuity Smart Parking.

You can execute this file repeatedly (e.g. on every container start).
It will only add missing records and will never drop / duplicate tables.

Run manually:
    python seed.py
"""

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
# Config – tweak these to enlarge or shrink demo dataset
# ───────────────────────────────────────────────────────────
DRIVER_COUNT_PER_LOCATION = 4    # 4×13 locations = 52 drivers
SLOTS_PER_LOCATION        = 20

# ───────────────────────────────────────────────────────────
# Demo data – locations + admin users
# ───────────────────────────────────────────────────────────
ADMIN_USERS = [
    {
        "email": "admin@sample.com",
        "password": "adminpw",
        "first_name": "Alice",
        "last_name": "Admin",
        "role": UserRole.admin,
    },
    {
        "email": "boss@sample.com",
        "password": "superpw",
        "first_name": "Carlos",
        "last_name": "Boss",
        "role": UserRole.admin,
    },
]

DAVAO_LOCS = [
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
    # ---- 10 more semi‑realistic locations ----
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

# ───────────────────────────────────────────────────────────
# Helper functions
# ───────────────────────────────────────────────────────────
def get_or_create_admin_users() -> None:
    """Create admin users only if they don't exist."""
    for data in ADMIN_USERS:
        if not UserService.get_by_email(data["email"]):
            UserService.create_user(**data)


def get_or_create_locations() -> list:
    """
    Create parking locations if missing and return the full list
    (both existing and newly created) as model objects.
    """
    loc_objs = []
    for loc in DAVAO_LOCS:
        existing = ParkingLocationService.get_by_name(loc["name"])
        if existing:
            loc_objs.append(existing)
        else:
            loc_objs.append(ParkingLocationService.create_location(**loc))
    return loc_objs


def ensure_slots_for_locations(locations: list) -> list:
    """
    Ensure each location has exactly SLOTS_PER_LOCATION slots.
    Missing ones are added; existing ones are left untouched.
    Returns all slot objects (existing + new) in a flat list.
    """
    all_slots = []
    for loc in locations:
        # Gather existing labels for quick lookup
        current_labels = {slot.slot_label for slot in loc.slots}
        for i in range(1, SLOTS_PER_LOCATION + 1):
            label = f"{loc.name.split()[0][0]}{i:02d}"  # e.g. "R01"
            if label not in current_labels:
                ParkingSlotService.create_slot(
                    slot_label=label,
                    location_id=loc.id,
                )
        # Refresh relationship to include any newly added slots
        db.session.refresh(loc)
        all_slots.extend(loc.slots)
    return all_slots


def ensure_driver_users(locations: list) -> list:
    """
    Create driver accounts so that each location has
    DRIVER_COUNT_PER_LOCATION drivers.
    Returns the full driver list.
    """
    drivers = []
    # We'll just count global total, not per‑location uniqueness
    existing_driver_count = UserService.count_by_role(UserRole.user)
    target_total = DRIVER_COUNT_PER_LOCATION * len(locations)

    # Skip creation if we already have enough drivers
    if existing_driver_count >= target_total:
        return UserService.get_all_by_role(UserRole.user)

    next_idx = existing_driver_count + 1
    while next_idx <= target_total:
        drivers.append(
            UserService.create_user(
                email=f"driver{next_idx}@example.com",
                password="driverpw",
                first_name=f"Driver{next_idx}",
                last_name="Davao",
                role=UserRole.user,
                is_active=(next_idx % 5 != 0),  # every 5th is inactive
            )
        )
        next_idx += 1

    drivers.extend(UserService.get_all_by_role(UserRole.user))
    return drivers


def seed_reservations(drivers: list, slots: list) -> None:
    """
    Seed demo reservations only if there are *no* reservations yet.
    """
    if ReservationService.count() > 0:
        print("Reservations already exist; skipping reservation seeding.")
        return

    now = datetime.now(timezone.utc)

    # Helper to pick deterministic slots/drivers
    def slot_for(idx: int):
        return slots[idx % len(slots)].id

    def driver_for(idx: int):
        return drivers[idx % len(drivers)].id

    # ➊ Upcoming bookings (status=booked)
    for i in range(6):
        ReservationService.create(
            user_id=driver_for(i),
            slot_id=slot_for(i),
            start_ts=now + timedelta(hours=2 + i),
            end_ts=now + timedelta(hours=4 + i),
            status=ReservationStatus.booked,
        )

    # ➋ Currently ongoing
    for i in range(6, 10):
        ReservationService.create(
            user_id=driver_for(i),
            slot_id=slot_for(i),
            start_ts=now - timedelta(hours=1),
            end_ts=now + timedelta(hours=1 + (i - 6)),
            status=ReservationStatus.ongoing,
        )

    # ➌ Recently finished
    for i in range(10, 14):
        ReservationService.create(
            user_id=driver_for(i),
            slot_id=slot_for(i),
            start_ts=now - timedelta(hours=5),
            end_ts=now - timedelta(hours=3),
            status=ReservationStatus.finished,
        )

    # ➍ Cancelled examples
    for i in range(14, 17):
        ReservationService.create(
            user_id=driver_for(i),
            slot_id=slot_for(i),
            start_ts=now + timedelta(days=1),
            end_ts=now + timedelta(days=1, hours=2),
            status=ReservationStatus.cancelled,
        )


# ───────────────────────────────────────────────────────────
# Main seeding function
# ───────────────────────────────────────────────────────────
def seed() -> None:
    """
    Entry point for idempotent seeding. Safe to run on each startup.
    """
    app = create_app()
    with app.app_context():
        # 1️⃣ Ensure all tables exist (no drop_all!)
        db.create_all()

        # 2️⃣ Core data
        get_or_create_admin_users()
        loc_objs  = get_or_create_locations()
        slot_objs = ensure_slots_for_locations(loc_objs)
        drivers   = ensure_driver_users(loc_objs)

        # 3️⃣ Demo reservations (only if none exist)
        seed_reservations(drivers, slot_objs)

        print("✅ Database seeded (idempotent run).")


if __name__ == "__main__":
    seed()
