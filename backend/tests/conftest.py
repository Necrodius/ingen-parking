"""
conftest.py – central Pytest helpers for Ingen‑Parking
──────────────────────────────────────────────────────
• Spins up an in‑memory SQLite DB for the test session.
• Provides fixtures:
    client, registered_user, admin_user,
    user_token, admin_token,
    make_location()  -> creates a unique ParkingLocation with N fresh slots.
"""

from __future__ import annotations

import pytest
import bcrypt
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from typing import Generator, Callable, Dict, Any

from app import create_app
from extensions import db as _db
from models.user import User, UserRole


# ──────────────────────────────────────────────────────────────
# 1.  APP + DB FIXTURE
# ──────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def app() -> Generator:
    """Create a Flask app bound to an in‑memory SQLite DB for the *entire* test run."""
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY="unit‑test‑secret‑key‑2024",
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1),
        FRONTEND_URL="http://localhost:3000",
        SCHEDULER_API_ENABLED=False,
        WTF_CSRF_ENABLED=False,  # Disable CSRF for testing
    )

    with flask_app.app_context():
        _db.create_all()

        # ── Import schema modules so subclasses are registered ─────────────
        try:
            from schemas import (
                parking_location_schema, 
                parking_slot_schema, 
                reservation_schema,
                user_schema
            )  # noqa: F401
        except ImportError:
            # Schemas might not exist yet or have different names
            pass

        # ── Monkey‑patch: inject test session into *all* schema subclasses ─
        try:
            from marshmallow_sqlalchemy import SQLAlchemySchema

            def _inject_session(cls: type) -> None:
                if hasattr(cls, 'opts') and getattr(cls.opts, "sqla_session", None) is None:
                    cls.opts.sqla_session = _db.session
                for sub in cls.__subclasses__():
                    _inject_session(sub)

            _inject_session(SQLAlchemySchema)
        except ImportError:
            # marshmallow_sqlalchemy might not be used
            pass

        yield flask_app

        # Cleanup
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """A test client for issuing requests to the Flask app."""
    return app.test_client()


# ──────────────────────────────────────────────────────────────
# 2.  USER HELPERS
# ──────────────────────────────────────────────────────────────
def _hash_password(password: str) -> str:
    """Generate a bcrypt hash with 12 rounds (fast in CI, still realistic)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def _create_or_update_user(email: str, password: str, role: UserRole, **kwargs) -> User:
    """Create or replace a user so each test starts from a clean slate."""
    # Remove existing user if any
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        _db.session.delete(existing_user)
        _db.session.flush()  # Ensure UNIQUE(email) constraint is freed

    # Create new user
    user_data = {
        'email': email,
        'password_hash': _hash_password(password),
        'first_name': kwargs.get('first_name', email.split('@')[0].title()),
        'last_name': kwargs.get('last_name', 'Test'),
        'role': role,
        'is_active': kwargs.get('is_active', True),
    }
    
    user = User(**user_data)
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture
def registered_user(app):
    """Create a regular user for testing."""
    return _create_or_update_user(
        email="user@test.dev", 
        password="pass1234", 
        role=UserRole.user,
        first_name="Regular",
        last_name="User"
    )


@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    return _create_or_update_user(
        email="admin@test.dev", 
        password="admin123", 
        role=UserRole.admin,
        first_name="Admin",
        last_name="User"
    )


# ──────────────────────────────────────────────────────────────
# 3.  TOKEN FIXTURES
# ──────────────────────────────────────────────────────────────
def _get_auth_token(client, email: str, password: str) -> str:
    """Login and return the access token."""
    response = client.post("/api/auth/login", json={
        "email": email, 
        "password": password
    })
    
    if response.status_code != 200:
        raise Exception(f"Login failed for {email}: {response.get_json()}")
    
    data = response.get_json()
    if "access_token" not in data:
        raise Exception(f"No access_token in response: {data}")
    
    return data["access_token"]


@pytest.fixture
def user_token(client, registered_user):
    """Get auth token for regular user."""
    return _get_auth_token(client, registered_user.email, "pass1234")


@pytest.fixture
def admin_token(client, admin_user):
    """Get auth token for admin user."""
    return _get_auth_token(client, admin_user.email, "admin123")


# ──────────────────────────────────────────────────────────────
# 4.  PARKING LOCATION HELPER
# ──────────────────────────────────────────────────────────────
@pytest.fixture
def make_location(client, admin_token, app) -> Callable[[int, str], Dict[str, Any]]:
    """
    Create a ParkingLocation + <total_slots> fresh slots, return its JSON dict.
    
    Usage:
        loc = make_location(total_slots=10, prefix="TestGarage")
    """
    
    def _create_location(total_slots: int = 10, prefix: str = "Garage") -> Dict[str, Any]:
        # Import here to avoid circular imports
        from models.parking_slot import ParkingSlot
        
        # 1️⃣ Create the location via HTTP API
        location_data = {
            "name": f"{prefix}-{uuid4()}",
            "address": f"{uuid4().hex[:8]} Test Street",
            "lat": round(1.0 + (hash(prefix) % 1000) / 1000, 6),  # Generate unique coords
            "lng": round(2.0 + (hash(prefix) % 1000) / 1000, 6),
        }
        
        response = client.post(
            "/api/parking_location/locations",
            json=location_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to create location: {response.get_json()}")
        
        location = response.get_json()["location"]
        
        # 2️⃣ Bulk‑insert parking slots for performance
        if total_slots > 0:
            with app.app_context():
                slot_objects = [
                    ParkingSlot(
                        slot_label=f"Slot-{i:03d}",  # Zero-padded for better sorting
                        location_id=location["id"],
                        is_available=True,
                    )
                    for i in range(1, total_slots + 1)
                ]
                
                _db.session.bulk_save_objects(slot_objects)
                _db.session.commit()
        
        # 3️⃣ Add slot counts to the returned location dict
        location["available_slots"] = total_slots
        location["total_slots"] = total_slots
        
        return location
    
    return _create_location


# ──────────────────────────────────────────────────────────────
# 5.  ADDITIONAL HELPER FIXTURES
# ──────────────────────────────────────────────────────────────
@pytest.fixture
def auth_headers():
    """Helper to create auth headers."""
    def _headers(token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {token}"}
    return _headers


@pytest.fixture
def future_datetime():
    """Helper to generate future datetime objects for reservations."""
    def _future(hours: int = 1) -> datetime:
        return datetime.now(timezone.utc) + timedelta(hours=hours)
    return _future


@pytest.fixture
def unique_email():
    """Generate unique email addresses for testing."""
    def _email(prefix: str = "test") -> str:
        return f"{prefix}-{uuid4()}@test.dev"
    return _email


# ──────────────────────────────────────────────────────────────
# 6.  DATABASE HELPERS
# ──────────────────────────────────────────────────────────────
@pytest.fixture
def db_session(app):
    """Direct access to database session for complex test setups."""
    return _db.session


@pytest.fixture(autouse=True)
def clean_db(app):
    """Automatically clean database between tests."""
    yield
    # Clean up after each test
    with app.app_context():
        _db.session.rollback()


# ──────────────────────────────────────────────────────────────
# 7.  TEST DATA FACTORIES
# ──────────────────────────────────────────────────────────────
@pytest.fixture
def reservation_factory(client, user_token, make_location, future_datetime):
    """Factory to create test reservations."""
    def _create_reservation(
        slot_id: int = None,
        hours_from_now: int = 1,
        duration_hours: int = 2,
        **kwargs
    ) -> Dict[str, Any]:
        # Create location and get slot if not provided
        if slot_id is None:
            location = make_location(total_slots=5)
            slots_response = client.get(f"/api/parking_slot/slots?location_id={location['id']}")
            slot_id = slots_response.get_json()["slots"][0]["id"]
        
        start_time = future_datetime(hours_from_now)
        end_time = start_time + timedelta(hours=duration_hours)
        
        payload = {
            "slot_id": slot_id,
            "start_ts": start_time.isoformat(),
            "end_ts": end_time.isoformat(),
            **kwargs
        }
        
        response = client.post(
            "/api/reservation/reservations",
            json=payload,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to create reservation: {response.get_json()}")
        
        return response.get_json()["reservation"]
    
    return _create_reservation