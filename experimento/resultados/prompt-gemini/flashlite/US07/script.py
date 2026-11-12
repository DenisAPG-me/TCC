import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"

@pytest.fixture
def unique_booking_data():
    import time
    unique_suffix = str(int(time.time() * 1000))
    return {
        "firstname": f"TestName{unique_suffix}",
        "lastname": f"TestLast{unique_suffix}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-06-01",
            "checkout": "2026-06-10"
        },
        "additionalneeds": "WiFi"
    }

def test_CT01_criar_reserva_com_dados_validos(unique_booking_data):
    response = requests.post(f"{BASE_URL}/booking", json=unique_booking_data)
    assert response.status_code == 200
    data = response.json()
    assert "bookingid" in data
    assert isinstance(data["bookingid"], int)
    
    booking = data["booking"]
    assert booking["firstname"] == unique_booking_data["firstname"]
    assert booking["lastname"] == unique_booking_data["lastname"]
    assert booking["totalprice"] == unique_booking_data["totalprice"]
    assert booking["depositpaid"] == unique_booking_data["depositpaid"]
    assert booking["bookingdates"] == unique_booking_data["bookingdates"]
    assert booking["additionalneeds"] == unique_booking_data["additionalneeds"]

def test_CT02_consultar_reserva_existente_por_id(unique_booking_data):
    post_response = requests.post(f"{BASE_URL}/booking", json=unique_booking_data)
    assert post_response.status_code == 200
    booking_id = post_response.json()["bookingid"]

    get_response = requests.get(f"{BASE_URL}/booking/{booking_id}")
    assert get_response.status_code == 200
    booking = get_response.json()
    
    assert booking["firstname"] == unique_booking_data["firstname"]
    assert booking["lastname"] == unique_booking_data["lastname"]
    assert booking["totalprice"] == unique_booking_data["totalprice"]
    assert booking["depositpaid"] == unique_booking_data["depositpaid"]
    assert booking["bookingdates"] == unique_booking_data["bookingdates"]
    assert booking["additionalneeds"] == unique_booking_data["additionalneeds"]

def test_CT03_consultar_reserva_com_id_inexistente():
    response = requests.get(f"{BASE_URL}/booking/99999999")
    assert response.status_code == 404

def test_CT04_listar_reservas_filtrando_por_nome_e_sobrenome_unicos(unique_booking_data):
    post_response = requests.post(f"{BASE_URL}/booking", json=unique_booking_data)
    assert post_response.status_code == 200
    booking_id = post_response.json()["bookingid"]

    params = {
        "firstname": unique_booking_data["firstname"],
        "lastname": unique_booking_data["lastname"]
    }
    get_response = requests.get(f"{BASE_URL}/booking", params=params)
    assert get_response.status_code == 200
    results = get_response.json()
    
    matched_ids = [item["bookingid"] for item in results]
    assert booking_id in matched_ids
