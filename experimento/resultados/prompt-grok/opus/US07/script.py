import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
TIMEOUT = 30
NONEXISTENT_ID = 99999999


@pytest.fixture
def session():
    s = requests.Session()
    s.headers.update(HEADERS)
    yield s
    s.close()


def unique_suffix():
    return uuid.uuid4().hex[:10]


def build_payload(**overrides):
    payload = {
        "firstname": f"Nome{unique_suffix()}",
        "lastname": f"Sobrenome{unique_suffix()}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-15"},
        "additionalneeds": "Breakfast",
    }
    payload.update(overrides)
    return payload


def create_booking(session, payload):
    return session.post(f"{BASE_URL}/booking", json=payload, timeout=TIMEOUT)


def get_booking(session, booking_id):
    return session.get(f"{BASE_URL}/booking/{booking_id}", timeout=TIMEOUT)


def list_bookings(session, firstname, lastname):
    return session.get(
        f"{BASE_URL}/booking",
        params={"firstname": firstname, "lastname": lastname},
        timeout=TIMEOUT,
    )


def assert_valid_id(booking_id):
    assert isinstance(booking_id, int) and not isinstance(booking_id, bool)
    assert booking_id > 0


def create_and_fetch(session, payload):
    created = create_booking(session, payload)
    assert created.status_code == 200, created.text
    body = created.json()
    assert_valid_id(body["bookingid"])
    assert body["booking"] == payload

    fetched = get_booking(session, body["bookingid"])
    assert fetched.status_code == 200, fetched.text
    assert fetched.json() == payload


def test_TC01_criar_reserva_com_corpo_valido(session):
    payload = build_payload()

    response = create_booking(session, payload)

    assert response.status_code == 200, response.text
    body = response.json()
    assert_valid_id(body["bookingid"])
    assert body["booking"] == payload


def test_TC02_consultar_reserva_criada_por_id(session):
    payload = build_payload()
    created = create_booking(session, payload)
    assert created.status_code == 200, created.text
    booking_id = created.json()["bookingid"]

    response = get_booking(session, booking_id)

    assert response.status_code == 200, response.text
    assert response.json() == payload


def test_TC03_consultar_reserva_com_id_inexistente(session):
    response = get_booking(session, NONEXISTENT_ID)

    assert response.status_code == 404


def test_TC04_listar_reservas_filtrando_por_nome_e_sobrenome_unicos(session):
    payload = build_payload()
    created = create_booking(session, payload)
    assert created.status_code == 200, created.text
    booking_id = created.json()["bookingid"]

    response = list_bookings(session, payload["firstname"], payload["lastname"])

    assert response.status_code == 200, response.text
    ids = [item["bookingid"] for item in response.json()]
    assert booking_id in ids


def test_TC05_criar_reserva_com_deposito_nao_pago_e_preco_zero(session):
    payload = build_payload(totalprice=0, depositpaid=False)

    create_and_fetch(session, payload)


def test_TC06_criar_reserva_com_checkin_igual_checkout(session):
    payload = build_payload(
        bookingdates={"checkin": "2026-12-01", "checkout": "2026-12-01"}
    )

    create_and_fetch(session, payload)


def test_TC07_criar_reserva_com_caracteres_acentuados(session):
    payload = build_payload(
        firstname=f"João{unique_suffix()}",
        lastname=f"Conceição{unique_suffix()}",
        additionalneeds="Café da manhã e berço",
    )

    create_and_fetch(session, payload)


def test_TC08_listar_reservas_com_nome_e_sobrenome_inexistentes(session):
    firstname = f"Inexistente{unique_suffix()}"
    lastname = f"Inexistente{unique_suffix()}"

    response = list_bookings(session, firstname, lastname)

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_TC09_consultar_reserva_com_id_zero(session):
    response = get_booking(session, 0)

    assert response.status_code == 404
