import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
USERNAME = "admin"
PASSWORD = "password123"
TIMEOUT = 30
NONEXISTENT_ID = 999999999
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def unique_name(prefix):
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def booking_payload(firstname=None, lastname=None):
    return {
        "firstname": firstname or unique_name("Qa"),
        "lastname": lastname or unique_name("Del"),
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


def filter_bookings(firstname, lastname):
    return requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": firstname, "lastname": lastname},
        headers={"Accept": "application/json"},
        timeout=TIMEOUT,
    )


def is_client_error(status_code):
    return 400 <= status_code < 500


@pytest.fixture(scope="session")
def valid_token():
    response = authenticate(USERNAME, PASSWORD)
    assert response.status_code == 200
    token = response.json().get("token")
    assert token
    return token


@pytest.fixture
def create_booking(valid_token):
    created_ids = []

    def _create(payload=None):
        payload = payload or booking_payload()
        response = requests.post(
            f"{BASE_URL}/booking", json=payload, headers=JSON_HEADERS, timeout=TIMEOUT
        )
        assert response.status_code == 200
        booking_id = response.json()["bookingid"]
        created_ids.append(booking_id)
        return booking_id, payload

    yield _create

    for booking_id in created_ids:
        try:
            delete_booking(booking_id, valid_token)
        except requests.RequestException:
            pass


def test_TC01_excluir_sem_token_retorna_403_e_reserva_permanece(create_booking):
    booking_id, _ = create_booking()

    response = delete_booking(booking_id)

    assert response.status_code == 403
    assert get_booking(booking_id).status_code == 200


def test_TC02_excluir_com_token_invalido_retorna_403_e_reserva_permanece(create_booking):
    booking_id, _ = create_booking()

    response = delete_booking(booking_id, token=f"invalid{uuid.uuid4().hex}")

    assert response.status_code == 403
    assert get_booking(booking_id).status_code == 200


def test_TC03_excluir_com_token_valido_retorna_201(create_booking, valid_token):
    booking_id, _ = create_booking()

    response = delete_booking(booking_id, valid_token)

    assert response.status_code == 201


def test_TC04_consultar_reserva_excluida_retorna_404(create_booking, valid_token):
    booking_id, _ = create_booking()
    assert delete_booking(booking_id, valid_token).status_code == 201

    response = get_booking(booking_id)

    assert response.status_code == 404


def test_TC05_excluir_novamente_retorna_4xx_sem_afetar_outras(create_booking, valid_token):
    target_id, _ = create_booking()
    other_id, other_payload = create_booking()
    assert delete_booking(target_id, valid_token).status_code == 201

    response = delete_booking(target_id, valid_token)

    assert is_client_error(response.status_code)
    other_response = get_booking(other_id)
    assert other_response.status_code == 200
    assert other_response.json() == other_payload


def test_TC06_filtro_por_nome_unico_apos_exclusao_retorna_lista_vazia(create_booking, valid_token):
    payload = booking_payload(unique_name("Uniq"), unique_name("Name"))
    booking_id, _ = create_booking(payload)

    before = filter_bookings(payload["firstname"], payload["lastname"])
    assert before.status_code == 200
    assert booking_id in [item["bookingid"] for item in before.json()]

    assert delete_booking(booking_id, valid_token).status_code == 201

    after = filter_bookings(payload["firstname"], payload["lastname"])
    assert after.status_code == 200
    assert after.json() == []


def test_TC07_excluir_com_token_vazio_retorna_403_e_reserva_permanece(create_booking):
    booking_id, _ = create_booking()

    response = delete_booking(booking_id, token="")

    assert response.status_code == 403
    assert get_booking(booking_id).status_code == 200


def test_TC08_tentativas_nao_autorizadas_nao_alteram_dados(create_booking):
    booking_id, payload = create_booking()

    assert delete_booking(booking_id).status_code == 403
    assert delete_booking(booking_id, token=f"invalid{uuid.uuid4().hex}").status_code == 403

    response = get_booking(booking_id)
    assert response.status_code == 200
    assert response.json() == payload


def test_TC09_credenciais_incorretas_nao_concedem_exclusao(create_booking):
    auth_response = authenticate(USERNAME, f"wrong{uuid.uuid4().hex[:8]}")
    body = auth_response.json()
    assert "token" not in body

    booking_id, _ = create_booking()
    response = delete_booking(booking_id, token=body.get("token", ""))

    assert response.status_code == 403
    assert get_booking(booking_id).status_code == 200


def test_TC10_excluir_id_inexistente_com_token_valido_retorna_4xx(valid_token):
    assert get_booking(NONEXISTENT_ID).status_code == 404

    response = delete_booking(NONEXISTENT_ID, valid_token)

    assert is_client_error(response.status_code)
