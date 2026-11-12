import random
import string

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 15
AUTH_CREDENTIALS = {"username": "admin", "password": "password123"}
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
INEXISTENT_BOOKING_ID = 99999999
ZERO_BOOKING_ID = 0
VALID_BOOKING_DATES = {"checkin": "2026-01-10", "checkout": "2026-01-15"}


def random_word(size=10):
    return "".join(random.choices(string.ascii_lowercase, k=size)).capitalize()


def build_payload(totalprice=150, depositpaid=True):
    return {
        "firstname": random_word(),
        "lastname": random_word(),
        "totalprice": totalprice,
        "depositpaid": depositpaid,
        "bookingdates": dict(VALID_BOOKING_DATES),
        "additionalneeds": "Breakfast",
    }


def create_booking(payload):
    return requests.post(f"{BASE_URL}/booking", json=payload, headers=JSON_HEADERS, timeout=TIMEOUT)


def create_tracked_booking(payload, created_ids):
    response = create_booking(payload)
    assert response.status_code == 200, response.text
    booking_id = response.json()["bookingid"]
    created_ids.append(booking_id)
    return booking_id


@pytest.fixture(scope="session")
def auth_token():
    response = requests.post(f"{BASE_URL}/auth", json=AUTH_CREDENTIALS, headers=JSON_HEADERS, timeout=TIMEOUT)
    assert response.status_code == 200, response.text
    token = response.json().get("token")
    assert token, response.text
    return token


@pytest.fixture
def created_ids(auth_token):
    ids = []
    yield ids
    for booking_id in ids:
        response = requests.delete(
            f"{BASE_URL}/booking/{booking_id}",
            headers={"Cookie": f"token={auth_token}"},
            timeout=TIMEOUT,
        )
        assert response.status_code == 201, response.text


def test_CT001_criar_reserva_com_dados_validos_retorna_200_e_dados_gravados(created_ids):
    payload = build_payload()
    response = create_booking(payload)
    assert response.status_code == 200, response.text
    body = response.json()
    created_ids.append(body["bookingid"])
    assert isinstance(body["bookingid"], int)
    assert body["booking"] == payload


def test_CT002_consultar_reserva_por_id_retorna_200_e_todos_os_campos(created_ids):
    payload = build_payload()
    booking_id = create_tracked_booking(payload, created_ids)
    response = requests.get(f"{BASE_URL}/booking/{booking_id}", headers=JSON_HEADERS, timeout=TIMEOUT)
    assert response.status_code == 200, response.text
    assert response.json() == payload


def test_CT003_consultar_identificador_inexistente_retorna_404():
    response = requests.get(
        f"{BASE_URL}/booking/{INEXISTENT_BOOKING_ID}", headers=JSON_HEADERS, timeout=TIMEOUT
    )
    assert response.status_code == 404


def test_CT004_consultar_identificador_zero_retorna_404():
    response = requests.get(f"{BASE_URL}/booking/{ZERO_BOOKING_ID}", headers=JSON_HEADERS, timeout=TIMEOUT)
    assert response.status_code == 404


def test_CT005_listar_por_nome_e_sobrenome_unicos_contem_id_criado(created_ids):
    payload = build_payload()
    booking_id = create_tracked_booking(payload, created_ids)
    response = requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": payload["firstname"], "lastname": payload["lastname"]},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, response.text
    booking_ids = [item["bookingid"] for item in response.json()]
    assert booking_id in booking_ids


def test_CT006_listar_por_nome_e_sobrenome_inexistentes_retorna_lista_vazia():
    response = requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": random_word(), "lastname": random_word()},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, response.text
    assert response.json() == []


def test_CT007_criar_reserva_com_total_zero_e_deposito_nao_pago_retorna_200_e_dados_gravados(created_ids):
    payload = build_payload(totalprice=0, depositpaid=False)
    response = create_booking(payload)
    assert response.status_code == 200, response.text
    body = response.json()
    created_ids.append(body["bookingid"])
    assert body["booking"] == payload
