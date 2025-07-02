# ══════════════════════════════════════════════════════════════════════════════
# REPORTS ROUTES TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestReportsRoutes:
    """Test admin reports endpoints"""
    
    def test_reservations_per_day_admin(self, client, admin_token):
        """Test admin can access reservations per day report"""
        res = client.get("/api/reports/reservations-per-day",
                        headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert "data" in data
    
    # def test_reservations_per_day_with_days_param(self, client, admin_token):