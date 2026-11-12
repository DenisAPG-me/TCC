import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
USERNAME = "admin"
PASSWORD = "password123"
WRONG_PASSWORD = "senha_errada_123"
INVALID_TOKEN = "token_invalido_inexistente"
NONEXISTENT_ID = 999999999
TIMEOUT = 15

JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

BOOKING_TEMPLATE = {
    "totalprice": 250,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-15"},
    "additionalneeds": "Breakfast",
}


def obter_token(username=USERNAME, password=PASSWORD):
    return requests.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )


def token_valido():
    resp = obter_token()
    assert resp.status_code == 200
    token = resp.json().get("token")
    assert token
    return token


def excluir(booking_id, token=None, cookie=None):
    headers = {"Content-Type": "application/json"}
    if cookie is not None:
        headers["Cookie"] = cookie
    elif token is not None:
        headers["Cookie"] = f"token={token}"
    return requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers, timeout=TIMEOUT)


def consultar(booking_id):
    return requests.get(
        f"{BASE_URL}/booking/{booking_id}", headers={"Accept": "application/json"}, timeout=TIMEOUT
    )


def filtrar(firstname, lastname):
    return requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": firstname, "lastname": lastname},
        headers={"Accept": "application/json"},
        timeout=TIMEOUT,
    )


@pytest.fixture
def criar_reserva():
    criadas = []

    def _criar():
        sufixo = uuid.uuid4().hex[:12]
        payload = dict(BOOKING_TEMPLATE, firstname=f"QA{sufixo}", lastname=f"Del{sufixo}")
        resp = requests.post(f"{BASE_URL}/booking", json=payload, headers=JSON_HEADERS, timeout=TIMEOUT)
        assert resp.status_code == 200
        booking_id = resp.json()["bookingid"]
        criadas.append(booking_id)
        return {"id": booking_id, "payload": payload}

    yield _criar

    try:
        token = obter_token().json().get("token")
        for booking_id in criadas:
            excluir(booking_id, token=token)
    except requests.RequestException:
        pass


def assert_reserva_intacta(reserva):
    resp = consultar(reserva["id"])
    assert resp.status_code == 200
    body = resp.json()
    assert body["firstname"] == reserva["payload"]["firstname"]
    assert body["lastname"] == reserva["payload"]["lastname"]
    assert body["totalprice"] == reserva["payload"]["totalprice"]
    assert body["bookingdates"] == reserva["payload"]["bookingdates"]


def test_ct01_excluir_sem_token_recusado(criar_reserva):
    reserva = criar_reserva()
    resp = excluir(reserva["id"])
    assert resp.status_code == 403
    assert_reserva_intacta(reserva)


def test_ct02_excluir_com_token_invalido_recusado(criar_reserva):
    reserva = criar_reserva()
    resp = excluir(reserva["id"], token=INVALID_TOKEN)
    assert resp.status_code == 403
    assert_reserva_intacta(reserva)


def test_ct03_excluir_com_token_vazio_recusado(criar_reserva):
    reserva = criar_reserva()
    resp = excluir(reserva["id"], cookie="token=")
    assert resp.status_code == 403
    assert consultar(reserva["id"]).status_code == 200


def test_ct04_credenciais_invalidas_nao_geram_token_para_excluir(criar_reserva):
    reserva = criar_reserva()
    auth = obter_token(password=WRONG_PASSWORD)
    body = auth.json()
    assert "token" not in body
    resp = excluir(reserva["id"], token=body.get("token", ""))
    assert resp.status_code == 403
    assert consultar(reserva["id"]).status_code == 200


def test_ct05_excluir_com_token_valido(criar_reserva):
    token = token_valido()
    reserva = criar_reserva()
    resp = excluir(reserva["id"], token=token)
    assert resp.status_code == 201


def test_ct06_consultar_reserva_excluida_retorna_404(criar_reserva):
    reserva = criar_reserva()
    token = token_valido()
    assert excluir(reserva["id"], token=token).status_code == 201
    assert consultar(reserva["id"]).status_code == 404


def test_ct07_excluir_novamente_retorna_4xx_sem_afetar_outras(criar_reserva):
    reserva_a = criar_reserva()
    reserva_b = criar_reserva()
    token = token_valido()
    assert excluir(reserva_a["id"], token=token).status_code == 201
    resp = excluir(reserva_a["id"], token=token)
    assert 400 <= resp.status_code < 500
    assert_reserva_intacta(reserva_b)


def test_ct08_excluir_id_inexistente_retorna_4xx(criar_reserva):
    controle = criar_reserva()
    token = token_valido()
    resp = excluir(NONEXISTENT_ID, token=token)
    assert 400 <= resp.status_code < 500
    assert_reserva_intacta(controle)


def test_ct09_excluir_reserva_nao_afeta_outra(criar_reserva):
    reserva_a = criar_reserva()
    reserva_b = criar_reserva()
    token = token_valido()
    assert excluir(reserva_a["id"], token=token).status_code == 201
    assert_reserva_intacta(reserva_b)
    resp = filtrar(reserva_b["payload"]["firstname"], reserva_b["payload"]["lastname"])
    assert resp.status_code == 200
    ids = [item["bookingid"] for item in resp.json()]
    assert reserva_b["id"] in ids


def test_ct10_filtro_por_nome_unico_encontra_reserva_antes_da_exclusao(criar_reserva):
    reserva = criar_reserva()
    resp = filtrar(reserva["payload"]["firstname"], reserva["payload"]["lastname"])
    assert resp.status_code == 200
    ids = [item["bookingid"] for item in resp.json()]
    assert ids == [reserva["id"]]


def test_ct11_filtro_por_nome_unico_apos_exclusao_retorna_vazio(criar_reserva):
    reserva = criar_reserva()
    token = token_valido()
    assert excluir(reserva["id"], token=token).status_code == 201
    resp = filtrar(reserva["payload"]["firstname"], reserva["payload"]["lastname"])
    assert resp.status_code == 200
    assert resp.json() == []
