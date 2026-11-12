import uuid
from datetime import date, timedelta

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = (5, 20)
CREDENTIALS = {
    "username": "admin",
    "password": "password123",
}


def api_request(method, path, *, token=None, payload=None, params=None):
    headers = {"Accept": "application/json"}
    if token is not None:
        headers["Cookie"] = f"token={token}"

    return requests.request(
        method=method,
        url=f"{BASE_URL.rstrip('/')}{path}",
        headers=headers,
        json=payload,
        params=params,
        timeout=TIMEOUT,
        allow_redirects=False,
    )


def assert_status(response, expected):
    assert response.status_code == expected, (
        f"{response.request.method} {response.request.url}: "
        f"esperado HTTP {expected}, recebido HTTP {response.status_code}"
    )


def get_booking(booking_id):
    response = api_request("GET", f"/booking/{booking_id}")
    assert_status(response, 200)
    content = response.json()
    assert isinstance(content, dict), "GET deve retornar um objeto JSON"
    return content


def delete_booking(booking_id, token=None):
    return api_request(
        "DELETE",
        f"/booking/{booking_id}",
        token=token,
    )


def assert_deleted(booking_id):
    response = api_request("GET", f"/booking/{booking_id}")
    assert_status(response, 404)


@pytest.fixture
def authenticate():
    # Token obtido sob demanda e reutilizado somente dentro deste teste.
    cached_token = None

    def obtain_token():
        nonlocal cached_token

        if cached_token is None:
            response = api_request(
                "POST",
                "/auth",
                payload=CREDENTIALS,
            )
            assert_status(response, 200)
            body = response.json()
            assert isinstance(body, dict), "Autenticação deve retornar objeto JSON"

            candidate = body.get("token")
            assert isinstance(candidate, str) and candidate.strip(), (
                "Autenticação deve fornecer token não vazio"
            )
            cached_token = candidate

        return cached_token

    return obtain_token


@pytest.fixture
def create_booking(authenticate):
    created_ids = []

    def create():
        unique = uuid.uuid4().hex
        checkin = date.today() + timedelta(days=30)
        checkout = checkin + timedelta(days=2)

        payload = {
            "firstname": f"QA{unique}",
            "lastname": f"Reserva{unique}",
            "totalprice": 150,
            "depositpaid": True,
            "bookingdates": {
                "checkin": checkin.isoformat(),
                "checkout": checkout.isoformat(),
            },
            "additionalneeds": "Breakfast",
        }

        response = api_request("POST", "/booking", payload=payload)

        # Registra o ID antes de validar o status para permitir limpeza
        # mesmo quando a criação responde com um status inesperado.
        try:
            body = response.json()
        except ValueError:
            body = None

        booking_id = body.get("bookingid") if isinstance(body, dict) else None
        valid_id = type(booking_id) is int and booking_id > 0

        if valid_id:
            assert booking_id not in created_ids, (
                "Criações distintas devem gerar identificadores distintos"
            )
            created_ids.append(booking_id)

        assert_status(response, 200)
        assert valid_id, "Criação deve retornar bookingid inteiro positivo"

        return booking_id, payload

    yield create

    cleanup_errors = []
    for booking_id in reversed(created_ids):
        try:
            response = api_request("GET", f"/booking/{booking_id}")

            if response.status_code == 404:
                continue

            assert_status(response, 200)
            response = delete_booking(booking_id, authenticate())
            assert_status(response, 201)
            assert_deleted(booking_id)
        except Exception as exc:
            # Continua limpando as demais reservas antes de reportar a falha.
            cleanup_errors.append(f"Reserva {booking_id}: {exc}")

    if cleanup_errors:
        pytest.fail(
            "Falha na limpeza das reservas do teste:\n"
            + "\n".join(cleanup_errors),
            pytrace=False,
        )


def test_TC01_impedir_exclusao_sem_token(create_booking):
    booking_id, _ = create_booking()
    original = get_booking(booking_id)

    response = delete_booking(booking_id)

    assert "Cookie" not in response.request.headers
    assert "Authorization" not in response.request.headers
    assert_status(response, 403)
    assert get_booking(booking_id) == original, (
        "Exclusão sem token alterou a reserva"
    )


def test_TC02_impedir_exclusao_com_token_invalido(create_booking):
    booking_id, _ = create_booking()
    original = get_booking(booking_id)
    invalid_token = f"invalid-{uuid.uuid4().hex}"

    response = delete_booking(booking_id, invalid_token)

    assert_status(response, 403)
    assert get_booking(booking_id) == original, (
        "Exclusão com token inválido alterou a reserva"
    )


def test_TC03_excluir_com_token_valido(create_booking, authenticate):
    booking_id, _ = create_booking()
    get_booking(booking_id)
    token = authenticate()

    response = delete_booking(booking_id, token)

    assert_status(response, 201)


def test_TC04_consultar_reserva_excluida(create_booking, authenticate):
    booking_id, _ = create_booking()
    token = authenticate()

    response = delete_booking(booking_id, token)

    assert_status(response, 201)
    assert_deleted(booking_id)


def test_TC05_repetir_exclusao_preservando_controle(
    create_booking, authenticate
):
    target_id, _ = create_booking()
    control_id, _ = create_booking()
    original_control = get_booking(control_id)
    token = authenticate()

    first_response = delete_booking(target_id, token)
    assert_status(first_response, 201)
    assert_deleted(target_id)
    assert get_booking(control_id) == original_control, (
        "Primeira exclusão alterou a reserva de controle"
    )

    second_response = delete_booking(target_id, token)

    assert 400 <= second_response.status_code <= 499, (
        "Segunda exclusão deve retornar 4xx; "
        f"recebido HTTP {second_response.status_code}"
    )
    assert_deleted(target_id)
    assert get_booking(control_id) == original_control, (
        "Segunda exclusão alterou a reserva de controle"
    )


def test_TC06_listar_por_nome_apos_exclusao(create_booking, authenticate):
    booking_id, payload = create_booking()
    filters = {
        "firstname": payload["firstname"],
        "lastname": payload["lastname"],
    }

    before_response = api_request("GET", "/booking", params=filters)
    assert_status(before_response, 200)
    before = before_response.json()

    assert isinstance(before, list), "Listagem deve retornar uma lista JSON"
    assert len(before) == 1, (
        "Filtro pelo nome único deve encontrar exatamente uma reserva"
    )
    assert isinstance(before[0], dict), "Item da listagem deve ser um objeto"
    assert before[0].get("bookingid") == booking_id, (
        "Listagem inicial deve identificar a reserva criada"
    )

    token = authenticate()
    delete_response = delete_booking(booking_id, token)
    assert_status(delete_response, 201)

    after_response = api_request("GET", "/booking", params=filters)
    assert_status(after_response, 200)
    assert after_response.json() == [], (
        "Listagem filtrada deve ficar vazia após a exclusão"
    )
