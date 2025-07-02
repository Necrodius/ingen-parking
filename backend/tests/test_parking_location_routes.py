class TestParkingLocationRoutes:
    """Test parking location endpoints"""
    
    def test_admin_create_location(self, make_location):
        """Test admin can create parking locations"""
        loc = make_location(total_slots=10, prefix="TestGarage")
        assert loc["name"].startswith("TestGarage")
        assert loc["total_slots"] == 10
    
    def test_user_cannot_create_location(self, client, user_token):
        """Test regular user cannot create locations"""
        payload = {
            "name": "Forbidden",
            "address": "123 Test St",
            "lat": 1.0,
            "lng": 2.0
        }
        res = client.post("/api/parking_location/locations",
                         json=payload,
                         headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 403
    
    def test_list_locations_public(self, client, make_location):
        """Test anyone can list locations (public endpoint)"""
        # Create a location first
        loc = make_location(total_slots=5)
        
        # List without authentication
        res = client.get("/api/parking_location/locations")
        assert res.status_code == 200
        data = res.get_json()
        assert "locations" in data
        
        # Find our created location
        created_loc = next((l for l in data["locations"] if l["name"] == loc["name"]), None)
        assert created_loc is not None
        assert created_loc["available_slots"] == 5
    
    def test_get_location_by_id(self, client, make_location):
        """Test getting specific location by ID"""
        loc = make_location(total_slots=3)
        
        res = client.get(f"/api/parking_location/locations/{loc['id']}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["location"]["id"] == loc["id"]
        assert data["location"]["available_slots"] == 3
    
    def test_get_nonexistent_location(self, client):
        """Test getting non-existent location returns 404"""
        res = client.get("/api/parking_location/locations/99999")
        assert res.status_code == 404
        assert "Location not found" in res.get_json()["error"]
    
    def test_admin_update_location(self, client, admin_token, make_location):
        """Test admin can update locations"""
        loc = make_location(total_slots=5)
        
        payload = {
            "name": "Updated Garage",
            "address": "456 New St"
        }
        res = client.put(f"/api/parking_location/locations/{loc['id']}",
                        json=payload,
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["location"]["name"] == "Updated Garage"
        assert data["location"]["address"] == "456 New St"
    
    def test_admin_delete_location(self, client, admin_token, make_location):
        """Test admin can delete locations"""
        loc = make_location(total_slots=2)
        
        res = client.delete(f"/api/parking_location/locations/{loc['id']}",
                           headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 204
        
        # Verify deletion
        res = client.get(f"/api/parking_location/locations/{loc['id']}")
        assert res.status_code == 404
