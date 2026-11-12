import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"


@pytest.fixture(scope="session")
def auth_token():
    payload = {"username": "admin", "password": "password123"}
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/auth", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    token = data.get("token")
    assert token is not None and token != ""
    return token


@pytest.fixture(scope="function")
def existing_booking_id(auth_token):
    # Create a booking to use in tests
    payload = {
        "firstname": "Jim",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {"checkin": "2018-01-01", "checkout": "2019-01-01"},
        "additionalneeds": "Breakfast",
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"token={auth_token}",
    }
    response = requests.post(f"{BASE_URL}/booking", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    return data["bookingid"]


def test_CT01_autenticacao_valida():
    payload = {"username": "admin", "password": "password123"}
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/auth", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] != ""


def test_CT02_autenticacao_invalida():
    payload = {"username": "invalid", "password": "wrongpassword"}
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/auth", json=payload, headers=headers)
    data = response.json()
    assert "token" not in data or data.get("token") is None
    assert data.get("reason") == "Bad credentials"


def test_CT03_atualizacao_completa_valida(auth_token, existing_booking_id):
    payload = {
        "firstname": "James",
        "lastname": "Smith",
        "totalprice": 222,
        "depositpaid": False,
        "bookingdates": {"checkin": "2020-01-01", "checkout": "2021-01-01"},
        "additionalneeds": "Lunch",
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"token={auth_token}",
    }
    response = requests.put(
        f"{BASE_URL}/booking/{existing_booking_id}",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["firstname"] == "James"
    assert data["totalprice"] == 222


def test_CT04_atualizacao_parcial_valida(auth_token, existing_booking_id):
    payload = {"lastname": "Johnson"}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"token={auth_token}",
    }
    response = requests.patch(
        f"{BASE_URL}/booking/{existing_booking_id}",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["lastname"] == "Johnson"
    # Ensure other fields remain intact
    assert "firstname" in data


def test_CT05_atualizacao_sem_token(existing_booking_id):
    payload = {
        "firstname": "Unauthorized",
        "lastname": "User",
        "totalprice": 100,
        "depositpaid": True,
        "bookingdates": {"checkin": "2021-01-01", "checkout": "2022-01-01"},
        "additionalneeds": "None",
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.put(
        f"{BASE_URL}/booking/{existing_booking_id}",
        json=payload,
        headers=headers,
    )
    assert response.status_code in [401, 403]


def test_CT06_atualizacao_completa_campos_ausentes(
    auth_token, existing_booking_id
):
    payload = {
        "firstname": "Incomplete"
        # Missing required fields like lastname, totalprice, bookingdates
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"token={auth_token}",
    }
    response = requests.put(
        f"{BASE_URL}/booking/{existing_booking_id}",
        json=payload,
        headers=headers,
    )
    assert response.status_code in [400, 500]
