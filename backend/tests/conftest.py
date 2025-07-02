"""
conftest.py – central Pytest helpers for Ingen‑Parking
-----------------------------------------------------
• Spins up a RAM SQLite DB for the whole session.
• Provides fixtures:
    client, registered_user, admin_user,
    user_token, admin_token,
    make_location()  -> creates a unique ParkingLocation.
• Binds Marshmallow schemas to the test DB session so .load() works.
"""

import pytest, bcrypt
from uuid import uuid4

from app import create_app
from extensions import db as _db
from models.user import User, UserRole

# ──────────────────────────────────────────────────────────────
# 1.  APP + DB FIXTURE
# ──────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def app():
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

        # ── Monkey‑patch: set default session for all Marshmallow‑SQLAlchemy schemas ──
        from marshmallow_sqlalchemy import SQLAlchemySchema, SQLAlchemyAutoSchema
        def _inject_session(cls):
            """Recursively set sqla_session on each Schema subclass."""
            if getattr(cls.opts, "sqla_session", None) is None:
                cls.opts.sqla_session = _db.session
            for sub in cls.__subclasses__():
                _inject_session(sub)

        _inject_session(SQLAlchemySchema)

        # ── Bind Marshmallow schemas to this session ───────────────────────
        from schemas import (
            parking_location_schema,
            parking_slot_schema,
            reservation_schema,
        )

        parking_location_schema.parking_location_schema.context["session"] = _db.session
        parking_location_schema.parking_locations_schema.context["session"] = _db.session
        parking_slot_schema.parking_slot_schema.context["session"] = _db.session
        parking_slot_schema.parking_slots_schema.context["session"] = _db.session
        reservation_schema.reservation_schema.context["session"] = _db.session
        reservation_schema.reservations_schema.context["session"] = _db.session
        # ──────────────────────────────────────────────────────────────────

        yield flask_app

        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ──────────────────────────────────────────────────────────────
# 2.  USER HELPERS
# ──────────────────────────────────────────────────────────────
def _hash(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(rounds=4)).decode()


def _upsert_user(email: str, password: str, role: UserRole) -> User:
    prior = User.query.filter_by(email=email).first()
    if prior:
        _db.session.delete(prior)
        _db.session.commit()

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
# 4.  make_location FIXTURE  (admin token inside)
# ──────────────────────────────────────────────────────────────
@pytest.fixture
def make_location(client, admin_token):
    """Factory helper that creates a ParkingLocation; returns its JSON dict."""
    def _create(total_slots: int = 10, prefix: str = "Garage") -> dict:
        payload = {
            "name": f"{prefix}-{uuid4()}",
            "address": "123 Main St",
            "latitude": 1.0,
            "longitude": 2.0,
            "total_slots": total_slots,
        }
        res = client.post(
            "/api/parking_location/locations",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res.status_code == 201, res.get_json()
        return res.get_json()["location"]

    return _create
