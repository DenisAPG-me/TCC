from copy import deepcopy
import warnings

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 15

CREDENCIAIS_VALIDAS = {
    "username": "admin",
    "password": "password123",
}
CREDENCIAIS_INVALIDAS = {
    "username": "admin",
    "password": "senha_incorreta",
}
CREDENCIAIS_VAZIAS = {
    "username": "",
    "password": "",
}

DADOS_RESERVA = {
    "firstname": "Ana",
    "lastname": "Silva",
    "totalprice": 150,
    "depositpaid": True,
    "bookingdates": {
        "checkin": "2030-01-10",
        "checkout": "2030-01-15",
    },
    "additionalneeds": "Breakfast",
}
NOVO_NOME = "Beatriz"
NOVO_PRECO = 275
NOVO_SOBRENOME = "Souza"
PAYLOAD_VAZIO = {}

CAMPOS_OBRIGATORIOS = (
    ("firstname",),
    ("lastname",),
    ("totalprice",),
    ("depositpaid",),
    ("bookingdates",),
    ("bookingdates", "checkin"),
    ("bookingdates", "checkout"),
)


@pytest.fixture
def api():
    with requests.Session() as session:
        session.trust_env = False
        session.headers.update({"Accept": "application/json"})
        yield session


def requisitar(api, metodo, caminho, *, payload=None, token=None):
    # Evita que cookies recebidos em chamadas anteriores autentiquem
    # acidentalmente uma requisição que deveria estar sem token.
    api.cookies.clear()
    headers = {}
    if token is not None:
        headers["Cookie"] = f"token={token}"

    return api.request(
        method=metodo,
        url=f"{BASE_URL}{caminho}",
        json=payload,
        headers=headers,
        timeout=TIMEOUT,
        allow_redirects=False,
    )


def verificar_status(resposta, esperado, contexto):
    assert resposta.status_code == esperado, (
        f"{contexto}: esperado status {esperado}, "
        f"recebido {resposta.status_code}. "
        f"Corpo: {resposta.text[:500]}"
    )


def objeto_json(resposta):
    try:
        corpo = resposta.json()
    except ValueError:
        pytest.fail(
            f"Esperado JSON válido; recebido: {resposta.text[:500]}",
            pytrace=False,
        )
    assert isinstance(corpo, dict), "A resposta deve ser um objeto JSON"
    return corpo


def autenticar(api, credenciais):
    return requisitar(api, "POST", "/auth", payload=deepcopy(credenciais))


def obter_token(api):
    resposta = autenticar(api, CREDENCIAIS_VALIDAS)
    verificar_status(resposta, 200, "Autenticação válida")
    corpo = objeto_json(resposta)
    token = corpo.get("token")
    assert isinstance(token, str), "O token deve ser texto"
    assert token.strip(), "O token não pode estar vazio"
    return token


def verificar_credenciais_rejeitadas(resposta):
    corpo = objeto_json(resposta)
    assert "token" not in corpo, "A resposta não deve conter a chave token"
    assert corpo.get("reason") == "Bad credentials", (
        f"Motivo inesperado: {corpo.get('reason')!r}"
    )


def verificar_objeto_exato(recebido, esperado, caminho="reserva"):
    # Verifica também tipos: em Python, True == 1, por exemplo.
    assert type(recebido) is type(esperado), (
        f"{caminho}: tipo esperado {type(esperado).__name__}, "
        f"recebido {type(recebido).__name__}"
    )
    if isinstance(esperado, dict):
        assert recebido.keys() == esperado.keys(), (
            f"{caminho}: conjunto de campos diferente do esperado"
        )
        for chave, valor in esperado.items():
            verificar_objeto_exato(
                recebido[chave], valor, f"{caminho}.{chave}"
            )
    else:
        assert recebido == esperado, (
            f"{caminho}: esperado {esperado!r}, recebido {recebido!r}"
        )


@pytest.fixture
def token_valido(api):
    return obter_token(api)


@pytest.fixture
def reserva(api):
    resposta = requisitar(
        api, "POST", "/booking", payload=deepcopy(DADOS_RESERVA)
    )
    verificar_status(resposta, 200, "Criação da reserva")
    corpo = objeto_json(resposta)
    booking_id = corpo.get("bookingid")

    assert type(booking_id) is int and booking_id > 0, (
        "A criação deve retornar bookingid inteiro positivo"
    )

    # O bloco finally cobre também falhas na validação da reserva criada.
    try:
        booking = corpo.get("booking")
        verificar_objeto_exato(booking, DADOS_RESERVA)
        yield booking_id, deepcopy(booking)
    finally:
        try:
            token_limpeza = obter_token(api)
            resposta_limpeza = requisitar(
                api,
                "DELETE",
                f"/booking/{booking_id}",
                token=token_limpeza,
            )
            verificar_status(
                resposta_limpeza, 201, "Exclusão da reserva de teste"
            )
        except (requests.RequestException, AssertionError, pytest.fail.Exception):
            warnings.warn(
                f"Não foi possível confirmar a limpeza da reserva "
                f"{booking_id}; verifique e remova esse dado de teste.",
                RuntimeWarning,
                stacklevel=2,
            )


def test_ct01_login_com_credenciais_validas(api):
    resposta = autenticar(api, CREDENCIAIS_VALIDAS)

    verificar_status(resposta, 200, "CA1")
    corpo = objeto_json(resposta)
    assert isinstance(corpo.get("token"), str)
    assert corpo["token"].strip(), "CA1: token vazio"


def test_ct02_login_com_senha_invalida(api):
    resposta = autenticar(api, CREDENCIAIS_INVALIDAS)

    verificar_credenciais_rejeitadas(resposta)


def test_ct03_login_com_credenciais_vazias(api):
    resposta = autenticar(api, CREDENCIAIS_VAZIAS)

    verificar_credenciais_rejeitadas(resposta)


def test_ct04_atualizacao_completa(api, reserva, token_valido):
    booking_id, original = reserva
    payload = deepcopy(original)
    payload["firstname"] = NOVO_NOME
    payload["totalprice"] = NOVO_PRECO

    resposta = requisitar(
        api,
        "PUT",
        f"/booking/{booking_id}",
        payload=payload,
        token=token_valido,
    )

    verificar_status(resposta, 200, "CA3")
    atualizado = objeto_json(resposta)
    assert atualizado.get("firstname") == NOVO_NOME
    assert atualizado.get("totalprice") == NOVO_PRECO
    verificar_objeto_exato(atualizado, payload)


def test_ct05_atualizacao_apenas_sobrenome(api, reserva, token_valido):
    booking_id, original = reserva

    resposta = requisitar(
        api,
        "PATCH",
        f"/booking/{booking_id}",
        payload={"lastname": NOVO_SOBRENOME},
        token=token_valido,
    )

    verificar_status(resposta, 200, "CA4")
    atualizado = objeto_json(resposta)
    assert atualizado.get("lastname") == NOVO_SOBRENOME
    assert atualizado["lastname"] != original["lastname"]

    esperado = deepcopy(original)
    esperado["lastname"] = NOVO_SOBRENOME
    verificar_objeto_exato(atualizado, esperado)


def test_ct06_atualizacao_sem_token(api, reserva):
    booking_id, original = reserva
    completo = deepcopy(original)
    completo["firstname"] = NOVO_NOME
    completo["totalprice"] = NOVO_PRECO

    # Executa as duas tentativas antes das asserções.
    respostas = [
        (
            "PUT",
            requisitar(
                api, "PUT", f"/booking/{booking_id}", payload=completo
            ),
        ),
        (
            "PATCH",
            requisitar(
                api,
                "PATCH",
                f"/booking/{booking_id}",
                payload={"lastname": NOVO_SOBRENOME},
            ),
        ),
    ]

    erros = []
    for metodo, resposta in respostas:
        if resposta.status_code != 403:
            erros.append(
                f"{metodo}: esperado 403, recebido {resposta.status_code}; "
                f"corpo={resposta.text[:300]}"
            )
    assert not erros, "CA5:\n" + "\n".join(erros)


def test_ct07_atualizacao_com_campos_ausentes(api, reserva, token_valido):
    booking_id, original = reserva
    erros = []

    for caminho in CAMPOS_OBRIGATORIOS:
        payload = deepcopy(original)
        objeto = payload
        for chave in caminho[:-1]:
            objeto = objeto[chave]
        del objeto[caminho[-1]]

        resposta = requisitar(
            api,
            "PUT",
            f"/booking/{booking_id}",
            payload=payload,
            token=token_valido,
        )

        if resposta.status_code != 400:
            erros.append(
                f"Ausência de {'.'.join(caminho)}: esperado 400, "
                f"recebido {resposta.status_code}; "
                f"corpo={resposta.text[:300]}"
            )

    assert not erros, "CA6:\n" + "\n".join(erros)


def test_ct08_atualizacao_com_objeto_vazio(api, reserva, token_valido):
    booking_id, _ = reserva

    resposta = requisitar(
        api,
        "PUT",
        f"/booking/{booking_id}",
        payload=deepcopy(PAYLOAD_VAZIO),
        token=token_valido,
    )

    verificar_status(resposta, 400, "CA6: objeto vazio")
