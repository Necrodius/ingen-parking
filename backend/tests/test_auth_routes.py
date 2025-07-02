"""
Happy‑path & failure‑path tests for /register and /login routes.
"""

def test_register_success(client):
    payload = {
        "email": "new@test.dev",
        "password": "hunter2",
        "first_name": "New",
        "last_name": "User",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201
    body = res.get_json()
    assert body["email"] == payload["email"]
    assert "id" in body


def test_register_duplicate(client, registered_user):
    dup = {
        "email": registered_user.email,
        "password": "whatever",
        "first_name": "Dup",
        "last_name": "User",
    }
    res = client.post("/api/auth/register", json=dup)
    assert res.status_code == 409
    assert "error" in res.get_json()


def test_login_invalid(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "user@test.dev", "password": "wrong"},
    )
    assert res.status_code == 401
    assert res.get_json()["error"] == "Invalid credentials"
