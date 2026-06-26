import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Arrange: preserve and restore the in-memory activities between tests."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_root_redirects():
    # Arrange
    # (client is already arranged)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert "/static/index.html" in response.headers.get("location", "")


def test_get_all_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_for_activity_success():
    # Arrange
    activity = "Chess Club"
    email = "test@example.com"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "Signed up" in body.get("message", "")
    assert email in activities[activity]["participants"]


def test_signup_duplicate_error():
    # Arrange
    activity = "Chess Club"
    existing_email = "michael@mergington.edu"
    assert existing_email in activities[activity]["participants"]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json().get("detail") == "Student already signed up"


def test_signup_nonexistent_activity():
    # Arrange
    activity = "Nonexistent"
    email = "test@example.com"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_unregister_from_activity_success():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    assert email in activities[activity]["participants"]

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert "Unregistered" in response.json().get("message", "")
    assert email not in activities[activity]["participants"]


def test_unregister_not_signed_up():
    # Arrange
    activity = "Chess Club"
    email = "nobody@example.com"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json().get("detail") == "Student not signed up"
