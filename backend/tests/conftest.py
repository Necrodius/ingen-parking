"""
conftest.py – central test helpers for Ingen‑Parking
===================================================
• Spins up the Flask app in TESTING mode with a RAM SQLite DB.
• Provides fixtures:
    client, registered_user, admin_user,
    user_token, admin_token,
    make_location()  -> creates a unique ParkingLocation via the API.
"""

import pytest
import bcrypt
from uuid import uuid4

from app import create_app
from extensions import db as _db
from models.user import User, UserRole


# ────────────── DB + APP FIXTURE ────────────── #
@pytest.fixture(scope="session")
def app():
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY="unit-test-secret",
        FRONTEND_URL="http://localhost",
        SCHEDULER_API_ENABLED=False,  # disable APScheduler inside tests
    )
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ────────────── USER HELPERS ────────────── #
def _hash_pw(pwd: str) -> str:
    # low rounds for CI speed; safe because test DB only
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(rounds=4)).decode()


def _upsert_user(email: str, password: str, role: UserRole) -> User:
    prev = User.query.filter_by(email=email).first()
    if prev:
        _db.session.delete(prev)
        _db.session.commit()

    user = User(
        email=email,
        password_hash=_hash_pw(password),
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


# ────────────── TOKEN HELPERS ────────────── #
def _login(client, email: str, password: str) -> str:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()["access_token"]


@pytest.fixture
def user_token(client, registered_user):
    return _login(client, registered_user.email, "pass1234")


@pytest.fixture
def admin_token(client, admin_user):
    return _login(client, admin_user.email, "admin123")


# ────────────── LOCATION HELPER ────────────── #
@pytest.fixture
def make_location(client, admin_token):
    """Return a helper that creates a ParkingLocation via the API."""
    def _create(total_slots: int = 10, prefix: str = "Garage") -> dict:
        payload = {
            "name": f"{prefix}-{uuid4()}",
            "address": "123 Main St",
            "latitude": 1.23,
            "longitude": 4.56,
            "total_slots": total_slots,
        }
        resp = client.post(
            "/api/parking_location/locations",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 201, resp.get_json()
        return resp.get_json()["location"]

    return _create
