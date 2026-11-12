import uuid

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
REQUEST_TIMEOUT_SECONDS = 15

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}


def make_booking(firstname="Ana", lastname="Silva"):
    return {
        "firstname": firstname,
        "lastname": lastname,
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2027-05-10",
            "checkout": "2027-05-15",
        },
        "additionalneeds": "Breakfast",
    }


def create_booking(payload):
    response = requests.post(
        f"{BASE_URL}/booking",
        json=payload,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return response


def assert_booking_fields(actual, expected):
    assert actual["firstname"] == expected["firstname"]
    assert actual["lastname"] == expected["lastname"]
    assert actual["totalprice"] == expected["totalprice"]
    assert actual["depositpaid"] == expected["depositpaid"]
    assert actual["bookingdates"]["checkin"] == expected["bookingdates"]["checkin"]
    assert actual["bookingdates"]["checkout"] == expected["bookingdates"]["checkout"]
    assert actual["additionalneeds"] == expected["additionalneeds"]


def test_CT001_criar_reserva_com_dados_validos():
    payload = make_booking()
    response = create_booking(payload)

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["bookingid"], int)
    assert body["bookingid"] > 0
    assert_booking_fields(body["booking"], payload)


def test_CT002_consultar_reserva_criada():
    payload = make_booking(firstname="Bruno", lastname="Costa")
    create_response = create_booking(payload)

    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]
    assert isinstance(booking_id, int)

    response = requests.get(
        f"{BASE_URL}/booking/{booking_id}",
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    assert_booking_fields(response.json(), payload)


def test_CT003_consultar_identificador_inexistente():
    response = requests.get(
        f"{BASE_URL}/booking/99999999",
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 404


def test_CT004_filtrar_reservas_por_nome_e_sobrenome():
    unique_suffix = uuid.uuid4().hex
    firstname = f"Teste{unique_suffix[:8]}"
    lastname = f"Reserva{unique_suffix[8:16]}"
    payload = make_booking(firstname=firstname, lastname=lastname)

    create_response = create_booking(payload)

    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]
    assert isinstance(booking_id, int)

    response = requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": firstname, "lastname": lastname},
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    assert response.status_code == 200
    bookings = response.json()
    assert isinstance(bookings, list)
    assert any(item["bookingid"] == booking_id for item in bookings)
