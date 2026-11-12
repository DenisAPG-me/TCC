import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
ADMIN_USER = "admin"
ADMIN_PASS = "password123"
INVALID_USER = "invalid"
INVALID_PASS = "wrong"
TIMEOUT = 10


@pytest.fixture
def auth_token():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": ADMIN_USER, "password": ADMIN_PASS},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    data = response.json()
    token = data.get("token")
    assert token is not None
    assert len(str(token)) > 0
    return token


@pytest.fixture
def existing_booking_id(auth_token):
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "totalprice": 100,
        "depositpaid": True,
        "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-01-10"},
        "additionalneeds": "SuperBowl",
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.post(f"{BASE_URL}/booking", json=payload, headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200
    booking_id = response.json().get("bookingid")
    assert booking_id is not None
    return booking_id


def test_ct01_login_com_credenciais_validas():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": ADMIN_USER, "password": ADMIN_PASS},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    data = response.json()
    token = data.get("token")
    assert token is not None
    assert len(str(token)) > 0


def test_ct02_login_com_credenciais_invalidas():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": INVALID_USER, "password": INVALID_PASS},
        timeout=TIMEOUT,
    )
    data = response.json()
    assert "token" not in data
    assert data.get("reason") == "Bad credentials"


def test_ct03_atualizacao_completa_reserva_token_valido(auth_token, existing_booking_id):
    updated_payload = {
        "firstname": "James",
        "lastname": "Brown",
        "totalprice": 250,
        "depositpaid": True,
        "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-01-10"},
        "additionalneeds": "Breakfast",
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"token={auth_token}",
    }
    response = requests.put(
        f"{BASE_URL}/booking/{existing_booking_id}",
        json=updated_payload,
        headers=headers,
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("firstname") == "James"
    assert data.get("totalprice") == 250


def test_ct04_atualizacao_parcial_sobrenome_token_valido(auth_token, existing_booking_id):
    partial_payload = {"lastname": "Smith"}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"token={auth_token}",
    }
    response = requests.patch(
        f"{BASE_URL}/booking/{existing_booking_id}",
        json=partial_payload,
        headers=headers,
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("lastname") == "Smith"
    assert data.get("firstname") == "John"
    assert data.get("totalprice") == 100


def test_ct05_tentar_atualizar_reserva_sem_token(existing_booking_id):
    updated_payload = {
        "firstname": "James",
        "lastname": "Brown",
        "totalprice": 250,
        "depositpaid": True,
        "bookingdates": {"checkin": "2023-01-01", "checkout": "2023-01-10"},
        "additionalneeds": "Breakfast",
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.put(
        f"{BASE_URL}/booking/{existing_booking_id}",
        json=updated_payload,
        headers=headers,
        timeout=TIMEOUT,
    )
    assert response.status_code == 403


def test_ct06_atualizacao_completa_campos_obrigatorios_ausentes(auth_token, existing_booking_id):
    invalid_payload = {"additionalneeds": "Dinner"}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"token={auth_token}",
    }
    response = requests.put(
        f"{BASE_URL}/booking/{existing_booking_id}",
        json=invalid_payload,
        headers=headers,
        timeout=TIMEOUT,
    )
    assert response.status_code == 400
