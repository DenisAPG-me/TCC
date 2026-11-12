import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
USUARIO = "admin"
SENHA = "password123"
TIMEOUT = 30
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
RESERVA = {
    "firstname": "Joao",
    "lastname": "Silva",
    "totalprice": 150,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-05"},
    "additionalneeds": "Breakfast",
}


def autenticar(username, password):
    return requests.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
        headers=JSON_HEADERS,
        timeout=TIMEOUT,
    )


def cabecalhos_autenticados(token):
    return {**JSON_HEADERS, "Cookie": f"token={token}"}


@pytest.fixture
def token():
    resp = autenticar(USUARIO, SENHA)
    assert resp.status_code == 200
    return resp.json()["token"]


@pytest.fixture
def reserva(token):
    resp = requests.post(f"{BASE_URL}/booking", json=RESERVA, headers=JSON_HEADERS, timeout=TIMEOUT)
    assert resp.status_code == 200
    booking_id = resp.json()["bookingid"]
    yield booking_id
    requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=cabecalhos_autenticados(token), timeout=TIMEOUT)


def test_ct01_autenticacao_com_credenciais_validas():
    resp = autenticar(USUARIO, SENHA)
    assert resp.status_code == 200
    token = resp.json().get("token")
    assert isinstance(token, str)
    assert token.strip() != ""


def test_ct02_autenticacao_com_senha_invalida():
    resp = autenticar(USUARIO, "senha_incorreta")
    body = resp.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_ct03_autenticacao_com_usuario_inexistente():
    resp = autenticar("usuario_inexistente", SENHA)
    body = resp.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_ct04_autenticacao_com_credenciais_em_branco():
    resp = autenticar("", "")
    body = resp.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_ct05_put_completo_atualiza_nome_e_preco(token, reserva):
    payload = {**RESERVA, "firstname": "Maria", "totalprice": 320}
    resp = requests.put(f"{BASE_URL}/booking/{reserva}", json=payload, headers=cabecalhos_autenticados(token), timeout=TIMEOUT)
    assert resp.status_code == 200
    body = resp.json()
    assert body["firstname"] == "Maria"
    assert body["totalprice"] == 320

    consulta = requests.get(f"{BASE_URL}/booking/{reserva}", headers=JSON_HEADERS, timeout=TIMEOUT)
    assert consulta.status_code == 200
    assert consulta.json()["firstname"] == "Maria"
    assert consulta.json()["totalprice"] == 320


def test_ct06_patch_atualiza_apenas_sobrenome(token, reserva):
    resp = requests.patch(f"{BASE_URL}/booking/{reserva}", json={"lastname": "Oliveira"}, headers=cabecalhos_autenticados(token), timeout=TIMEOUT)
    assert resp.status_code == 200
    body = resp.json()
    assert body["lastname"] == "Oliveira"
    assert body["firstname"] == RESERVA["firstname"]
    assert body["totalprice"] == RESERVA["totalprice"]
    assert body["depositpaid"] == RESERVA["depositpaid"]
    assert body["bookingdates"] == RESERVA["bookingdates"]
    assert body["additionalneeds"] == RESERVA["additionalneeds"]


def test_ct07_put_sem_token_retorna_403(reserva):
    resp = requests.put(f"{BASE_URL}/booking/{reserva}", json=RESERVA, headers=JSON_HEADERS, timeout=TIMEOUT)
    assert resp.status_code == 403


def test_ct08_patch_sem_token_retorna_403(reserva):
    resp = requests.patch(f"{BASE_URL}/booking/{reserva}", json={"lastname": "Oliveira"}, headers=JSON_HEADERS, timeout=TIMEOUT)
    assert resp.status_code == 403


def test_ct09_put_com_token_invalido_retorna_403(reserva):
    headers = cabecalhos_autenticados("token_invalido")
    resp = requests.put(f"{BASE_URL}/booking/{reserva}", json=RESERVA, headers=headers, timeout=TIMEOUT)
    assert resp.status_code == 403


def test_ct10_put_sem_firstname_retorna_400(token, reserva):
    payload = {chave: valor for chave, valor in RESERVA.items() if chave != "firstname"}
    resp = requests.put(f"{BASE_URL}/booking/{reserva}", json=payload, headers=cabecalhos_autenticados(token), timeout=TIMEOUT)
    assert resp.status_code == 400


def test_ct11_put_com_corpo_vazio_retorna_400(token, reserva):
    resp = requests.put(f"{BASE_URL}/booking/{reserva}", json={}, headers=cabecalhos_autenticados(token), timeout=TIMEOUT)
    assert resp.status_code == 400


def test_ct12_put_com_nome_acentuado_preserva_caracteres(token, reserva):
    payload = {**RESERVA, "firstname": "José", "lastname": "Ação"}
    resp = requests.put(f"{BASE_URL}/booking/{reserva}", json=payload, headers=cabecalhos_autenticados(token), timeout=TIMEOUT)
    assert resp.status_code == 200
    body = resp.json()
    assert body["firstname"] == "José"
    assert body["lastname"] == "Ação"


def test_ct13_patch_com_corpo_vazio_mantem_reserva(token, reserva):
    resp = requests.patch(f"{BASE_URL}/booking/{reserva}", json={}, headers=cabecalhos_autenticados(token), timeout=TIMEOUT)
    assert resp.status_code == 200
    body = resp.json()
    assert body["firstname"] == RESERVA["firstname"]
    assert body["lastname"] == RESERVA["lastname"]
    assert body["totalprice"] == RESERVA["totalprice"]
    assert body["depositpaid"] == RESERVA["depositpaid"]
    assert body["bookingdates"] == RESERVA["bookingdates"]
    assert body["additionalneeds"] == RESERVA["additionalneeds"]
