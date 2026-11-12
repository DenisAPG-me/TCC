import sys
from datetime import date, timedelta
from uuid import uuid4

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 30
USERNAME = "admin"
PASSWORD = "password123"


def api_request(method, path, *, token=None, **kwargs):
    headers = {"Accept": "application/json"}
    if token is not None:
        headers["Cookie"] = f"token={token}"

    # Sessão isolada: não reutiliza cookies ou credenciais entre chamadas.
    with requests.Session() as session:
        # Evita autenticação implícita por arquivos .netrc.
        session.trust_env = False
        return session.request(
            method=method,
            url=f"{BASE_URL.rstrip('/')}{path}",
            headers=headers,
            timeout=TIMEOUT,
            allow_redirects=False,
            **kwargs,
        )


def assert_status(response, expected):
    assert response.status_code == expected, (
        f"{response.request.method} {response.url}: "
        f"esperado {expected}, recebido {response.status_code}. "
        f"Corpo: {response.text[:500]}"
    )


def get_booking(booking_id):
    response = api_request("GET", f"/booking/{booking_id}")
    assert_status(response, 200)
    data = response.json()
    assert isinstance(data, dict), "GET deve retornar um objeto JSON."
    return data


def delete_booking(booking_id, token):
    return api_request("DELETE", f"/booking/{booking_id}", token=token)


@pytest.fixture
def valid_token():
    response = api_request(
        "POST",
        "/auth",
        json={"username": USERNAME, "password": PASSWORD},
    )
    assert_status(response, 200)
    body = response.json()
    assert isinstance(body, dict), "Autenticação deve retornar um objeto JSON."
    token = body.get("token")
    assert isinstance(token, str) and token.strip(), (
        "Autenticação não retornou um token válido."
    )
    return token


@pytest.fixture
def create_booking(valid_token):
    created_ids = []

    def create():
        unique_id = uuid4().hex
        checkin = date.today() + timedelta(days=30)
        checkout = checkin + timedelta(days=2)
        payload = {
            "firstname": f"Auto{unique_id}",
            "lastname": f"Reserva{unique_id}",
            "totalprice": 250,
            "depositpaid": True,
            "bookingdates": {
                "checkin": checkin.isoformat(),
                "checkout": checkout.isoformat(),
            },
            "additionalneeds": "Breakfast",
        }

        response = api_request("POST", "/booking", json=payload)
        assert_status(response, 200)
        body = response.json()
        assert isinstance(body, dict), "Criação deve retornar um objeto JSON."
        booking_id = body.get("bookingid")
        assert type(booking_id) is int and booking_id > 0, (
            f"Identificador de reserva inválido: {booking_id!r}"
        )

        created_ids.append(booking_id)
        persisted = get_booking(booking_id)
        for key, value in payload.items():
            assert persisted.get(key) == value, (
                f"Preparação inconsistente no campo {key!r}."
            )

        return {"id": booking_id, "payload": payload, "data": persisted}

    yield create

    # Tenta limpar todas as reservas mesmo se uma limpeza falhar.
    cleanup_errors = []
    for booking_id in reversed(created_ids):
        try:
            response = api_request("GET", f"/booking/{booking_id}")
            if response.status_code == 404:
                continue

            assert_status(response, 200)
            response = delete_booking(booking_id, valid_token)
            assert_status(response, 201)
            response = api_request("GET", f"/booking/{booking_id}")
            assert_status(response, 404)
        except (requests.RequestException, AssertionError) as exc:
            cleanup_errors.append(f"Reserva {booking_id}: {exc}")

    if cleanup_errors:
        pytest.fail("Falhas na limpeza:\n" + "\n".join(cleanup_errors))


def test_CT01_exclusao_sem_token_preserva_reserva(create_booking):
    booking = create_booking()

    response = api_request("DELETE", f"/booking/{booking['id']}")

    assert_status(response, 403)
    assert get_booking(booking["id"]) == booking["data"], (
        "A tentativa sem token alterou a reserva."
    )


def test_CT02_exclusao_com_token_invalido_preserva_reserva(create_booking):
    booking = create_booking()
    invalid_token = f"invalid-{uuid4().hex}"

    response = delete_booking(booking["id"], invalid_token)

    assert_status(response, 403)
    assert get_booking(booking["id"]) == booking["data"], (
        "A tentativa com token inválido alterou a reserva."
    )


def test_CT03_exclusao_com_token_valido_retorna_201(
    create_booking, valid_token
):
    booking = create_booking()

    response = delete_booking(booking["id"], valid_token)

    assert_status(response, 201)


def test_CT04_consulta_de_reserva_excluida_retorna_404(
    create_booking, valid_token
):
    booking = create_booking()
    response = delete_booking(booking["id"], valid_token)
    assert_status(response, 201)

    response = api_request("GET", f"/booking/{booking['id']}")

    assert_status(response, 404)


def test_CT05_exclusao_repetida_retorna_4xx_e_preserva_controle(
    create_booking, valid_token
):
    target = create_booking()
    control = create_booking()
    assert target["id"] != control["id"], (
        "A reserva alvo e a reserva de controle precisam ser distintas."
    )

    response = delete_booking(target["id"], valid_token)
    assert_status(response, 201)

    repeated_delete = delete_booking(target["id"], valid_token)
    target_after = api_request("GET", f"/booking/{target['id']}")
    control_after = api_request("GET", f"/booking/{control['id']}")

    # Todas as consultas são realizadas mesmo se a segunda exclusão falhar.
    assert 400 <= repeated_delete.status_code < 500, (
        "A segunda exclusão deveria retornar 4xx; "
        f"recebido {repeated_delete.status_code}. "
        f"Corpo: {repeated_delete.text[:500]}"
    )
    assert_status(target_after, 404)
    assert_status(control_after, 200)
    assert control_after.json() == control["data"], (
        "A reserva de controle foi alterada."
    )


def test_CT06_filtro_por_nome_unico_apos_exclusao_retorna_lista_vazia(
    create_booking, valid_token
):
    booking = create_booking()
    filters = {
        "firstname": booking["payload"]["firstname"],
        "lastname": booking["payload"]["lastname"],
    }

    before = api_request("GET", "/booking", params=filters)
    assert_status(before, 200)
    matches = before.json()
    assert isinstance(matches, list), "A listagem deve retornar uma lista."
    assert len(matches) == 1, (
        f"O filtro deveria identificar uma única reserva: {matches!r}"
    )
    assert isinstance(matches[0], dict)
    assert matches[0].get("bookingid") == booking["id"]

    response = delete_booking(booking["id"], valid_token)
    assert_status(response, 201)

    after = api_request("GET", "/booking", params=filters)

    assert_status(after, 200)
    assert after.json() == [], (
        "O filtro ainda retornou reservas após a exclusão."
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", *sys.argv[1:]]))
