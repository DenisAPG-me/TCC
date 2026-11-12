import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"
AUTH_URL = f"{BASE_URL}/auth"
BOOKING_URL = f"{BASE_URL}/booking"
REQUEST_TIMEOUT = 15
JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

ADMIN_CREDENTIALS = {"username": "admin", "password": "password123"}
WRONG_PASSWORD_CREDENTIALS = {"username": "admin", "password": "senha-incorreta"}
EMPTY_CREDENTIALS = {"username": "", "password": ""}
BAD_CREDENTIALS_REASON = "Bad credentials"

DELETE_SUCCESS_STATUS = 201
CHECKIN_DATE = "2026-11-01"
CHECKOUT_DATE = "2026-11-05"


def build_booking(firstname="Ana", lastname="Silva", totalprice=150):
    return {
        "firstname": firstname,
        "lastname": lastname,
        "totalprice": totalprice,
        "depositpaid": True,
        "bookingdates": {"checkin": CHECKIN_DATE, "checkout": CHECKOUT_DATE},
        "additionalneeds": "Café da manhã",
    }


def auth_headers(token):
    return {**JSON_HEADERS, "Cookie": f"token={token}"}


def authenticate(credentials):
    return requests.post(AUTH_URL, json=credentials, headers=JSON_HEADERS, timeout=REQUEST_TIMEOUT)


def create_booking(payload):
    return requests.post(BOOKING_URL, json=payload, headers=JSON_HEADERS, timeout=REQUEST_TIMEOUT)


def get_booking(booking_id):
    return requests.get(f"{BOOKING_URL}/{booking_id}", headers=JSON_HEADERS, timeout=REQUEST_TIMEOUT)


def update_booking(booking_id, payload, headers):
    return requests.put(f"{BOOKING_URL}/{booking_id}", json=payload, headers=headers, timeout=REQUEST_TIMEOUT)


def partial_update_booking(booking_id, payload, headers):
    return requests.patch(f"{BOOKING_URL}/{booking_id}", json=payload, headers=headers, timeout=REQUEST_TIMEOUT)


def delete_booking(booking_id, token):
    return requests.delete(f"{BOOKING_URL}/{booking_id}", headers=auth_headers(token), timeout=REQUEST_TIMEOUT)


@pytest.fixture
def admin_token():
    response = authenticate(ADMIN_CREDENTIALS)
    assert response.status_code == 200, response.text
    token = response.json().get("token")
    assert token, "Token não retornado na preparação"
    return token


@pytest.fixture
def existing_booking(admin_token):
    response = create_booking(build_booking())
    assert response.status_code == 200, response.text
    booking_id = response.json()["bookingid"]
    yield booking_id
    cleanup = delete_booking(booking_id, admin_token)
    assert cleanup.status_code == DELETE_SUCCESS_STATUS, cleanup.text


def test_CT001_autenticacao_com_credenciais_validas_retorna_token():
    response = authenticate(ADMIN_CREDENTIALS)
    assert response.status_code == 200, response.text
    token = response.json().get("token")
    assert isinstance(token, str)
    assert token.strip() != ""


def test_CT002_autenticacao_com_senha_incorreta_nao_retorna_token():
    response = authenticate(WRONG_PASSWORD_CREDENTIALS)
    body = response.json()
    assert "token" not in body
    assert body.get("reason") == BAD_CREDENTIALS_REASON


def test_CT003_autenticacao_com_campos_vazios_nao_retorna_token():
    response = authenticate(EMPTY_CREDENTIALS)
    body = response.json()
    assert "token" not in body
    assert body.get("reason") == BAD_CREDENTIALS_REASON


def test_CT004_atualizacao_completa_altera_nome_e_preco(admin_token, existing_booking):
    payload = build_booking(firstname="Beatriz", lastname="Souza", totalprice=320)
    response = update_booking(existing_booking, payload, auth_headers(admin_token))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["firstname"] == "Beatriz"
    assert body["totalprice"] == 320
    assert body["lastname"] == "Souza"


def test_CT005_atualizacao_parcial_altera_somente_sobrenome(admin_token, existing_booking):
    before_response = get_booking(existing_booking)
    assert before_response.status_code == 200, before_response.text
    before = before_response.json()

    response = partial_update_booking(existing_booking, {"lastname": "Pereira"}, auth_headers(admin_token))
    assert response.status_code == 200, response.text
    after = response.json()
    assert after["lastname"] == "Pereira"
    for field in ("firstname", "totalprice", "depositpaid", "bookingdates", "additionalneeds"):
        assert after[field] == before[field]


def test_CT006_atualizacao_completa_sem_token_retorna_403(existing_booking):
    response = update_booking(existing_booking, build_booking(), JSON_HEADERS)
    assert response.status_code == 403, response.text


def test_CT007_atualizacao_completa_com_corpo_vazio_retorna_400(admin_token, existing_booking):
    response = update_booking(existing_booking, {}, auth_headers(admin_token))
    assert response.status_code == 400, response.text


def test_CT008_atualizacao_completa_sem_bookingdates_retorna_400(admin_token, existing_booking):
    payload = build_booking()
    del payload["bookingdates"]
    response = update_booking(existing_booking, payload, auth_headers(admin_token))
    assert response.status_code == 400, response.text
