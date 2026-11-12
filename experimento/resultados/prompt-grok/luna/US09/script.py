import uuid

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 15


def unique_names():
    suffix = uuid.uuid4().hex
    return f"QA{suffix}", f"Test{suffix}"


def create_booking(firstname, lastname):
    response = requests.post(
        f"{BASE_URL}/booking",
        json={
            "firstname": firstname,
            "lastname": lastname,
            "totalprice": 123,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2027-01-01",
                "checkout": "2027-01-05",
            },
            "additionalneeds": "QA test",
        },
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, response.text
    booking_id = response.json()["bookingid"]
    return booking_id


def get_token():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": "admin", "password": "password123"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, response.text
    token = response.json().get("token")
    assert token, response.text
    return token


def delete_booking(booking_id, token=None):
    headers = {}
    if token is not None:
        headers["Cookie"] = f"token={token}"
    return requests.delete(
        f"{BASE_URL}/booking/{booking_id}",
        headers=headers,
        timeout=TIMEOUT,
    )


def booking_exists(booking_id):
    return requests.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=TIMEOUT,
    )


def test_TC01_delete_without_token_returns_403_and_booking_remains():
    firstname, lastname = unique_names()
    booking_id = create_booking(firstname, lastname)

    delete_response = delete_booking(booking_id)
    assert delete_response.status_code == 403

    get_response = booking_exists(booking_id)
    assert get_response.status_code == 200


def test_TC02_delete_with_invalid_token_returns_403_and_booking_remains():
    firstname, lastname = unique_names()
    booking_id = create_booking(firstname, lastname)

    delete_response = delete_booking(booking_id, token="invalid-token")
    assert delete_response.status_code == 403

    get_response = booking_exists(booking_id)
    assert get_response.status_code == 200


def test_TC03_delete_with_valid_token_returns_201_and_booking_is_gone():
    firstname, lastname = unique_names()
    booking_id = create_booking(firstname, lastname)
    token = get_token()

    delete_response = delete_booking(booking_id, token=token)
    assert delete_response.status_code == 201

    get_response = booking_exists(booking_id)
    assert get_response.status_code == 404


def test_TC04_repeated_delete_returns_4xx_without_affecting_other_booking():
    token = get_token()
    first_id = create_booking(*unique_names())
    second_id = create_booking(*unique_names())

    first_delete = delete_booking(first_id, token=token)
    assert first_delete.status_code == 201

    repeated_delete = delete_booking(first_id, token=token)
    assert 400 <= repeated_delete.status_code < 500

    unaffected_booking = booking_exists(second_id)
    assert unaffected_booking.status_code == 200


def test_TC05_listing_by_unique_name_is_empty_after_deletion():
    firstname, lastname = unique_names()
    booking_id = create_booking(firstname, lastname)
    token = get_token()

    delete_response = delete_booking(booking_id, token=token)
    assert delete_response.status_code == 201

    list_response = requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": firstname, "lastname": lastname},
        timeout=TIMEOUT,
    )
    assert list_response.status_code == 200
    assert list_response.json() == []
