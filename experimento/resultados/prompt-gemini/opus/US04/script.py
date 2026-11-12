import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"
TIMEOUT = 10_000

VALID_NAME = "Maria Silva"
VALID_EMAIL = "maria.silva@example.com"
VALID_PHONE = "01234567890"
VALID_SUBJECT = "Duvida sobre reserva"
VALID_MESSAGE = "Gostaria de saber se aceitam animais de estimacao."

PHONE_ERROR = "Phone must be between 11 and 21 characters."
SUBJECT_ERROR = "Subject must be between 5 and 100 characters."
MESSAGE_ERROR = "Message must be between 20 and 2000 characters."
EMAIL_ERROR = "must be a well-formed email address"


def open_home(page: Page, base_url) -> None:
    page.goto(base_url or BASE_URL)


def fill_contact_form(
    page: Page,
    name: str = VALID_NAME,
    email: str = VALID_EMAIL,
    phone: str = VALID_PHONE,
    subject: str = VALID_SUBJECT,
    message: str = VALID_MESSAGE,
) -> None:
    page.get_by_test_id("ContactName").fill(name)
    page.get_by_test_id("ContactEmail").fill(email)
    page.get_by_test_id("ContactPhone").fill(phone)
    page.get_by_test_id("ContactSubject").fill(subject)
    page.get_by_test_id("ContactDescription").fill(message)


def submit(page: Page) -> None:
    page.get_by_role("button", name="Submit").click()


def expect_message(page: Page, text: str) -> None:
    expect(page.get_by_text(text)).to_be_visible(timeout=TIMEOUT)


def expect_success(page: Page, name: str, subject: str) -> None:
    expect(
        page.get_by_role("heading", name=f"Thanks for getting in touch {name}!")
    ).to_be_visible(timeout=TIMEOUT)
    expect(page.get_by_text(subject, exact=True)).to_be_visible(timeout=TIMEOUT)


def test_ct01_formulario_vazio_exibe_campos_obrigatorios(page: Page, base_url):
    open_home(page, base_url)
    submit(page)
    for text in (
        "Name may not be blank",
        "Email may not be blank",
        "Phone may not be blank",
        "Subject may not be blank",
        "Message may not be blank",
    ):
        expect_message(page, text)


def test_ct02_telefone_com_10_caracteres_exibe_erro(page: Page, base_url):
    open_home(page, base_url)
    fill_contact_form(page, phone="0" * 10)
    submit(page)
    expect_message(page, PHONE_ERROR)


def test_ct03_telefone_com_11_caracteres_e_aceito(page: Page, base_url):
    open_home(page, base_url)
    fill_contact_form(page, phone="0" * 11)
    submit(page)
    expect_success(page, VALID_NAME, VALID_SUBJECT)


def test_ct04_telefone_com_21_caracteres_e_aceito(page: Page, base_url):
    open_home(page, base_url)
    fill_contact_form(page, phone="0" * 21)
    submit(page)
    expect_success(page, VALID_NAME, VALID_SUBJECT)


def test_ct05_telefone_com_22_caracteres_exibe_erro(page: Page, base_url):
    open_home(page, base_url)
    fill_contact_form(page, phone="0" * 22)
    submit(page)
    expect_message(page, PHONE_ERROR)


def test_ct06_assunto_4_e_mensagem_19_caracteres_exibem_erros(page: Page, base_url):
    open_home(page, base_url)
    fill_contact_form(page, subject="a" * 4, message="m" * 19)
    submit(page)
    expect_message(page, SUBJECT_ERROR)
    expect_message(page, MESSAGE_ERROR)


def test_ct07_assunto_5_e_mensagem_20_caracteres_sao_aceitos(page: Page, base_url):
    subject = "a" * 5
    open_home(page, base_url)
    fill_contact_form(page, subject=subject, message="m" * 20)
    submit(page)
    expect_success(page, VALID_NAME, subject)


def test_ct08_assunto_100_e_mensagem_2000_caracteres_sao_aceitos(page: Page, base_url):
    subject = "a" * 100
    open_home(page, base_url)
    fill_contact_form(page, subject=subject, message="m" * 2000)
    submit(page)
    expect_success(page, VALID_NAME, subject)


def test_ct09_assunto_101_e_mensagem_2001_caracteres_exibem_erros(page: Page, base_url):
    open_home(page, base_url)
    fill_contact_form(page, subject="a" * 101, message="m" * 2001)
    submit(page)
    expect_message(page, SUBJECT_ERROR)
    expect_message(page, MESSAGE_ERROR)


def test_ct10_email_malformado_exibe_erro(page: Page, base_url):
    open_home(page, base_url)
    fill_contact_form(page, email="bad")
    submit(page)
    expect_message(page, EMAIL_ERROR)


def test_ct11_dados_validos_exibem_confirmacao(page: Page, base_url):
    open_home(page, base_url)
    fill_contact_form(page)
    submit(page)
    expect_success(page, VALID_NAME, VALID_SUBJECT)
    expect(page.get_by_test_id("ContactName")).to_have_count(0)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *__import__("sys").argv[1:]]))
