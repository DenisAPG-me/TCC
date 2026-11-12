import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
USUARIO = "admin"
SENHA = "password123"
TOKEN_INVALIDO = "token_invalido_123"
SOBRENOME = "Silva"
CHECKIN = "2027-01-10"
CHECKOUT = "2027-01-15"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def _obter_token():
    resp = requests.post(
        f"{BASE_URL}/auth",
        json={"username": USUARIO, "password": SENHA},
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    assert resp.status_code == 200, resp.text
    token = resp.json().get("token")
    assert token, resp.text
    return token


def _criar_reserva(nome=None):
    nome = nome or f"Nome{uuid.uuid4().hex[:12]}"
    payload = {
        "firstname": nome,
        "lastname": SOBRENOME,
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": CHECKIN, "checkout": CHECKOUT},
        "additionalneeds": "Breakfast",
    }
    resp = requests.post(f"{BASE_URL}/booking", json=payload, headers=HEADERS, timeout=TIMEOUT)
    assert resp.status_code == 200, resp.text
    return resp.json()["bookingid"], nome


def _excluir(booking_id, token=None):
    headers = {"Cookie": f"token={token}"} if token is not None else {}
    return requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers, timeout=TIMEOUT)


def _consultar(booking_id):
    return requests.get(f"{BASE_URL}/booking/{booking_id}", headers=HEADERS, timeout=TIMEOUT)


def test_ct01_excluir_sem_token_retorna_403_e_reserva_permanece():
    booking_id, _ = _criar_reserva()

    resp = _excluir(booking_id)
    assert resp.status_code == 403

    consulta = _consultar(booking_id)
    assert consulta.status_code == 200


def test_ct02_excluir_com_token_invalido_retorna_403_e_reserva_permanece():
    booking_id, _ = _criar_reserva()

    resp = _excluir(booking_id, TOKEN_INVALIDO)
    assert resp.status_code == 403

    consulta = _consultar(booking_id)
    assert consulta.status_code == 200


def test_ct03_excluir_com_token_valido_retorna_201():
    token = _obter_token()
    booking_id, _ = _criar_reserva()

    resp = _excluir(booking_id, token)
    assert resp.status_code == 201


def test_ct04_consultar_reserva_excluida_retorna_404():
    token = _obter_token()
    booking_id, _ = _criar_reserva()

    assert _excluir(booking_id, token).status_code == 201

    consulta = _consultar(booking_id)
    assert consulta.status_code == 404


def test_ct05_excluir_reserva_ja_excluida_retorna_erro_4xx():
    token = _obter_token()
    booking_id, _ = _criar_reserva()

    assert _excluir(booking_id, token).status_code == 201

    resp = _excluir(booking_id, token)
    assert 400 <= resp.status_code < 500


def test_ct06_excluir_uma_reserva_nao_afeta_as_demais():
    token = _obter_token()
    id_a, _ = _criar_reserva()
    id_b, nome_b = _criar_reserva()

    assert _excluir(id_a, token).status_code == 201

    consulta_b = _consultar(id_b)
    assert consulta_b.status_code == 200
    assert consulta_b.json()["firstname"] == nome_b


def test_ct07_listar_por_nome_unico_apos_exclusao_retorna_lista_vazia():
    token = _obter_token()
    booking_id, nome = _criar_reserva()

    assert _excluir(booking_id, token).status_code == 201

    resp = requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": nome},
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    assert resp.status_code == 200
    assert resp.json() == []


def test_ct08_excluir_com_token_vazio_retorna_403_e_reserva_permanece():
    booking_id, _ = _criar_reserva()

    resp = _excluir(booking_id, "")
    assert resp.status_code == 403

    consulta = _consultar(booking_id)
    assert consulta.status_code == 200
