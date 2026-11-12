import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"
TIMEOUT = 30


def build_booking():
    return {
        "firstname": f"Tester{uuid.uuid4().hex[:8]}",
        "lastname": f"Silva{uuid.uuid4().hex[:8]}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-05"},
        "additionalneeds": "Breakfast",
    }


def create_booking(booking=None):
    booking = booking or build_booking()
    response = requests.post(f"{BASE_URL}/booking", json=booking, timeout=TIMEOUT)
    assert response.status_code == 200, response.text
    body = response.json()
    return body["bookingid"], body["booking"]


def get_token():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, response.text
    return response.json()["token"]


def get_booking(booking_id):
    return requests.get(f"{BASE_URL}/booking/{booking_id}", timeout=TIMEOUT)


def delete_booking(booking_id, token=None):
    headers = {} if token is None else {"Cookie": f"token={token}"}
    return requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers, timeout=TIMEOUT)


def test_TC01_delete_without_token_returns_403_and_booking_remains():
    booking_id, _ = create_booking()

    response = delete_booking(booking_id)

    assert response.status_code == 403
    assert get_booking(booking_id).status_code == 200


def test_TC02_delete_with_invalid_token_returns_403_and_booking_remains():
    booking_id, _ = create_booking()

    response = delete_booking(booking_id, token="invalid-token-123")

    assert response.status_code == 403
    assert get_booking(booking_id).status_code == 200


def test_TC03_delete_with_valid_token_returns_201():
    token = get_token()
    booking_id, _ = create_booking()

    response = delete_booking(booking_id, token=token)

    assert response.status_code == 201


def test_TC04_get_deleted_booking_returns_404():
    token = get_token()
    booking_id, _ = create_booking()
    assert delete_booking(booking_id, token=token).status_code == 201

    response = get_booking(booking_id)

    assert response.status_code == 404


def test_TC05_delete_already_deleted_booking_returns_4xx_and_other_booking_unaffected():
    token = get_token()
    booking_a_id, _ = create_booking()
    booking_b_id, booking_b = create_booking()
    assert delete_booking(booking_a_id, token=token).status_code == 201

    response = delete_booking(booking_a_id, token=token)

    assert 400 <= response.status_code < 500
    other = get_booking(booking_b_id)
    assert other.status_code == 200
    assert other.json()["firstname"] == booking_b["firstname"]
    assert other.json()["lastname"] == booking_b["lastname"]


def test_TC06_list_by_unique_name_is_empty_after_delete():
    token = get_token()
    booking_id, booking = create_booking()
    params = {"firstname": booking["firstname"], "lastname": booking["lastname"]}
    before = requests.get(f"{BASE_URL}/booking", params=params, timeout=TIMEOUT)
    assert {"bookingid": booking_id} in before.json()
    assert delete_booking(booking_id, token=token).status_code == 201

    response = requests.get(f"{BASE_URL}/booking", params=params, timeout=TIMEOUT)

    assert response.status_code == 200
    assert response.json() == []


def test_TC07_delete_with_empty_token_returns_403_and_booking_remains():
    booking_id, _ = create_booking()

    response = delete_booking(booking_id, token="")

    assert response.status_code == 403
    assert get_booking(booking_id).status_code == 200


def test_TC08_delete_nonexistent_booking_returns_4xx():
    token = get_token()

    response = delete_booking(999999999, token=token)

    assert 400 <= response.status_code < 500


def test_TC09_delete_after_invalid_credentials_returns_403_and_booking_remains():
    booking_id, _ = create_booking()
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": ADMIN_USERNAME, "password": "wrong-password"},
        timeout=TIMEOUT,
    )
    assert "token" not in response.json()

    delete_response = delete_booking(booking_id)

    assert delete_response.status_code == 403
    assert get_booking(booking_id).status_code == 200
