from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"

# Contratos e valores inferidos que podem exigir ajuste.
BOOKING_PATH = "/booking"
BOOKING_ID_PATH = "/booking/{booking_id}"
REQUEST_TIMEOUT = (5, 20)
FOLLOW_REDIRECTS = False
HTTP_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

FIELDS = {
    "firstname": "firstname",
    "lastname": "lastname",
    "totalprice": "totalprice",
    "depositpaid": "depositpaid",
    "bookingdates": "bookingdates",
    "checkin": "checkin",
    "checkout": "checkout",
    "additionalneeds": "additionalneeds",
}
RESPONSE_ID_FIELD = "bookingid"
RESPONSE_BOOKING_FIELD = "booking"
FILTER_FIRSTNAME = "firstname"
FILTER_LASTNAME = "lastname"

FIRSTNAME_PREFIX = "TesteNome"
LASTNAME_PREFIX = "TesteSobrenome"
TOTAL_PRICE = 150
DEPOSIT_PAID = True
ADDITIONAL_NEEDS = "Breakfast"
CHECKIN_OFFSET_DAYS = 30
STAY_DAYS = 1
DATE_FORMAT = "%Y-%m-%d"
NONEXISTENT_BOOKING_ID = 99999999

CREATE_STATUS = 200
READ_STATUS = 200
LIST_STATUS = 200
NOT_FOUND_STATUS = 404


def endpoint(path):
    return BASE_URL.rstrip("/") + "/" + path.lstrip("/")


def booking_path(booking_id):
    return BOOKING_ID_PATH.format(booking_id=booking_id)


def send_request(session, method, path, **kwargs):
    return session.request(
        method=method,
        url=endpoint(path),
        timeout=REQUEST_TIMEOUT,
        allow_redirects=FOLLOW_REDIRECTS,
        **kwargs,
    )


def assert_status(response, expected):
    assert response.status_code == expected, (
        f"{response.request.method} {response.url}: "
        f"esperado HTTP {expected}, recebido {response.status_code}. "
        f"Corpo: {response.text[:1000]}"
    )


def assert_booking_data(actual, expected):
    assert isinstance(actual, dict), (
        f"Esperado objeto JSON para a reserva; recebido: {actual!r}"
    )
    assert set(actual) == set(expected), (
        f"Campos divergentes: esperado {set(expected)}, recebido {set(actual)}"
    )

    for field, expected_value in expected.items():
        actual_value = actual[field]
        assert type(actual_value) is type(expected_value), (
            f"Tipo divergente no campo {field}: "
            f"esperado {type(expected_value).__name__}, "
            f"recebido {type(actual_value).__name__}"
        )
        assert actual_value == expected_value, (
            f"Campo {field}: esperado {expected_value!r}, "
            f"recebido {actual_value!r}"
        )


def create_booking(session, payload):
    response = send_request(session, "POST", BOOKING_PATH, json=payload)
    assert_status(response, CREATE_STATUS)

    body = response.json()
    assert isinstance(body, dict), "A criação deve retornar um objeto JSON."
    assert RESPONSE_ID_FIELD in body, "Identificador ausente na criação."
    assert type(body[RESPONSE_ID_FIELD]) is int, (
        "O identificador retornado deve ser inteiro."
    )
    assert RESPONSE_BOOKING_FIELD in body, "Dados da reserva ausentes."
    assert_booking_data(body[RESPONSE_BOOKING_FIELD], payload)

    return body[RESPONSE_ID_FIELD]


@pytest.fixture
def api_session():
    with requests.Session() as session:
        session.headers.update(HTTP_HEADERS)
        yield session


@pytest.fixture
def booking_payload():
    unique_suffix = uuid4().hex
    checkin = (
        datetime.now(timezone.utc).date()
        + timedelta(days=CHECKIN_OFFSET_DAYS)
    )
    checkout = checkin + timedelta(days=STAY_DAYS)

    return {
        FIELDS["firstname"]: FIRSTNAME_PREFIX + unique_suffix,
        FIELDS["lastname"]: LASTNAME_PREFIX + unique_suffix,
        FIELDS["totalprice"]: TOTAL_PRICE,
        FIELDS["depositpaid"]: DEPOSIT_PAID,
        FIELDS["bookingdates"]: {
            FIELDS["checkin"]: checkin.strftime(DATE_FORMAT),
            FIELDS["checkout"]: checkout.strftime(DATE_FORMAT),
        },
        FIELDS["additionalneeds"]: ADDITIONAL_NEEDS,
    }


def test_CT001_criar_reserva_com_dados_validos(api_session, booking_payload):
    # O helper verifica status, identificador e todos os dados retornados.
    booking_id = create_booking(api_session, booking_payload)
    assert type(booking_id) is int


def test_CT002_consultar_reserva_criada(api_session, booking_payload):
    booking_id = create_booking(api_session, booking_payload)

    response = send_request(api_session, "GET", booking_path(booking_id))

    assert_status(response, READ_STATUS)
    assert_booking_data(response.json(), booking_payload)


def test_CT003_consultar_identificador_inexistente(api_session):
    response = send_request(
        api_session,
        "GET",
        booking_path(NONEXISTENT_BOOKING_ID),
    )

    assert_status(response, NOT_FOUND_STATUS)


def test_CT004_filtrar_por_nome_e_sobrenome(api_session, booking_payload):
    booking_id = create_booking(api_session, booking_payload)

    response = send_request(
        api_session,
        "GET",
        BOOKING_PATH,
        params={
            FILTER_FIRSTNAME: booking_payload[FIELDS["firstname"]],
            FILTER_LASTNAME: booking_payload[FIELDS["lastname"]],
        },
    )

    assert_status(response, LIST_STATUS)
    results = response.json()
    assert isinstance(results, list), "A listagem deve retornar um array JSON."

    returned_ids = []
    for item in results:
        assert isinstance(item, dict), (
            f"Cada resultado deve ser um objeto JSON; recebido: {item!r}"
        )
        assert RESPONSE_ID_FIELD in item, (
            f"Resultado sem identificador: {item!r}"
        )
        assert type(item[RESPONSE_ID_FIELD]) is int, (
            f"Identificador deve ser inteiro: {item!r}"
        )
        returned_ids.append(item[RESPONSE_ID_FIELD])

    assert booking_id in returned_ids, (
        f"A reserva {booking_id} não apareceu na listagem filtrada "
        "pelo nome e sobrenome enviados."
    )
