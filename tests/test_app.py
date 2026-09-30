import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Test Club"
EXISTING_EMAIL = "already@example.edu"
NEW_EMAIL = "new@example.edu"


@pytest.fixture
def activity_data(monkeypatch):
    test_activities = {
        ACTIVITY_NAME: {
            "description": "A test activity",
            "schedule": "Mondays",
            "max_participants": 5,
            "participants": [EXISTING_EMAIL],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return test_activities


@pytest.fixture
def client(activity_data):
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_details(client, activity_data):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activity_data


def test_signup_adds_participant(client, activity_data):
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": NEW_EMAIL}
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {NEW_EMAIL} for {ACTIVITY_NAME}"}
    assert NEW_EMAIL in activity_data[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_participant(client, activity_data):
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": EXISTING_EMAIL}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activity_data[ACTIVITY_NAME]["participants"] == [EXISTING_EMAIL]


def test_signup_rejects_unknown_activity(client):
    response = client.post("/activities/Unknown/signup", params={"email": NEW_EMAIL})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client, activity_data):
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": EXISTING_EMAIL}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {EXISTING_EMAIL} from {ACTIVITY_NAME}"
    }
    assert activity_data[ACTIVITY_NAME]["participants"] == []


def test_unregister_rejects_unknown_participant(client, activity_data):
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": NEW_EMAIL}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert activity_data[ACTIVITY_NAME]["participants"] == [EXISTING_EMAIL]


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown/signup", params={"email": EXISTING_EMAIL}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"