import requests

BASE_URL = "https://restful-booker.herokuapp.com"
USERNAME = "admin"
PASSWORD = "password123"
INVALID_USERNAME = "invalid-admin"
INVALID_PASSWORD = "invalid-password"
TIMEOUT = 10

INITIAL_BOOKING = {
    "firstname": "QA",
    "lastname": "Original",
    "totalprice": 100,
    "depositpaid": True,
    "bookingdates": {
        "checkin": "2026-11-01",
        "checkout": "2026-11-05",
    },
    "additionalneeds": "Breakfast",
}


def _authenticate(username=USERNAME, password=PASSWORD):
    return requests.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
        timeout=TIMEOUT,
    )


def _create_booking():
    response = requests.post(
        f"{BASE_URL}/booking",
        json=INITIAL_BOOKING,
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, (
        f"Booking creation failed: {response.status_code} {response.text}"
    )
    booking_id = response.json().get("bookingid")
    assert booking_id is not None
    return booking_id


def _get_token():
    response = _authenticate()
    assert response.status_code == 200
    token = response.json().get("token")
    assert isinstance(token, str) and token
    return token


def test_ct01_autenticar_com_credenciais_validas():
    response = _authenticate()

    assert response.status_code == 200
    token = response.json().get("token")
    assert isinstance(token, str)
    assert token.strip()


def test_ct02_rejeitar_credenciais_invalidas():
    response = _authenticate(INVALID_USERNAME, INVALID_PASSWORD)

    assert response.status_code == 200
    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_ct03_atualizar_reserva_completa():
    booking_id = _create_booking()
    token = _get_token()
    updated_booking = {
        **INITIAL_BOOKING,
        "firstname": "Updated",
        "totalprice": 250,
    }

    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=updated_booking,
        cookies={"token": token},
        timeout=TIMEOUT,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["firstname"] == "Updated"
    assert body["totalprice"] == 250


def test_ct04_atualizar_parcialmente_o_sobrenome():
    booking_id = _create_booking()
    token = _get_token()

    response = requests.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json={"lastname": "Changed"},
        cookies={"token": token},
        timeout=TIMEOUT,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["lastname"] == "Changed"
    assert body["firstname"] == INITIAL_BOOKING["firstname"]
    assert body["totalprice"] == INITIAL_BOOKING["totalprice"]
    assert body["depositpaid"] == INITIAL_BOOKING["depositpaid"]
    assert body["bookingdates"] == INITIAL_BOOKING["bookingdates"]
    assert body["additionalneeds"] == INITIAL_BOOKING["additionalneeds"]


def test_ct05_atualizar_sem_token():
    booking_id = _create_booking()

    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json={**INITIAL_BOOKING, "firstname": "NoToken"},
        timeout=TIMEOUT,
    )

    assert response.status_code == 403


def test_ct06_atualizar_sem_campo_obrigatorio():
    booking_id = _create_booking()
    token = _get_token()
    incomplete_booking = {
        key: value
        for key, value in INITIAL_BOOKING.items()
        if key != "firstname"
    }

    response = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=incomplete_booking,
        cookies={"token": token},
        timeout=TIMEOUT,
    )

    assert response.status_code == 400
