"""
End‑to‑end flows for both a normal user and an admin.
"""

from uuid import uuid4
import pytest


# ────────────────────────────────────────────────
#  USER FLOW
# ────────────────────────────────────────────────
def test_user_flow(client):
    # 1. register & login
    email = f"user-{uuid4()}@test.dev"
    payload = {
        "email": email,
        "password": "hunter2",
        "first_name": "E2E",
        "last_name": "User",
    }
    assert client.post("/api/auth/register", json=payload).status_code == 201
    login = client.post("/api/auth/login", json={"email": email, "password": "hunter2"})
    assert login.status_code == 200
    token = login.get_json()["access_token"]

    # 2. list locations (public route)
    res = client.get("/api/parking_location/locations")
    assert res.status_code == 200

    # 3. try to create a location (should fail 401/403)
    bad = client.post(
        "/api/parking_location/locations",
        json={"name": "Hack", "address": "X", "lat": 0, "lng": 0, "total_slots": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert bad.status_code in (401, 403)

    # 4. “logout” – just drop the token and ensure no auth header = 401
    res2 = client.get("/api/users/me")
    assert res2.status_code == 401


# ────────────────────────────────────────────────
#  ADMIN FLOW
# ────────────────────────────────────────────────
def test_admin_flow(client, admin_user, admin_token, make_location):
    # 1. list users (admin‑only route)
    res_users = client.get(
        "/api/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_users.status_code == 200

    # 2. create a parking location
    loc = make_location(total_slots=42)
    assert loc["total_slots"] == 42

    # 3. list locations (should include the one we just created)
    res_list = client.get("/api/parking_location/locations")
    assert res_list.status_code == 200
    names = [l["name"] for l in res_list.get_json()["locations"]]
    assert loc["name"] in names

    # 4. “logout” – drop token, access admin route should now fail
    fail = client.get("/api/users/", headers={"Authorization": "Bearer invalid"})
    assert fail.status_code in (401, 422)
