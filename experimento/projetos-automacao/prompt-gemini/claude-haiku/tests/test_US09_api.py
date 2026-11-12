import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
ADMIN_CREDENTIALS = {"username": "admin", "password": "password123"}
INVALID_TOKEN = "token-invalido-0000"
TIMEOUT = 30
JSON_HEADERS = {"Accept": "application/json"}


def get_booking(booking_id):
    return requests.get(f"{BASE_URL}/booking/{booking_id}", headers=JSON_HEADERS, timeout=TIMEOUT)


def delete_booking(booking_id, token=None):
    headers = {} if token is None else {"Cookie": f"token={token}"}
    return requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers, timeout=TIMEOUT)


@pytest.fixture(scope="session")
def token():
    response = requests.post(f"{BASE_URL}/auth", json=ADMIN_CREDENTIALS, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()["token"]


@pytest.fixture
def new_booking(token):
    created_ids = []

    def factory():
        name = f"Nome{uuid.uuid4().hex}"
        payload = {
            "firstname": name,
            "lastname": "Teste",
            "totalprice": 150,
            "depositpaid": True,
            "bookingdates": {"checkin": "2027-01-10", "checkout": "2027-01-15"},
            "additionalneeds": "Café da manhã",
        }
        response = requests.post(f"{BASE_URL}/booking", json=payload, headers=JSON_HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        booking_id = response.json()["bookingid"]
        created_ids.append(booking_id)
        return booking_id, name

    yield factory

    for booking_id in created_ids:
        delete_booking(booking_id, token)


def test_ct_01_excluir_sem_token_retorna_403_e_reserva_permanece(new_booking):
    booking_id, _ = new_booking()

    assert delete_booking(booking_id).status_code == 403
    assert get_booking(booking_id).status_code == 200


def test_ct_02_excluir_com_token_invalido_retorna_403_e_reserva_permanece(new_booking):
    booking_id, _ = new_booking()

    assert delete_booking(booking_id, INVALID_TOKEN).status_code == 403
    assert get_booking(booking_id).status_code == 200


def test_ct_03_excluir_com_token_valido_retorna_201(token, new_booking):
    booking_id, _ = new_booking()

    assert delete_booking(booking_id, token).status_code == 201


def test_ct_04_consultar_reserva_excluida_retorna_404(token, new_booking):
    booking_id, _ = new_booking()
    assert delete_booking(booking_id, token).status_code == 201

    assert get_booking(booking_id).status_code == 404


def test_ct_05_excluir_novamente_retorna_4xx_e_outra_reserva_nao_e_afetada(token, new_booking):
    booking_id, _ = new_booking()
    other_booking_id, _ = new_booking()
    assert delete_booking(booking_id, token).status_code == 201

    response = delete_booking(booking_id, token)

    assert 400 <= response.status_code < 500
    assert get_booking(other_booking_id).status_code == 200


def test_ct_06_listar_por_nome_unico_apos_exclusao_retorna_lista_vazia(token, new_booking):
    booking_id, name = new_booking()
    assert delete_booking(booking_id, token).status_code == 201

    response = requests.get(
        f"{BASE_URL}/booking", params={"firstname": name}, headers=JSON_HEADERS, timeout=TIMEOUT
    )

    assert response.status_code == 200
    assert response.json() == []


def test_ct_07_excluir_reserva_inexistente_com_token_valido_retorna_4xx(token):
    response = delete_booking(999999999, token)

    assert 400 <= response.status_code < 500


def test_ct_08_excluir_com_token_vazio_retorna_403_e_reserva_permanece(new_booking):
    booking_id, _ = new_booking()

    assert delete_booking(booking_id, "").status_code == 403
    assert get_booking(booking_id).status_code == 200
