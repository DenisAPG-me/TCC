import requests

BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT = 15

VALID_CREDENTIALS = {
    "username": "admin",
    "password": "password123",
}


def create_booking():
    payload = {
        "firstname": "Joana",
        "lastname": "Silva",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-11-01",
            "checkout": "2026-11-05",
        },
        "additionalneeds": "Breakfast",
    }
    response = requests.post(
        f"{BASE_URL}/booking",
        json=payload,
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, response.text
    booking_id = response.json().get("bookingid")
    assert booking_id is not None
    return booking_id, payload


def get_token(credentials=None):
    response = requests.post(
        f"{BASE_URL}/auth",
        json=credentials or VALID_CREDENTIALS,
        timeout=TIMEOUT,
    )
    return response


def test_CT01_autenticar_com_credenciais_validas():
    response = get_token()

    assert response.status_code == 200, response.text
    assert response.json().get("token")


def test_CT02_rejeitar_credenciais_invalidas():
    response = get_token({
        "username": "admin",
        "password": "senha-incorreta",
    })

    assert response.status_code == 200, response.text
    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_CT03_atualizar_reserva_completa():
    booking_id, _ = create_booking()
    token_response = get_token()
    assert token_response.status_code == 200, token_response.text
    token = token_response.json()["token"]

    updated_booking = {
        "firstname": "Marina",
        "lastname": "Oliveira",
        "totalprice": 275,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-11-10",
            "checkout": "2026-11-15",
        },
        "additionalneeds": "Lunch",
    }
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=updated_booking,
        cookies={"token": token},
        timeout=TIMEOUT,
    )

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["firstname"] == "Marina"
    assert result["totalprice"] == 275


def test_CT04_atualizar_somente_sobrenome():
    booking_id, original = create_booking()
    token_response = get_token()
    assert token_response.status_code == 200, token_response.text
    token = token_response.json()["token"]

    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json={"lastname": "Pereira"},
        cookies={"token": token},
        timeout=TIMEOUT,
    )

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["lastname"] == "Pereira"
    assert result["firstname"] == original["firstname"]
    assert result["totalprice"] == original["totalprice"]
    assert result["depositpaid"] == original["depositpaid"]
    assert result["bookingdates"] == original["bookingdates"]
    assert result["additionalneeds"] == original["additionalneeds"]


def test_CT05_rejeitar_atualizacao_sem_token():
    booking_id, payload = create_booking()

    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=payload,
        timeout=TIMEOUT,
    )

    assert response.status_code == 403, response.text


def test_CT06_rejeitar_atualizacao_com_campo_obrigatorio_ausente():
    booking_id, _ = create_booking()
    token_response = get_token()
    assert token_response.status_code == 200, token_response.text
    token = token_response.json()["token"]

    incomplete_booking = {
        "firstname": "Joana",
        "lastname": "Silva",
        "totalprice": 150,
        "depositpaid": True,
        "additionalneeds": "Breakfast",
    }
    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=incomplete_booking,
        cookies={"token": token},
        timeout=TIMEOUT,
    )

    assert response.status_code == 400, response.text
