from uuid import uuid4

def test_user_reservation_flow(client, make_location, user_token):
    # Admin sets up location + slots
    loc = make_location(total_slots=5, prefix="ResvGarage")
    # user reserves slot #1
    booking = {
        "parking_location_id": loc["id"],
        "slot_number": 1,
        "start_time": "2030-01-01T00:00:00Z",
        "end_time": "2030-01-01T01:00:00Z",
    }
    res_create = client.post(
        "/api/reservation/reservations",
        json=booking,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res_create.status_code == 201
    res_id = res_create.get_json()["reservation"]["id"]

    # fetch should succeed
    res_get = client.get(
        f"/api/reservation/reservations/{res_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res_get.status_code == 200
    assert res_get.get_json()["reservation"]["id"] == res_id
