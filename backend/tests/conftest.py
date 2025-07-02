"""
conftest.py – central Pytest helpers for Ingen‑Parking
──────────────────────────────────────────────────────
• Spins up an in‑memory SQLite DB for the test session.
• Provides fixtures:
    client, registered_user, admin_user,
    user_token, admin_token,
    make_location()  -> creates a unique ParkingLocation with N fresh slots.
"""

from __future__ import annotations

import pytest, bcrypt
from uuid import uuid4
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
        JWT_SECRET_KEY="unit‑test‑secret",
        FRONTEND_URL="http://localhost",
        SCHEDULER_API_ENABLED=False,
    )

    with flask_app.app_context():
        _db.create_all()

        # ── Import every schema module so subclasses are registered ─────────
        from schemas import parking_location_schema, parking_slot_schema, reservation_schema  # noqa: F401

        # ── Monkey‑patch: inject test session into *all* schema subclasses ──
        from marshmallow_sqlalchemy import SQLAlchemySchema

        def _inject_session(cls: type) -> None:
            if getattr(cls.opts, "sqla_session", None) is None:
                cls.opts.sqla_session = _db.session
            for sub in cls.__subclasses__():
                _inject_session(sub)

        _inject_session(SQLAlchemySchema)

        yield flask_app

        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """A test client for issuing requests to the Flask app."""
    return app.test_client()

# ──────────────────────────────────────────────────────────────
# 2.  USER HELPERS
# ──────────────────────────────────────────────────────────────
def _hash(pwd: str) -> str:
    """Generate a bcrypt hash with 12 rounds (fast in CI, still realistic)."""
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(rounds=12)).decode()


def _upsert_user(email: str, password: str, role: UserRole) -> User:
    """Create or replace a user so each test starts from a clean slate."""
    prior = User.query.filter_by(email=email).first()
    if prior:
        _db.session.delete(prior)
    user = User(
        email=email,
        password_hash=_hash(password),
        first_name=email.split("@")[0],
        last_name="Test",
        role=role,
        is_active=True,
    )
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture
def registered_user(app):
    return _upsert_user("user@test.dev", "pass1234", UserRole.user)


@pytest.fixture
def admin_user(app):
    return _upsert_user("admin@test.dev", "admin123", UserRole.admin)

# ──────────────────────────────────────────────────────────────
# 3.  TOKEN FIXTURES
# ──────────────────────────────────────────────────────────────
def _login(client, email: str, password: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.get_json()
    return res.get_json()["access_token"]


@pytest.fixture
def user_token(client, registered_user):
    return _login(client, registered_user.email, "pass1234")


@pytest.fixture
def admin_token(client, admin_user):
    return _login(client, admin_user.email, "admin123")

# ──────────────────────────────────────────────────────────────
# 4.  make_location FIXTURE
# ──────────────────────────────────────────────────────────────
@pytest.fixture
def make_location(client, admin_token) -> Callable[[int, str], Dict[str, Any]]:
    """Create a ParkingLocation + <slot_count> fresh slots, return its JSON dict."""

    from models.parking_slot import ParkingSlot  # late import keeps startup quick

    def _create(slot_count: int = 10, prefix: str = "Garage") -> Dict[str, Any]:
        # 1️⃣  Create the location via real HTTP route
        payload = {
            "name": f"{prefix}-{uuid4()}",
            "address": "123 Main St",
            "lat": 1.0,
            "lng": 2.0,
        }
        res = client.post(
            "/api/parking_location/locations",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res.status_code == 201, res.get_json()
        location = res.get_json()["location"]

        # 2️⃣  Bulk‑insert slots for speed
        _db.session.bulk_save_objects(
            [
                ParkingSlot(
                    slot_label=f"Slot-{i}",
                    location_id=location["id"],
                    is_available=True,
                )
                for i in range(1, slot_count + 1)
            ]
        )
        _db.session.commit()

        location["available_slots"] = slot_count
        return location

    return _create
