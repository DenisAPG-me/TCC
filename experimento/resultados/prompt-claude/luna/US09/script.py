import uuid

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
USERNAME = "admin"
PASSWORD = "password123"
INVALID_TOKEN = "token-invalido-para-teste"
REQUEST_TIMEOUT = 10


def unique_name():
    return f"Teste{uuid.uuid4().hex[:12]}"


def create_booking(firstname=None):
    firstname = firstname or unique_name()
    payload = {
        "firstname": firstname,
        "lastname": "Automacao",
        "totalprice": 123,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-11-01",
            "checkout": "2026-11-05",
        },
        "additionalneeds": "Nenhuma",
    }
    response = requests.post(
        f"{BASE_URL}/booking",
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code == 200, (
        f"Falha ao criar reserva: {response.status_code} {response.text}"
    )
    booking_id = response.json().get("bookingid")
    assert booking_id is not None, "Resposta de criação não contém bookingid"
    return booking_id, firstname


def get_token():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": USERNAME, "password": PASSWORD},
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code == 200, (
        f"Falha na autenticação: {response.status_code} {response.text}"
    )
    token = response.json().get("token")
    assert token, "Resposta de autenticação não contém token"
    return token


def delete_booking(booking_id, token=None):
    headers = {"Cookie": f"token={token}"} if token is not None else {}
    return requests.delete(
        f"{BASE_URL}/booking/{booking_id}",
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )


def test_ct01_excluir_sem_token():
    booking_id, _ = create_booking()

    delete_response = delete_booking(booking_id)
    assert delete_response.status_code == 403

    get_response = requests.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=REQUEST_TIMEOUT,
    )
    assert get_response.status_code == 200


def test_ct02_excluir_com_token_invalido():
    booking_id, _ = create_booking()

    delete_response = delete_booking(booking_id, INVALID_TOKEN)
    assert delete_response.status_code == 403

    get_response = requests.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=REQUEST_TIMEOUT,
    )
    assert get_response.status_code == 200


def test_ct03_excluir_com_token_valido():
    booking_id, _ = create_booking()
    token = get_token()

    delete_response = delete_booking(booking_id, token)
    assert delete_response.status_code == 201

    get_response = requests.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=REQUEST_TIMEOUT,
    )
    assert get_response.status_code == 404


def test_ct04_reexcluir_reserva_removida():
    booking_id, _ = create_booking()
    control_id, _ = create_booking()
    token = get_token()

    first_delete = delete_booking(booking_id, token)
    assert first_delete.status_code == 201

    second_delete = delete_booking(booking_id, token)
    assert 400 <= second_delete.status_code <= 499

    control_response = requests.get(
        f"{BASE_URL}/booking/{control_id}",
        timeout=REQUEST_TIMEOUT,
    )
    assert control_response.status_code == 200


def test_ct05_listar_filtrando_nome_apos_exclusao():
    booking_id, firstname = create_booking()
    token = get_token()

    delete_response = delete_booking(booking_id, token)
    assert delete_response.status_code == 201

    list_response = requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": firstname, "lastname": "Automacao"},
        timeout=REQUEST_TIMEOUT,
    )
    assert list_response.status_code == 200
    assert list_response.json() == []
