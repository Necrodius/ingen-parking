# ══════════════════════════════════════════════════════════════════════════════
# USER ROUTES TESTS
# ══════════════════════════════════════════════════════════════════════════════

from uuid import uuid4


class TestUserRoutes:
    """Test user management endpoints"""
    
    def test_admin_create_user(self, client, admin_token):
        """Test admin can create users"""
        payload = {
            "email": f"created-{uuid4()}@test.dev",
            "password": "newpass123",
            "first_name": "Created",
            "last_name": "User",
            "role": "user"
        }
        res = client.post("/api/users/", 
                         json=payload,
                         headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 201
        data = res.get_json()
        assert data["user"]["email"] == payload["email"]
    
    def test_user_cannot_create_user(self, client, user_token):
        """Test regular user cannot create users"""
        payload = {
            "email": f"forbidden-{uuid4()}@test.dev",
            "password": "pass123",
            "first_name": "Test",
            "last_name": "User"
        }
        res = client.post("/api/users/", 
                         json=payload,
                         headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 403
    
    def test_admin_list_users(self, client, admin_token):
        """Test admin can list all users"""
        res = client.get("/api/users/",
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert "users" in data
        assert len(data["users"]) >= 2  # At least admin and regular user
    
    def test_user_cannot_list_users(self, client, user_token):
        """Test regular user cannot list all users"""
        res = client.get("/api/users/",
                        headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 403
    
    def test_get_me(self, client, user_token, registered_user):
        """Test getting own user profile"""
        res = client.get("/api/users/me",
                        headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["user"]["email"] == registered_user.email
    
    def test_get_me_unauthenticated(self, client):
        """Test getting profile without authentication"""
        res = client.get("/api/users/me")
        assert res.status_code == 401
    
    def test_get_user_by_id_self(self, client, user_token, registered_user):
        """Test user can get their own profile by ID"""
        res = client.get(f"/api/users/{registered_user.id}",
                        headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["user"]["id"] == registered_user.id
    
    def test_get_user_by_id_admin(self, client, admin_token, registered_user):
        """Test admin can get any user by ID"""
        res = client.get(f"/api/users/{registered_user.id}",
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["user"]["id"] == registered_user.id
    
    def test_get_user_forbidden(self, client, user_token, admin_user):
        """Test user cannot get other users' profiles"""
        res = client.get(f"/api/users/{admin_user.id}",
                        headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 403
    
    def test_update_own_profile(self, client, user_token, registered_user):
        """Test user can update their own profile"""
        payload = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        res = client.put(f"/api/users/{registered_user.id}",
                        json=payload,
                        headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["user"]["first_name"] == "Updated"
    
    def test_admin_delete_user(self, client, admin_token, registered_user):
        """Test admin can delete users"""
        res = client.delete(f"/api/users/{registered_user.id}",
                           headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 204
    
    def test_admin_deactivate_user(self, client, admin_token, registered_user):
        """Test admin can deactivate users"""
        res = client.post(f"/api/users/{registered_user.id}/deactivate",
                         headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["user"]["is_active"] is False
    
    def test_change_password_success(self, client, user_token, registered_user):
        """Test successful password change"""
        payload = {
            "old_password": "pass1234",
            "new_password": "newpass123"
        }
        res = client.post(f"/api/users/{registered_user.id}/change-password",
                         json=payload,
                         headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 200
        assert "Password updated successfully" in res.get_json()["message"]
    
    def test_change_password_wrong_old(self, client, user_token, registered_user):
        """Test password change with wrong old password"""
        payload = {
            "old_password": "wrongpass",
            "new_password": "newpass123"
        }
        res = client.post(f"/api/users/{registered_user.id}/change-password",
                         json=payload,
                         headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 400
        assert "Incorrect old password" in res.get_json()["error"]