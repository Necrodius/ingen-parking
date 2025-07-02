# ══════════════════════════════════════════════════════════════════════════════
# RESERVATION ROUTES TESTS
# ══════════════════════════════════════════════════════════════════════════════

from datetime import datetime, timedelta, timezone


class TestReservationRoutes:
    """Test reservation endpoints"""
    
    def test_create_reservation_success(self, client, user_token, make_location):
        """Test successful reservation creation"""
        loc = make_location(total_slots=5)
        
        # Get a slot ID
        slots_res = client.get(f"/api/parking_slot/slots?location_id={loc['id']}")
        slot_id = slots_res.get_json()["slots"][0]["id"]
        
        start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        payload = {
            "slot_id": slot_id,
            "start_ts": start_time.isoformat(),
            "end_ts": end_time.isoformat()
        }
        res = client.post("/api/reservation/reservations",
                         json=payload,
                         headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 201
        data = res.get_json()
        assert data["reservation"]["slot_id"] == slot_id
        assert data["reservation"]["status"] == "booked"
    
    def test_create_overlapping_reservation(self, client, user_token, make_location):
        """Test creating overlapping reservations fails"""
        loc = make_location(total_slots=1)
        
        # Get slot ID
        slots_res = client.get(f"/api/parking_slot/slots?location_id={loc['id']}")
        slot_id = slots_res.get_json()["slots"][0]["id"]
        
        start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        # Create first reservation
        payload1 = {
            "slot_id": slot_id,
            "start_ts": start_time.isoformat(),
            "end_ts": end_time.isoformat()
        }
        res1 = client.post("/api/reservation/reservations",
                          json=payload1,
                          headers={"Authorization": f"Bearer {user_token}"})
        assert res1.status_code == 201
        
        # Try to create overlapping reservation
        payload2 = {
            "slot_id": slot_id,
            "start_ts": (start_time + timedelta(minutes=30)).isoformat(),
            "end_ts": (end_time + timedelta(minutes=30)).isoformat()
        }
        res2 = client.post("/api/reservation/reservations",
                          json=payload2,
                          headers={"Authorization": f"Bearer {user_token}"})
        assert res2.status_code == 400
        assert "already booked" in res2.get_json()["error"]
    
    def test_user_list_own_reservations(self, client, user_token, make_location):
        """Test user can list their own reservations"""
        loc = make_location(total_slots=2)
        
        # Create a reservation
        slots_res = client.get(f"/api/parking_slot/slots?location_id={loc['id']}")
        slot_id = slots_res.get_json()["slots"][0]["id"]
        
        start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        payload = {
            "slot_id": slot_id,
            "start_ts": start_time.isoformat(),
            "end_ts": (start_time + timedelta(hours=1)).isoformat()
        }
        client.post("/api/reservation/reservations",
                   json=payload,
                   headers={"Authorization": f"Bearer {user_token}"})
        
        # List reservations
        res = client.get("/api/reservation/reservations",
                        headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["reservations"]) >= 1
    
    def test_admin_list_all_reservations(self, client, admin_token, user_token, make_location):
        """Test admin can see all reservations"""
        loc = make_location(total_slots=2)
        
        # User creates a reservation
        slots_res = client.get(f"/api/parking_slot/slots?location_id={loc['id']}")
        slot_id = slots_res.get_json()["slots"][0]["id"]
        
        start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        payload = {
            "slot_id": slot_id,
            "start_ts": start_time.isoformat(),
            "end_ts": (start_time + timedelta(hours=1)).isoformat()
        }
        client.post("/api/reservation/reservations",
                   json=payload,
                   headers={"Authorization": f"Bearer {user_token}"})
        
        # Admin lists all reservations
        res = client.get("/api/reservation/reservations",
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["reservations"]) >= 1
    
    def test_cancel_reservation(self, client, user_token, make_location):
        """Test canceling a reservation"""
        loc = make_location(total_slots=1)
        
        # Create reservation
        slots_res = client.get(f"/api/parking_slot/slots?location_id={loc['id']}")
        slot_id = slots_res.get_json()["slots"][0]["id"]
        
        start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        payload = {
            "slot_id": slot_id,
            "start_ts": start_time.isoformat(),
            "end_ts": (start_time + timedelta(hours=1)).isoformat()
        }
        create_res = client.post("/api/reservation/reservations",
                                json=payload,
                                headers={"Authorization": f"Bearer {user_token}"})
        reservation_id = create_res.get_json()["reservation"]["id"]
        
        # Cancel reservation
        res = client.post(f"/api/reservation/reservations/{reservation_id}/cancel",
                         headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["reservation"]["status"] == "cancelled"
    
    def test_update_reservation(self, client, user_token, make_location):
        """Test updating a reservation"""
        loc = make_location(total_slots=2)
        
        # Create reservation
        slots_res = client.get(f"/api/parking_slot/slots?location_id={loc['id']}")
        slot_id = slots_res.get_json()["slots"][0]["id"]
        
        start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        payload = {
            "slot_id": slot_id,
            "start_ts": start_time.isoformat(),
            "end_ts": (start_time + timedelta(hours=1)).isoformat()
        }
        create_res = client.post("/api/reservation/reservations",
                                json=payload,
                                headers={"Authorization": f"Bearer {user_token}"})
        reservation_id = create_res.get_json()["reservation"]["id"]
        
        # Update reservation
        new_end_time = start_time + timedelta(hours=2)
        update_payload = {
            "end_ts": new_end_time.isoformat()
        }
        res = client.put(f"/api/reservation/reservations/{reservation_id}",
                        json=update_payload,
                        headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 200
    
    def test_delete_reservation(self, client, user_token, make_location):
        """Test deleting a reservation"""
        loc = make_location(total_slots=1)
        
        # Create reservation
        slots_res = client.get(f"/api/parking_slot/slots?location_id={loc['id']}")
        slot_id = slots_res.get_json()["slots"][0]["id"]
        
        start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        payload = {
            "slot_id": slot_id,
            "start_ts": start_time.isoformat(),
            "end_ts": (start_time + timedelta(hours=1)).isoformat()
        }
        create_res = client.post("/api/reservation/reservations",
                                json=payload,
                                headers={"Authorization": f"Bearer {user_token}"})
        reservation_id = create_res.get_json()["reservation"]["id"]
        
        # Delete reservation
        res = client.delete(f"/api/reservation/reservations/{reservation_id}",
                           headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 204
        
        # Verify deletion
        res = client.get(f"/api/reservation/reservations/{reservation_id}",
                        headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 404
    
    def test_unauthorized_access_to_others_reservation(self, client, admin_token, user_token, make_location):
        """Test user cannot access another user's reservation"""
        loc = make_location(total_slots=1)
        
        # Admin creates a reservation
        slots_res = client.get(f"/api/parking_slot/slots?location_id={loc['id']}")
        slot_id = slots_res.get_json()["slots"][0]["id"]
        
        start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        payload = {
            "slot_id": slot_id,
            "start_ts": start_time.isoformat(),
            "end_ts": (start_time + timedelta(hours=1)).isoformat()
        }
        create_res = client.post("/api/reservation/reservations",
                                json=payload,
                                headers={"Authorization": f"Bearer {admin_token}"})
        reservation_id = create_res.get_json()["reservation"]["id"]
        
        # Regular user tries to access admin's reservation
        res = client.get(f"/api/reservation/reservations/{reservation_id}",
                        headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 403