from copy import deepcopy
from datetime import date, timedelta
import warnings

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = (5, 20)

VALID_CREDENTIALS = {
    "username": "admin",
    "password": "password123",
}

REQUIRED_PATHS = (
    ("firstname",),
    ("lastname",),
    ("totalprice",),
    ("depositpaid",),
    ("bookingdates",),
    ("bookingdates", "checkin"),
    ("bookingdates", "checkout"),
)


def api_request(method, path, *, payload=None, token=None):
    headers = {"Accept": "application/json"}

    if token is not None:
        headers["Cookie"] = f"token={token}"

    # Cada chamada usa uma sessão independente, sem reutilizar cookies.
    return requests.request(
        method=method,
        url=f"{BASE_URL}{path}",
        headers=headers,
        json=payload,
        timeout=TIMEOUT,
        allow_redirects=False,
    )


def assert_status(response, expected):
    assert response.status_code == expected, (
        f"{response.request.method} {response.request.url}: "
        f"esperado status {expected}, recebido {response.status_code}"
    )


def json_object(response):
    try:
        body = response.json()
    except ValueError:
        pytest.fail("A resposta deveria conter JSON válido.")

    assert isinstance(body, dict), "A resposta deveria ser um objeto JSON."
    return body


def authenticate():
    response = api_request(
        "POST",
        "/auth",
        payload=VALID_CREDENTIALS,
    )
    assert_status(response, 200)

    body = json_object(response)
    token = body.get("token")
    assert isinstance(token, str), "O token deveria ser textual."
    assert token.strip(), "O token não pode ser vazio ou conter só espaços."
    return token


def assert_bad_credentials(response):
    # O critério 2 não define um status HTTP.
    body = json_object(response)
    assert "token" not in body, "Credenciais inválidas não devem retornar token."
    assert body.get("reason") == "Bad credentials"


def booking_payload():
    checkin = date.today() + timedelta(days=30)
    checkout = checkin + timedelta(days=3)

    return {
        "firstname": "Ana",
        "lastname": "Silva",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": checkin.isoformat(),
            "checkout": checkout.isoformat(),
        },
        "additionalneeds": "Breakfast",
    }


def read_booking(booking_id):
    response = api_request("GET", f"/booking/{booking_id}")
    assert_status(response, 200)
    return json_object(response)


def complete_update(original):
    updated = deepcopy(original)
    updated["firstname"] = "Beatriz"
    updated["totalprice"] = 275
    return updated


@pytest.fixture
def valid_token():
    return authenticate()


@pytest.fixture
def booking_factory(valid_token):
    created_ids = []

    def create():
        payload = booking_payload()
        response = api_request("POST", "/booking", payload=payload)
        assert_status(response, 200)

        body = json_object(response)
        booking_id = body.get("bookingid")
        assert type(booking_id) is int and booking_id > 0, (
            "A criação deveria retornar bookingid inteiro positivo."
        )

        # Registrar antes de consultar garante tentativa de limpeza
        # mesmo se a verificação da preparação falhar.
        created_ids.append(booking_id)

        initial_state = read_booking(booking_id)
        for field, value in payload.items():
            assert field in initial_state, (
                f"Preparação: campo {field} ausente na reserva criada."
            )
            assert initial_state[field] == value, (
                f"Preparação: campo {field} diferente do enviado."
            )

        return booking_id, payload, initial_state

    yield create

    cleanup_problems = []
    for booking_id in reversed(created_ids):
        try:
            response = api_request(
                "DELETE",
                f"/booking/{booking_id}",
                token=valid_token,
            )
            if response.status_code not in (200, 201, 204):
                cleanup_problems.append(
                    f"reserva {booking_id}: status {response.status_code}"
                )
        except requests.RequestException as exc:
            cleanup_problems.append(
                f"reserva {booking_id}: {type(exc).__name__}"
            )

    if cleanup_problems:
        warnings.warn(
            "Falha na limpeza; podem existir reservas de teste restantes: "
            + "; ".join(cleanup_problems),
            RuntimeWarning,
            stacklevel=2,
        )


def test_TC01_autenticacao_com_credenciais_validas():
    authenticate()


def test_TC02_autenticacao_com_credenciais_incorretas():
    response = api_request(
        "POST",
        "/auth",
        payload={
            "username": "usuario_invalido_qa",
            "password": "senha_invalida_qa",
        },
    )
    assert_bad_credentials(response)


def test_TC03_autenticacao_com_credenciais_vazias():
    response = api_request(
        "POST",
        "/auth",
        payload={"username": "", "password": ""},
    )
    assert_bad_credentials(response)


def test_TC04_atualizacao_completa(booking_factory, valid_token):
    booking_id, original, _ = booking_factory()
    updated = complete_update(original)

    response = api_request(
        "PUT",
        f"/booking/{booking_id}",
        payload=updated,
        token=valid_token,
    )
    assert_status(response, 200)

    returned = json_object(response)
    assert returned["firstname"] == updated["firstname"]
    assert returned["totalprice"] == updated["totalprice"]

    persisted = read_booking(booking_id)
    assert persisted["firstname"] == updated["firstname"]
    assert persisted["totalprice"] == updated["totalprice"]


def test_TC05_atualizacao_parcial_preserva_demais_campos(
    booking_factory, valid_token
):
    booking_id, _, initial_state = booking_factory()
    new_lastname = "Oliveira"
    assert initial_state["lastname"] != new_lastname

    response = api_request(
        "PATCH",
        f"/booking/{booking_id}",
        payload={"lastname": new_lastname},
        token=valid_token,
    )
    assert_status(response, 200)

    expected = deepcopy(initial_state)
    expected["lastname"] = new_lastname

    # Comparação integral verifica também campos aninhados e adicionais.
    assert json_object(response) == expected
    assert read_booking(booking_id) == expected


def test_TC06_atualizacao_completa_sem_token(booking_factory):
    booking_id, original, _ = booking_factory()

    response = api_request(
        "PUT",
        f"/booking/{booking_id}",
        payload=complete_update(original),
    )
    assert_status(response, 403)


def test_TC07_atualizacao_parcial_sem_token(booking_factory):
    booking_id, _, _ = booking_factory()

    response = api_request(
        "PATCH",
        f"/booking/{booking_id}",
        payload={"lastname": "Oliveira"},
    )
    assert_status(response, 403)


def test_TC08_atualizacao_com_omissao_de_campo_obrigatorio(
    booking_factory, valid_token
):
    failures = []

    for field_path in REQUIRED_PATHS:
        booking_id, original, _ = booking_factory()
        incomplete = complete_update(original)

        parent = incomplete
        for field in field_path[:-1]:
            parent = parent[field]
        del parent[field_path[-1]]

        response = api_request(
            "PUT",
            f"/booking/{booking_id}",
            payload=incomplete,
            token=valid_token,
        )

        # Acumular divergências permite verificar todas as omissões,
        # mesmo quando uma delas retorna um status inesperado.
        if response.status_code != 400:
            failures.append(
                f"Sem {'.'.join(field_path)}: esperado 400, "
                f"recebido {response.status_code}"
            )

    assert not failures, "\n".join(failures)


def test_TC09_atualizacao_com_objeto_vazio(booking_factory, valid_token):
    booking_id, _, _ = booking_factory()

    response = api_request(
        "PUT",
        f"/booking/{booking_id}",
        payload={},
        token=valid_token,
    )
    assert_status(response, 400)
