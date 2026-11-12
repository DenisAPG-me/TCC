import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"

@pytest.fixture(scope="session")
def auth_token():
    auth_response = requests.post(f"{BASE_URL}/auth", json={
        "username": "admin",
        "password": "password123"
    })
    assert auth_response.status_code == 200
    token = auth_response.json().get("token")
    assert token is not None
    return token

@pytest.fixture
def f_sample_booking():
    booking_data = {
        "firstname": "TestUserUnique",
        "lastname": "Integration",
        "totalprice:int" if False else "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-01-01",
            "checkout": "2026-01-02"
        },
        "additionalneeds": "Breakfast"
    }
    response = requests.post(f"{BASE_URL}/booking", json=booking_data)
    assert response.status_code == 200
    data = response.json()
    booking_id = data.get("bookingid")
    return booking_id, booking_data

def test_TC01_excluir_reserva_sem_token(f_sample_booking):
    booking_id, _ = f_sample_booking
    
    # Tentar excluir sem token
    delete_response = requests.delete(f"{BASE_URL}/booking/{booking_id}")
    assert delete_response.status_code == 403
    
    # A reserva continua consultável com status 200
    get_response = requests.get(f"{BASE_URL}/booking/{booking_id}")
    assert get_response.status_code == 200

def test_TC02_excluir_reserva_token_invalido(f_sample_booking):
    booking_id, _ = f_sample_booking
    
    # Tentar excluir com token inválido
    headers = {"Cookie": "token=invalid_token_123"}
    delete_response = requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers)
    assert delete_response.status_code == 403
    
    # A reserva continua existindo
    get_response = requests.get(f"{BASE_URL}/booking/{booking_id}")
    assert get_response.status_code == 200

def test_TC03_excluir_reserva_token_valido(f_sample_booking, f_auth_token):
    booking_id, _ = f_sample_booking
    
    headers = {"Cookie": f"token={f_auth_token}"}
    delete_response = requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers)
    assert delete_response.status_code == 201

def test_TC04_consultar_reserva_apos_exclusao(f_sample_booking, f_auth_token):
    booking_id, _ = f_sample_booking
    
    # Excluir
    headers = {"Cookie": f"token={f_auth_token}"}
    requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers)
    
    # Consultar pelo mesmo identificador
    get_response = requests.get(f"{BASE_URL}/booking/{booking_id}")
    assert get_response.status_code == 404

def test_TC05_excluir_reserva_novamente(f_sample_booking, f_auth_token):
    booking_id, _ = f_sample_booking
    
    headers = {"Cookie": f"token={f_auth_token}"}
    
    # Primeira exclusão
    first_delete = requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers)
    assert first_delete.status_code == 201
    
    # Segunda exclusão
    second_delete = requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers)
    assert 400 <= second_delete.status_code < 500

def test_TC06_listar_reservas_filtrando_nome_apos_exclusao(f_sample_booking, f_auth_token):
    booking_id, booking_data = f_sample_booking
    fname = booking_data["firstname"]
    lname = booking_data["lastname"]
    
    # Excluir
    headers = {"Cookie": f"token={f_auth_token}"}
    requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers)
    
    # Listar filtrando pelo nome único
    list_response = requests.get(f"{BASE_URL}/booking", params={"firstname": fname, "lastname": lname})
    assert list_response.status_code == 200
    reservations = list_response.json()
    
    # Verificar se a lista retornada está vazia ou não contém o ID excluído
    matching_ids = [r for r in reservations if r.get("bookingid") == booking_id]
    assert len(matching_ids) == 0
