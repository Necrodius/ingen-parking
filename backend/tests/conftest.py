"""
conftest.py – Shared Pytest fixtures for the Ingen‑Parking backend
------------------------------------------------------------------
• Spins up the Flask app in TESTING mode with an in‑memory SQLite DB.
• Provides clean `client`, `registered_user`, `admin_user`,
  and ready‑to‑use JWT fixtures (`user_token`, `admin_token`).
"""

import pytest
import bcrypt
from uuid import uuid4
from app import create_app, db
from models.user import User, UserRole

# ------------------------------------------------------------------ #
# Config helpers
# ------------------------------------------------------------------ #
TEST_DB_URI = "sqlite:///:memory:"        # blazing‑fast disposable DB


def _hash_password(plain: str) -> str:
    """Return a bcrypt hash.  rounds=4 keeps CI snappy."""
    return bcrypt.hashpw(
        plain.encode("utf-8"),
        bcrypt.gensalt(rounds=4),
    ).decode("utf-8")


# ------------------------------------------------------------------ #
# App‑level fixtures
# ------------------------------------------------------------------ #
@pytest.fixture(scope="session")
def app():
    """Factory‑based test app with a clean DB for the whole session."""
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=TEST_DB_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY="unit-test-secret",
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
    """Fresh Flask test client per test function."""
    return app.test_client()


# ------------------------------------------------------------------ #
# User helpers
# ------------------------------------------------------------------ #
def _insert_user(email: str, password: str, role: UserRole):
    """Upsert utility to avoid UNIQUE clashes."""
    existing = User.query.filter_by(email=email).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()

    user = User(
        email=email,
        password_hash=_hash_password(password),
        first_name=email.split("@")[0],
        last_name="Test",
        role=role,
        is_active=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def registered_user(app):
    return _insert_user("user@test.dev", "pass1234", UserRole.user)


@pytest.fixture
def admin_user(app):
    return _insert_user("admin@test.dev", "admin123", UserRole.admin)


# ------------------------------------------------------------------ #
# JWT helpers
# ------------------------------------------------------------------ #
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
