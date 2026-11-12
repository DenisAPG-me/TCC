import uuid

import pytest
import requests

# Valores inferidos que podem exigir ajuste
BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
AUTH_CREDENTIALS = {"username": "admin", "password": "password123"}
NONEXISTENT_BOOKING_ID = 99999999
BOOKING_PATH = "/booking"
AUTH_PATH = "/auth"


def unique_suffix():
    return uuid.uuid4().hex[:12]


def build_booking(**overrides):
    suffix = unique_suffix()
    booking = {
        "firstname": f"Nome{suffix}",
        "lastname": f"Sobrenome{suffix}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-05"},
        "additionalneeds": "Breakfast",
    }
    booking.update(overrides)
    return booking


def create_booking(payload):
    return requests.post(f"{BASE_URL}{BOOKING_PATH}", json=payload, headers=HEADERS, timeout=TIMEOUT)


def get_booking(booking_id):
    return requests.get(f"{BASE_URL}{BOOKING_PATH}/{booking_id}", headers=HEADERS, timeout=TIMEOUT)


def assert_valid_booking_id(booking_id):
    assert isinstance(booking_id, int) and not isinstance(booking_id, bool), f"bookingid não é inteiro: {booking_id!r}"
    assert booking_id > 0, f"bookingid não é positivo: {booking_id}"


@pytest.fixture
def created_ids():
    ids = []
    yield ids
    if not ids:
        return
    auth = requests.post(f"{BASE_URL}{AUTH_PATH}", json=AUTH_CREDENTIALS, headers=HEADERS, timeout=TIMEOUT)
    assert auth.status_code == 200, f"Falha na autenticação para limpeza: {auth.status_code} {auth.text}"
    token = auth.json().get("token")
    assert token, f"Token ausente na resposta de autenticação: {auth.text}"
    for booking_id in ids:
        resp = requests.delete(
            f"{BASE_URL}{BOOKING_PATH}/{booking_id}",
            headers={**HEADERS, "Cookie": f"token={token}"},
            timeout=TIMEOUT,
        )
        assert resp.status_code == 201, f"Falha ao remover reserva {booking_id}: {resp.status_code} {resp.text}"


@pytest.fixture
def booking_factory(created_ids):
    def _create(payload):
        resp = create_booking(payload)
        assert resp.status_code == 200, f"Criação falhou: {resp.status_code} {resp.text}"
        body = resp.json()
        booking_id = body["bookingid"]
        assert_valid_booking_id(booking_id)
        created_ids.append(booking_id)
        return booking_id, body

    return _create


def test_CT001_criar_reserva_com_corpo_valido(created_ids):
    payload = build_booking()

    resp = create_booking(payload)

    assert resp.status_code == 200, f"Status inesperado: {resp.status_code} {resp.text}"
    body = resp.json()
    assert "bookingid" in body, f"bookingid ausente: {body}"
    assert_valid_booking_id(body["bookingid"])
    created_ids.append(body["bookingid"])
    assert body["booking"] == payload


def test_CT002_consultar_reserva_criada_pelo_identificador(booking_factory):
    payload = build_booking()
    booking_id, _ = booking_factory(payload)

    resp = get_booking(booking_id)

    assert resp.status_code == 200, f"Status inesperado: {resp.status_code} {resp.text}"
    assert resp.json() == payload


def test_CT003_consultar_reserva_inexistente_retorna_404():
    resp = get_booking(NONEXISTENT_BOOKING_ID)

    assert resp.status_code == 404, f"Status inesperado: {resp.status_code} {resp.text}"


def test_CT004_listar_reservas_filtrando_por_nome_e_sobrenome(booking_factory):
    payload = build_booking()
    booking_id, _ = booking_factory(payload)

    resp = requests.get(
        f"{BASE_URL}{BOOKING_PATH}",
        params={"firstname": payload["firstname"], "lastname": payload["lastname"]},
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    assert resp.status_code == 200, f"Status inesperado: {resp.status_code} {resp.text}"
    results = resp.json()
    assert isinstance(results, list), f"Resposta não é lista: {results!r}"
    returned_ids = [item["bookingid"] for item in results]
    assert booking_id in returned_ids, f"bookingid {booking_id} não encontrado em {returned_ids}"


def test_CT005_criar_e_consultar_reserva_com_valores_limite_e_caracteres_especiais(booking_factory):
    suffix = unique_suffix()
    payload = build_booking(
        firstname=f"José{suffix}",
        lastname=f"Conceição-D'Ávila{suffix}",
        totalprice=0,
        depositpaid=False,
        bookingdates={"checkin": "2026-12-10", "checkout": "2026-12-10"},
        additionalneeds="Café da manhã & berço ç ã é",
    )

    booking_id, create_body = booking_factory(payload)
    assert create_body["booking"] == payload

    resp = get_booking(booking_id)

    assert resp.status_code == 200, f"Status inesperado: {resp.status_code} {resp.text}"
    assert resp.json() == payload
