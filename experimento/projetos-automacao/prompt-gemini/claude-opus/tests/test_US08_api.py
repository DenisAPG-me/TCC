import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
USERNAME = "admin"
PASSWORD = "password123"
TIMEOUT = 30
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def booking_payload(**overrides):
    payload = {
        "firstname": "Maria",
        "lastname": "Silva",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-05"},
        "additionalneeds": "Breakfast",
    }
    payload.update(overrides)
    return payload


def authenticate(username, password):
    return requests.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )


def auth_headers(token):
    return {**JSON_HEADERS, "Cookie": f"token={token}"}


def get_booking(booking_id):
    response = requests.get(
        f"{BASE_URL}/booking/{booking_id}",
        headers={"Accept": "application/json"},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="session")
def token():
    response = authenticate(USERNAME, PASSWORD)
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def booking(token):
    payload = booking_payload()
    response = requests.post(
        f"{BASE_URL}/booking", json=payload, headers=JSON_HEADERS, timeout=TIMEOUT
    )
    assert response.status_code == 200
    booking_id = response.json()["bookingid"]
    yield booking_id, payload
    requests.delete(
        f"{BASE_URL}/booking/{booking_id}", headers=auth_headers(token), timeout=TIMEOUT
    )


def test_ct01_autenticacao_credenciais_validas():
    response = authenticate(USERNAME, PASSWORD)

    assert response.status_code == 200
    token = response.json().get("token")
    assert isinstance(token, str)
    assert token.strip() != ""


def test_ct02_autenticacao_senha_invalida():
    response = authenticate(USERNAME, "senha_errada")

    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_ct03_autenticacao_usuario_invalido():
    response = authenticate("usuario_inexistente", PASSWORD)

    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_ct04_autenticacao_credenciais_vazias():
    response = authenticate("", "")

    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_ct05_atualizacao_completa_novo_nome_e_preco(booking, token):
    booking_id, _ = booking
    updated = booking_payload(firstname="Joana", totalprice=320)

    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=updated,
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["firstname"] == "Joana"
    assert body["totalprice"] == 320


def test_ct06_atualizacao_completa_persiste(booking, token):
    booking_id, _ = booking
    updated = booking_payload(firstname="Carla", totalprice=480)

    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=updated,
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )
    assert response.status_code == 200

    stored = get_booking(booking_id)
    assert stored["firstname"] == "Carla"
    assert stored["totalprice"] == 480


def test_ct07_atualizacao_parcial_sobrenome(booking, token):
    booking_id, original = booking

    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json={"lastname": "Oliveira"},
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["lastname"] == "Oliveira"
    for field in ("firstname", "totalprice", "depositpaid", "bookingdates", "additionalneeds"):
        assert body[field] == original[field]


def test_ct08_atualizacao_completa_sem_token(booking):
    booking_id, _ = booking

    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=booking_payload(firstname="SemToken"),
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )

    assert response.status_code == 403


def test_ct09_atualizacao_parcial_sem_token(booking):
    booking_id, _ = booking

    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json={"lastname": "SemToken"},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )

    assert response.status_code == 403


def test_ct10_atualizacao_completa_token_invalido(booking):
    booking_id, _ = booking

    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=booking_payload(firstname="TokenInvalido"),
        headers=auth_headers("token_invalido_123"),
        timeout=TIMEOUT,
    )

    assert response.status_code == 403


def test_ct11_atualizacao_completa_sem_campo_obrigatorio(booking, token):
    booking_id, _ = booking
    incomplete = booking_payload()
    del incomplete["firstname"]

    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=incomplete,
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )

    assert response.status_code == 400


def test_ct12_atualizacao_completa_corpo_vazio(booking, token):
    booking_id, _ = booking

    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json={},
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )

    assert response.status_code == 400


def test_ct13_atualizacao_rejeitada_nao_altera_reserva(booking, token):
    booking_id, original = booking
    incomplete = booking_payload(totalprice=999)
    del incomplete["firstname"]

    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=incomplete,
        headers=auth_headers(token),
        timeout=TIMEOUT,
    )
    assert response.status_code == 400

    stored = get_booking(booking_id)
    assert stored["firstname"] == original["firstname"]
    assert stored["totalprice"] == original["totalprice"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
