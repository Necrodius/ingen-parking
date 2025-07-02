def test_register_and_login_flow(client, registered_user):
    # fresh email ensures 201
    email = f"new-{uuid4()}@test.dev"
    payload = {
        "email": email,
        "password": "hunter2",
        "first_name": "New",
        "last_name": "User",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201
    # duplicate should now 409
    res_dup = client.post("/api/auth/register", json=payload)
    assert res_dup.status_code == 409
    # wrong password login
    bad_login = client.post("/api/auth/login",
                            json={"email": email, "password": "bad"})
    assert bad_login.status_code == 401
