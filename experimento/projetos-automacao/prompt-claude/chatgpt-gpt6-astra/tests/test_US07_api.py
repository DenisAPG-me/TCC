from copy import deepcopy
from uuid import uuid4

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
CREDENTIALS = None
TIMEOUT = (5, 20)
HEADERS = {"Accept": "application/json"}
INEXISTENT_BOOKING_ID = 99999999

BASE_BOOKING = {
    "firstname": "Ana",
    "lastname": "Teste",
    "totalprice": 250,
    "depositpaid": True,
    "bookingdates": {
        "checkin": "2030-11-10",
        "checkout": "2030-11-12",
    },
    "additionalneeds": "Breakfast",
}

ZERO_PRICE_OVERRIDES = {
    "totalprice": 0,
    "depositpaid": False,
}

UNICODE_OVERRIDES = {
    "firstname": "João",
    "lastname": "Conceição",
    "additionalneeds": "",
}


@pytest.fixture
def api():
    with requests.Session() as session:
        session.headers.update(HEADERS)
        session.auth = CREDENTIALS
        yield session


def make_booking(overrides=None):
    payload = deepcopy(BASE_BOOKING)
    if overrides is not None:
        payload.update(deepcopy(overrides))

    suffix = uuid4().hex
    payload["firstname"] = f"{payload['firstname']}_{suffix}"
    payload["lastname"] = f"{payload['lastname']}_{suffix}"
    return payload


def assert_status(response, expected):
    assert response.status_code == expected, (
        f"{response.request.method} {response.url}: "
        f"esperado status {expected}, recebido {response.status_code}. "
        f"Corpo: {response.text[:1000]}"
    )


def read_json(response):
    try:
        return response.json()
    except ValueError as exc:
        pytest.fail(
            f"Resposta não contém JSON válido em {response.url}: "
            f"{exc}. Corpo: {response.text[:1000]}"
        )


def assert_same_data(actual, expected, path="booking"):
    # A comparação de tipos evita aceitar True como 1 ou False como 0.
    assert type(actual) is type(expected), (
        f"{path}: tipo esperado {type(expected).__name__}, "
        f"recebido {type(actual).__name__}"
    )

    if isinstance(expected, dict):
        assert set(actual) == set(expected), (
            f"{path}: campos esperados {sorted(expected)}, "
            f"recebidos {sorted(actual)}"
        )
        for key, value in expected.items():
            assert_same_data(actual[key], value, f"{path}.{key}")
    else:
        assert actual == expected, (
            f"{path}: esperado {expected!r}, recebido {actual!r}"
        )


def create_booking(api, payload):
    response = api.post(
        f"{BASE_URL}/booking",
        json=payload,
        timeout=TIMEOUT,
        allow_redirects=False,
    )
    assert_status(response, 200)

    body = read_json(response)
    assert isinstance(body, dict), "Criação deve retornar um objeto JSON"
    assert "bookingid" in body, "Resposta sem bookingid"
    assert type(body["bookingid"]) is int, (
        "bookingid deve ser inteiro, não booleano ou string"
    )
    assert body["bookingid"] > 0, "bookingid deve ser positivo"
    assert "booking" in body, "Resposta sem booking"
    assert_same_data(body["booking"], payload)
    return body["bookingid"]


def fetch_booking(api, booking_id):
    return api.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=TIMEOUT,
        allow_redirects=False,
    )


def list_bookings(api, payload):
    return api.get(
        f"{BASE_URL}/booking",
        params={
            "firstname": payload["firstname"],
            "lastname": payload["lastname"],
        },
        timeout=TIMEOUT,
        allow_redirects=False,
    )


def assert_list_contains(response, booking_id):
    assert_status(response, 200)
    body = read_json(response)
    assert isinstance(body, list), "Listagem deve retornar uma lista JSON"

    returned_ids = []
    for index, item in enumerate(body):
        assert isinstance(item, dict), f"Item {index} deve ser objeto JSON"
        assert "bookingid" in item, f"Item {index} sem bookingid"
        assert type(item["bookingid"]) is int, (
            f"bookingid do item {index} deve ser inteiro"
        )
        returned_ids.append(item["bookingid"])

    assert booking_id in returned_ids, (
        f"Reserva {booking_id} ausente na listagem filtrada: {returned_ids}"
    )


def test_ct01_criar_reserva_valida(api):
    payload = make_booking()

    booking_id = create_booking(api, payload)

    assert type(booking_id) is int
    assert booking_id > 0


def test_ct02_consultar_reserva_criada(api):
    payload = make_booking()
    booking_id = create_booking(api, payload)

    response = fetch_booking(api, booking_id)

    assert_status(response, 200)
    assert_same_data(read_json(response), payload)


def test_ct03_consultar_identificador_inexistente(api):
    response = fetch_booking(api, INEXISTENT_BOOKING_ID)

    assert_status(response, 404)


def test_ct04_filtrar_por_nome_e_sobrenome(api):
    payload = make_booking()
    booking_id = create_booking(api, payload)

    response = list_bookings(api, payload)

    assert_list_contains(response, booking_id)


def test_ct05_preservar_preco_zero_e_deposito_falso(api):
    payload = make_booking(ZERO_PRICE_OVERRIDES)
    booking_id = create_booking(api, payload)

    response = fetch_booking(api, booking_id)

    assert_status(response, 200)
    body = read_json(response)
    assert_same_data(body, payload)
    assert type(body["totalprice"]) is int
    assert body["totalprice"] == 0
    assert body["depositpaid"] is False


def test_ct06_preservar_acentos_e_necessidades_vazias(api):
    payload = make_booking(UNICODE_OVERRIDES)
    booking_id = create_booking(api, payload)

    response = fetch_booking(api, booking_id)

    assert_status(response, 200)
    body = read_json(response)
    assert_same_data(body, payload)
    assert body["firstname"] == payload["firstname"]
    assert body["lastname"] == payload["lastname"]
    assert body["additionalneeds"] == ""

    filtered_response = list_bookings(api, payload)

    assert_list_contains(filtered_response, booking_id)
