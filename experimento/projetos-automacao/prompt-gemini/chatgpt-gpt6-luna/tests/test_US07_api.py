import uuid

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
REQUEST_TIMEOUT = 15


def criar_payload(nome, sobrenome):
    return {
        "firstname": nome,
        "lastname": sobrenome,
        "totalprice": 123,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-11-01",
            "checkout": "2026-11-05",
        },
        "additionalneeds": "Café da manhã",
    }


def criar_reserva(payload):
    response = requests.post(
        f"{BASE_URL}/booking",
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    return response


def dados_unicos():
    sufixo = uuid.uuid4().hex[:12]
    return f"Teste{sufixo}", f"Reserva{sufixo}"


def test_CT_01_criar_reserva_com_dados_validos():
    nome, sobrenome = dados_unicos()
    payload = criar_payload(nome, sobrenome)

    response = criar_reserva(payload)

    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body.get("bookingid"), int)
    assert body.get("booking") == payload


def test_CT_02_consultar_reserva_criada():
    nome, sobrenome = dados_unicos()
    payload = criar_payload(nome, sobrenome)

    create_response = criar_reserva(payload)
    assert create_response.status_code == 200, create_response.text
    booking_id = create_response.json().get("bookingid")
    assert isinstance(booking_id, int)

    response = requests.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200, response.text
    assert response.json() == payload


def test_CT_03_consultar_identificador_inexistente():
    response = requests.get(
        f"{BASE_URL}/booking/99999999",
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 404


def test_CT_04_listar_reservas_por_nome_e_sobrenome_unicos():
    nome, sobrenome = dados_unicos()
    payload = criar_payload(nome, sobrenome)

    create_response = criar_reserva(payload)
    assert create_response.status_code == 200, create_response.text
    booking_id = create_response.json().get("bookingid")
    assert isinstance(booking_id, int)

    response = requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": nome, "lastname": sobrenome},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200, response.text
    bookings = response.json()
    assert isinstance(bookings, list)
    assert any(
        isinstance(item, dict) and item.get("bookingid") == booking_id
        for item in bookings
    )
