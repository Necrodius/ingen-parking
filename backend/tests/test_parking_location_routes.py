def test_admin_can_create_location(client, make_location):
    loc = make_location(total_slots=42)
    assert loc["total_slots"] == 42


def test_user_cannot_create_location(client, user_token):
    res = client.post(
        "/api/parking_location/locations",
        json={"name": "Forbidden", "address": "X", "latitude": 0,
              "longitude": 0, "total_slots": 1},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code in (401, 403)
