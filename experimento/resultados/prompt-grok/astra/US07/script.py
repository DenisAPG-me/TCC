from datetime import date
from uuid import uuid4

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT_SECONDS = 15


@pytest.fixture
def api():
    with requests.Session() as session:
        session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        yield session


def enviar(api, metodo, caminho, **kwargs):
    return api.request(
        method=metodo,
        url=f"{BASE_URL.rstrip('/')}/{caminho.lstrip('/')}",
        timeout=TIMEOUT_SECONDS,
        allow_redirects=False,
        **kwargs,
    )


def verificar_status(resposta, esperado):
    assert resposta.status_code == esperado, (
        f"{resposta.request.method} {resposta.url}: "
        f"esperado status {esperado}, recebido {resposta.status_code}. "
        f"Corpo: {resposta.text[:1000]}"
    )


def verificar_json_exato(recebido, esperado, caminho="$"):
    # A igualdade comum do Python considera True == 1 e 150 == 150.0.
    # A verificação explícita de tipos evita aceitar essas diferenças.
    assert type(recebido) is type(esperado), (
        f"{caminho}: tipo esperado {type(esperado).__name__}, "
        f"recebido {type(recebido).__name__}"
    )

    if isinstance(esperado, dict):
        assert recebido.keys() == esperado.keys(), (
            f"{caminho}: campos diferentes. "
            f"Esperados: {list(esperado)}; recebidos: {list(recebido)}"
        )
        for campo, valor in esperado.items():
            verificar_json_exato(
                recebido[campo], valor, f"{caminho}.{campo}"
            )
    else:
        assert recebido == esperado, (
            f"{caminho}: esperado {esperado!r}, recebido {recebido!r}"
        )


def novos_dados(deposito_pago=True, virada_de_ano=False):
    sufixo = uuid4().hex
    ano = date.today().year + 1

    if virada_de_ano:
        checkin = date(ano, 12, 31)
        checkout = date(ano + 1, 1, 1)
    else:
        checkin = date(ano, 6, 10)
        checkout = date(ano, 6, 12)

    return {
        "firstname": f"Nome{sufixo}",
        "lastname": f"Sobrenome{sufixo}",
        "totalprice": 150,
        "depositpaid": deposito_pago,
        "bookingdates": {
            "checkin": checkin.isoformat(),
            "checkout": checkout.isoformat(),
        },
        "additionalneeds": "Breakfast",
    }


def criar_e_validar(api, dados):
    resposta = enviar(api, "POST", "/booking", json=dados)
    verificar_status(resposta, 200)

    corpo = resposta.json()
    assert isinstance(corpo, dict), "Criação deve retornar um objeto JSON."
    assert "bookingid" in corpo, "Resposta sem bookingid."
    assert type(corpo["bookingid"]) is int, (
        "bookingid deve ser um inteiro JSON, não um booleano."
    )
    assert "booking" in corpo, "Resposta sem booking."

    verificar_json_exato(corpo["booking"], dados, "$.booking")
    return corpo["bookingid"]


def consultar_e_validar(api, identificador, dados):
    resposta = enviar(api, "GET", f"/booking/{identificador}")
    verificar_status(resposta, 200)
    verificar_json_exato(resposta.json(), dados)


def test_TC01_criar_reserva_com_todos_os_campos_validos(api):
    dados = novos_dados()
    criar_e_validar(api, dados)


def test_TC02_consultar_reserva_criada_pelo_identificador(api):
    dados = novos_dados()
    identificador = criar_e_validar(api, dados)
    consultar_e_validar(api, identificador, dados)


def test_TC03_consultar_identificador_inexistente(api):
    resposta = enviar(api, "GET", "/booking/99999999")
    verificar_status(resposta, 404)
    # A User Story não especifica o conteúdo ou formato do corpo do erro.


def test_TC04_filtrar_por_nome_e_sobrenome_unicos(api):
    dados = novos_dados()
    identificador = criar_e_validar(api, dados)

    resposta = enviar(
        api,
        "GET",
        "/booking",
        params={
            "firstname": dados["firstname"],
            "lastname": dados["lastname"],
        },
    )
    verificar_status(resposta, 200)

    itens = resposta.json()
    assert isinstance(itens, list), "Listagem deve retornar uma lista JSON."

    identificadores = []
    for indice, item in enumerate(itens):
        assert isinstance(item, dict), f"Item {indice} deve ser um objeto."
        assert "bookingid" in item, f"Item {indice} sem bookingid."
        assert type(item["bookingid"]) is int, (
            f"Item {indice}: bookingid deve ser um inteiro JSON."
        )
        identificadores.append(item["bookingid"])

    assert identificador in identificadores, (
        f"Reserva {identificador} ausente na listagem filtrada."
    )


def test_TC05_criar_e_consultar_com_deposito_nao_pago(api):
    dados = novos_dados(deposito_pago=False)
    identificador = criar_e_validar(api, dados)
    consultar_e_validar(api, identificador, dados)


def test_TC06_criar_e_consultar_na_mudanca_de_ano(api):
    dados = novos_dados(virada_de_ano=True)
    identificador = criar_e_validar(api, dados)
    consultar_e_validar(api, identificador, dados)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
