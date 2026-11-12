from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"

# Contratos e valores inferidos que podem exigir ajuste.
ROUTES = {
    "auth": "/auth",
    "bookings": "/booking",
    "booking": "/booking/{booking_id}",
}
METHODS = {
    "auth": "POST",
    "create": "POST",
    "read": "GET",
    "complete_update": "PUT",
    "partial_update": "PATCH",
    "delete": "DELETE",
}
STATUS = {
    "auth_success": 200,
    "auth_invalid": 200,
    "created": 200,
    "read": 200,
    "updated": 200,
    "forbidden": 403,
    "invalid_payload": 400,
    "deleted": 201,
}
FIELDS = {
    "token": "token",
    "reason": "reason",
    "booking_id": "bookingid",
    "booking": "booking",
    "first_name": "firstname",
    "last_name": "lastname",
    "price": "totalprice",
    "deposit_paid": "depositpaid",
    "dates": "bookingdates",
    "checkin": "checkin",
    "checkout": "checkout",
    "needs": "additionalneeds",
}
VALID_CREDENTIALS = {"username": "admin", "password": "password123"}
INVALID_CREDENTIALS = {
    "username": "admin",
    "password": "senha-incorreta-123",
}
BAD_CREDENTIALS_REASON = "Bad credentials"
AUTH_COOKIE_NAME = "token"
REQUEST_TIMEOUT = (10, 30)
INITIAL_VALUES = {
    "first_name_prefix": "Cliente",
    "last_name": "Silva",
    "price": 150,
    "deposit_paid": True,
    "needs": "Breakfast",
}
UPDATED_FIRST_NAME = "Mariana"
UPDATED_LAST_NAME = "Oliveira"
UPDATED_PRICE = 275
CHECKIN_DAYS_AHEAD = 30
STAY_DAYS = 3
OMITTED_REQUIRED_FIELDS = (
    FIELDS["first_name"],
    FIELDS["price"],
)


def endpoint(route, **parameters):
    return BASE_URL.rstrip("/") + ROUTES[route].format(**parameters)


def request_api(session, operation, url, **kwargs):
    # Evita que cookies recebidos por uma chamada autentiquem outra.
    session.cookies.clear()
    return session.request(
        method=METHODS[operation],
        url=url,
        timeout=REQUEST_TIMEOUT,
        allow_redirects=False,
        **kwargs,
    )


def assert_status(response, expected):
    assert response.status_code == expected, (
        f"{response.request.method} {response.url}: "
        f"esperado HTTP {expected}, recebido HTTP {response.status_code}"
    )


def json_object(response):
    payload = response.json()
    assert isinstance(payload, dict), "A resposta deve ser um objeto JSON"
    return payload


def auth_headers(token):
    return {"Cookie": f"{AUTH_COOKIE_NAME}={token}"}


def authenticate(session):
    response = request_api(
        session,
        "auth",
        endpoint("auth"),
        json=VALID_CREDENTIALS,
    )
    assert_status(response, STATUS["auth_success"])
    payload = json_object(response)
    assert FIELDS["token"] in payload, "Token ausente"
    token = payload[FIELDS["token"]]
    assert isinstance(token, str), "O token deve ser textual"
    assert token.strip(), "O token deve ser não vazio"
    return token


def new_booking_payload():
    checkin = datetime.now(timezone.utc).date() + timedelta(
        days=CHECKIN_DAYS_AHEAD
    )
    checkout = checkin + timedelta(days=STAY_DAYS)
    return {
        FIELDS["first_name"]: (
            f"{INITIAL_VALUES['first_name_prefix']}{uuid4().hex[:12]}"
        ),
        FIELDS["last_name"]: INITIAL_VALUES["last_name"],
        FIELDS["price"]: INITIAL_VALUES["price"],
        FIELDS["deposit_paid"]: INITIAL_VALUES["deposit_paid"],
        FIELDS["dates"]: {
            FIELDS["checkin"]: checkin.isoformat(),
            FIELDS["checkout"]: checkout.isoformat(),
        },
        FIELDS["needs"]: INITIAL_VALUES["needs"],
    }


def read_booking(session, booking_id):
    response = request_api(
        session,
        "read",
        endpoint("booking", booking_id=booking_id),
    )
    assert_status(response, STATUS["read"])
    return json_object(response)


def complete_update_payload(original):
    updated = deepcopy(original)
    updated[FIELDS["first_name"]] = UPDATED_FIRST_NAME
    updated[FIELDS["price"]] = UPDATED_PRICE
    return updated


@pytest.fixture
def api():
    with requests.Session() as session:
        # Impede autenticação implícita via .netrc e uso de proxies do ambiente.
        session.trust_env = False
        session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        yield session


@pytest.fixture
def valid_token(api):
    return authenticate(api)


@pytest.fixture
def booking(api, valid_token):
    sent = new_booking_payload()
    response = request_api(
        api,
        "create",
        endpoint("bookings"),
        json=sent,
    )
    assert_status(response, STATUS["created"])
    created = json_object(response)
    booking_id = created[FIELDS["booking_id"]]
    assert type(booking_id) is int and booking_id > 0, (
        "bookingid deve ser inteiro positivo"
    )

    # Uma vez conhecido o ID, a limpeza ocorre mesmo se a preparação falhar.
    try:
        assert created[FIELDS["booking"]] == sent, (
            "A criação deve devolver os dados enviados"
        )
        baseline = read_booking(api, booking_id)
        assert baseline == sent, "A reserva criada deve estar disponível"
        yield {"id": booking_id, "data": baseline}
    finally:
        cleanup = request_api(
            api,
            "delete",
            endpoint("booking", booking_id=booking_id),
            headers=auth_headers(valid_token),
        )
        assert_status(cleanup, STATUS["deleted"])


def test_CT001_autenticar_com_credenciais_validas(api):
    response = request_api(
        api,
        "auth",
        endpoint("auth"),
        json=VALID_CREDENTIALS,
    )
    assert_status(response, STATUS["auth_success"])
    payload = json_object(response)
    assert FIELDS["token"] in payload
    assert isinstance(payload[FIELDS["token"]], str)
    assert payload[FIELDS["token"]].strip(), "Token vazio"


def test_CT002_rejeitar_credenciais_invalidas(api):
    response = request_api(
        api,
        "auth",
        endpoint("auth"),
        json=INVALID_CREDENTIALS,
    )
    assert_status(response, STATUS["auth_invalid"])
    payload = json_object(response)
    assert FIELDS["token"] not in payload
    assert payload[FIELDS["reason"]] == BAD_CREDENTIALS_REASON


def test_CT003_atualizar_reserva_completamente(api, valid_token, booking):
    updated = complete_update_payload(booking["data"])
    assert updated[FIELDS["first_name"]] != booking["data"][FIELDS["first_name"]]
    assert updated[FIELDS["price"]] != booking["data"][FIELDS["price"]]

    response = request_api(
        api,
        "complete_update",
        endpoint("booking", booking_id=booking["id"]),
        headers=auth_headers(valid_token),
        json=updated,
    )
    assert_status(response, STATUS["updated"])
    assert json_object(response) == updated
    assert read_booking(api, booking["id"]) == updated


def test_CT004_atualizar_apenas_sobrenome(api, valid_token, booking):
    original = deepcopy(booking["data"])
    expected = deepcopy(original)
    expected[FIELDS["last_name"]] = UPDATED_LAST_NAME
    assert original[FIELDS["last_name"]] != UPDATED_LAST_NAME

    response = request_api(
        api,
        "partial_update",
        endpoint("booking", booking_id=booking["id"]),
        headers=auth_headers(valid_token),
        json={FIELDS["last_name"]: UPDATED_LAST_NAME},
    )
    assert_status(response, STATUS["updated"])

    returned = json_object(response)
    assert returned[FIELDS["last_name"]] == UPDATED_LAST_NAME
    assert returned == expected, "Demais campos devem permanecer iguais"
    assert read_booking(api, booking["id"]) == expected


def test_CT005_rejeitar_atualizacao_completa_sem_token(booking):
    with requests.Session() as anonymous:
        anonymous.trust_env = False
        anonymous.headers.update({"Accept": "application/json"})
        response = request_api(
            anonymous,
            "complete_update",
            endpoint("booking", booking_id=booking["id"]),
            json=complete_update_payload(booking["data"]),
        )

    assert "Cookie" not in response.request.headers
    assert "Authorization" not in response.request.headers
    assert_status(response, STATUS["forbidden"])


def test_CT006_rejeitar_atualizacao_parcial_sem_token(booking):
    with requests.Session() as anonymous:
        anonymous.trust_env = False
        anonymous.headers.update({"Accept": "application/json"})
        response = request_api(
            anonymous,
            "partial_update",
            endpoint("booking", booking_id=booking["id"]),
            json={FIELDS["last_name"]: UPDATED_LAST_NAME},
        )

    assert "Cookie" not in response.request.headers
    assert "Authorization" not in response.request.headers
    assert_status(response, STATUS["forbidden"])


def test_CT007_rejeitar_campos_obrigatorios_ausentes(api, valid_token, booking):
    incomplete = complete_update_payload(booking["data"])
    for field in OMITTED_REQUIRED_FIELDS:
        del incomplete[field]

    response = request_api(
        api,
        "complete_update",
        endpoint("booking", booking_id=booking["id"]),
        headers=auth_headers(valid_token),
        json=incomplete,
    )
    assert_status(response, STATUS["invalid_payload"])


def test_CT008_rejeitar_atualizacao_com_objeto_vazio(api, valid_token, booking):
    response = request_api(
        api,
        "complete_update",
        endpoint("booking", booking_id=booking["id"]),
        headers=auth_headers(valid_token),
        json={},
    )
    assert_status(response, STATUS["invalid_payload"])
