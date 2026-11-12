import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
USERNAME = "admin"
PASSWORD = "password123"
TIMEOUT = 30
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def unique_name(prefix):
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def booking_payload(firstname, lastname):
    return {
        "firstname": firstname,
        "lastname": lastname,
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-05"},
        "additionalneeds": "Breakfast",
    }


def authenticate(username, password):
    return requests.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )


def get_booking(booking_id):
    return requests.get(
        f"{BASE_URL}/booking/{booking_id}",
        headers={"Accept": "application/json"},
        timeout=TIMEOUT,
    )


def delete_booking(booking_id, token=None):
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["Cookie"] = f"token={token}"
    return requests.delete(
        f"{BASE_URL}/booking/{booking_id}", headers=headers, timeout=TIMEOUT
    )


def list_bookings_by_name(firstname, lastname):
    return requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": firstname, "lastname": lastname},
        headers={"Accept": "application/json"},
        timeout=TIMEOUT,
    )


@pytest.fixture
def token():
    response = authenticate(USERNAME, PASSWORD)
    assert response.status_code == 200, response.text
    value = response.json().get("token")
    assert value, f"Token não retornado: {response.text}"
    return value


@pytest.fixture
def create_booking(token):
    created = []

    def _create():
        payload = booking_payload(unique_name("Qa"), unique_name("Del"))
        response = requests.post(
            f"{BASE_URL}/booking", json=payload, headers=JSON_HEADERS, timeout=TIMEOUT
        )
        assert response.status_code == 200, response.text
        booking_id = response.json()["bookingid"]
        created.append(booking_id)
        return booking_id, payload

    yield _create

    for booking_id in created:
        try:
            delete_booking(booking_id, token)
        except requests.RequestException:
            pass


def test_ct01_excluir_reserva_sem_token_retorna_403(create_booking):
    booking_id, _ = create_booking()

    response = delete_booking(booking_id)

    assert response.status_code == 403
    assert get_booking(booking_id).status_code == 200


def test_ct02_excluir_reserva_com_token_invalido_retorna_403(create_booking):
    booking_id, payload = create_booking()

    response = delete_booking(booking_id, f"invalido{uuid.uuid4().hex}")

    assert response.status_code == 403
    get_response = get_booking(booking_id)
    assert get_response.status_code == 200
    assert get_response.json() == payload


def test_ct03_excluir_reserva_com_token_vazio_retorna_403(create_booking):
    booking_id, _ = create_booking()

    response = delete_booking(booking_id, "")

    assert response.status_code == 403
    assert get_booking(booking_id).status_code == 200


def test_ct04_autenticacao_com_credenciais_invalidas_nao_gera_token():
    response = authenticate(USERNAME, f"errada{uuid.uuid4().hex[:8]}")

    assert "token" not in response.json()


def test_ct05_excluir_reserva_com_token_valido_retorna_201(create_booking, token):
    booking_id, _ = create_booking()

    response = delete_booking(booking_id, token)

    assert response.status_code == 201


def test_ct06_consultar_reserva_excluida_retorna_404(create_booking, token):
    booking_id, _ = create_booking()
    assert delete_booking(booking_id, token).status_code == 201

    response = get_booking(booking_id)

    assert response.status_code == 404


def test_ct07_excluir_reserva_ja_excluida_retorna_4xx_sem_afetar_outras(create_booking, token):
    target_id, _ = create_booking()
    other_id, other_payload = create_booking()
    assert delete_booking(target_id, token).status_code == 201

    response = delete_booking(target_id, token)

    assert 400 <= response.status_code < 500
    other_response = get_booking(other_id)
    assert other_response.status_code == 200
    assert other_response.json() == other_payload


def test_ct08_listar_por_nome_unico_apos_exclusao_retorna_lista_vazia(create_booking, token):
    booking_id, payload = create_booking()
    before = list_bookings_by_name(payload["firstname"], payload["lastname"])
    assert before.status_code == 200
    assert {"bookingid": booking_id} in before.json()
    assert delete_booking(booking_id, token).status_code == 201

    response = list_bookings_by_name(payload["firstname"], payload["lastname"])

    assert response.status_code == 200
    assert response.json() == []


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
