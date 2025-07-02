"""
conftest.py – Pytest fixtures shared by all test files.
Each line has comments to show exactly what is happening.
"""
import pytest
from app import create_app, db   # your factory & db instance
from models.user import User, UserRole  # adjust import if path differs
from werkzeug.security import generate_password_hash

TEST_DB_URI = "sqlite:///:memory:"  # fast, disposable DB for tests


@pytest.fixture(scope="session")
def app():
    """
    Build a fully configured Flask app in TESTING mode, backed by an
    in‑memory SQLite DB so every test run starts from a clean slate.
    """
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,                         # tells Flask & extensions we’re in test mode
        SQLALCHEMY_DATABASE_URI=TEST_DB_URI,  # swap real DB → SQLite RAM
        JWT_SECRET_KEY="unit‑test‑secret",    # simple secret for JWT
        SCHEDULER_API_ENABLED=False           # don’t spin up APScheduler
    )

    with flask_app.app_context():
        db.create_all()     # create tables once per test session
        yield flask_app
        db.session.remove() # cleanly close connections
        db.drop_all()       # drop all tables after the session


@pytest.fixture
def client(app):
    """
    Returns Flask’s built‑in test client, already bound to the app fixture.
    A fresh client is supplied to each test so cookies / headers don’t leak.
    """
    return app.test_client()


# ------------------------------------------------------------------
# Helper fixtures for quickly creating a user and grabbing a JWT
# ------------------------------------------------------------------

@pytest.fixture
def registered_user(app):
    """
    Inserts a normal USER row directly via SQLAlchemy (bypassing routes)
    so tests don’t rely on /register for setup.
    """
    user = User(
        email="user@test.dev",
        password_hash=generate_password_hash("pass1234"),  # 🔑 same as login payload
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
    """
    Same idea as registered_user but with admin privileges.
    """
    admin = User(
        email="admin@test.dev",
        password_hash=generate_password_hash("admin123"),
        first_name="Admin",
        last_name="Root",
        role=UserRole.admin,
        is_active=True,
    )
    db.session.add(admin)
    db.session.commit()
    return admin


def _login(client, email, password):
    """Utility: POST /api/auth/login and return JWT string."""
    res = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200, res.get_json()
    return res.get_json()["access_token"]


@pytest.fixture
def user_token(client, registered_user):
    """JWT for normal user."""
    return _login(client, registered_user.email, "pass1234")


@pytest.fixture
def admin_token(client, admin_user):
    """JWT for admin."""
    return _login(client, admin_user.email, "admin123")
