import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 30
ADMIN_USER = "admin"
ADMIN_PASSWORD = "password123"
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def build_booking(**overrides):
    booking = {
        "firstname": "Joao",
        "lastname": "Silva",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"},
        "additionalneeds": "Breakfast",
    }
    booking.update(overrides)
    return booking


def auth_headers(token):
    return {**JSON_HEADERS, "Cookie": f"token={token}"}


def get_booking(booking_id):
    response = requests.get(f"{BASE_URL}/booking/{booking_id}", headers=JSON_HEADERS, timeout=TIMEOUT)
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="session")
def auth_token():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": ADMIN_USER, "password": ADMIN_PASSWORD},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )
    token = response.json().get("token")
    assert token, f"Token não obtido: {response.text}"
    return token


@pytest.fixture
def booking_id():
    response = requests.post(
        f"{BASE_URL}/booking",
        json=build_booking(),
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    return response.json()["bookingid"]


def test_CT01_autenticacao_credenciais_validas():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": ADMIN_USER, "password": ADMIN_PASSWORD},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    token = response.json().get("token")
    assert isinstance(token, str) and token.strip()


def test_CT02_autenticacao_senha_invalida():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": ADMIN_USER, "password": "senha_errada"},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )
    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_CT03_autenticacao_usuario_inexistente():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": "usuario_inexistente", "password": ADMIN_PASSWORD},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )
    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_CT04_autenticacao_credenciais_vazias():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": "", "password": ""},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )
    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_CT05_put_atualizacao_completa_novo_nome_e_preco(auth_token, booking_id):
    payload = build_booking(firstname="Maria", totalprice=999)
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=payload,
        headers=auth_headers(auth_token),
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["firstname"] == "Maria"
    assert body["totalprice"] == 999


def test_CT06_patch_atualizacao_parcial_sobrenome(auth_token, booking_id):
    original = get_booking(booking_id)
    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json={"lastname": "Oliveira"},
        headers=auth_headers(auth_token),
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["lastname"] == "Oliveira"
    assert body["firstname"] == original["firstname"]
    assert body["totalprice"] == original["totalprice"]
    assert body["depositpaid"] == original["depositpaid"]
    assert body["bookingdates"] == original["bookingdates"]


def test_CT07_put_sem_token_retorna_403(booking_id):
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=build_booking(firstname="Maria"),
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )
    assert response.status_code == 403


def test_CT08_put_campos_obrigatorios_ausentes_retorna_400(auth_token, booking_id):
    payload = build_booking()
    del payload["firstname"]
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=payload,
        headers=auth_headers(auth_token),
        timeout=TIMEOUT,
    )
    assert response.status_code == 400


def test_CT09_put_token_invalido_retorna_403(booking_id):
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=build_booking(firstname="Maria"),
        headers=auth_headers("token_invalido_123"),
        timeout=TIMEOUT,
    )
    assert response.status_code == 403


def test_CT10_patch_sem_token_retorna_403(booking_id):
    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json={"lastname": "Oliveira"},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )
    assert response.status_code == 403


def test_CT11_put_preco_zero_borda(auth_token, booking_id):
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=build_booking(totalprice=0),
        headers=auth_headers(auth_token),
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    assert response.json()["totalprice"] == 0
