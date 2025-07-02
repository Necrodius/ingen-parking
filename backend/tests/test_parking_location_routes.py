"""
Admin‑only endpoints. Uses admin_token fixture for auth header.
"""
def test_create_location_ok(client, admin_token):
    new_loc = {"name": "Uptown Garage", "address": "123 Main", "latitude": 1.23,
               "longitude": 4.56, "total_slots": 50}
    res = client.post(
        "/api/parking_location/locations",
        json=new_loc,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 201
    assert res.get_json()["location"]["name"] == new_loc["name"]


def test_create_location_forbidden(client, user_token):
    """
    Normal USER should be blocked (403) by @role_required(UserRole.admin).
    """
    bad_loc = {"name": "Forbidden", "address": "n/a", "latitude": 0, "longitude": 0,
               "total_slots": 1}
    res = client.post("/api/parking_location/locations",
                      json=bad_loc,
                      headers={"Authorization": f"Bearer {user_token}"})
    # 403 from decorator OR 401 if jwt_required not satisfied → accept both
    assert res.status_code in (403, 401)
