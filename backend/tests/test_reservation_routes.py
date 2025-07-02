"""
Illustrative flow: admin creates a location; user makes a reservation.
"""

import pytest
from uuid import uuid4

def test_user_can_create_and_get_reservation(client, admin_token, user_token):
    # 1. Admin sets up a location
    loc_payload = {
        "name": f"Test-Garage-{uuid4()}",
        "address": "A St",
        "latitude": 0,
        "longitude": 0,
        "total_slots": 2,
    }
    admin_res = client.post(
        "/api/parking_location/locations",
        json=loc_payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_res.status_code == 201
    loc_id = admin_res.get_json()["location"]["id"]

    # 2. User books slot #1
    booking = {
        "parking_location_id": loc_id,
        "slot_number": 1,
        "start_time": "2030-01-01T00:00:00Z",
        "end_time": "2030-01-01T01:00:00Z",
    }
    res = client.post(
        "/api/reservation/reservations",
        json=booking,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code == 201
    reservation_id = res.get_json()["reservation"]["id"]

    # 3. Fetch by ID should succeed
    res2 = client.get(
        f"/api/reservation/reservations/{reservation_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res2.status_code == 200
    assert res2.get_json()["reservation"]["id"] == reservation_id
