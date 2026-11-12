import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 10

def _get_auth_token():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": "admin", "password": "password123"},
        timeout=TIMEOUT
    )
    return response.json().get("token")

def _create_sample_booking():
    payload = {
        "firstname": "Jim",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2018-01-01",
            "checkout": "2019-01-01"
        },
        "additionalneeds": "Breakfast"
    }
    response = requests.post(
        f"{BASE_URL}/booking",
        json=payload,
        timeout=TIMEOUT
    )
    return response.json().get("bookingid")

def test_CT001_autenticacao_valida():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": "admin", "password": "password123"},
        timeout=TIMEOUT
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert len(data["token"]) > 0

def test_CT002_autenticacao_invalida():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": "invalid_user", "password": "wrongpassword"},
        timeout=TIMEOUT
    )
    data = response.json()
    assert "token" not in data
    assert data.get("reason") == "Bad credentials"

def test_CT003_atualizacao_completa():
    booking_id = _create_sample_booking()
    token = _get_auth_token()
    
    updated_payload = {
        "firstname": "JamesNew",
        "lastname": "Bond",
        "totalprice": 999,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2024-01-01",
            "checkout": "2024-01-10"
        },
        "additionalneeds": "Lunch"
    }
    
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        headers={
            "Cookie": f"token={token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json=updated_payload,
        timeout=TIMEOUT
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["firstname"] == "JamesNew"
    assert data["totalprice"] == 999

def test_CT004_atualizacao_parcial():
    booking_id = _create_sample_booking()
    token = _get_auth_token()
    
    partial_payload = {
        "lastname": "UpdatedLastName"
    }
    
    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}",
        headers={
            "Cookie": f"token={token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json=partial_payload,
        timeout=TIMEOUT
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["lastname"] == "UpdatedLastName"
    assert data["firstname"] == "Jim"
    assert data["totalprice"] == 111

def test_CT005_atualizacao_sem_token():
    booking_id = _create_sample_booking()
    
    updated_payload = {
        "firstname": "NoToken",
        "lastname": "User",
        "totalprice": 100,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2024-01-01",
            "checkout": "2024-01-02"
        },
        "additionalneeds": "None"
    }
    
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json=updated_payload,
        timeout=TIMEOUT
    )
    
    assert response.status_code == 403

def test_CT006_atualizacao_campos_obrigatorios_ausentes():
    booking_id = _create_sample_booking()
    token = _get_auth_token()
    
    incomplete_payload = {
        "totalprice": 500
    }
    
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        headers={
            "Cookie": f"token={token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json=incomplete_payload,
        timeout=TIMEOUT
    )
    
    assert response.status_code == 400
