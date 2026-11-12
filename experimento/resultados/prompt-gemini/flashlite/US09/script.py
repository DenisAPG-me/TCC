import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"


@pytest.fixture(scope="session")
def auth_token():
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": "admin", "password": "password123"},
    )
    assert response.status_code == 200
    return response.json().get("token")


@pytest.fixture
def sample_booking():
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"},
        "additionalneeds": "Breakfast",
    }
    response = requests.post(f"{BASE_URL}/booking", json=payload)
    assert response.status_code == 200
    data = response.json()
    return data["bookingid"]


def test_CT01_exclusao_sem_token(sample_booking):
    delete_response = requests.delete(f"{BASE_URL}/booking/{sample_booking}")
    assert delete_response.status_code == 403

    get_response = requests.get(f"{BASE_URL}/booking/{sample_booking}")
    assert get_response.status_code == 200


def test_CT02_exclusao_token_invalido(sample_booking):
    headers = {"Cookie": "token=invalidtoken123"}
    delete_response = requests.delete(
        f"{BASE_URL}/booking/{sample_booking}", headers=headers
    )
    assert delete_response.status_code == 403

    get_response = requests.get(f"{BASE_URL}/booking/{sample_booking}")
    assert get_response.status_code == 200


def test_CT03_exclusao_com_sucesso(auth_token, sample_booking):
    headers = {"Cookie": f"token={auth_token}"}
    delete_response = requests.delete(
        f"{BASE_URL}/booking/{sample_booking}", headers=headers
    )
    assert delete_response.status_code in [201, 200]


def test_CT04_consulta_apos_exclusao(auth_token, sample_booking):
    headers = {"Cookie": f"token={auth_token}"}
    requests.delete(f"{BASE_URL}/booking/{sample_booking}", headers=headers)

    get_response = requests.get(f"{BASE_URL}/booking/{sample_booking}")
    assert get_response.status_code == 404


def test_CT05_exclusao_duplicada(auth_token, sample_booking):
    headers = {"Cookie": f"token={auth_token}"}
    # Primeira exclusão
    res1 = requests.delete(f"{BASE_URL}/booking/{sample_booking}", headers=headers)
    assert res1.status_code in [201, 200]

    # Segunda exclusão
    res2 = requests.delete(f"{BASE_URL}/booking/{sample_booking}", headers=headers)
    assert 400 <= res2.status_code < 500


def test_CT06_listagem_por_nome_apos_exclusao(auth_token):
    unique_firstname = "UniqueNameDeleteTest"
    unique_lastname = "UniqueLast"
    payload = {
        "firstname": unique_firstname,
        "lastname": unique_lastname,
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-05-01", "checkout": "2026-05-05"},
        "additionalneeds": "Lunch",
    }
    create_res = requests.post(f"{BASE_URL}/booking", json=payload)
    assert create_res.status_code == 200
    booking_id = create_res.json()["bookingid"]

    headers = {"Cookie": f"token={auth_token}"}
    del_res = requests.delete(f"{BASE_URL}/booking/{booking_id}", headers=headers)
    assert del_res.status_code in [201, 200]

    list_res = requests.get(
        f"{BASE_URL}/booking",
        params={"firstname": unique_firstname, "lastname": unique_lastname},
    )
    assert list_res.status_code == 200
    assert list_res.json() == []
