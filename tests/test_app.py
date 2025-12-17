import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivities:
    """Test activities endpoint"""
    
    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities


class TestSignup:
    """Test signup endpoint"""
    
    def test_signup_for_activity(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert "test@mergington.edu" in response.json()["message"]
    
    def test_signup_duplicate_email(self):
        """Test that duplicate signup is rejected"""
        # First signup
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        # Try duplicate signup
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_full_activity(self):
        """Test signup for full activity"""
        # Get an activity with max capacity
        activities = client.get("/activities").json()
        
        # Find an activity with small capacity
        full_activity = None
        for name, details in activities.items():
            if details["max_participants"] == len(details["participants"]):
                full_activity = name
                break
        
        if full_activity:
            response = client.post(
                f"/activities/{full_activity}/signup",
                params={"email": "full@mergington.edu"}
            )
            assert response.status_code == 400
            assert "full" in response.json()["detail"]


class TestUnregister:
    """Test unregister endpoint"""
    
    def test_unregister_participant(self):
        """Test successful unregistration"""
        # First, sign up
        client.post(
            "/activities/Basketball/signup",
            params={"email": "unregister_test@mergington.edu"}
        )
        # Then unregister
        response = client.delete(
            "/activities/Basketball/unregister",
            params={"email": "unregister_test@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_nonexistent_activity(self):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_unregister_not_registered(self):
        """Test unregister when not registered"""
        response = client.delete(
            "/activities/Tennis/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]


class TestRoot:
    """Test root endpoint"""
    
    def test_root_redirect(self):
        """Test that root redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
