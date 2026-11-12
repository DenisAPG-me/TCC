import requests
import pytest


BASE_URL = "https://restful-booker.herokuapp.com"
TIMEOUT_SECONDS = 15

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

BOOKING_TEMPLATE = {
    "firstname": "Casey",
    "lastname": "Original",
    "totalprice": 120,
    "depositpaid": True,
    "bookingdates": {
        "checkin": "2027-05-10",
        "checkout": "2027-05-15",
    },
    "additionalneeds": "Breakfast",
}


def authenticate(username=ADMIN_USERNAME, password=ADMIN_PASSWORD):
    return requests.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
        timeout=TIMEOUT_SECONDS,
    )


def create_booking():
    response = requests.post(
        f"{BASE_URL}/booking",
        json=BOOKING_TEMPLATE,
        timeout=TIMEOUT_SECONDS,
    )
    assert response.status_code == 200, (
        f"Reserva de preparação não criada: HTTP {response.status_code}, "
        f"corpo: {response.text}"
    )
    booking_id = response.json()["bookingid"]
    assert booking_id
    return booking_id


def get_booking(booking_id):
    response = requests.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=TIMEOUT_SECONDS,
    )
    assert response.status_code == 200, (
        f"Não foi possível consultar reserva {booking_id}: "
        f"HTTP {response.status_code}, corpo: {response.text}"
    )
    return response.json()


def admin_cookie():
    response = authenticate()
    assert response.status_code == 200, (
        f"Falha ao obter token para preparação: HTTP {response.status_code}, "
        f"corpo: {response.text}"
    )
    token = response.json().get("token")
    assert isinstance(token, str) and token
    return {"Cookie": f"token={token}"}


def delete_booking(booking_id, headers):
    response = requests.delete(
        f"{BASE_URL}/booking/{booking_id}",
        headers=headers,
        timeout=TIMEOUT_SECONDS,
    )
    assert response.status_code in (200, 201), (
        f"Falha ao remover reserva de teste {booking_id}: "
        f"HTTP {response.status_code}, corpo: {response.text}"
    )


def test_CT001_autenticar_com_credenciais_validas():
    response = authenticate()

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("token"), str)
    assert body["token"].strip()


def test_CT002_rejeitar_credenciais_invalidas():
    response = authenticate(password="senha_incorreta")

    body = response.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"


def test_CT003_atualizar_todos_os_dados_da_reserva():
    booking_id = create_booking()
    headers = admin_cookie()
    updated_booking = {
        "firstname": "Jordan",
        "lastname": "Updated",
        "totalprice": 345,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2027-06-01",
            "checkout": "2027-06-08",
        },
        "additionalneeds": "Late checkout",
    }

    try:
        response = requests.put(
            f"{BASE_URL}/booking/{booking_id}",
            json=updated_booking,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )

        assert response.status_code == 200
        assert response.json()["firstname"] == updated_booking["firstname"]
        assert response.json()["totalprice"] == updated_booking["totalprice"]

        stored_booking = get_booking(booking_id)
        assert stored_booking["firstname"] == updated_booking["firstname"]
        assert stored_booking["totalprice"] == updated_booking["totalprice"]
    finally:
        delete_booking(booking_id, headers)


def test_CT004_atualizar_apenas_o_sobrenome():
    booking_id = create_booking()
    headers = admin_cookie()
    before = get_booking(booking_id)
    new_lastname = "Changed"

    try:
        response = requests.patch(
            f"{BASE_URL}/booking/{booking_id}",
            json={"lastname": new_lastname},
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )

        assert response.status_code == 200
        assert response.json()["lastname"] == new_lastname

        after = get_booking(booking_id)
        assert after["lastname"] == new_lastname
        for field in ("firstname", "totalprice", "depositpaid", "bookingdates", "additionalneeds"):
            assert after[field] == before[field]
    finally:
        delete_booking(booking_id, headers)


def test_CT005_recusar_atualizacao_sem_token():
    booking_id = create_booking()
    cleanup_headers = admin_cookie()

    try:
        response = requests.put(
            f"{BASE_URL}/booking/{booking_id}",
            json=BOOKING_TEMPLATE,
            timeout=TIMEOUT_SECONDS,
        )

        assert response.status_code == 403
    finally:
        delete_booking(booking_id, cleanup_headers)


def test_CT006_recusar_atualizacao_sem_campo_obrigatorio():
    booking_id = create_booking()
    headers = admin_cookie()
    incomplete_booking = {
        "lastname": "MissingFirstName",
        "totalprice": 250,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2027-07-01",
            "checkout": "2027-07-03",
        },
        "additionalneeds": "None",
    }

    try:
        response = requests.put(
            f"{BASE_URL}/booking/{booking_id}",
            json=incomplete_booking,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )

        assert response.status_code == 400
    finally:
        delete_booking(booking_id, headers)
