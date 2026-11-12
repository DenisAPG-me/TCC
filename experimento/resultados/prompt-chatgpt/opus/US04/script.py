import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

FIELD_TEST_IDS = {
    "name": "ContactName",
    "email": "ContactEmail",
    "phone": "ContactPhone",
    "subject": "ContactSubject",
    "message": "ContactDescription",
}

SUBMIT_BUTTON_NAME = "Submit"

BLANK_MESSAGES = [
    "Name may not be blank",
    "Email may not be blank",
    "Phone may not be blank",
    "Subject may not be blank",
    "Message may not be blank",
]

PHONE_LENGTH_MESSAGE = "Phone must be between 11 and 21 characters."
SUBJECT_LENGTH_MESSAGE = "Subject must be between 5 and 100 characters."
MESSAGE_LENGTH_MESSAGE = "Message must be between 20 and 2000 characters."
EMAIL_FORMAT_MESSAGE = "must be a well-formed email address"
SUCCESS_PREFIX = "Thanks for getting in touch"

VALID_DATA = {
    "name": "Maria Teste",
    "email": "maria.teste@example.com",
    "phone": "01234567890123",
    "subject": "Question about booking",
    "message": "I would like to know if breakfast is included in the price.",
}


def resolve_base_url(base_url):
    return base_url or BASE_URL


def open_home(page: Page, base_url):
    page.goto(resolve_base_url(base_url))
    expect(page.get_by_test_id(FIELD_TEST_IDS["name"])).to_be_visible()


def fill_contact_form(page: Page, data):
    for field, value in data.items():
        page.get_by_test_id(FIELD_TEST_IDS[field]).fill(value)


def submit_form(page: Page):
    page.get_by_role("button", name=SUBMIT_BUTTON_NAME).click()


def success_heading(page: Page, name):
    return page.get_by_role("heading", name=f"{SUCCESS_PREFIX} {name}!")


def any_success_heading(page: Page):
    return page.get_by_role("heading", name=re.compile(re.escape(SUCCESS_PREFIX)))


def test_CT001_formulario_vazio_exibe_campos_em_branco(page: Page, base_url):
    open_home(page, base_url)
    submit_form(page)
    for text in BLANK_MESSAGES:
        expect(page.get_by_text(text, exact=True)).to_be_visible()
    expect(any_success_heading(page)).to_have_count(0)


def test_CT002_telefone_com_10_caracteres_exibe_erro(page: Page, base_url):
    open_home(page, base_url)
    fill_contact_form(page, {**VALID_DATA, "phone": "0123456789"})
    submit_form(page)
    expect(page.get_by_text(PHONE_LENGTH_MESSAGE, exact=True)).to_be_visible()
    expect(any_success_heading(page)).to_have_count(0)


def test_CT003_telefone_com_11_caracteres_e_aceito(page: Page, base_url):
    open_home(page, base_url)
    data = {**VALID_DATA, "phone": "01234567890"}
    fill_contact_form(page, data)
    submit_form(page)
    expect(success_heading(page, data["name"])).to_be_visible()
    expect(page.get_by_text(PHONE_LENGTH_MESSAGE, exact=True)).to_have_count(0)


def test_CT004_assunto_e_mensagem_curtos_exibem_erros(page: Page, base_url):
    open_home(page, base_url)
    fill_contact_form(
        page,
        {**VALID_DATA, "subject": "Abcd", "message": "Mensagem curta 1234"},
    )
    submit_form(page)
    expect(page.get_by_text(SUBJECT_LENGTH_MESSAGE, exact=True)).to_be_visible()
    expect(page.get_by_text(MESSAGE_LENGTH_MESSAGE, exact=True)).to_be_visible()
    expect(any_success_heading(page)).to_have_count(0)


def test_CT005_assunto_5_e_mensagem_20_caracteres_sao_aceitos(page: Page, base_url):
    open_home(page, base_url)
    data = {**VALID_DATA, "subject": "Abcde", "message": "Mensagem curta 12345"}
    assert len(data["subject"]) == 5
    assert len(data["message"]) == 20
    fill_contact_form(page, data)
    submit_form(page)
    expect(success_heading(page, data["name"])).to_be_visible()
    expect(page.get_by_text(data["subject"])).to_be_visible()
    expect(page.get_by_text(SUBJECT_LENGTH_MESSAGE, exact=True)).to_have_count(0)
    expect(page.get_by_text(MESSAGE_LENGTH_MESSAGE, exact=True)).to_have_count(0)


def test_CT006_email_malformado_exibe_erro(page: Page, base_url):
    open_home(page, base_url)
    fill_contact_form(page, {**VALID_DATA, "email": "bad"})
    submit_form(page)
    expect(page.get_by_text(EMAIL_FORMAT_MESSAGE, exact=True)).to_be_visible()
    expect(any_success_heading(page)).to_have_count(0)


def test_CT007_dados_validos_exibem_confirmacao(page: Page, base_url):
    open_home(page, base_url)
    fill_contact_form(page, VALID_DATA)
    submit_form(page)
    expect(success_heading(page, VALID_DATA["name"])).to_be_visible()
    expect(page.get_by_text(VALID_DATA["subject"])).to_be_visible()
