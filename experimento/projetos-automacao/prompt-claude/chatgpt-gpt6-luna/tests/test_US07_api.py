import uuid

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
REQUEST_TIMEOUT = 10
MISSING_BOOKING_ID = 99999999


def make_booking(firstname="Ana", lastname="Silva"):
    return {
        "firstname": firstname,
        "lastname": lastname,
        "totalprice": 275,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2027-04-10",
            "checkout": "2027-04-15",
        },
        "additionalneeds": "Café da manhã",
    }


def create_booking(payload):
    response = requests.post(
        f"{BASE_URL}/booking",
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    return response


def test_ct01_criar_reserva_com_dados_validos():
    payload = make_booking()
    response = create_booking(payload)

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("bookingid"), int)
    assert body["bookingid"] > 0
    assert body.get("booking") == payload


def test_ct02_consultar_reserva_criada():
    payload = make_booking()
    create_response = create_booking(payload)

    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]

    get_response = requests.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=REQUEST_TIMEOUT,
    )

    assert get_response.status_code == 200
    assert get_response.json() == payload


def test_ct03_consultar_identificador_inexistente():
    response = requests.get(
        f"{BASE_URL}/booking/{MISSING_BOOKING_ID}",
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 404


def test_ct04_filtrar_por_nome_e_sobrenome_unicos():
    unique_suffix = uuid.uuid4().hex[:12]
    payload = make_booking(
        firstname=f"Ana{unique_suffix}",
        lastname=f"Silva{unique_suffix}",
    )
    create_response = create_booking(payload)

    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]

    list_response = requests.get(
        f"{BASE_URL}/booking",
        params={
            "firstname": payload["firstname"],
            "lastname": payload["lastname"],
        },
        timeout=REQUEST_TIMEOUT,
    )

    assert list_response.status_code == 200
    results = list_response.json()
    assert isinstance(results, list)
    assert any(
        isinstance(item, dict) and item.get("bookingid") == booking_id
        for item in results
    )


def test_ct05_filtrar_sem_reservas_correspondentes():
    unique_suffix = uuid.uuid4().hex
    response = requests.get(
        f"{BASE_URL}/booking",
        params={
            "firstname": f"Inexistente{unique_suffix}",
            "lastname": f"NaoEncontrado{unique_suffix}",
        },
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200
    assert response.json() == []
