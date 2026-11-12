import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 10

@pytest.fixture
def unique_booking_data():
    import time
    unique_suffix = str(int(time.time() * 1000))
    return {
        "firstname": f"TestFirst{unique_suffix}",
        "lastname": f"TestLast{unique_suffix}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-01-01",
            "checkout": "2026-01-10"
        },
        "additionalneeds": "Lunch"
    }

def test_CT001_criar_reserva_valida(unique_booking_data):
    url = f"{BASE_URL}/booking"
    response = requests.post(url, json=unique_booking_data, timeout=TIMEOUT)
    assert response.status_code == 200
    data = response.json()
    assert "bookingid" in data
    assert isinstance(data["bookingid"], int)
    booking = data["booking"]
    assert booking["firstname"] == unique_booking_data["firstname"]
    assert booking["lastname"] == unique_booking_data["lastname"]
    assert booking["totalprice"] == unique_booking_data["totalprice"]
    assert booking["depositpaid"] == unique_booking_data["depositpaid"]
    assert booking["bookingdates"]["checkin"] == unique_booking_data["bookingdates"]["checkin"]
    assert booking["bookingdates"]["checkout"] == unique_booking_data["bookingdates"]["checkout"]
    assert booking["additionalneeds"] == unique_booking_data["additionalneeds"]

def test_CT002_consultar_reserva_existente(unique_booking_data):
    url_create = f"{BASE_URL}/booking"
    create_response = requests.post(url_create, json=unique_booking_data, timeout=TIMEOUT)
    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]

    url_get = f"{BASE_URL}/booking/{booking_id}"
    get_response = requests.get(url_get, timeout=TIMEOUT)
    assert get_response.status_code == 200
    booking = get_response.json()
    assert booking["firstname"] == unique_booking_data["firstname"]
    assert booking["lastname"] == unique_booking_data["lastname"]
    assert booking["totalprice"] == unique_booking_data["totalprice"]
    assert booking["depositpaid"] == unique_booking_data["depositpaid"]
    assert booking["bookingdates"]["checkin"] == unique_booking_data["bookingdates"]["checkin"]
    assert booking["bookingdates"]["checkout"] == unique_booking_data["bookingdates"]["checkout"]
    assert booking["additionalneeds"] == unique_booking_data["additionalneeds"]

def test_CT003_consultar_reserva_inexistente():
    url = f"{BASE_URL}/booking/99999999"
    response = requests.get(url, timeout=TIMEOUT)
    assert response.status_code == 404

def test_CT004_filtrar_reservas_por_nome(unique_booking_data):
    url_create = f"{BASE_URL}/booking"
    create_response = requests.post(url_create, json=unique_booking_data, timeout=TIMEOUT)
    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]

    fn = unique_booking_data["firstname"]
    ln = unique_booking_data["lastname"]
    url_filter = f"{BASE_URL}/booking?firstname={fn}&lastname={ln}"
    filter_response = requests.get(url_filter, timeout=TIMEOUT)
    assert filter_response.status_code == 200
    results = filter_response.json()
    
    found = any(item.get("bookingid") == booking_id for item in results)
    assert found is True
