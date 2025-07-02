"""
Admin‑only endpoints. Uses admin_token fixture for auth header.
"""

import time
from uuid import uuid4

def test_create_location_ok(client, admin_token):
    # unique name avoids 409 conflicts across tests
    loc_name = f"Garage-{uuid4()}"
    new_loc = {
        "name": loc_name,
        "address": "123 Main",
        "latitude": 1.23,
        "longitude": 4.56,
        "total_slots": 50,
    }
    res = client.post(
        "/api/parking_location/locations",
        json=new_loc,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 201
    assert res.get_json()["location"]["name"] == loc_name


def test_create_location_forbidden(client, user_token):
    bad_loc = {
        "name": f"Forbidden-{time.time()}",
        "address": "n/a",
        "latitude": 0,
        "longitude": 0,
        "total_slots": 1,
    }
    res = client.post(
        "/api/parking_location/locations",
        json=bad_loc,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code in (403, 401)
