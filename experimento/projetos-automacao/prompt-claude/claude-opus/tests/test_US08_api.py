import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
USERNAME = "admin"
PASSWORD = "password123"
INVALID_PASSWORD = "senha_errada"
INEXISTENT_USERNAME = "usuario_inexistente"
INVALID_TOKEN = "token_invalido_123"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

ORIGINAL_BOOKING = {
    "firstname": "Joao",
    "lastname": "Silva",
    "totalprice": 150,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-15"},
    "additionalneeds": "Breakfast",
}
NEW_FIRSTNAME = "Carlos"
NEW_TOTALPRICE = 275
NEW_LASTNAME = "Souza"
BAD_CREDENTIALS_REASON = "Bad credentials"


def authenticate(username, password):
    return requests.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
        headers=HEADERS,
        timeout=TIMEOUT,
    )


def auth_headers(token):
    return {**HEADERS, "Cookie": f"token={token}"}


def get_booking(booking_id):
    return requests.get(f"{BASE_URL}/booking/{booking_id}", headers=HEADERS, timeout=TIMEOUT)


def full_update_payload():
    return {**ORIGINAL_BOOKING, "firstname": NEW_FIRSTNAME, "totalprice": NEW_TOTALPRICE}


@pytest.fixture
def token():
    response = authenticate(USERNAME, PASSWORD)
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def booking_id(token):
    response = requests.post(f"{BASE_URL}/booking", json=ORIGINAL_BOOKING, headers=HEADERS, timeout=TIMEOUT)
    assert response.status_code == 200
    created_id = response.json()["bookingid"]
    yield created_id
    requests.delete(f"{BASE_URL}/booking/{created_id}", headers=auth_headers(token), timeout=TIMEOUT)


def test_ct01_autenticacao_com_credenciais_validas():
    response = authenticate(USERNAME, PASSWORD)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("token"), str)
    assert body["token"].strip() != ""


def test_ct02_autenticacao_com_senha_invalida():
    body = authenticate(USERNAME, INVALID_PASSWORD).json()
    assert "token" not in body
    assert body.get("reason") == BAD_CREDENTIALS_REASON


def test_ct03_autenticacao_com_usuario_inexistente():
    body = authenticate(INEXISTENT_USERNAME, PASSWORD).json()
    assert "token" not in body
    assert body.get("reason") == BAD_CREDENTIALS_REASON


def test_ct04_autenticacao_com_credenciais_vazias():
    body = authenticate("", "").json()
    assert "token" not in body
    assert body.get("reason") == BAD_CREDENTIALS_REASON


def test_ct05_atualizacao_completa_com_novo_nome_e_preco(token, booking_id):
    payload = full_update_payload()
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}", json=payload, headers=auth_headers(token), timeout=TIMEOUT
    )
    assert response.status_code == 200
    body = response.json()
    assert body["firstname"] == NEW_FIRSTNAME
    assert body["totalprice"] == NEW_TOTALPRICE
    assert body == payload


def test_ct06_atualizacao_completa_persistida_na_consulta(token, booking_id):
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}", json=full_update_payload(), headers=auth_headers(token), timeout=TIMEOUT
    )
    assert response.status_code == 200
    stored = get_booking(booking_id)
    assert stored.status_code == 200
    assert stored.json()["firstname"] == NEW_FIRSTNAME
    assert stored.json()["totalprice"] == NEW_TOTALPRICE


def test_ct07_atualizacao_parcial_apenas_do_sobrenome(token, booking_id):
    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json={"lastname": NEW_LASTNAME},
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["lastname"] == NEW_LASTNAME
    assert body == {**ORIGINAL_BOOKING, "lastname": NEW_LASTNAME}


def test_ct08_atualizacao_parcial_persistida_sem_alterar_demais_campos(token, booking_id):
    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json={"lastname": NEW_LASTNAME},
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    stored = get_booking(booking_id)
    assert stored.status_code == 200
    assert stored.json() == {**ORIGINAL_BOOKING, "lastname": NEW_LASTNAME}


def test_ct09_atualizacao_completa_sem_token(booking_id):
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}", json=full_update_payload(), headers=HEADERS, timeout=TIMEOUT
    )
    assert response.status_code == 403
    stored = get_booking(booking_id)
    assert stored.status_code == 200
    assert stored.json() == ORIGINAL_BOOKING


def test_ct10_atualizacao_parcial_sem_token(booking_id):
    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}", json={"lastname": NEW_LASTNAME}, headers=HEADERS, timeout=TIMEOUT
    )
    assert response.status_code == 403
    stored = get_booking(booking_id)
    assert stored.status_code == 200
    assert stored.json()["lastname"] == ORIGINAL_BOOKING["lastname"]


def test_ct11_atualizacao_completa_com_token_invalido(booking_id):
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=full_update_payload(),
        headers=auth_headers(INVALID_TOKEN),
        timeout=TIMEOUT,
    )
    assert response.status_code == 403


def test_ct12_atualizacao_completa_sem_firstname(token, booking_id):
    payload = full_update_payload()
    del payload["firstname"]
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}", json=payload, headers=auth_headers(token), timeout=TIMEOUT
    )
    assert response.status_code == 400


def test_ct13_atualizacao_completa_sem_bookingdates(token, booking_id):
    payload = full_update_payload()
    del payload["bookingdates"]
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}", json=payload, headers=auth_headers(token), timeout=TIMEOUT
    )
    assert response.status_code == 400


def test_ct14_atualizacao_completa_com_corpo_vazio(token, booking_id):
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}", json={}, headers=auth_headers(token), timeout=TIMEOUT
    )
    assert response.status_code == 400
