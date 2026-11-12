import uuid

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

VALID_NAME = "Maria Silva"
VALID_EMAIL = "maria.silva@example.com"
VALID_PHONE = "01234567890"
VALID_SUBJECT = "Duvida sobre reserva"
VALID_MESSAGE = "Gostaria de saber se aceitam animais de estimacao."
INVALID_EMAIL = "bad"

PHONE_TOO_SHORT = "0123456789"
PHONE_TOO_LONG = "0123456789012345678901"
SUBJECT_TOO_SHORT = "Abcd"
SUBJECT_MIN = "Abcde"
MESSAGE_TOO_SHORT = "a" * 19
MESSAGE_MIN = "a" * 20

MSG_NAME_BLANK = "Name may not be blank"
MSG_EMAIL_BLANK = "Email may not be blank"
MSG_PHONE_BLANK = "Phone may not be blank"
MSG_SUBJECT_BLANK = "Subject may not be blank"
MSG_MESSAGE_BLANK = "Message may not be blank"
MSG_PHONE_SIZE = "Phone must be between 11 and 21 characters."
MSG_SUBJECT_SIZE = "Subject must be between 5 and 100 characters."
MSG_MESSAGE_SIZE = "Message must be between 20 and 2000 characters."
MSG_EMAIL_FORMAT = "must be a well-formed email address"
MSG_THANKS_PREFIX = "Thanks for getting in touch"


@pytest.fixture
def home(page: Page) -> Page:
    page.goto(BASE_URL)
    expect(page.get_by_test_id("ContactName")).to_be_visible()
    return page


def unique_subject(base: str = VALID_SUBJECT) -> str:
    return f"{base} {uuid.uuid4().hex[:6]}"


def submit_contact(page: Page, name="", email="", phone="", subject="", message=""):
    page.get_by_test_id("ContactName").fill(name)
    page.get_by_test_id("ContactEmail").fill(email)
    page.get_by_test_id("ContactPhone").fill(phone)
    page.get_by_test_id("ContactSubject").fill(subject)
    page.get_by_test_id("ContactDescription").fill(message)
    page.get_by_role("button", name="Submit").click()


def expect_success(page: Page, name: str, subject: str):
    expect(page.get_by_text(f"{MSG_THANKS_PREFIX} {name}!")).to_be_visible()
    expect(page.get_by_text(subject, exact=True)).to_be_visible()


def test_ct01_envio_formulario_vazio(home: Page):
    submit_contact(home)
    for msg in (MSG_NAME_BLANK, MSG_EMAIL_BLANK, MSG_PHONE_BLANK, MSG_SUBJECT_BLANK, MSG_MESSAGE_BLANK):
        expect(home.get_by_text(msg)).to_be_visible()
    expect(home.get_by_text(MSG_THANKS_PREFIX)).to_have_count(0)


def test_ct02_telefone_com_10_caracteres(home: Page):
    submit_contact(home, VALID_NAME, VALID_EMAIL, PHONE_TOO_SHORT, unique_subject(), VALID_MESSAGE)
    expect(home.get_by_text(MSG_PHONE_SIZE)).to_be_visible()
    expect(home.get_by_text(MSG_THANKS_PREFIX)).to_have_count(0)


def test_ct03_telefone_com_11_caracteres(home: Page):
    subject = unique_subject()
    submit_contact(home, VALID_NAME, VALID_EMAIL, VALID_PHONE, subject, VALID_MESSAGE)
    expect_success(home, VALID_NAME, subject)
    expect(home.get_by_text(MSG_PHONE_SIZE)).to_have_count(0)


def test_ct04_telefone_com_22_caracteres(home: Page):
    submit_contact(home, VALID_NAME, VALID_EMAIL, PHONE_TOO_LONG, unique_subject(), VALID_MESSAGE)
    expect(home.get_by_text(MSG_PHONE_SIZE)).to_be_visible()
    expect(home.get_by_text(MSG_THANKS_PREFIX)).to_have_count(0)


def test_ct05_assunto_e_mensagem_abaixo_do_minimo(home: Page):
    submit_contact(home, VALID_NAME, VALID_EMAIL, VALID_PHONE, SUBJECT_TOO_SHORT, MESSAGE_TOO_SHORT)
    expect(home.get_by_text(MSG_SUBJECT_SIZE)).to_be_visible()
    expect(home.get_by_text(MSG_MESSAGE_SIZE)).to_be_visible()
    expect(home.get_by_text(MSG_THANKS_PREFIX)).to_have_count(0)


def test_ct06_assunto_e_mensagem_no_limite_minimo(home: Page):
    subject = f"{SUBJECT_MIN}{uuid.uuid4().hex[:4]}"
    submit_contact(home, VALID_NAME, VALID_EMAIL, VALID_PHONE, subject[:5], MESSAGE_MIN)
    expect_success(home, VALID_NAME, subject[:5])
    expect(home.get_by_text(MSG_SUBJECT_SIZE)).to_have_count(0)
    expect(home.get_by_text(MSG_MESSAGE_SIZE)).to_have_count(0)


def test_ct07_email_malformado(home: Page):
    submit_contact(home, VALID_NAME, INVALID_EMAIL, VALID_PHONE, unique_subject(), VALID_MESSAGE)
    expect(home.get_by_text(MSG_EMAIL_FORMAT)).to_be_visible()
    expect(home.get_by_text(MSG_THANKS_PREFIX)).to_have_count(0)


def test_ct08_envio_com_dados_validos(home: Page):
    subject = unique_subject()
    submit_contact(home, VALID_NAME, VALID_EMAIL, VALID_PHONE, subject, VALID_MESSAGE)
    expect_success(home, VALID_NAME, subject)
