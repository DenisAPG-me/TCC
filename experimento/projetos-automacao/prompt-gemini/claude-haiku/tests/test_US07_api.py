import uuid

import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 10


def build_payload(**overrides):
    payload = {
        "firstname": f"Ana{uuid.uuid4().hex[:8]}",
        "lastname": f"Silva{uuid.uuid4().hex[:8]}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-05"},
        "additionalneeds": "Café da manhã",
    }
    payload.update(overrides)
    return payload


@pytest.fixture
def created_booking():
    payload = build_payload()
    response = requests.post(f"{BASE_URL}/booking", json=payload, timeout=TIMEOUT)
    assert response.status_code == 200
    return response.json()["bookingid"], payload


def test_ct01_criar_reserva_com_dados_validos():
    payload = build_payload()

    response = requests.post(f"{BASE_URL}/booking", json=payload, timeout=TIMEOUT)

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["bookingid"], int) and not isinstance(body["bookingid"], bool)
    assert body["booking"] == payload


def test_ct02_consultar_reserva_criada_pelo_identificador(created_booking):
    booking_id, payload = created_booking

    response = requests.get(f"{BASE_URL}/booking/{booking_id}", timeout=TIMEOUT)

    assert response.status_code == 200
    assert response.json() == payload


def test_ct03_consultar_identificador_inexistente_retorna_404():
    response = requests.get(f"{BASE_URL}/booking/99999999", timeout=TIMEOUT)

    assert response.status_code == 404


def test_ct04_listar_reservas_por_nome_contem_identificador_criado(created_booking):
    booking_id, payload = created_booking

    response = requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": payload["firstname"], "lastname": payload["lastname"]},
        timeout=TIMEOUT,
    )

    assert response.status_code == 200
    assert any(item["bookingid"] == booking_id for item in response.json())


def test_ct05_consultar_identificador_zero_retorna_404():
    response = requests.get(f"{BASE_URL}/booking/0", timeout=TIMEOUT)

    assert response.status_code == 404


def test_ct06_listar_reservas_sem_correspondencia_retorna_lista_vazia():
    response = requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": f"Inexistente{uuid.uuid4().hex}", "lastname": f"Nulo{uuid.uuid4().hex}"},
        timeout=TIMEOUT,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_ct07_criar_reserva_com_preco_zero_e_deposito_nao_pago():
    payload = build_payload(totalprice=0, depositpaid=False)

    response = requests.post(f"{BASE_URL}/booking", json=payload, timeout=TIMEOUT)

    assert response.status_code == 200
    assert response.json()["booking"] == payload


def test_ct08_criar_reserva_com_caracteres_especiais_e_acentuados():
    payload = build_payload(
        firstname="José-Ângelo",
        lastname="O'Neil Çaçá",
        additionalneeds="Berço ao lado da janela, sem glúten",
    )

    response = requests.post(f"{BASE_URL}/booking", json=payload, timeout=TIMEOUT)

    assert response.status_code == 200
    assert response.json()["booking"] == payload


def test_ct09_criar_reserva_com_corpo_sem_campos_obrigatorios_retorna_erro():
    response = requests.post(f"{BASE_URL}/booking", json={}, timeout=TIMEOUT)

    assert response.status_code >= 400
    assert "bookingid" not in response.text


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
