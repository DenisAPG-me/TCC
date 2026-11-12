import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 15


def _authenticate(username="admin", password="password123"):
    return requests.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
        timeout=TIMEOUT,
    )


def _create_booking():
    payload = {
        "firstname": "Ana",
        "lastname": "Silva",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-11-01",
            "checkout": "2026-11-05",
        },
        "additionalneeds": "Breakfast",
    }
    response = requests.post(
        f"{BASE_URL}/booking",
        json=payload,
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    booking_id = response.json().get("bookingid")
    assert booking_id is not None
    return booking_id, payload


def test_TC01_authenticate_with_valid_credentials():
    response = _authenticate()
    assert response.status_code == 200
    assert response.json().get("token")


def test_TC02_authenticate_with_invalid_credentials():
    response = _authenticate("admin", "wrong-password")
    body = response.json()
    assert "token" not in body or not body["token"]
    assert body.get("reason") == "Bad credentials"


def test_TC03_full_update_with_valid_token():
    booking_id, _ = _create_booking()
    auth_response = _authenticate()
    assert auth_response.status_code == 200
    token = auth_response.json()["token"]

    payload = {
        "firstname": "Marina",
        "lastname": "Oliveira",
        "totalprice": 275,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2026-12-10",
            "checkout": "2026-12-15",
        },
        "additionalneeds": "Lunch",
    }
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=payload,
        headers={"Cookie": f"token={token}"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["firstname"] == payload["firstname"]
    assert body["totalprice"] == payload["totalprice"]


def test_TC04_partial_update_lastname_preserves_other_fields():
    booking_id, original = _create_booking()
    auth_response = _authenticate()
    assert auth_response.status_code == 200
    token = auth_response.json()["token"]

    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json={"lastname": "Santos"},
        headers={"Cookie": f"token={token}"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["lastname"] == "Santos"
    for field in ("firstname", "totalprice", "depositpaid", "bookingdates", "additionalneeds"):
        assert body[field] == original[field]


def test_TC05_update_without_token_is_forbidden():
    booking_id, payload = _create_booking()
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=payload,
        timeout=TIMEOUT,
    )
    assert response.status_code == 403


def test_TC06_full_update_missing_required_fields_returns_400():
    booking_id, _ = _create_booking()
    auth_response = _authenticate()
    assert auth_response.status_code == 200
    token = auth_response.json()["token"]

    incomplete_payload = {
        "lastname": "Incomplete",
        "totalprice": 200,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-12-10",
            "checkout": "2026-12-15",
        },
        "additionalneeds": "None",
    }
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=incomplete_payload,
        headers={"Cookie": f"token={token}"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 400
