BASE_URL = "https://restful-booker.herokuapp.com"

import copy
import sys
import uuid
import warnings
from datetime import date, timedelta

import pytest
import requests


TIMEOUT = 30
VALID_CREDENTIALS = {
    "username": "admin",
    "password": "password123",
}


def api_request(method, path, *, token=None, payload=None):
    headers = {"Accept": "application/json"}
    if token is not None:
        headers["Cookie"] = f"token={token}"

    # Uma sessão nova impede reaproveitamento acidental de cookies.
    with requests.Session() as session:
        # Evita autenticação implícita por .netrc e configurações do ambiente.
        session.trust_env = False
        return session.request(
            method=method,
            url=f"{BASE_URL.rstrip('/')}{path}",
            headers=headers,
            json=payload,
            timeout=TIMEOUT,
            allow_redirects=False,
        )


def assert_status(response, expected):
    # Não inclui corpos de autenticação, que podem conter tokens.
    assert response.status_code == expected, (
        f"{response.request.method} {response.request.url}: "
        f"esperado HTTP {expected}, recebido HTTP {response.status_code}"
    )


def json_object(response):
    try:
        body = response.json()
    except ValueError:
        pytest.fail("A resposta deveria conter JSON válido.", pytrace=False)
    assert isinstance(body, dict), "A resposta JSON deveria ser um objeto."
    return body


def authenticate():
    response = api_request("POST", "/auth", payload=VALID_CREDENTIALS)
    assert_status(response, 200)
    body = json_object(response)
    token = body.get("token")
    assert isinstance(token, str), "Token ausente ou não textual."
    assert token.strip(), "Token vazio."
    return token


def assert_invalid_credentials(username, password):
    response = api_request(
        "POST",
        "/auth",
        payload={"username": username, "password": password},
    )
    body = json_object(response)
    assert "token" not in body, "Credenciais inválidas retornaram chave token."
    assert body.get("reason") == "Bad credentials"


@pytest.fixture
def valid_token():
    return authenticate()


@pytest.fixture
def booking(valid_token):
    checkin = date.today() + timedelta(days=30)
    payload = {
        "firstname": "Cliente",
        "lastname": f"Teste{uuid.uuid4().hex[:10]}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": checkin.isoformat(),
            "checkout": (checkin + timedelta(days=3)).isoformat(),
        },
        "additionalneeds": "Breakfast",
    }

    response = api_request("POST", "/booking", payload=payload)
    assert_status(response, 200)
    body = json_object(response)
    booking_id = body.get("bookingid")
    assert type(booking_id) is int, "Criação não retornou bookingid inteiro."

    try:
        created = body.get("booking")
        assert isinstance(created, dict), "Criação não retornou objeto booking."
        for key, value in payload.items():
            assert created.get(key) == value, (
                f"Pré-condição inválida: campo {key} diverge do enviado."
            )
        yield {
            "id": booking_id,
            "original": copy.deepcopy(created),
            "payload": copy.deepcopy(payload),
        }
    finally:
        try:
            cleanup = api_request(
                "DELETE",
                f"/booking/{booking_id}",
                token=valid_token,
            )
            if cleanup.status_code not in {200, 201, 204}:
                warnings.warn(
                    f"Limpeza da reserva {booking_id} retornou "
                    f"HTTP {cleanup.status_code}.",
                    RuntimeWarning,
                    stacklevel=2,
                )
        except requests.RequestException as exc:
            warnings.warn(
                f"Limpeza da reserva {booking_id} falhou: "
                f"{type(exc).__name__}.",
                RuntimeWarning,
                stacklevel=2,
            )


def complete_update(booking):
    payload = copy.deepcopy(booking["payload"])
    payload["firstname"] = "ClienteAtualizado"
    payload["totalprice"] = 275
    return payload


def assert_missing_field(booking, valid_token, *field_path):
    payload = complete_update(booking)
    parent = payload
    for key in field_path[:-1]:
        parent = parent[key]
    del parent[field_path[-1]]

    response = api_request(
        "PUT",
        f"/booking/{booking['id']}",
        token=valid_token,
        payload=payload,
    )
    assert_status(response, 400)


def test_CT01_autenticacao_valida():
    authenticate()


def test_CT02_usuario_incorreto():
    assert_invalid_credentials("usuario_invalido", "password123")


def test_CT03_senha_incorreta():
    assert_invalid_credentials("admin", "senha_invalida")


def test_CT04_ambas_credenciais_incorretas():
    assert_invalid_credentials("usuario_invalido", "senha_invalida")


def test_CT05_credenciais_vazias():
    assert_invalid_credentials("", "")


def test_CT06_atualizacao_completa(booking, valid_token):
    payload = complete_update(booking)
    response = api_request(
        "PUT",
        f"/booking/{booking['id']}",
        token=valid_token,
        payload=payload,
    )
    assert_status(response, 200)
    body = json_object(response)
    assert body.get("firstname") == payload["firstname"]
    assert body.get("totalprice") == payload["totalprice"]


def test_CT07_atualizacao_parcial_sobrenome(booking, valid_token):
    new_lastname = "SobrenomeAtualizado"
    response = api_request(
        "PATCH",
        f"/booking/{booking['id']}",
        token=valid_token,
        payload={"lastname": new_lastname},
    )
    assert_status(response, 200)
    expected = copy.deepcopy(booking["original"])
    expected["lastname"] = new_lastname
    assert json_object(response) == expected


def test_CT08_atualizacao_completa_sem_token(booking):
    response = api_request(
        "PUT",
        f"/booking/{booking['id']}",
        payload=complete_update(booking),
    )
    assert_status(response, 403)


def test_CT09_atualizacao_parcial_sem_token(booking):
    response = api_request(
        "PATCH",
        f"/booking/{booking['id']}",
        payload={"lastname": "SobrenomeAtualizado"},
    )
    assert_status(response, 403)


def test_CT10_sem_firstname(booking, valid_token):
    assert_missing_field(booking, valid_token, "firstname")


def test_CT11_sem_lastname(booking, valid_token):
    assert_missing_field(booking, valid_token, "lastname")


def test_CT12_sem_totalprice(booking, valid_token):
    assert_missing_field(booking, valid_token, "totalprice")


def test_CT13_sem_depositpaid(booking, valid_token):
    assert_missing_field(booking, valid_token, "depositpaid")


def test_CT14_sem_bookingdates(booking, valid_token):
    assert_missing_field(booking, valid_token, "bookingdates")


def test_CT15_sem_checkin(booking, valid_token):
    assert_missing_field(booking, valid_token, "bookingdates", "checkin")


def test_CT16_sem_checkout(booking, valid_token):
    assert_missing_field(booking, valid_token, "bookingdates", "checkout")


def test_CT17_payload_vazio(booking, valid_token):
    response = api_request(
        "PUT",
        f"/booking/{booking['id']}",
        token=valid_token,
        payload={},
    )
    assert_status(response, 400)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", *sys.argv[1:]]))
