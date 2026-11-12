import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"

@pytest.fixture
def booking_payload():
    return {
        "firstname": "John",
        "lastname": "DoeTest",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-06-01",
            "checkout": "2026-06-10"
        },
        "additionalneeds": "Lunch"
    }

def test_TC01_criar_reserva_valida(booking_payload):
    response = requests.post(f"{BASE_URL}/booking", json=booking_payload)
    assert response.status_code == 200
    data = response.json()
    assert "bookingid" in data
    assert isinstance(data["bookingid"], int)
    
    created_booking = data["booking"]
    assert created_booking["firstname"] == booking_payload["firstname"]
    assert created_booking["lastname"] == booking_payload["lastname"]
    assert created_booking["totalprice"] == booking_payload["totalprice"]
    assert created_booking["depositpaid"] == booking_payload["depositpaid"]
    assert created_booking["bookingdates"] == booking_payload["bookingdates"]
    assert created_booking["additionalneeds"] == booking_payload["additionalneeds"]

def test_TC02_consultar_reserva_existente(booking_payload):
    post_response = requests.post(f"{BASE_URL}/booking", json=booking_payload)
    assert post_response.status_code == 200
    booking_id = post_response.json()["bookingid"]

    get_response = requests.get(f"{BASE_URL}/booking/{booking_id}")
    assert get_response.status_code == 200
    data = get_response.json()

    assert data["firstname"] == booking_payload["firstname"]
    assert data["lastname"] == booking_payload["lastname"]
    assert data["totalprice"] == booking_payload["totalprice"]
    assert data["depositpaid"] == booking_payload["depositpaid"]
    assert data["bookingdates"] == booking_payload["bookingdates"]
    assert data["additionalneeds"] == booking_payload["additionalneeds"]

def test_TC03_consultar_reserva_inexistente():
    response = requests.get(f"{BASE_URL}/booking/99999999")
    assert response.status_code == 404

def test_TC04_listar_reservas_filtrando_por_nome():
    unique_payload = {
        "firstname": "UniqueNameX",
        "lastname": "UniqueLastNameY",
        "totalprice": 200,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2026-07-01",
            "checkout": "2026-07-05"
        },
        "additionalneeds": "Dinner"
    }
    post_response = requests.post(f"{BASE_URL}/booking", json=unique_payload)
    assert post_response.status_code == 200
    booking_id = post_response.json()["bookingid"]

    params = {
        "firstname": unique_payload["firstname"],
        "lastname": unique_payload["lastname"]
    }
    get_response = requests.get(f"{BASE_URL}/booking", params=params)
    assert get_response.status_code == 200
    
    bookings_list = get_response.json()
    ids = [item.get("bookingid") for item in bookings_list]
    assert booking_id in ids
