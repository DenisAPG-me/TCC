import time
import requests
import pytest

BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 10


def test_ct01_criar_reserva_com_dados_validos():
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-01-01",
            "checkout": "2026-01-05"
        },
        "additionalneeds": "Breakfast"
    }
    response = requests.post(f"{BASE_URL}/booking", json=payload, timeout=TIMEOUT)
    assert response.status_code == 200
    data = response.json()
    assert "bookingid" in data
    assert isinstance(data["bookingid"], int)
    assert data["booking"]["firstname"] == payload["firstname"]
    assert data["booking"]["lastname"] == payload["lastname"]
    assert data["booking"]["totalprice"] == payload["totalprice"]
    assert data["booking"]["depositpaid"] == payload["depositpaid"]
    assert data["booking"]["bookingdates"]["checkin"] == payload["bookingdates"]["checkin"]
    assert data["booking"]["bookingdates"]["checkout"] == payload["bookingdates"]["checkout"]
    assert data["booking"]["additionalneeds"] == payload["additionalneeds"]


def test_ct02_consultar_reserva_existente_por_identificador():
    payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "totalprice": 200,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2026-03-10",
            "checkout": "2026-03-15"
        },
        "additionalneeds": "Lunch"
    }
    create_response = requests.post(f"{BASE_URL}/booking", json=payload, timeout=TIMEOUT)
    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]

    get_response = requests.get(f"{BASE_URL}/booking/{booking_id}", timeout=TIMEOUT)
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["firstname"] == payload["firstname"]
    assert data["firstname"] == payload["firstname"]
    assert data["lastname"] == payload["lastname"]
    assert data["totalprice"] == payload["totalprice"]
    assert data["depositpaid"] == payload["depositpaid"]
    assert data["bookingdates"]["checkin"] == payload["bookingdates"]["checkin"]
    assert data["bookingdates"]["checkout"] == payload["bookingdates"]["checkout"]
    assert data["additionalneeds"] == payload["additionalneeds"]


def test_ct03_consultar_reserva_com_identificador_inexistente():
    response = requests.get(f"{BASE_URL}/booking/99999999", timeout=TIMEOUT)
    assert response.status_code == 404


def test_ct04_listar_reservas_filtrando_por_nome_e_sobrenome_unicos():
    unique_suffix = str(int(time.time() * 1000))
    unique_firstname = f"TestFirst{unique_suffix}"
    unique_lastname = f"TestLast{unique_suffix}"

    payload = {
        "firstname": unique_firstname,
        "lastname": unique_lastname,
        "totalprice": 300,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-06-01",
            "checkout": "2026-06-10"
        },
        "additionalneeds": "Dinner"
    }
    create_response = requests.post(f"{BASE_URL}/booking", json=payload, timeout=TIMEOUT)
    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]

    params = {
        "firstname": unique_firstname,
        "lastname": unique_lastname
    }
    list_response = requests.get(f"{BASE_URL}/booking", params=params, timeout=TIMEOUT)
    assert list_response.status_code == 200
    bookings = list_response.json()
    assert isinstance(bookings, list)
    matching_ids = [b["bookingid"] for b in bookings if b["bookingid"] == booking_id]
    assert len(matching_ids) == 1
