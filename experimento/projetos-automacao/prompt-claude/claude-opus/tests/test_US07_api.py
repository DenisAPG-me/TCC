import uuid

import requests

BASE_URL = "https://restful-booker.herokuapp.com"
BOOKING_URL = f"{BASE_URL}/booking"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

NONEXISTENT_ID = 99999999
NON_NUMERIC_ID = "abc"

DEFAULT_BOOKING = {
    "firstname": "Joao",
    "lastname": "Silva",
    "totalprice": 150,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-15"},
    "additionalneeds": "Breakfast",
}

BOUNDARY_BOOKING = {
    "firstname": "Maria",
    "lastname": "Souza",
    "totalprice": 0,
    "depositpaid": False,
    "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-01"},
    "additionalneeds": "Late checkout",
}

ACCENTED_BOOKING = {
    "firstname": "José",
    "lastname": "Conceição",
    "totalprice": 320,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-11-20", "checkout": "2026-11-22"},
    "additionalneeds": "Café da manhã e berço",
}


def unique_name(prefix):
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def build_booking(base=DEFAULT_BOOKING, **overrides):
    payload = {**base, "bookingdates": dict(base["bookingdates"])}
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


def create_booking_id(payload):
    response = create_booking(payload)
    assert response.status_code == 200, response.text
    booking_id = response.json()["bookingid"]
    assert isinstance(booking_id, int)
    return booking_id


def test_ct01_criar_reserva_com_corpo_valido():
    payload = build_booking()

    response = create_booking(payload)

    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body["bookingid"], int)
    assert not isinstance(body["bookingid"], bool)
    assert body["bookingid"] > 0
    assert body["booking"] == payload


def test_ct02_consultar_reserva_criada_pelo_id():
    payload = build_booking()
    booking_id = create_booking_id(payload)

    response = get_booking(booking_id)

    assert response.status_code == 200, response.text
    assert response.json() == payload


def test_ct03_consultar_reserva_id_inexistente():
    response = get_booking(NONEXISTENT_ID)

    assert response.status_code == 404


def test_ct04_consultar_reserva_id_nao_numerico():
    response = get_booking(NON_NUMERIC_ID)

    assert response.status_code == 404


def test_ct05_listar_reservas_por_nome_e_sobrenome_unicos():
    firstname = unique_name("Nome")
    lastname = unique_name("Sobrenome")
    booking_id = create_booking_id(build_booking(firstname=firstname, lastname=lastname))

    response = list_bookings(firstname, lastname)

    assert response.status_code == 200, response.text
    ids = [item["bookingid"] for item in response.json()]
    assert booking_id in ids


def test_ct06_listar_reservas_nome_e_sobrenome_inexistentes():
    firstname = unique_name("Inexistente")
    lastname = unique_name("Inexistente")

    response = list_bookings(firstname, lastname)

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_ct07_criar_e_consultar_reserva_com_valores_limite():
    payload = build_booking(BOUNDARY_BOOKING)

    create_response = create_booking(payload)

    assert create_response.status_code == 200, create_response.text
    body = create_response.json()
    assert isinstance(body["bookingid"], int)
    assert body["booking"] == payload

    get_response = get_booking(body["bookingid"])

    assert get_response.status_code == 200, get_response.text
    assert get_response.json() == payload


def test_ct08_criar_e_consultar_reserva_com_caracteres_acentuados():
    payload = build_booking(ACCENTED_BOOKING)

    create_response = create_booking(payload)

    assert create_response.status_code == 200, create_response.text
    body = create_response.json()
    assert isinstance(body["bookingid"], int)
    assert body["booking"] == payload

    get_response = get_booking(body["bookingid"])

    assert get_response.status_code == 200, get_response.text
    assert get_response.json() == payload
