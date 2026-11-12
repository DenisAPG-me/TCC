import copy

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 30

VALID_USERNAME = "admin"
VALID_PASSWORD = "password123"

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

ORIGINAL_BOOKING = {
    "firstname": "Maria",
    "lastname": "Silva",
    "totalprice": 150,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-15"},
    "additionalneeds": "Breakfast",
}

UPDATED_BOOKING = {
    "firstname": "Joana",
    "lastname": "Souza",
    "totalprice": 320,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-15"},
    "additionalneeds": "Breakfast",
}

NEW_LASTNAME = "Oliveira"


def authenticate(http, username, password):
    return http.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
        timeout=TIMEOUT,
    )


def auth_headers(token):
    return {"Cookie": f"token={token}"}


def booking_url(booking_id):
    return f"{BASE_URL}/booking/{booking_id}"


@pytest.fixture
def http():
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    yield session
    session.close()


@pytest.fixture
def token(http):
    response = authenticate(http, VALID_USERNAME, VALID_PASSWORD)
    assert response.status_code == 200
    value = response.json().get("token")
    assert value
    return value


@pytest.fixture
def booking_id(http, token):
    response = http.post(f"{BASE_URL}/booking", json=ORIGINAL_BOOKING, timeout=TIMEOUT)
    assert response.status_code == 200
    created_id = response.json()["bookingid"]
    yield created_id
    http.delete(booking_url(created_id), headers=auth_headers(token), timeout=TIMEOUT)


def test_TC01_autenticacao_com_credenciais_validas(http):
    response = authenticate(http, VALID_USERNAME, VALID_PASSWORD)

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("token"), str)
    assert body["token"].strip() != ""


def test_TC02_autenticacao_com_senha_invalida(http):
    response = authenticate(http, VALID_USERNAME, "senha_errada")

    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_TC03_autenticacao_com_usuario_inexistente(http):
    response = authenticate(http, "usuario_inexistente", VALID_PASSWORD)

    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_TC04_autenticacao_com_credenciais_vazias(http):
    response = authenticate(http, "", "")

    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_TC05_atualizacao_completa_com_novo_nome_e_preco(http, token, booking_id):
    response = http.put(
        booking_url(booking_id),
        json=UPDATED_BOOKING,
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["firstname"] == UPDATED_BOOKING["firstname"]
    assert body["lastname"] == UPDATED_BOOKING["lastname"]
    assert body["totalprice"] == UPDATED_BOOKING["totalprice"]
    assert body == UPDATED_BOOKING


def test_TC06_atualizacao_completa_persiste_novos_valores(http, token, booking_id):
    update = http.put(
        booking_url(booking_id),
        json=UPDATED_BOOKING,
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )
    assert update.status_code == 200

    response = http.get(booking_url(booking_id), timeout=TIMEOUT)

    assert response.status_code == 200
    body = response.json()
    assert body["firstname"] == UPDATED_BOOKING["firstname"]
    assert body["lastname"] == UPDATED_BOOKING["lastname"]
    assert body["totalprice"] == UPDATED_BOOKING["totalprice"]


def test_TC07_atualizacao_parcial_apenas_do_sobrenome(http, token, booking_id):
    response = http.patch(
        booking_url(booking_id),
        json={"lastname": NEW_LASTNAME},
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )

    assert response.status_code == 200
    expected = copy.deepcopy(ORIGINAL_BOOKING)
    expected["lastname"] = NEW_LASTNAME
    assert response.json() == expected


def test_TC08_atualizacao_parcial_persiste_e_preserva_demais_campos(http, token, booking_id):
    update = http.patch(
        booking_url(booking_id),
        json={"lastname": NEW_LASTNAME},
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )
    assert update.status_code == 200

    response = http.get(booking_url(booking_id), timeout=TIMEOUT)

    assert response.status_code == 200
    expected = copy.deepcopy(ORIGINAL_BOOKING)
    expected["lastname"] = NEW_LASTNAME
    assert response.json() == expected


def test_TC09_atualizacao_completa_sem_token(http, booking_id):
    response = http.put(booking_url(booking_id), json=UPDATED_BOOKING, timeout=TIMEOUT)

    assert response.status_code == 403


def test_TC10_atualizacao_parcial_sem_token(http, booking_id):
    response = http.patch(
        booking_url(booking_id),
        json={"lastname": NEW_LASTNAME},
        timeout=TIMEOUT,
    )

    assert response.status_code == 403


def test_TC11_atualizacao_completa_com_token_invalido(http, booking_id):
    response = http.put(
        booking_url(booking_id),
        json=UPDATED_BOOKING,
        headers=auth_headers("token_invalido_123"),
        timeout=TIMEOUT,
    )

    assert response.status_code == 403


def test_TC12_atualizacao_completa_sem_firstname(http, token, booking_id):
    payload = copy.deepcopy(UPDATED_BOOKING)
    del payload["firstname"]

    response = http.put(
        booking_url(booking_id),
        json=payload,
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )

    assert response.status_code == 400


def test_TC13_atualizacao_completa_sem_bookingdates(http, token, booking_id):
    payload = copy.deepcopy(UPDATED_BOOKING)
    del payload["bookingdates"]

    response = http.put(
        booking_url(booking_id),
        json=payload,
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )

    assert response.status_code == 400


def test_TC14_atualizacao_completa_com_corpo_vazio(http, token, booking_id):
    response = http.put(
        booking_url(booking_id),
        json={},
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )

    assert response.status_code == 400
