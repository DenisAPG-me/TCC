import uuid

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"


def _booking_payload(firstname=None, lastname=None):
    suffix = uuid.uuid4().hex[:10]
    return {
        "firstname": firstname or f"Teste{suffix}",
        "lastname": lastname or f"Reserva{suffix}",
        "totalprice": 123,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2027-01-10",
            "checkout": "2027-01-15",
        },
        "additionalneeds": "Café da manhã",
    }


def _create_booking(payload):
    response = requests.post(
        f"{BASE_URL}/booking",
        json=payload,
        headers={"Accept": "application/json"},
        timeout=30,
    )
    return response


def test_TC01_criar_reserva_com_dados_validos():
    payload = _booking_payload()

    response = _create_booking(payload)

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("bookingid"), int)
    assert body.get("booking") == payload


def test_TC02_consultar_reserva_recém_criada():
    payload = _booking_payload()
    create_response = _create_booking(payload)

    assert create_response.status_code == 200
    booking_id = create_response.json().get("bookingid")
    assert isinstance(booking_id, int)

    response = requests.get(
        f"{BASE_URL}/booking/{booking_id}",
        headers={"Accept": "application/json"},
        timeout=30,
    )

    assert response.status_code == 200
    assert response.json() == payload


def test_TC03_consultar_identificador_inexistente():
    response = requests.get(
        f"{BASE_URL}/booking/99999999",
        headers={"Accept": "application/json"},
        timeout=30,
    )

    assert response.status_code == 404


def test_TC04_listar_reserva_por_nome_e_sobrenome_unicos():
    payload = _booking_payload()
    create_response = _create_booking(payload)

    assert create_response.status_code == 200
    booking_id = create_response.json().get("bookingid")
    assert isinstance(booking_id, int)

    response = requests.get(
        f"{BASE_URL}/booking",
        params={
            "firstname": payload["firstname"],
            "lastname": payload["lastname"],
        },
        timeout=30,
    )

    assert response.status_code == 200
    booking_ids = response.json()
    assert isinstance(booking_ids, list)
    assert any(
        isinstance(item, dict) and item.get("bookingid") == booking_id
        for item in booking_ids
    )
