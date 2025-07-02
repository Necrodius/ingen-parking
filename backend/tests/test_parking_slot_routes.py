
# PARKING SLOT ROUTES TESTS
class TestParkingSlotRoutes:
#   TO FIX    
#    def test_admin_create_slot(self, client, admin_token, make_location):
#        loc = make_location(total_slots=0)  # Create location without slots
#        
#        payload = {
#            "slot_label": "A1",
#            "location_id": loc["id"],
#            "is_available": True
#        }
#        res = client.post("/api/parking_slot/slots",
#                         json=payload,
#                         headers={"Authorization": f"Bearer {admin_token}"})
#        assert res.status_code == 201
#        data = res.get_json()
#        assert data["slot"]["slot_label"] == "A1"
#        assert data["slot"]["location_id"] == loc["id"]
    
    def test_user_cannot_create_slot(self, client, user_token, make_location):
        loc = make_location(total_slots=0)
        
        payload = {
            "slot_label": "B1",
            "location_id": loc["id"],
            "is_available": True
        }
        res = client.post("/api/parking_slot/slots",
                         json=payload,
                         headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 403
    
    def test_list_all_slots(self, client, make_location):
        make_location(total_slots=3)
        
        res = client.get("/api/parking_slot/slots")
        assert res.status_code == 200
        data = res.get_json()
        assert "slots" in data
        assert len(data["slots"]) >= 3
    
    def test_list_slots_by_location(self, client, make_location):
        loc1 = make_location(total_slots=2, prefix="Garage1")
        loc2 = make_location(total_slots=3, prefix="Garage2")
        
        # Get slots for location 1
        res = client.get(f"/api/parking_slot/slots?location_id={loc1['id']}")
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["slots"]) == 2
        
        # Verify all slots belong to location 1
        for slot in data["slots"]:
            assert slot["location_id"] == loc1["id"]
    
    def test_get_slot_by_id(self, client, make_location):
        loc = make_location(total_slots=1)
        
        # Get the slot ID from listing
        slots_res = client.get(f"/api/parking_slot/slots?location_id={loc['id']}")
        slot_id = slots_res.get_json()["slots"][0]["id"]
        
        res = client.get(f"/api/parking_slot/slots/{slot_id}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["slot"]["id"] == slot_id
    
    def test_admin_update_slot(self, client, admin_token, make_location):
        loc = make_location(total_slots=1)
        
        # Get slot ID
        slots_res = client.get(f"/api/parking_slot/slots?location_id={loc['id']}")
        slot_id = slots_res.get_json()["slots"][0]["id"]
        
        payload = {
            "slot_label": "Updated-A1",
            "is_available": False
        }
        res = client.put(f"/api/parking_slot/slots/{slot_id}",
                        json=payload,
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["slot"]["slot_label"] == "Updated-A1"
        assert data["slot"]["is_available"] is False
    
    def test_admin_delete_slot(self, client, admin_token, make_location):
        loc = make_location(total_slots=1)
        
        # Get slot ID
        slots_res = client.get(f"/api/parking_slot/slots?location_id={loc['id']}")
        slot_id = slots_res.get_json()["slots"][0]["id"]
        
        res = client.delete(f"/api/parking_slot/slots/{slot_id}",
                           headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 204
        
        # Verify deletion
        res = client.get(f"/api/parking_slot/slots/{slot_id}")
        assert res.status_code == 404