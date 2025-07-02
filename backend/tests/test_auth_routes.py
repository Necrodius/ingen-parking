# ══════════════════════════════════════════════════════════════════════════════
# AUTH ROUTES TESTS
# ══════════════════════════════════════════════════════════════════════════════

from uuid import uuid4

from models.user import UserRole


class TestAuthRoutes:
    """Test authentication endpoints"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        email = f"new-{uuid4()}@test.dev"
        payload = {
            "email": email,
            "password": "hunter2",
            "first_name": "New",
            "last_name": "User",
        }
        res = client.post("/api/auth/register", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["email"] == email
        assert "id" in data
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email returns 409"""
        email = f"dup-{uuid4()}@test.dev"
        payload = {
            "email": email,
            "password": "hunter2",
            "first_name": "First",
            "last_name": "User",
        }
        # First registration
        res1 = client.post("/api/auth/register", json=payload)
        assert res1.status_code == 201
        
        # Duplicate registration
        res2 = client.post("/api/auth/register", json=payload)
        assert res2.status_code == 409
        assert "error" in res2.get_json()
    
    def test_register_validation_errors(self, client):
        """Test registration with invalid data"""
        # Missing required fields
        res = client.post("/api/auth/register", json={})
        assert res.status_code == 400
        assert "errors" in res.get_json()
        
        # Invalid email format
        res = client.post("/api/auth/register", json={
            "email": "invalid-email",
            "password": "pass123",
            "first_name": "Test",
            "last_name": "User"
        })
        assert res.status_code == 400
    
    def test_login_success(self, client, registered_user):
        """Test successful login"""
        res = client.post("/api/auth/login", json={
            "email": registered_user.email,
            "password": "pass1234"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert "access_token" in data
    
    def test_login_invalid_credentials(self, client, registered_user):
        """Test login with wrong password"""
        res = client.post("/api/auth/login", json={
            "email": registered_user.email,
            "password": "wrongpass"
        })
        assert res.status_code == 401
        assert res.get_json()["error"] == "Invalid credentials"
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email"""
        res = client.post("/api/auth/login", json={
            "email": "nonexistent@test.dev",
            "password": "anypass"
        })
        assert res.status_code == 401
    
    def test_login_deactivated_account(self, client, app):
        """Test login with deactivated account returns 403"""
        from models.user import User
        from extensions import db
        from utils.security import hash_password
        
        # Create deactivated user
        with app.app_context():
            user = User(
                email="deactivated@test.dev",
                password_hash=hash_password("pass123"),
                first_name="Deactivated",
                last_name="User",
                role=UserRole.user,
                active=False
            )
            db.session.add(user)
            db.session.commit()
        
        res = client.post("/api/auth/login", json={
            "email": "deactivated@test.dev",
            "password": "pass123"
        })
        assert res.status_code == 403
        assert "Account disabled" in res.get_json()["error"]