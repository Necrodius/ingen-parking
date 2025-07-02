"""
conftest.py – central Pytest helpers for Ingen‑Parking
──────────────────────────────────────────────────────
• Spins up an in‑memory SQLite DB for the test session.
• Provides fixtures:
    client, registered_user, admin_user,
    user_token, admin_token,
    make_location()  → returns a dict‑AND‑model hybrid.
"""

from __future__ import annotations

import bcrypt
import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from typing import Generator, Callable, Dict, Any
from collections.abc import MutableMapping

from app import create_app
from extensions import db as _db
from models.user import User, UserRole

# ╭─────────────────────────────────────────────────────────────╮
# │ 0.  A tiny reusable wrapper – model ⇄ dict hybrid           │
# ╰─────────────────────────────────────────────────────────────╯
class _HybridModelDict(MutableMapping):
    """
    Wrap a SQLAlchemy model so it can be used BOTH as:
      • an object  – `obj.id`, `obj.name`
      • a mapping – `json={**obj}`
    """
    def __init__(self, model, data: Dict[str, Any]):
        self._model = model
        self._data  = data     # serialised dict (API‑friendly)

    # attribute access proxies to the model
    def __getattr__(self, item):    return getattr(self._model, item)

    # mapping protocol
    def __getitem__(self, k):       return self._data[k]
    def __setitem__(self, k, v):    self._data[k] = v
    def __delitem__(self, k):       del self._data[k]
    def __iter__(self):             return iter(self._data)
    def __len__(self):              return len(self._data)

    # nice repr for test failures
    def __repr__(self):
        cls = self._model.__class__.__name__
        return f"<Hybrid {cls} id={getattr(self._model, 'id', None)}>"

# ╭─────────────────────────────────────────────────────────────╮
# │ 1.  APP + DB FIXTURE                                        │
# ╰─────────────────────────────────────────────────────────────╯
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

        # ── Import schema modules so subclasses register themselves ──
        try:
            from schemas import (
                parking_location_schema,
                parking_slot_schema,
                reservation_schema,
                user_schema,
            )  # noqa: F401
        except ImportError:
            pass

        # ── Inject the test session into every Marshmallow‑SQLA schema ──
        try:
            from marshmallow_sqlalchemy import SQLAlchemySchema

            def _inject_session(cls: type) -> None:
                if hasattr(cls, "opts") and getattr(cls.opts, "sqla_session", None) is None:
                    cls.opts.sqla_session = _db.session
                for sub in cls.__subclasses__():
                    _inject_session(sub)

            _inject_session(SQLAlchemySchema)
        except ImportError:
            pass

        yield flask_app

        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """A test client for issuing requests to the Flask app."""
    return app.test_client()

# ╭─────────────────────────────────────────────────────────────╮
# │ 2.  USER HELPERS                                            │
# ╰─────────────────────────────────────────────────────────────╯
def _hash_password(password: str) -> str:
    """Generate a bcrypt hash with 12 rounds (fast in CI, still realistic)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def _create_or_update_user(email: str, password: str, role: UserRole, **kwargs) -> User:
    """Create or replace a user so each test starts from a clean slate."""
    existing = User.query.filter_by(email=email).first()
    if existing:
        _db.session.delete(existing)
        _db.session.flush()

    user = User(
        email=email,
        password_hash=_hash_password(password),
        first_name=kwargs.get("first_name", email.split("@")[0].title()),
        last_name=kwargs.get("last_name", "Test"),
        role=role,
        active=kwargs.get("active", True),
    )
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture
def registered_user(app):
    return _create_or_update_user(
        email="user@test.dev",
        password="pass1234",
        role=UserRole.user,
        first_name="Regular",
        last_name="User",
    )


@pytest.fixture
def admin_user(app):
    return _create_or_update_user(
        email="admin@test.dev",
        password="admin123",
        role=UserRole.admin,
        first_name="Admin",
        last_name="User",
    )

# ╭─────────────────────────────────────────────────────────────╮
# │ 3.  TOKEN FIXTURES                                          │
# ╰─────────────────────────────────────────────────────────────╯
def _get_auth_token(client, email: str, password: str) -> str:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()["access_token"]


@pytest.fixture
def user_token(client, registered_user):
    return _get_auth_token(client, registered_user.email, "pass1234")


@pytest.fixture
def admin_token(client, admin_user):
    return _get_auth_token(client, admin_user.email, "admin123")

# ╭─────────────────────────────────────────────────────────────╮
# │ 4.  PARKING LOCATION FACTORY                                │
# ╰─────────────────────────────────────────────────────────────╯
@pytest.fixture
def make_location(client, admin_token, app) -> Callable[..., _HybridModelDict]:
    """
    Factory: create a ParkingLocation plus N fresh slots and
    return a dict‑AND‑model hybrid.

    Usage:
        loc = make_location(total_slots=20, prefix="Expo‑Garage")
        client.post("/api/parking_location/locations", json={**loc})
    """
    from models.parking_slot import ParkingSlot
    from models.parking_location import ParkingLocation
    from schemas.parking_location_schema import ParkingLocationSchema

    def _factory(total_slots: int = 10, prefix: str = "Garage") -> _HybridModelDict:
        # 1️⃣  Build payload expected by the create‑location endpoint
        payload = {
            "name": f"{prefix}-{uuid4()}",
            "address": f"{uuid4().hex[:8]} Test Street",
            "lat": round(10 + (hash(prefix) % 1000) / 1000, 6),
            "lng": round(123 + (hash(prefix) % 1000) / 1000, 6),
        }

        # 2️⃣  Create the location via HTTP to exercise the real route
        resp = client.post(
            "/api/parking_location/locations",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 201, resp.get_json()
        loc_json = resp.get_json()["location"]

        # 3️⃣  Add slots quickly in bulk (DB‑level, faster than API loop)
        if total_slots:
            with app.app_context():
                slots = [
                    ParkingSlot(
                        slot_label=f"S-{i:03d}",
                        location_id=loc_json["id"],
                        is_available=True,
                    )
                    for i in range(1, total_slots + 1)
                ]
                _db.session.bulk_save_objects(slots)
                _db.session.commit()

        loc_json["total_slots"] = total_slots
        loc_json["available_slots"] = total_slots

        # 4️⃣  Wrap model + dict together
        with app.app_context():
            model = ParkingLocation.query.get(loc_json["id"])
            # Serialise again to make sure field names match schema
            api_dict = ParkingLocationSchema().dump(model)
            # Keep the counts we injected
            api_dict |= {"total_slots": total_slots, "available_slots": total_slots}
            return _HybridModelDict(model, api_dict)

    return _factory

# ╭─────────────────────────────────────────────────────────────╮
# │ 5.  ADDITIONAL HELPERS                                      │
# ╰─────────────────────────────────────────────────────────────╯
@pytest.fixture
def auth_headers():
    return lambda tok: {"Authorization": f"Bearer {tok}"}


@pytest.fixture
def future_datetime():
    return lambda hrs=1: datetime.now(timezone.utc) + timedelta(hours=hrs)


@pytest.fixture
def unique_email():
    return lambda prefix="test": f"{prefix}-{uuid4()}@test.dev"

# ╭─────────────────────────────────────────────────────────────╮
# │ 6.  DB CLEAN‑UP                                            │
# ╰─────────────────────────────────────────────────────────────╯
@pytest.fixture
def db_session(app):
    return _db.session


@pytest.fixture(autouse=True)
def clean_db(app):
    yield
    with app.app_context():
        _db.session.rollback()

# ╭─────────────────────────────────────────────────────────────╮
# │ 7.  RESERVATION FACTORY                                     │
# ╰─────────────────────────────────────────────────────────────╯
@pytest.fixture
def reservation_factory(client, user_token, make_location, future_datetime):
    """
    Quickly create a reservation for tests.

    Example:
        res = reservation_factory(hours_from_now=2)
    """
    def _factory(
        slot_id: int | None = None,
        hours_from_now: int = 1,
        duration_hours: int = 2,
        **overrides,
    ) -> Dict[str, Any]:
        # Auto‑provision a slot if caller didn’t give one
        if slot_id is None:
            loc = make_location(total_slots=5)
            resp = client.get(f"/api/parking_slot/slots?location_id={loc['id']}")
            slot_id = resp.get_json()["slots"][0]["id"]

        start = future_datetime(hours_from_now)
        end   = start + timedelta(hours=duration_hours)

        payload = {
            "slot_id": slot_id,
            "start_ts": start.isoformat(),
            "end_ts": end.isoformat(),
            **overrides,
        }

        resp = client.post(
            "/api/reservation/reservations",
            json=payload,
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 201, resp.get_json()
        return resp.get_json()["reservation"]

    return _factory
