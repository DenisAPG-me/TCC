import sys
import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
BOOKING_URL = f"{BASE_URL}/booking"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
TIMEOUT = 30
NONEXISTENT_ID = 99999999


def unique_suffix():
    return uuid.uuid4().hex[:12]


def build_payload(**overrides):
    suffix = unique_suffix()
    payload = {
        "firstname": f"Nome{suffix}",
        "lastname": f"Sobrenome{suffix}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-15"},
        "additionalneeds": "Breakfast",
    }
    payload.update(overrides)
    return payload


def create_booking(payload):
    return requests.post(BOOKING_URL, json=payload, headers=HEADERS, timeout=TIMEOUT)


def get_booking(booking_id):
    return requests.get(f"{BOOKING_URL}/{booking_id}", headers=HEADERS, timeout=TIMEOUT)


def list_bookings(firstname, lastname):
    return requests.get(
        BOOKING_URL,
        params={"firstname": firstname, "lastname": lastname},
        headers=HEADERS,
        timeout=TIMEOUT,
    )


def assert_create_and_retrieve(payload):
    create_response = create_booking(payload)
    assert create_response.status_code == 200, create_response.text
    body = create_response.json()
    booking_id = body["bookingid"]
    assert isinstance(booking_id, int) and not isinstance(booking_id, bool)
    assert body["booking"] == payload

    get_response = get_booking(booking_id)
    assert get_response.status_code == 200, get_response.text
    assert get_response.json() == payload


@pytest.fixture
def created_booking():
    payload = build_payload()
    response = create_booking(payload)
    assert response.status_code == 200, response.text
    return payload, response.json()["bookingid"]


def test_ct01_criar_reserva_com_corpo_valido():
    payload = build_payload()

    response = create_booking(payload)

    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body["bookingid"], int) and not isinstance(body["bookingid"], bool)
    assert body["booking"] == payload


def test_ct02_consultar_reserva_criada_pelo_identificador(created_booking):
    payload, booking_id = created_booking

    response = get_booking(booking_id)

    assert response.status_code == 200, response.text
    assert response.json() == payload


def test_ct03_consultar_reserva_com_identificador_inexistente():
    response = get_booking(NONEXISTENT_ID)

    assert response.status_code == 404


def test_ct04_listar_reservas_filtrando_por_nome_e_sobrenome_unicos(created_booking):
    payload, booking_id = created_booking

    response = list_bookings(payload["firstname"], payload["lastname"])

    assert response.status_code == 200, response.text
    ids = [item["bookingid"] for item in response.json()]
    assert booking_id in ids


def test_ct05_filtrar_por_nome_e_sobrenome_sem_reservas_correspondentes():
    suffix = unique_suffix()

    response = list_bookings(f"Inexistente{suffix}", f"Ninguem{suffix}")

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_ct06_criar_e_consultar_reserva_com_deposito_nao_pago():
    assert_create_and_retrieve(build_payload(depositpaid=False))


def test_ct07_criar_e_consultar_reserva_com_checkin_igual_checkout():
    payload = build_payload(bookingdates={"checkin": "2026-12-01", "checkout": "2026-12-01"})
    assert_create_and_retrieve(payload)


def test_ct08_criar_e_consultar_reserva_com_preco_total_zero():
    assert_create_and_retrieve(build_payload(totalprice=0))


def test_ct09_criar_e_consultar_reserva_com_acentos_e_caracteres_especiais():
    suffix = unique_suffix()
    payload = build_payload(
        firstname=f"João{suffix}",
        lastname=f"Conceição-D'Ávila{suffix}",
        additionalneeds="Café da manhã & berço extra",
    )
    assert_create_and_retrieve(payload)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
