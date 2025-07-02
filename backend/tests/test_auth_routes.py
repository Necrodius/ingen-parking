from uuid import uuid4


def test_register_and_login_flow(client):
    # 1. register
    email = f"new-{uuid4()}@test.dev"
    payload = {
        "email": email,
        "password": "hunter2",
        "first_name": "New",
        "last_name": "User",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201

    # 2. duplicate register = 409
    dup = client.post("/api/auth/register", json=payload)
    assert dup.status_code == 409

    # 3. wrong‑password login = 401
    bad = client.post("/api/auth/login",
                      json={"email": email, "password": "bad"})
    assert bad.status_code == 401
