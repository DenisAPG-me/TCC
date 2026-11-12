import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 15


def build_payload(**overrides):
    payload = {
        "firstname": f"Ana{uuid.uuid4().hex[:8]}",
        "lastname": f"Silva{uuid.uuid4().hex[:8]}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-01-10", "checkout": "2026-01-15"},
        "additionalneeds": "Café da manhã",
    }
    payload.update(overrides)
    return payload


def create_booking(payload):
    return requests.post(f"{BASE_URL}/booking", json=payload, timeout=TIMEOUT)


def get_booking(booking_id):
    return requests.get(f"{BASE_URL}/booking/{booking_id}", timeout=TIMEOUT)


def search_bookings(firstname, lastname):
    return requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": firstname, "lastname": lastname},
        timeout=TIMEOUT,
    )


@pytest.fixture
def created_booking():
    payload = build_payload()
    response = create_booking(payload)
    assert response.status_code == 200
    return response.json()["bookingid"], payload


def test_TC01_criar_reserva_com_dados_validos_retorna_200_e_dados_iguais():
    payload = build_payload()

    response = create_booking(payload)

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["bookingid"], int)
    assert body["booking"] == payload


def test_TC02_consultar_reserva_criada_retorna_200_e_campos_iguais(created_booking):
    booking_id, payload = created_booking

    response = get_booking(booking_id)

    assert response.status_code == 200
    assert response.json() == payload


def test_TC03_consultar_identificador_inexistente_retorna_404():
    response = get_booking(99999999)

    assert response.status_code == 404


def test_TC04_listar_por_nome_e_sobrenome_inclui_identificador_criado(created_booking):
    booking_id, payload = created_booking

    response = search_bookings(payload["firstname"], payload["lastname"])

    assert response.status_code == 200
    booking_ids = [item["bookingid"] for item in response.json()]
    assert booking_id in booking_ids


def test_TC05_consultar_identificador_zero_retorna_404():
    response = get_booking(0)

    assert response.status_code == 404


def test_TC06_criar_reserva_com_valores_de_borda_retorna_200_e_dados_iguais():
    payload = build_payload(
        totalprice=0,
        depositpaid=False,
        bookingdates={"checkin": "2026-01-10", "checkout": "2026-01-10"},
    )

    response = create_booking(payload)

    assert response.status_code == 200
    assert response.json()["booking"] == payload


def test_TC07_listar_por_nome_inexistente_retorna_lista_vazia():
    response = search_bookings(f"Inexistente{uuid.uuid4().hex}", f"Fantasma{uuid.uuid4().hex}")

    assert response.status_code == 200
    assert response.json() == []


def test_TC08_criar_reserva_com_json_malformado_retorna_erro():
    response = requests.post(
        f"{BASE_URL}/booking",
        data="{invalido",
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT,
    )

    assert response.status_code >= 400
    assert "bookingid" not in response.text
