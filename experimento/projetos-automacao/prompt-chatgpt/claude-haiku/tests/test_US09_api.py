import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
ADMIN_CREDENTIALS = {"username": "admin", "password": "password123"}
INVALID_TOKEN = "token-invalido-000000000000"
EMPTY_TOKEN = ""
TIMEOUT = 15
JSON_HEADERS = {"Accept": "application/json"}


def authenticate():
    response = requests.post(f"{BASE_URL}/auth", json=ADMIN_CREDENTIALS, headers=JSON_HEADERS, timeout=TIMEOUT)
    assert response.status_code == 200, response.text
    token = response.json().get("token")
    assert token, response.text
    return token


def create_booking():
    suffix = uuid.uuid4().hex[:12]
    payload = {
        "firstname": f"Nome{suffix}",
        "lastname": f"Sobrenome{suffix}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-05"},
        "additionalneeds": "Breakfast",
    }
    response = requests.post(f"{BASE_URL}/booking", json=payload, headers=JSON_HEADERS, timeout=TIMEOUT)
    assert response.status_code == 200, response.text
    return {"id": response.json()["bookingid"], "firstname": payload["firstname"], "lastname": payload["lastname"]}


def get_booking(booking_id):
    return requests.get(f"{BASE_URL}/booking/{booking_id}", headers=JSON_HEADERS, timeout=TIMEOUT)


def delete_booking(booking_id, token=None):
    headers = {} if token is None else {"Cookie": f"token={token}"}
    return requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers, timeout=TIMEOUT)


def search_bookings(booking):
    params = {"firstname": booking["firstname"], "lastname": booking["lastname"]}
    return requests.get(f"{BASE_URL}/booking", params=params, headers=JSON_HEADERS, timeout=TIMEOUT)


def assert_booking_persists(booking):
    response = get_booking(booking["id"])
    assert response.status_code == 200, response.text
    assert response.json()["firstname"] == booking["firstname"]


@pytest.fixture
def bookings():
    created = []
    yield created
    for booking in created:
        if get_booking(booking["id"]).status_code == 200:
            response = delete_booking(booking["id"], authenticate())
            assert response.status_code == 201, response.text


def test_CT001_excluir_sem_token_retorna_403_e_reserva_permanece(bookings):
    booking = create_booking()
    bookings.append(booking)

    response = delete_booking(booking["id"])

    assert response.status_code == 403, response.text
    assert_booking_persists(booking)


def test_CT002_excluir_com_token_invalido_retorna_403_e_reserva_permanece(bookings):
    booking = create_booking()
    bookings.append(booking)

    response = delete_booking(booking["id"], INVALID_TOKEN)

    assert response.status_code == 403, response.text
    assert_booking_persists(booking)


def test_CT003_excluir_com_token_vazio_retorna_403_e_reserva_permanece(bookings):
    booking = create_booking()
    bookings.append(booking)

    response = delete_booking(booking["id"], EMPTY_TOKEN)

    assert response.status_code == 403, response.text
    assert_booking_persists(booking)


def test_CT004_excluir_com_token_valido_retorna_201(bookings):
    booking = create_booking()
    bookings.append(booking)
    token = authenticate()

    response = delete_booking(booking["id"], token)

    assert response.status_code == 201, response.text


def test_CT005_consultar_reserva_excluida_retorna_404(bookings):
    booking = create_booking()
    bookings.append(booking)
    token = authenticate()
    delete_response = delete_booking(booking["id"], token)
    assert delete_response.status_code == 201, delete_response.text

    response = get_booking(booking["id"])

    assert response.status_code == 404, response.text


def test_CT006_excluir_novamente_reserva_ja_excluida_retorna_erro_4xx(bookings):
    booking = create_booking()
    bookings.append(booking)
    token = authenticate()
    first_response = delete_booking(booking["id"], token)
    assert first_response.status_code == 201, first_response.text

    response = delete_booking(booking["id"], token)

    assert 400 <= response.status_code < 500, response.text
    assert get_booking(booking["id"]).status_code == 404


def test_CT007_exclusao_repetida_nao_afeta_reserva_vizinha(bookings):
    target = create_booking()
    bookings.append(target)
    neighbor = create_booking()
    bookings.append(neighbor)
    token = authenticate()
    first_response = delete_booking(target["id"], token)
    assert first_response.status_code == 201, first_response.text
    second_response = delete_booking(target["id"], token)
    assert 400 <= second_response.status_code < 500, second_response.text

    assert_booking_persists(neighbor)


def test_CT008_listar_por_nome_unico_apos_exclusao_retorna_lista_vazia(bookings):
    booking = create_booking()
    bookings.append(booking)
    before_response = search_bookings(booking)
    assert before_response.status_code == 200, before_response.text
    assert before_response.json() == [{"bookingid": booking["id"]}]
    token = authenticate()
    delete_response = delete_booking(booking["id"], token)
    assert delete_response.status_code == 201, delete_response.text

    after_response = search_bookings(booking)

    assert after_response.status_code == 200, after_response.text
    assert after_response.json() == []
