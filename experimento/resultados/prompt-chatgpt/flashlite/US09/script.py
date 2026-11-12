import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 10
ADMIN_USER = "admin"
ADMIN_PASS = "password123"


def get_auth_token():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": ADMIN_USER, "password": ADMIN_PASS},
        timeout=TIMEOUT,
    )
    assert response.status_code == 200
    return response.json().get("token")


def create_test_booking(firstname="TestFirst", lastname="TestLast"):
    payload = {
        "firstname": firstname,
        "lastname": lastname,
        "totalprice1": 111,  # Note: restful-booker expects totalprice
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"},
        "additionalneeds": "Breakfast",
    }
    response = requests.post(
        f"{BASE_URL}/booking", json=payload, timeout=TIMEOUT
    )
    assert response.status_code == 200
    data = response.json()
    return data["bookingid"]


def test_CT001_exclusao_sem_token_falha():
    booking_id = create_test_booking(
        firstname="NoToken", lastname="Booking"
    )

    # Tenta excluir sem token
    delete_response = requests.delete(
        f"{BASE_URL}/booking/{booking_id}", timeout=TIMEOUT
    )
    assert delete_response.status_code == 403

    # Verifica se a reserva continua consultável com status 200
    get_response = requests.get(
        f"{BASE_URL}/booking/{booking_id}", timeout=TIMEOUT
    )
    assert get_response.status_code == 200


def test_CT002_exclusao_com_token_invalido_falha():
    booking_id = create_test_booking(
        firstname="InvalidToken", lastname="Booking"
    )

    # Tenta excluir com token inválido
    cookies = {"token": "invalidtoken123"}
    delete_response = requests.delete(
        f"{BASE_URL}/booking/{booking_id}", cookies=cookies, timeout=TIMEOUT
    )
    assert delete_response.status_code == 403

    # Verifica se a reserva continua existindo
    get_response = requests.get(
        f"{BASE_URL}/booking/{booking_id}", timeout=TIMEOUT
    )
    assert get_response.status_code == 200


def test_CT003_exclusao_com_token_valido_sucede():
    token = get_auth_token()
    booking_id = create_test_booking(
        firstname="ValidToken", lastname="Booking"
    )

    cookies = {"token": token}
    delete_response = requests.delete(
        f"{BASE_URL}/booking/{booking_id}", cookies=cookies, timeout=TIMEOUT
    )
    assert delete_response.status_code == 201


def test_CT004_consulta_de_reserva_excluida_retorna_nao_encontrada():
    token = get_auth_token()
    booking_id = create_test_booking(
        firstname="DeletedCheck", lastname="Booking"
    )

    cookies = {"token": token}
    delete_response = requests.delete(
        f"{BASE_URL}/booking/{booking_id}", cookies=cookies, timeout=TIMEOUT
    )
    assert delete_response.status_code == 201

    get_response = requests.get(
        f"{BASE_URL}/booking/{booking_id}", timeout=TIMEOUT
    )
    assert get_response.status_code == 404


def test_CT005_exclusao_repetida_de_reserva_retorna_erro_4xx():
    token = get_auth_token()
    booking_id = create_test_booking(
        firstname="DoubleDelete", lastname="Booking"
    )

    cookies = {"token": token}
    delete_response_first = requests.delete(
        f"{BASE_URL}/booking/{booking_id}", cookies=cookies, timeout=TIMEOUT
    )
    assert delete_response_first.status_code == 201

    delete_response_second = requests.delete(
        f"{BASE_URL}/booking/{booking_id}", cookies=cookies, timeout=TIMEOUT
    )
    assert 400 <= delete_response_second.status_code < 500


def test_CT006_listagem_por_filtro_apos_exclusao_retorna_vazio():
    unique_name = "UniqueTargetName12345"
    token = get_auth_token()
    booking_id = create_test_booking(
        firstname=unique_name, lastname="FilterTest"
    )

    cookies = {"token": token}
    delete_response = requests.delete(
        f"{BASE_URL}/booking/{booking_id}", cookies=cookies, timeout=TIMEOUT
    )
    assert delete_response.status_code == 201

    list_response = requests.get(
        f"{BASE_URL}/booking", params={"firstname": unique_name}, timeout=TIMEOUT
    )
    assert list_response.status_code == 200
    bookings = list_response.json()
    assert len(bookings) == 0
