import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"


@pytest.fixture
def api_client():
    return requests.Session()


@pytest.fixture
def auth_token(api_client):
    response = api_client.post(
        f"{BASE_URL}/auth",
        json={"username": "admin", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    return data.get("token")


@pytest.fixture
def existing_booking_id(api_client):
    payload = {
        "firstname": "Jim",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {"checkin": "2018-01-01", "checkout": "2019-01-01"},
        "additionalneeds": "Breakfast",
    }
    response = api_client.post(f"{BASE_URL}/booking", json=payload)
    assert response.status_code == 200
    return response.json().get("bookingid")


def test_TC01_successful_authentication(api_client):
    response = api_client.post(
        f"{BASE_URL}/auth",
        json={"username": "admin", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] is not None
    assert len(data["token"]) > 0


def test_TC02_invalid_authentication(api_client):
    response = api_client.post(
        f"{BASE_URL}/auth",
        json={"username": "invalid_user", "password": "wrongpassword"},
    )
    data = response.json()
    assert "token" not in data or data.get("token") is None
    reason = data.get("reason", "")
    assert reason == "Bad credentials"


def test_TC03_full_update_valid_token(api_client, auth_token, existing_booking_id):
    updated_payload = {
        "firstname": "JamesUpdated",
        "lastname": "BrownUpdated",
        "totalprice": 222,
        "depositpaid": True,
        "bookingdates": {"checkin": "2019-01-01", "checkout": "2020-01-01"},
        "additionalneeds": "Dinner",
    }
    headers = {"Cookie": f"token={auth_token}"}
    response = api_client.put(
        f"{BASE_URL}/booking/{existing_booking_id}",
        json=updated_payload,
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["firstname"] == "JamesUpdated"
    assert data["totalprice"] == 222


def test_TC04_partial_update_lastname_valid_token(
    api_client, auth_token, existing_booking_id
):
    partial_payload = {"lastname": "SmithPartial"}
    headers = {"Cookie": f"token={auth_token}"}
    response = api_client.patch(
        f"{BASE_URL}/booking/{existing_booking_id}",
        json=partial_payload,
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["lastname"] == "SmithPartial"
    assert data["firstname"] == "Jim"
    assert data["totalprice"] == 111


def test_TC05_update_without_token(api_client, existing_booking_id):
    updated_payload = {
        "firstname": "NoToken",
        "lastname": "User",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2020-01-01", "checkout": "2020-01-02"},
        "additionalneeds": "None",
    }
    response = api_client.put(
        f"{BASE_URL}/booking/{existing_booking_id}", json=updated_payload
    )
    assert response.status_code == 403


def test_TC06_full_update_missing_mandatory_fields(
    api_client, auth_token, existing_booking_id
):
    incomplete_payload = {
        "firstname": "Incomplete",
        "totalprice": 100,
    }
    headers = {"Cookie": f"token={auth_token}"}
    response = api_client.put(
        f"{BASE_URL}/booking/{existing_booking_id}",
        json=incomplete_payload,
        headers=headers,
    )
    assert response.status_code == 400
