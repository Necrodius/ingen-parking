"""
conftest.py – Shared Pytest fixtures for the Ingen‑Parking backend
------------------------------------------------------------------
• Spins up the Flask app in TESTING mode with an in‑memory SQLite DB.
• Provides clean `client`, `registered_user`, `admin_user`,
  and ready‑to‑use JWT fixtures (`user_token`, `admin_token`).
• Uses bcrypt everywhere so test hashing = production hashing.
"""

import pytest
import bcrypt
from app import create_app, db
from models.user import User, UserRole

# ---------------------------------------------------------------------
# Basic config
# ---------------------------------------------------------------------
TEST_DB_URI = "sqlite:///:memory:"  # super‑fast disposable DB


def _hash_password(plain: str) -> str:
    """Return a bcrypt hash (low cost factor = faster CI)."""
    return bcrypt.hashpw(
        plain.encode("utf-8"),
        bcrypt.gensalt(rounds=4),      # rounds=4 ⇒ much faster than default 12
    ).decode("utf-8")


# ---------------------------------------------------------------------
# Flask application & client fixtures
# ---------------------------------------------------------------------
@pytest.fixture(scope="session")
def app():
    """
    Factory‑based app in TESTING mode.
    Creates all tables once per session and drops them when done.
    """
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=TEST_DB_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY="unit‑test‑secret",
        FRONTEND_URL="http://localhost",
        SCHEDULER_API_ENABLED=False,   # disable APScheduler during tests
    )

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client (fresh instance each test)."""
    return app.test_client()


# ---------------------------------------------------------------------
# User fixtures
# ---------------------------------------------------------------------
@pytest.fixture
def registered_user(app):
    """
    Normal USER account hashed with bcrypt.
    Deleted & re‑added each time to avoid UNIQUE clashes.
    """
    existing = User.query.filter_by(email="user@test.dev").first()
    if existing:
        db.session.delete(existing)
        db.session.commit()

    user = User(
        email="user@test.dev",
        password_hash=_hash_password("pass1234"),
        first_name="Jane",
        last_name="Doe",
        role=UserRole.user,
        is_active=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(app):
    """Admin account for privileged‑endpoint tests."""
    existing = User.query.filter_by(email="admin@test.dev").first()
    if existing:
        db.session.delete(existing)
        db.session.commit()

    admin = User(
        email="admin@test.dev",
        password_hash=_hash_password("admin123"),
        first_name="Admin",
        last_name="Root",
        role=UserRole.admin,
        is_active=True,
    )
    db.session.add(admin)
    db.session.commit()
    return admin


# ---------------------------------------------------------------------
# Helper to perform real /login and extract JWT
# ---------------------------------------------------------------------
def _login(client, email: str, password: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.get_json()
    return res.get_json()["access_token"]


@pytest.fixture
def user_token(client, registered_user):
    """JWT for the normal user fixture."""
    return _login(client, registered_user.email, "pass1234")


@pytest.fixture
def admin_token(client, admin_user):
    """JWT for the admin user fixture."""
    return _login(client, admin_user.email, "admin123")
