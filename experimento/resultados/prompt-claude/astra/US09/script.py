from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
CREDENTIALS = {
    "username": "admin",
    "password": "password123",
}
TIMEOUT = (10, 30)
INVALID_TOKEN = "token-deliberadamente-invalido-ct02"

TODAY = datetime.now(timezone.utc).date()
BOOKING_DATA = {
    "firstname": "TesteExclusao",
    "lastname": "Automacao",
    "totalprice": 150,
    "depositpaid": True,
    "bookingdates": {
        "checkin": (TODAY + timedelta(days=30)).isoformat(),
        "checkout": (TODAY + timedelta(days=32)).isoformat(),
    },
    "additionalneeds": "Breakfast",
}


def api_request(method, path, *, token=None, **kwargs):
    # Uma sessão nova impede reaproveitamento acidental de cookies.
    with requests.Session() as session:
        session.trust_env = False
        session.headers.update({"Accept": "application/json"})
        cookies = {} if token is None else {"token": token}
        return session.request(
            method=method,
            url=f"{BASE_URL}{path}",
            cookies=cookies,
            timeout=TIMEOUT,
            allow_redirects=False,
            **kwargs,
        )


def assert_status(response, expected):
    assert response.status_code == expected, (
        f"{response.request.method} {response.request.url}: "
        f"esperado {expected}, recebido {response.status_code}"
    )


def read_booking(booking_id):
    response = api_request("GET", f"/booking/{booking_id}")
    assert_status(response, 200)
    body = response.json()
    assert isinstance(body, dict), "GET deve retornar um objeto JSON"
    return body


def delete_booking(booking_id, token=None):
    return api_request("DELETE", f"/booking/{booking_id}", token=token)


def list_bookings(payload):
    response = api_request(
        "GET",
        "/booking",
        params={
            "firstname": payload["firstname"],
            "lastname": payload["lastname"],
        },
    )
    assert_status(response, 200)
    body = response.json()
    assert isinstance(body, list), "Listagem deve retornar um array JSON"
    return body


def cleanup_booking(booking_id, token):
    response = api_request("GET", f"/booking/{booking_id}")
    if response.status_code == 404:
        return

    assert_status(response, 200)
    assert_status(delete_booking(booking_id, token), 201)
    assert_status(api_request("GET", f"/booking/{booking_id}"), 404)


@pytest.fixture
def valid_token():
    response = api_request("POST", "/auth", json=CREDENTIALS)
    assert_status(response, 200)

    body = response.json()
    assert isinstance(body, dict), "Autenticação deve retornar um objeto JSON"
    token = body.get("token")
    assert isinstance(token, str) and token.strip(), (
        "Autenticação deve fornecer um token textual não vazio"
    )
    return token


@pytest.fixture
def create_booking(request, valid_token):
    def create():
        payload = deepcopy(BOOKING_DATA)
        payload["firstname"] = f"{BOOKING_DATA['firstname']}{uuid4().hex}"

        response = api_request("POST", "/booking", json=payload)
        assert_status(response, 200)

        body = response.json()
        assert isinstance(body, dict), "Criação deve retornar um objeto JSON"
        booking_id = body.get("bookingid")
        assert type(booking_id) is int and booking_id > 0, (
            "Criação deve fornecer bookingid inteiro positivo"
        )

        # Registra a limpeza antes das demais verificações.
        # O pytest executa cada finalizador mesmo se outro falhar.
        request.addfinalizer(
            lambda: cleanup_booking(booking_id, valid_token)
        )

        original = read_booking(booking_id)
        for field, expected in payload.items():
            assert original.get(field) == expected, (
                f"Campo criado difere do enviado: {field}"
            )

        return {
            "id": booking_id,
            "payload": payload,
            "original": original,
        }

    return create


def test_ct01_exclusao_sem_token(create_booking):
    booking = create_booking()

    response = delete_booking(booking["id"])
    assert_status(response, 403)

    current = read_booking(booking["id"])
    assert current == booking["original"], (
        "A tentativa sem token alterou a reserva"
    )


def test_ct02_exclusao_com_token_invalido(create_booking):
    booking = create_booking()

    response = delete_booking(booking["id"], INVALID_TOKEN)
    assert_status(response, 403)

    current = read_booking(booking["id"])
    assert current == booking["original"], (
        "A tentativa com token inválido alterou a reserva"
    )


def test_ct03_exclusao_com_token_valido(create_booking, valid_token):
    assert isinstance(valid_token, str) and valid_token.strip()
    booking = create_booking()

    response = delete_booking(booking["id"], valid_token)
    assert_status(response, 201)


def test_ct04_consulta_apos_exclusao(create_booking, valid_token):
    booking = create_booking()

    response = delete_booking(booking["id"], valid_token)
    assert_status(response, 201)

    response = api_request("GET", f"/booking/{booking['id']}")
    assert_status(response, 404)


def test_ct05_exclusao_repetida_preserva_controles(
    create_booking, valid_token
):
    target = create_booking()
    controls = [create_booking(), create_booking()]
    ids = [target["id"]] + [booking["id"] for booking in controls]
    assert len(set(ids)) == 3, "As reservas devem ter IDs distintos"

    before = {
        booking["id"]: read_booking(booking["id"])
        for booking in controls
    }

    response = delete_booking(target["id"], valid_token)
    assert_status(response, 201)

    response = delete_booking(target["id"], valid_token)
    assert 400 <= response.status_code <= 499, (
        "Exclusão repetida deve retornar 4xx; "
        f"recebido {response.status_code}"
    )

    response = api_request("GET", f"/booking/{target['id']}")
    assert_status(response, 404)

    for booking in controls:
        current = read_booking(booking["id"])
        assert current == before[booking["id"]], (
            f"Reserva de controle {booking['id']} foi alterada"
        )


def test_ct06_listagem_filtrada_apos_exclusao(
    create_booking, valid_token
):
    booking = create_booking()

    initial = list_bookings(booking["payload"])
    assert len(initial) == 1, (
        "O filtro pelo nome único deve localizar exatamente uma reserva"
    )
    assert isinstance(initial[0], dict)
    assert initial[0].get("bookingid") == booking["id"], (
        "A listagem inicial deve localizar a reserva criada"
    )

    response = delete_booking(booking["id"], valid_token)
    assert_status(response, 201)

    remaining = list_bookings(booking["payload"])
    assert remaining == [], (
        "A listagem filtrada deve ficar vazia após a exclusão"
    )
