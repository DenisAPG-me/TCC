import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
AUTH_PATH = "/auth"
BOOKING_PATH = "/booking"
USERNAME = "admin"
PASSWORD = "password123"
TIMEOUT = 30
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def booking_url(booking_id=None):
    if booking_id is None:
        return f"{BASE_URL}{BOOKING_PATH}"
    return f"{BASE_URL}{BOOKING_PATH}/{booking_id}"


def build_payload():
    suffix = uuid.uuid4().hex[:12]
    return {
        "firstname": f"Teste{suffix}",
        "lastname": f"Exclusao{suffix}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-15"},
        "additionalneeds": "Breakfast",
    }


def auth_cookie(token):
    return {"Accept": "application/json", "Cookie": f"token={token}"}


def get_booking(booking_id):
    return requests.get(booking_url(booking_id), headers={"Accept": "application/json"}, timeout=TIMEOUT)


def delete_booking(booking_id, headers):
    return requests.delete(booking_url(booking_id), headers=headers, timeout=TIMEOUT)


def obtain_token():
    response = requests.post(
        f"{BASE_URL}{AUTH_PATH}",
        json={"username": USERNAME, "password": PASSWORD},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, response.text
    token = response.json().get("token")
    assert isinstance(token, str) and token, response.text
    return token


@pytest.fixture
def token():
    return obtain_token()


@pytest.fixture
def create_booking():
    created_ids = []

    def _create():
        payload = build_payload()
        response = requests.post(booking_url(), json=payload, headers=JSON_HEADERS, timeout=TIMEOUT)
        assert response.status_code == 200, response.text
        body = response.json()
        booking_id = body["bookingid"]
        assert isinstance(booking_id, int)
        assert body["booking"] == payload
        created_ids.append(booking_id)
        return booking_id, payload

    yield _create

    if created_ids:
        cleanup_token = obtain_token()
        for booking_id in created_ids:
            if get_booking(booking_id).status_code == 200:
                response = delete_booking(booking_id, auth_cookie(cleanup_token))
                assert response.status_code == 201, response.text


def assert_booking_unchanged(booking_id, payload):
    response = get_booking(booking_id)
    assert response.status_code == 200, response.text
    assert response.json() == payload


def test_CT001_excluir_sem_token_retorna_403_e_reserva_permanece(create_booking):
    booking_id, payload = create_booking()

    response = delete_booking(booking_id, {"Accept": "application/json"})

    assert response.status_code == 403, response.text
    assert_booking_unchanged(booking_id, payload)


def test_CT002_excluir_com_token_invalido_retorna_403_e_reserva_permanece(create_booking):
    booking_id, payload = create_booking()
    invalid_token = f"token-invalido-{uuid.uuid4().hex}"

    response = delete_booking(booking_id, auth_cookie(invalid_token))

    assert response.status_code == 403, response.text
    assert_booking_unchanged(booking_id, payload)


def test_CT003_excluir_com_token_vazio_retorna_403_e_reserva_permanece(create_booking):
    booking_id, payload = create_booking()

    response = delete_booking(booking_id, auth_cookie(""))

    assert response.status_code == 403, response.text
    assert_booking_unchanged(booking_id, payload)


def test_CT004_excluir_com_token_valido_retorna_201(create_booking, token):
    booking_id, _ = create_booking()

    response = delete_booking(booking_id, auth_cookie(token))

    assert response.status_code == 201, response.text


def test_CT005_consultar_reserva_excluida_retorna_404(create_booking, token):
    booking_id, _ = create_booking()
    delete_response = delete_booking(booking_id, auth_cookie(token))
    assert delete_response.status_code == 201, delete_response.text

    response = get_booking(booking_id)

    assert response.status_code == 404, response.text


def test_CT006_excluir_novamente_retorna_4xx_sem_afetar_outra_reserva(create_booking, token):
    target_id, _ = create_booking()
    control_id, control_payload = create_booking()
    first_delete = delete_booking(target_id, auth_cookie(token))
    assert first_delete.status_code == 201, first_delete.text

    second_delete = delete_booking(target_id, auth_cookie(token))

    assert 400 <= second_delete.status_code <= 499, second_delete.status_code
    assert get_booking(target_id).status_code == 404
    assert_booking_unchanged(control_id, control_payload)


def test_CT007_filtro_por_nome_unico_nao_retorna_reserva_excluida(create_booking, token):
    booking_id, payload = create_booking()
    params = {"firstname": payload["firstname"], "lastname": payload["lastname"]}

    before = requests.get(booking_url(), params=params, headers={"Accept": "application/json"}, timeout=TIMEOUT)
    assert before.status_code == 200, before.text
    assert booking_id in [item["bookingid"] for item in before.json()]

    delete_response = delete_booking(booking_id, auth_cookie(token))
    assert delete_response.status_code == 201, delete_response.text

    after = requests.get(booking_url(), params=params, headers={"Accept": "application/json"}, timeout=TIMEOUT)

    assert after.status_code == 200, after.text
    assert after.json() == []
