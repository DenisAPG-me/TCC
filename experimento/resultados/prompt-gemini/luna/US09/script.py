import uuid

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
USERNAME = "admin"
PASSWORD = "password123"
TIMEOUT_SECONDS = 15


def unique_name(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def create_booking(firstname=None):
    firstname = firstname or unique_name("Test")
    payload = {
        "firstname": firstname,
        "lastname": "Automation",
        "totalprice": 123,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-11-01",
            "checkout": "2026-11-05",
        },
        "additionalneeds": "Breakfast",
    }
    response = requests.post(
        f"{BASE_URL}/booking",
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )
    assert response.status_code == 200, (
        f"Falha ao criar reserva: {response.status_code} {response.text}"
    )
    booking_id = response.json().get("bookingid")
    assert booking_id is not None, "A resposta de criação não contém bookingid."
    return booking_id, firstname


def get_token():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": USERNAME, "password": PASSWORD},
        timeout=TIMEOUT_SECONDS,
    )
    assert response.status_code == 200, (
        f"Falha na autenticação: {response.status_code} {response.text}"
    )
    token = response.json().get("token")
    assert token, "A resposta de autenticação não contém token."
    return token


def delete_booking(booking_id, token):
    return requests.delete(
        f"{BASE_URL}/booking/{booking_id}",
        headers={"Cookie": f"token={token}"},
        timeout=TIMEOUT_SECONDS,
    )


def cleanup_booking(booking_id):
    """Tenta remover uma reserva de apoio; não mascara o resultado do teste."""
    try:
        token = get_token()
        delete_booking(booking_id, token)
    except requests.RequestException:
        pass


def test_CT_01_excluir_reserva_sem_token():
    booking_id, _ = create_booking()
    try:
        delete_response = requests.delete(
            f"{BASE_URL}/booking/{booking_id}",
            timeout=TIMEOUT_SECONDS,
        )
        assert delete_response.status_code == 403

        get_response = requests.get(
            f"{BASE_URL}/booking/{booking_id}",
            timeout=TIMEOUT_SECONDS,
        )
        assert get_response.status_code == 200
    finally:
        cleanup_booking(booking_id)


def test_CT_02_excluir_reserva_com_token_invalido():
    booking_id, _ = create_booking()
    try:
        delete_response = requests.delete(
            f"{BASE_URL}/booking/{booking_id}",
            headers={"Cookie": "token=invalid-token"},
            timeout=TIMEOUT_SECONDS,
        )
        assert delete_response.status_code == 403

        get_response = requests.get(
            f"{BASE_URL}/booking/{booking_id}",
            timeout=TIMEOUT_SECONDS,
        )
        assert get_response.status_code == 200
    finally:
        cleanup_booking(booking_id)


def test_CT_03_excluir_reserva_com_token_valido():
    booking_id, _ = create_booking()
    try:
        token = get_token()
        delete_response = delete_booking(booking_id, token)
        assert delete_response.status_code == 201
    finally:
        cleanup_booking(booking_id)


def test_CT_04_consultar_reserva_excluida():
    booking_id, _ = create_booking()
    token = get_token()

    delete_response = delete_booking(booking_id, token)
    assert delete_response.status_code == 201

    get_response = requests.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=TIMEOUT_SECONDS,
    )
    assert get_response.status_code == 404


def test_CT_05_repetir_exclusao_sem_afetar_outra_reserva():
    first_booking_id, _ = create_booking()
    second_booking_id, _ = create_booking()
    token = get_token()

    try:
        first_delete = delete_booking(first_booking_id, token)
        assert first_delete.status_code == 201

        repeated_delete = delete_booking(first_booking_id, token)
        assert 400 <= repeated_delete.status_code < 500

        second_get = requests.get(
            f"{BASE_URL}/booking/{second_booking_id}",
            timeout=TIMEOUT_SECONDS,
        )
        assert second_get.status_code == 200
    finally:
        cleanup_booking(first_booking_id)
        cleanup_booking(second_booking_id)


def test_CT_06_listar_reservas_filtrando_nome_exclusivo_apos_exclusao():
    firstname = unique_name("Unique")
    booking_id, _ = create_booking(firstname=firstname)
    token = get_token()

    delete_response = delete_booking(booking_id, token)
    assert delete_response.status_code == 201

    list_response = requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": firstname},
        timeout=TIMEOUT_SECONDS,
    )
    assert list_response.status_code == 200
    assert list_response.json() == []
