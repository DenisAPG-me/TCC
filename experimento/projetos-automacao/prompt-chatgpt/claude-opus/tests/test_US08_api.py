import copy
import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 30

AUTH_ENDPOINT = "/auth"
BOOKING_ENDPOINT = "/booking"

VALID_USERNAME = "admin"
VALID_PASSWORD = "password123"
INVALID_PASSWORD = "senha_invalida_123"
BAD_CREDENTIALS_REASON = "Bad credentials"

JSON_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

BASE_BOOKING = {
    "firstname": "Carlos",
    "lastname": "Silva",
    "totalprice": 150,
    "depositpaid": True,
    "bookingdates": {
        "checkin": "2026-11-10",
        "checkout": "2026-11-15",
    },
    "additionalneeds": "Breakfast",
}


def url(path):
    return f"{BASE_URL}{path}"


def booking_url(booking_id):
    return url(f"{BOOKING_ENDPOINT}/{booking_id}")


def authenticate(username, password):
    return requests.post(
        url(AUTH_ENDPOINT),
        json={"username": username, "password": password},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )


def auth_headers(token):
    return {**JSON_HEADERS, "Cookie": f"token={token}"}


def get_booking(booking_id):
    response = requests.get(booking_url(booking_id), headers=JSON_HEADERS, timeout=TIMEOUT)
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture
def token():
    response = authenticate(VALID_USERNAME, VALID_PASSWORD)
    assert response.status_code == 200, response.text
    value = response.json().get("token")
    assert isinstance(value, str) and value, response.text
    return value


@pytest.fixture
def booking(token):
    payload = copy.deepcopy(BASE_BOOKING)
    payload["firstname"] = f"Carlos{uuid.uuid4().hex[:8]}"
    response = requests.post(url(BOOKING_ENDPOINT), json=payload, headers=JSON_HEADERS, timeout=TIMEOUT)
    assert response.status_code == 200, response.text
    body = response.json()
    booking_id = body["bookingid"]
    assert body["booking"] == payload
    yield booking_id, payload
    delete_response = requests.delete(booking_url(booking_id), headers=auth_headers(token), timeout=TIMEOUT)
    assert delete_response.status_code == 201, delete_response.text


def test_CT001_autenticar_com_credenciais_validas():
    response = authenticate(VALID_USERNAME, VALID_PASSWORD)

    assert response.status_code == 200
    body = response.json()
    assert "token" in body
    assert isinstance(body["token"], str)
    assert body["token"].strip() != ""


def test_CT002_autenticar_com_senha_incorreta():
    response = authenticate(VALID_USERNAME, INVALID_PASSWORD)

    body = response.json()
    assert "token" not in body
    assert body.get("reason") == BAD_CREDENTIALS_REASON


def test_CT003_autenticar_com_usuario_e_senha_vazios():
    response = authenticate("", "")

    body = response.json()
    assert "token" not in body
    assert body.get("reason") == BAD_CREDENTIALS_REASON


def test_CT004_atualizacao_completa_com_novo_nome_e_novo_preco(booking, token):
    booking_id, original = booking
    updated = copy.deepcopy(original)
    updated["firstname"] = "Mariana"
    updated["lastname"] = "Souza"
    updated["totalprice"] = original["totalprice"] + 250

    response = requests.put(booking_url(booking_id), json=updated, headers=auth_headers(token), timeout=TIMEOUT)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["firstname"] == "Mariana"
    assert body["lastname"] == "Souza"
    assert body["totalprice"] == updated["totalprice"]
    assert body == updated


def test_CT005_atualizacao_parcial_apenas_do_sobrenome(booking, token):
    booking_id, original = booking
    new_lastname = "Oliveira"

    response = requests.patch(
        booking_url(booking_id),
        json={"lastname": new_lastname},
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["lastname"] == new_lastname
    assert body["lastname"] != original["lastname"]
    expected = copy.deepcopy(original)
    expected["lastname"] = new_lastname
    assert body == expected


def test_CT006_atualizacao_completa_sem_token(booking):
    booking_id, original = booking
    updated = copy.deepcopy(original)
    updated["firstname"] = "SemToken"
    updated["totalprice"] = original["totalprice"] + 100

    response = requests.put(booking_url(booking_id), json=updated, headers=JSON_HEADERS, timeout=TIMEOUT)

    assert response.status_code == 403, response.text
    assert get_booking(booking_id) == original


def test_CT007_atualizacao_parcial_sem_token(booking):
    booking_id, original = booking

    response = requests.patch(
        booking_url(booking_id),
        json={"lastname": "SemToken"},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )

    assert response.status_code == 403, response.text
    assert get_booking(booking_id) == original


def test_CT008_atualizacao_completa_sem_firstname_e_totalprice(booking, token):
    booking_id, original = booking
    incomplete = copy.deepcopy(original)
    del incomplete["firstname"]
    del incomplete["totalprice"]

    response = requests.put(booking_url(booking_id), json=incomplete, headers=auth_headers(token), timeout=TIMEOUT)

    assert response.status_code == 400, response.text


def test_CT009_atualizacao_completa_com_corpo_vazio(booking, token):
    booking_id, _ = booking

    response = requests.put(booking_url(booking_id), json={}, headers=auth_headers(token), timeout=TIMEOUT)

    assert response.status_code == 400, response.text
