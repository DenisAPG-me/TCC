import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
USERNAME = "admin"
PASSWORD = "password123"
TIMEOUT = 10
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def _dados_reserva(**alteracoes):
    dados = {
        "firstname": "Joao",
        "lastname": "Silva",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2027-03-10", "checkout": "2027-03-15"},
        "additionalneeds": "Cafe da manha",
    }
    dados.update(alteracoes)
    return dados


def _nome_unico():
    return f"Nome{uuid.uuid4().hex[:10]}"


def _criar_reserva(dados):
    return requests.post(f"{BASE_URL}/booking", json=dados, headers=HEADERS, timeout=TIMEOUT)


def _consultar_reserva(booking_id):
    return requests.get(f"{BASE_URL}/booking/{booking_id}", headers=HEADERS, timeout=TIMEOUT)


def _remover_reserva(booking_id):
    token = requests.post(
        f"{BASE_URL}/auth",
        json={"username": USERNAME, "password": PASSWORD},
        headers=HEADERS,
        timeout=TIMEOUT,
    ).json()["token"]
    requests.delete(
        f"{BASE_URL}/booking/{booking_id}",
        headers={"Cookie": f"token={token}"},
        timeout=TIMEOUT,
    )


@pytest.fixture
def ids_para_remover():
    ids = []
    yield ids
    for booking_id in ids:
        _remover_reserva(booking_id)


def test_ct01_criar_reserva_com_dados_validos_retorna_200_e_dados_iguais(ids_para_remover):
    dados = _dados_reserva(firstname=_nome_unico(), lastname=_nome_unico())

    resposta = _criar_reserva(dados)

    assert resposta.status_code == 200
    corpo = resposta.json()
    ids_para_remover.append(corpo["bookingid"])
    assert isinstance(corpo["bookingid"], int)
    assert corpo["booking"] == dados


def test_ct02_consultar_reserva_criada_retorna_todos_os_campos_iguais(ids_para_remover):
    dados = _dados_reserva(firstname=_nome_unico(), lastname=_nome_unico())
    booking_id = _criar_reserva(dados).json()["bookingid"]
    ids_para_remover.append(booking_id)

    resposta = _consultar_reserva(booking_id)

    assert resposta.status_code == 200
    assert resposta.json() == dados


def test_ct03_consultar_id_inexistente_retorna_404():
    resposta = _consultar_reserva(99999999)

    assert resposta.status_code == 404


def test_ct04_listar_por_nome_e_sobrenome_contem_id_criado(ids_para_remover):
    dados = _dados_reserva(firstname=_nome_unico(), lastname=_nome_unico())
    booking_id = _criar_reserva(dados).json()["bookingid"]
    ids_para_remover.append(booking_id)

    resposta = requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": dados["firstname"], "lastname": dados["lastname"]},
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    assert resposta.status_code == 200
    assert booking_id in [item["bookingid"] for item in resposta.json()]


def test_ct05_listar_por_nome_inexistente_retorna_lista_vazia():
    resposta = requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": _nome_unico(), "lastname": _nome_unico()},
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_ct06_consultar_reserva_com_caracteres_especiais_retorna_dados_iguais(ids_para_remover):
    dados = _dados_reserva(
        firstname="José Ângela",
        lastname="D'Ávila-Müller",
        additionalneeds="Berço & cadeira de rodas",
    )
    booking_id = _criar_reserva(dados).json()["bookingid"]
    ids_para_remover.append(booking_id)

    resposta = _consultar_reserva(booking_id)

    assert resposta.status_code == 200
    assert resposta.json() == dados


def test_ct07_consultar_id_zero_retorna_404():
    resposta = _consultar_reserva(0)

    assert resposta.status_code == 404


def test_ct08_criar_reserva_com_preco_zero_e_sem_deposito_retorna_dados_iguais(ids_para_remover):
    dados = _dados_reserva(
        firstname=_nome_unico(),
        lastname=_nome_unico(),
        totalprice=0,
        depositpaid=False,
    )

    resposta = _criar_reserva(dados)

    assert resposta.status_code == 200
    corpo = resposta.json()
    ids_para_remover.append(corpo["bookingid"])
    assert isinstance(corpo["bookingid"], int)
    assert corpo["booking"] == dados
