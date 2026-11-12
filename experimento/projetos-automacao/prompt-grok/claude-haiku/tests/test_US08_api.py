import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "password123"
TIMEOUT = 30


def _booking_payload(**overrides):
    payload = {
        "firstname": "Ana",
        "lastname": "Silva",
        "totalprice": 100,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-01-10", "checkout": "2026-01-15"},
        "additionalneeds": "Breakfast",
    }
    payload.update(overrides)
    return payload


def _auth_headers(token):
    return {"Cookie": f"token={token}"}


@pytest.fixture(scope="session")
def token():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": ADMIN_USER, "password": ADMIN_PASSWORD},
        timeout=TIMEOUT,
    )
    return response.json()["token"]


@pytest.fixture
def booking_id():
    response = requests.post(f"{BASE_URL}/booking", json=_booking_payload(), timeout=TIMEOUT)
    return response.json()["bookingid"]


def test_TC01_autenticacao_com_credenciais_validas_retorna_token():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": ADMIN_USER, "password": ADMIN_PASSWORD},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    token_value = response.json().get("token")
    assert isinstance(token_value, str) and token_value.strip()


def test_TC02_autenticacao_com_senha_invalida_nao_retorna_token():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": ADMIN_USER, "password": "senha-errada"},
        timeout=TIMEOUT,
    )
    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_TC03_senha_com_caixa_diferente_nao_autentica():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": ADMIN_USER, "password": "PASSWORD123"},
        timeout=TIMEOUT,
    )
    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_TC04_atualizacao_completa_com_novo_nome_e_preco(token, booking_id):
    payload = _booking_payload(firstname="Carlos", lastname="Souza", totalprice=250)
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=payload,
        headers=_auth_headers(token),
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["firstname"] == "Carlos"
    assert body["lastname"] == "Souza"
    assert body["totalprice"] == 250


def test_TC05_atualizacao_parcial_altera_apenas_sobrenome(token, booking_id):
    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json={"lastname": "Pereira"},
        headers=_auth_headers(token),
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    body = response.json()
    original = _booking_payload()
    assert body["lastname"] == "Pereira"
    assert body["firstname"] == original["firstname"]
    assert body["totalprice"] == original["totalprice"]
    assert body["depositpaid"] == original["depositpaid"]
    assert body["bookingdates"] == original["bookingdates"]
    assert body["additionalneeds"] == original["additionalneeds"]


def test_TC06_put_sem_token_retorna_403(booking_id):
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=_booking_payload(firstname="Sem", lastname="Token"),
        timeout=TIMEOUT,
    )
    assert response.status_code == 403


def test_TC07_patch_sem_token_retorna_403(booking_id):
    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json={"lastname": "SemToken"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 403


def test_TC08_put_com_token_invalido_retorna_403(booking_id):
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=_booking_payload(firstname="Token", lastname="Invalido"),
        headers=_auth_headers("token-invalido"),
        timeout=TIMEOUT,
    )
    assert response.status_code == 403


def test_TC09_put_com_campo_obrigatorio_ausente_retorna_400(token, booking_id):
    payload = _booking_payload()
    del payload["firstname"]
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=payload,
        headers=_auth_headers(token),
        timeout=TIMEOUT,
    )
    assert response.status_code == 400


def test_TC10_patch_com_corpo_vazio_nao_altera_reserva(token, booking_id):
    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json={},
        headers=_auth_headers(token),
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    body = response.json()
    original = _booking_payload()
    for field, value in original.items():
        assert body[field] == value
