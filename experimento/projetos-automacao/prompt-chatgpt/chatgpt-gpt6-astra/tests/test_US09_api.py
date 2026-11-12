from copy import deepcopy
from uuid import uuid4

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"

# Contrato inferido: ajustar se o contrato real for diferente.
AUTH_PATH = "/auth"
BOOKING_PATH = "/booking"
BOOKING_ID_PATH = "/booking/{booking_id}"
TOKEN_COOKIE_NAME = "token"
NAME_FILTER_PARAMETER = "firstname"
INVALID_TOKEN = "token-invalido-ct002"

CREDENTIALS = {
    "username": "admin",
    "password": "password123",
}

TIMEOUT = (10, 30)
HEADERS = {"Accept": "application/json"}
AUTH_SUCCESS_STATUS = 200
CREATE_SUCCESS_STATUS = 200
READ_SUCCESS_STATUS = 200
DELETE_SUCCESS_STATUS = 201
FORBIDDEN_STATUS = 403
NOT_FOUND_STATUS = 404

BOOKING_TEMPLATE = {
    "firstname": "Teste",
    "lastname": "Automacao",
    "totalprice": 150,
    "depositpaid": True,
    "bookingdates": {
        "checkin": "2030-06-10",
        "checkout": "2030-06-12",
    },
    "additionalneeds": "Breakfast",
}


def api_request(method, path, *, token=None, params=None, payload=None):
    # Uma sessão por requisição impede herança de cookies.
    with requests.Session() as session:
        # Evita autenticação implícita de .netrc e configurações externas.
        session.trust_env = False
        cookies = {}
        if token is not None:
            cookies[TOKEN_COOKIE_NAME] = token

        response = session.request(
            method=method,
            url=f"{BASE_URL.rstrip('/')}{path}",
            headers=HEADERS,
            cookies=cookies,
            params=params,
            json=payload,
            timeout=TIMEOUT,
            allow_redirects=False,
        )
    return response


def assert_status(response, expected):
    assert response.status_code == expected, (
        f"{response.request.method} {response.url}: "
        f"esperado HTTP {expected}, recebido {response.status_code}; "
        f"corpo={response.text[:500]!r}"
    )


def booking_path(booking_id):
    return BOOKING_ID_PATH.format(booking_id=booking_id)


def get_booking(booking_id):
    response = api_request("GET", booking_path(booking_id))
    assert_status(response, READ_SUCCESS_STATUS)
    data = response.json()
    assert isinstance(data, dict), "Consulta deve retornar um objeto JSON"
    return data


def list_booking_ids(params=None):
    response = api_request("GET", BOOKING_PATH, params=params)
    assert_status(response, READ_SUCCESS_STATUS)
    data = response.json()
    assert isinstance(data, list), "Listagem deve retornar um array JSON"

    ids = []
    for item in data:
        assert isinstance(item, dict), "Item da listagem deve ser objeto JSON"
        assert "bookingid" in item, "Item sem bookingid"
        booking_id = item["bookingid"]
        assert type(booking_id) is int and booking_id > 0, (
            f"Identificador inválido: {booking_id!r}"
        )
        ids.append(booking_id)

    assert len(ids) == len(set(ids)), "Listagem contém identificadores duplicados"
    return ids


def delete_successfully(booking_id, token):
    response = api_request(
        "DELETE", booking_path(booking_id), token=token
    )
    assert_status(response, DELETE_SUCCESS_STATUS)


def assert_missing(booking_id):
    response = api_request("GET", booking_path(booking_id))
    assert_status(response, NOT_FOUND_STATUS)


@pytest.fixture
def valid_token():
    response = api_request("POST", AUTH_PATH, payload=CREDENTIALS)
    assert_status(response, AUTH_SUCCESS_STATUS)
    data = response.json()
    assert isinstance(data, dict), "Autenticação deve retornar objeto JSON"
    assert "token" in data, "Autenticação não retornou token"
    token = data["token"]
    assert isinstance(token, str) and token.strip(), "Token vazio ou inválido"
    return token


@pytest.fixture
def create_booking(valid_token):
    def create():
        payload = deepcopy(BOOKING_TEMPLATE)
        payload["firstname"] = f"Teste{uuid4().hex}"
        response = api_request("POST", BOOKING_PATH, payload=payload)
        assert_status(response, CREATE_SUCCESS_STATUS)

        data = response.json()
        assert isinstance(data, dict), "Criação deve retornar objeto JSON"
        assert "bookingid" in data, "Criação não retornou bookingid"
        booking_id = data["bookingid"]
        assert type(booking_id) is int and booking_id > 0

        # Registrar antes das demais verificações permite limpar uma
        # reserva criada mesmo se o conteúdo retornado estiver incorreto.
        created_ids.append(booking_id)

        assert "booking" in data, "Criação não retornou booking"
        assert data["booking"] == payload, "Dados da criação divergentes"
        assert get_booking(booking_id) == payload
        return booking_id, payload

    created_ids = []
    yield create

    # Tenta limpar todos os recursos conhecidos e propaga cada falha.
    cleanup_failures = []
    for booking_id in reversed(created_ids):
        try:
            response = api_request("GET", booking_path(booking_id))
            if response.status_code == NOT_FOUND_STATUS:
                continue

            assert_status(response, READ_SUCCESS_STATUS)
            delete_successfully(booking_id, valid_token)
            assert_missing(booking_id)
        except (requests.RequestException, AssertionError) as error:
            cleanup_failures.append(f"Reserva {booking_id}: {error}")

    if cleanup_failures:
        pytest.fail("Falhas de limpeza:\n" + "\n".join(cleanup_failures))


def test_CT001_negar_exclusao_sem_token(create_booking):
    booking_id, original = create_booking()

    response = api_request("DELETE", booking_path(booking_id))

    assert_status(response, FORBIDDEN_STATUS)
    assert "Cookie" not in response.request.headers
    assert "Authorization" not in response.request.headers
    assert get_booking(booking_id) == original


def test_CT002_negar_exclusao_com_token_invalido(create_booking):
    booking_id, original = create_booking()

    response = api_request(
        "DELETE", booking_path(booking_id), token=INVALID_TOKEN
    )

    assert_status(response, FORBIDDEN_STATUS)
    assert response.request.headers["Cookie"] == (
        f"{TOKEN_COOKIE_NAME}={INVALID_TOKEN}"
    )
    assert get_booking(booking_id) == original


def test_CT003_excluir_com_token_valido(create_booking, valid_token):
    booking_id, _ = create_booking()

    response = api_request(
        "DELETE", booking_path(booking_id), token=valid_token
    )

    assert_status(response, DELETE_SUCCESS_STATUS)


def test_CT004_consultar_reserva_excluida(create_booking, valid_token):
    booking_id, _ = create_booking()
    delete_successfully(booking_id, valid_token)

    response = api_request("GET", booking_path(booking_id))

    assert_status(response, NOT_FOUND_STATUS)


def test_CT005_repetir_exclusao_preservando_demais(
    create_booking, valid_token
):
    target_id, _ = create_booking()
    control_id, control_data = create_booking()
    assert target_id != control_id

    delete_successfully(target_id, valid_token)
    assert_missing(target_id)

    before_ids = set(list_booking_ids())
    assert target_id not in before_ids
    assert control_id in before_ids

    before_data = {
        booking_id: get_booking(booking_id)
        for booking_id in sorted(before_ids)
    }
    assert before_data[control_id] == control_data

    response = api_request(
        "DELETE", booking_path(target_id), token=valid_token
    )

    assert 400 <= response.status_code <= 499, (
        f"Segunda exclusão deveria retornar 4xx; "
        f"recebido {response.status_code}; corpo={response.text[:500]!r}"
    )
    assert_missing(target_id)

    after_ids = set(list_booking_ids())
    assert after_ids == before_ids, (
        "A segunda exclusão alterou os identificadores das demais reservas"
    )

    for booking_id in sorted(before_ids):
        assert get_booking(booking_id) == before_data[booking_id], (
            f"Dados da reserva {booking_id} foram alterados"
        )


def test_CT006_filtrar_nome_da_reserva_excluida(
    create_booking, valid_token
):
    booking_id, original = create_booking()
    params = {NAME_FILTER_PARAMETER: original["firstname"]}

    assert list_booking_ids(params) == [booking_id], (
        "Filtro inicial deve encontrar somente a reserva de nome único"
    )

    delete_successfully(booking_id, valid_token)

    response = api_request("GET", BOOKING_PATH, params=params)
    assert_status(response, READ_SUCCESS_STATUS)
    assert response.json() == [], (
        "Filtro pelo nome da reserva excluída deve retornar lista vazia"
    )
