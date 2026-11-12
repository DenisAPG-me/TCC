import uuid

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
REQUEST_TIMEOUT_SECONDS = 15

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"
INVALID_TOKEN = "token-invalido-para-teste"

BOOKING_PAYLOAD_BASE = {
    "totalprice": 123,
    "depositpaid": True,
    "bookingdates": {
        "checkin": "2026-11-01",
        "checkout": "2026-11-05",
    },
    "additionalneeds": "Breakfast",
}


def create_booking(session, firstname):
    payload = {
        **BOOKING_PAYLOAD_BASE,
        "firstname": firstname,
        "lastname": "Teste",
    }
    response = session.post(
        f"{BASE_URL}/booking",
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    assert response.status_code == 200, (
        f"Criação de reserva retornou {response.status_code}: {response.text}"
    )
    body = response.json()
    assert "bookingid" in body, "Resposta de criação não contém bookingid"
    return body["bookingid"]


def authenticate(session):
    response = session.post(
        f"{BASE_URL}/auth",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    assert response.status_code == 200, (
        f"Autenticação retornou {response.status_code}: {response.text}"
    )
    body = response.json()
    assert body.get("token"), "Resposta de autenticação não contém token"
    return body["token"]


def delete_booking(session, booking_id, token=None):
    headers = {}
    if token is not None:
        headers["Cookie"] = f"token={token}"
    return session.delete(
        f"{BASE_URL}/booking/{booking_id}",
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )


def unique_firstname():
    return f"Teste{uuid.uuid4().hex}"


@pytest.fixture
def booking_factory():
    session = requests.Session()
    created_booking_ids = []

    def create(firstname=None):
        name = firstname or unique_firstname()
        booking_id = create_booking(session, name)
        created_booking_ids.append(booking_id)
        return {"id": booking_id, "firstname": name}

    yield create

    token = authenticate(session)
    for booking_id in created_booking_ids:
        response = delete_booking(session, booking_id, token)
        assert response.status_code in (201, 404), (
            f"Limpeza da reserva {booking_id} retornou "
            f"{response.status_code}: {response.text}"
        )
    session.close()


@pytest.fixture
def api_session():
    session = requests.Session()
    yield session
    session.close()


def test_CT001_excluir_sem_token(booking_factory, api_session):
    booking = booking_factory()

    delete_response = delete_booking(api_session, booking["id"])
    assert delete_response.status_code == 403

    get_response = api_session.get(
        f"{BASE_URL}/booking/{booking['id']}",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    assert get_response.status_code == 200
    assert get_response.json()["firstname"] == booking["firstname"]


def test_CT002_excluir_com_token_invalido(booking_factory, api_session):
    booking = booking_factory()

    delete_response = delete_booking(
        api_session,
        booking["id"],
        INVALID_TOKEN,
    )
    assert delete_response.status_code == 403

    get_response = api_session.get(
        f"{BASE_URL}/booking/{booking['id']}",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    assert get_response.status_code == 200
    assert get_response.json()["firstname"] == booking["firstname"]


def test_CT003_excluir_com_token_valido(booking_factory, api_session):
    booking = booking_factory()
    token = authenticate(api_session)

    delete_response = delete_booking(api_session, booking["id"], token)
    assert delete_response.status_code == 201


def test_CT004_consultar_reserva_excluida(booking_factory, api_session):
    booking = booking_factory()
    token = authenticate(api_session)

    delete_response = delete_booking(api_session, booking["id"], token)
    assert delete_response.status_code == 201

    get_response = api_session.get(
        f"{BASE_URL}/booking/{booking['id']}",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    assert get_response.status_code == 404


def test_CT005_repetir_exclusao_sem_afetar_outra_reserva(
    booking_factory,
    api_session,
):
    booking = booking_factory()
    unaffected_booking = booking_factory()
    token = authenticate(api_session)

    first_delete = delete_booking(api_session, booking["id"], token)
    assert first_delete.status_code == 201

    second_delete = delete_booking(api_session, booking["id"], token)
    assert 400 <= second_delete.status_code < 500

    unaffected_response = api_session.get(
        f"{BASE_URL}/booking/{unaffected_booking['id']}",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    assert unaffected_response.status_code == 200
    assert unaffected_response.json()["firstname"] == unaffected_booking["firstname"]


def test_CT006_listar_vazia_pelo_nome_da_reserva_excluida(
    booking_factory,
    api_session,
):
    booking = booking_factory()
    token = authenticate(api_session)

    delete_response = delete_booking(api_session, booking["id"], token)
    assert delete_response.status_code == 201

    list_response = api_session.get(
        f"{BASE_URL}/booking",
        params={"firstname": booking["firstname"]},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    assert list_response.status_code == 200
    assert list_response.json() == []
