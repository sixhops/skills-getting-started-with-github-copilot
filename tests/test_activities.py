"""
Tests for the activities API endpoints.
"""

import pytest


class TestGetActivities:
    """Test the GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that get_activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Tennis Club" in activities
        assert "Basketball Team" in activities
        assert "Chess Club" in activities
        
    def test_get_activities_includes_details(self, client):
        """Test that activities include all required details."""
        response = client.get("/activities")
        activities = response.json()
        
        tennis_club = activities["Tennis Club"]
        assert "description" in tennis_club
        assert "schedule" in tennis_club
        assert "max_participants" in tennis_club
        assert "participants" in tennis_club
        assert isinstance(tennis_club["participants"], list)
        
    def test_get_activities_includes_existing_participants(self, client):
        """Test that activities show existing participants."""
        response = client.get("/activities")
        activities = response.json()
        
        assert "alex@mergington.edu" in activities["Tennis Club"]["participants"]
        assert "james@mergington.edu" in activities["Basketball Team"]["participants"]


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Tennis Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Tennis Club" in data["message"]
        
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant."""
        client.post(
            "/activities/Tennis Club/signup?email=newstudent@mergington.edu"
        )
        
        response = client.get("/activities")
        activities = response.json()
        
        assert "newstudent@mergington.edu" in activities["Tennis Club"]["participants"]
        
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist."""
        response = client.post(
            "/activities/Fake Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]
        
    def test_signup_duplicate_student(self, client):
        """Test that a student cannot sign up twice for the same activity."""
        # Student already signed up for Tennis Club
        response = client.post(
            "/activities/Tennis Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]
        
    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple different students can sign up."""
        client.post(
            "/activities/Tennis Club/signup?email=student1@mergington.edu"
        )
        client.post(
            "/activities/Tennis Club/signup?email=student2@mergington.edu"
        )
        
        response = client.get("/activities")
        activities = response.json()
        participants = activities["Tennis Club"]["participants"]
        
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants
        assert len(participants) == 3  # 1 original + 2 new


class TestUnregisterFromActivity:
    """Test the POST /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity."""
        response = client.post(
            "/activities/Tennis Club/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "alex@mergington.edu" in data["message"]
        
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant."""
        client.post(
            "/activities/Tennis Club/unregister?email=alex@mergington.edu"
        )
        
        response = client.get("/activities")
        activities = response.json()
        
        assert "alex@mergington.edu" not in activities["Tennis Club"]["participants"]
        
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist."""
        response = client.post(
            "/activities/Fake Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]
        
    def test_unregister_not_signed_up_student(self, client):
        """Test that a student not signed up cannot unregister."""
        response = client.post(
            "/activities/Tennis Club/unregister?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "not signed up" in data["detail"]
        
    def test_unregister_then_signup_again(self, client):
        """Test that a student can sign up again after unregistering."""
        # Unregister
        client.post(
            "/activities/Tennis Club/unregister?email=alex@mergington.edu"
        )
        
        # Sign up again should work
        response = client.post(
            "/activities/Tennis Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        activities = response.json()
        assert "alex@mergington.edu" in activities["Tennis Club"]["participants"]


class TestRoot:
    """Test the root endpoint."""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static index."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
