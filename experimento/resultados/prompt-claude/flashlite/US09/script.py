import pytest
import requests
import time

BASE_URL = "https://restful-booker.herokuapp.com"
ADMIN_USER = "admin"
ADMIN_PASS = "password123"
REQUEST_TIMEOUT = 10

def obter_token():
    url = f"{BASE_URL}/auth"
    payload = {
        "username": ADMIN_USER,
        "password": ADMIN_PASS
    }
    response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    assert response.status_code == 200
    return response.json().get("token")

def criar_reserva_teste(firstname, lastname):
    url = f"{BASE_URL}/booking"
    payload = {
        "firstname": firstname,
        "lastname": lastname,
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-01-01",
            "checkout": "2026-01-02"
        },
        "additionalneeds": "Breakfast"
    }
    response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    assert response.status_code == 200
    data = response.json()
    return data["bookingid"]

def test_ct01_tentar_excluir_reserva_sem_token():
    unique_name = f"TestNoToken_{int(time.time() * 1000)}"
    booking_id = criar_reserva_teste(unique_name, "User")
    
    url = f"{BASE_URL}/booking/{booking_id}"
    response = requests.delete(url, timeout=REQUEST_TIMEOUT)
    assert response.status_code == 403
    
    get_response = requests.get(url, timeout=REQUEST_TIMEOUT)
    assert get_response.status_code == 200

def test_ct02_tentar_excluir_reserva_com_token_invalido():
    unique_name = f"TestInvalidToken_{int(time.time() * 1000)}"
    booking_id = criar_reserva_teste(unique_name, "User")
    
    url = f"{BASE_URL}/booking/{booking_id}"
    headers = {"Cookie": "token=invalidtoken123"}
    response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
    assert response.status_code == 403
    
    get_response = requests.get(url, timeout=REQUEST_TIMEOUT)
    assert get_response.status_code == 200

def test_ct03_excluir_reserva_com_token_valido():
    unique_name = f"TestValidToken_{int(time.time() * 1000)}"
    booking_id = criar_reserva_teste(unique_name, "User")
    
    token = obter_token()
    url = f"{BASE_URL}/booking/{booking_id}"
    headers = {"Cookie": f"token={token}"}
    response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
    assert response.status_code == 201

def test_ct04_consultar_reserva_apos_exclusao():
    unique_name = f"TestConsultDeleted_{int(time.time() * 1000)}"
    booking_id = criar_reserva_teste(unique_name, "User")
    
    token = obter_token()
    url = f"{BASE_URL}/booking/{booking_id}"
    headers = {"Cookie": f"token={token}"}
    
    del_response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
    assert del_response.status_code == 201
    
    get_response = requests.get(url, timeout=REQUEST_TIMEOUT)
    assert get_response.status_code == 404

def test_ct05_excluir_reserva_ja_excluida():
    unique_name = f"TestDoubleDelete_{int(time.time() * 1000)}"
    booking_id = criar_reserva_teste(unique_name, "User")
    
    token = obter_token()
    url = f"{BASE_URL}/booking/{booking_id}"
    headers = {"Cookie": f"token={token}"}
    
    del_response_1 = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
    assert del_response_1.status_code == 201
    
    del_response_2 = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
    assert 400 <= del_response_2.status_code < 500

def test_ct06_listar_reservas_filtrando_por_nome_unico_apos_exclusao():
    unique_name = f"UniqueTarget_{int(time.time() * 1000)}"
    booking_id = criar_reserva_teste(unique_name, "UniqueLast")
    
    token = obter_token()
    url = f"{BASE_URL}/booking/{booking_id}"
    headers = {"Cookie": f"token={token}"}
    
    del_response = requests.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
    assert del_response.status_code == 201
    
    list_url = f"{BASE_URL}/booking?firstname={unique_name}&lastname=UniqueLast"
    list_response = requests.get(list_url, timeout=REQUEST_TIMEOUT)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 0
