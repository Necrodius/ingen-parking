"""
conftest.py – central test helpers for Ingen‑Parking
===================================================
• Spins up the Flask app in TESTING mode with a RAM SQLite DB.
• Provides ready‑to‑use fixtures:
  ─ client           → Flask test‑client
  ─ admin_user       → admin SQLA model
  ─ registered_user  → normal user model
  ─ admin_token      → JWT string for admin_user
  ─ user_token       → JWT string for registered_user
  ─ make_location    → helper to create a unique parking location
"""

import pytest, bcrypt, time
from uuid import uuid4
from app import create_app, db
from models.user import User, UserRole


# ------------------------------------------------------------------ #
# Helper utils
# ------------------------------------------------------------------ #
TEST_DB_URI = "sqlite:///:memory:"            # fast & disposable


def _hash_pw(pwd: str) -> str:
    """bcrypt with low cost rounds (CI‑friendly)."""
    return bcrypt.hashpw(
        pwd.encode(),
        bcrypt.gensalt(rounds=4)
    ).decode()


def _upsert_user(email: str, raw_pw: str, role: UserRole):
    """Insert or replace a user to avoid UNIQUE conflicts."""
    existing = User.query.filter_by(email=email).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
    user = User(
        email=email,
        password_hash=_hash_pw(raw_pw),
        first_name=email.split("@")[0],
        last_name="Test",
        role=role,
        is_active=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


def _login(client, email: str, password: str) -> str:
    """Return JWT from real /login route."""
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.get_json()
    return res.get_json()["access_token"]


# ------------------------------------------------------------------ #
# Core app / db fixtures
# ------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def app():
    """Factory‑based Flask app with clean in‑memory DB."""
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=TEST_DB_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY="unit‑test‑secret",
        FRONTEND_URL="http://localhost",
        SCHEDULER_API_ENABLED=False,
    )

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Fresh client per test → cookies, headers isolated."""
    return app.test_client()


# ------------------------------------------------------------------ #
# User & token fixtures
# ------------------------------------------------------------------ #
@pytest.fixture
def registered_user(app):
    return _upsert_user("user@test.dev", "pass1234", UserRole.user)


@pytest.fixture
def admin_user(app):
    return _upsert_user("admin@test.dev", "admin123", UserRole.admin)


@pytest.fixture
def user_token(client, registered_user):
    return _login(client, registered_user.email, "pass1234")


@pytest.fixture
def admin_token(client, admin_user):
    return _login(client, admin_user.email, "admin123")


# ------------------------------------------------------------------ #
# Parking‑location factory fixture
# ------------------------------------------------------------------ #
@pytest.fixture
def make_location(client, admin_token):
    """
    Callable fixture → returns a helper that creates a fresh, unique
    parking location (using admin privileges) and returns its JSON dict.
    """

    def _create(total_slots: int = 10, prefix: str = "Garage") -> dict:
        payload = {
            "name": f"{prefix}-{uuid4()}",
            "address": "123 Main St",
            "latitude": 1.23,
            "longitude": 4.56,
            "total_slots": total_slots,
        }
        res = client.post(
            "/api/parking_location/locations",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert res.status_code == 201, res.get_json()
        return res.get_json()["location"]

    return _create
