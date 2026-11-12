BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT_SECONDS = 30

import uuid

import pytest
import requests


@pytest.fixture
def api():
    with requests.Session() as session:
        session.headers.update({"Accept": "application/json"})
        yield session


def montar_payload(
    depositpaid=True,
    checkin="2028-06-15",
    checkout="2028-06-18",
):
    return {
        "firstname": f"Nome{uuid.uuid4().hex}",
        "lastname": f"Sobrenome{uuid.uuid4().hex}",
        "totalprice": 350,
        "depositpaid": depositpaid,
        "bookingdates": {
            "checkin": checkin,
            "checkout": checkout,
        },
        "additionalneeds": "Breakfast",
    }


def verificar_status(response, esperado):
    assert response.status_code == esperado, (
        f"{response.request.method} {response.url}: "
        f"esperado status {esperado}, recebido {response.status_code}. "
        f"Corpo: {response.text[:1000]}"
    )


def verificar_campos(recebido, esperado, caminho="booking"):
    assert type(recebido) is type(esperado), (
        f"{caminho}: tipo esperado {type(esperado).__name__}, "
        f"recebido {type(recebido).__name__}"
    )

    if isinstance(esperado, dict):
        for chave, valor in esperado.items():
            assert chave in recebido, f"Campo ausente: {caminho}.{chave}"
            verificar_campos(recebido[chave], valor, f"{caminho}.{chave}")
    else:
        assert recebido == esperado, (
            f"{caminho}: esperado {esperado!r}, recebido {recebido!r}"
        )


def criar_reserva(api, payload):
    response = api.post(
        f"{BASE_URL}/booking",
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )
    verificar_status(response, 200)

    resultado = response.json()
    assert isinstance(resultado, dict), "Criação deve retornar um objeto JSON"
    assert "bookingid" in resultado, "Identificador ausente"
    assert type(resultado["bookingid"]) is int, (
        "bookingid deve ser inteiro e não booleano"
    )
    assert "booking" in resultado, "Objeto booking ausente"
    verificar_campos(resultado["booking"], payload)

    return resultado["bookingid"]


def consultar_e_verificar(api, booking_id, payload):
    response = api.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=TIMEOUT_SECONDS,
    )
    verificar_status(response, 200)
    verificar_campos(response.json(), payload)


def test_CT01_criar_reserva_completa(api):
    payload = montar_payload()
    criar_reserva(api, payload)


def test_CT02_consultar_reserva_criada(api):
    payload = montar_payload()
    booking_id = criar_reserva(api, payload)
    consultar_e_verificar(api, booking_id, payload)


def test_CT03_consultar_identificador_inexistente(api):
    response = api.get(
        f"{BASE_URL}/booking/99999999",
        timeout=TIMEOUT_SECONDS,
    )
    verificar_status(response, 404)


def test_CT04_filtrar_por_nome_e_sobrenome_unicos(api):
    payload = montar_payload()
    booking_id = criar_reserva(api, payload)

    response = api.get(
        f"{BASE_URL}/booking",
        params={
            "firstname": payload["firstname"],
            "lastname": payload["lastname"],
        },
        timeout=TIMEOUT_SECONDS,
    )
    verificar_status(response, 200)

    reservas = response.json()
    assert isinstance(reservas, list), "Listagem deve retornar um array JSON"

    identificadores = []
    for reserva in reservas:
        assert isinstance(reserva, dict), "Cada item deve ser um objeto JSON"
        assert "bookingid" in reserva, "Item sem bookingid"
        assert type(reserva["bookingid"]) is int, (
            "bookingid listado deve ser inteiro e não booleano"
        )
        identificadores.append(reserva["bookingid"])

    assert booking_id in identificadores, (
        f"Reserva {booking_id} ausente no resultado dos filtros"
    )


def test_CT05_preservar_deposito_nao_pago(api):
    payload = montar_payload(depositpaid=False)
    booking_id = criar_reserva(api, payload)
    consultar_e_verificar(api, booking_id, payload)


def test_CT06_preservar_datas_na_virada_do_ano(api):
    payload = montar_payload(
        checkin="2028-12-31",
        checkout="2029-01-01",
    )
    booking_id = criar_reserva(api, payload)
    consultar_e_verificar(api, booking_id, payload)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
