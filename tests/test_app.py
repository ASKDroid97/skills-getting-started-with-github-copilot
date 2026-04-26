import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesAPI:
    """Test suite for the Mergington High School Activities API"""

    def test_get_activities(self):
        # Arrange: No special setup needed as data is in-memory

        # Act: Make GET request to /activities
        response = client.get("/activities")

        # Assert: Check status and response structure
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "description" in data["Chess Club"]
        assert "participants" in data["Chess Club"]

    def test_signup_success(self):
        # Arrange: Ensure the activity exists and email not signed up
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data["Programming Class"]["participants"])

        # Act: Sign up a new student
        response = client.post("/activities/Programming%20Class/signup?email=newstudent@mergington.edu")

        # Assert: Check success response and participant added
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

        # Verify participant was added
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        assert len(updated_data["Programming Class"]["participants"]) == initial_count + 1
        assert "newstudent@mergington.edu" in updated_data["Programming Class"]["participants"]

    def test_signup_duplicate(self):
        # Arrange: Sign up a student first
        client.post("/activities/Gym%20Class/signup?email=duplicate@mergington.edu")

        # Act: Try to sign up the same student again
        response = client.post("/activities/Gym%20Class/signup?email=duplicate@mergington.edu")

        # Assert: Check error response
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_invalid_activity(self):
        # Arrange: No setup needed

        # Act: Try to sign up for non-existent activity
        response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")

        # Assert: Check 404 error
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_delete_success(self):
        # Arrange: Sign up a student first
        client.post("/activities/Soccer%20Club/signup?email=deletetest@mergington.edu")

        # Act: Delete the student
        response = client.delete("/activities/Soccer%20Club/signup?email=deletetest@mergington.edu")

        # Assert: Check success response
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

        # Verify participant was removed
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        assert "deletetest@mergington.edu" not in updated_data["Soccer Club"]["participants"]

    def test_delete_not_signed_up(self):
        # Arrange: No setup needed

        # Act: Try to delete a student not signed up
        response = client.delete("/activities/Art%20Club/signup?email=notsignedup@mergington.edu")

        # Assert: Check 404 error
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"]

    def test_delete_invalid_activity(self):
        # Arrange: No setup needed

        # Act: Try to delete from non-existent activity
        response = client.delete("/activities/InvalidActivity/signup?email=test@mergington.edu")

        # Assert: Check 404 error
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]