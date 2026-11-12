import re

import pytest
from playwright.sync_api import expect


BASE_URL = "https://automationintesting.online/"

VALID_NAME = "Ana Silva"
VALID_EMAIL = "ana@example.com"
VALID_PHONE = "11987654321"
VALID_SUBJECT = "Dúvida"
VALID_MESSAGE = "Gostaria de saber mais sobre as acomodações."


def open_home(page):
    page.goto(BASE_URL)


def fill_contact_form(
    page,
    *,
    name=VALID_NAME,
    email=VALID_EMAIL,
    phone=VALID_PHONE,
    subject=VALID_SUBJECT,
    message=VALID_MESSAGE,
):
    page.get_by_label("Name").fill(name)
    page.get_by_label("Email").fill(email)
    page.get_by_label("Phone").fill(phone)
    page.get_by_label("Subject").fill(subject)
    page.get_by_label("Message").fill(message)


def submit_contact_form(page):
    page.get_by_role("button", name="Submit").click()


def expect_success(page, name, subject):
    expect(page.get_by_text(f"Thanks for getting in touch {name}!", exact=True)).to_be_visible()
    expect(page.get_by_text(subject, exact=True)).to_be_visible()


def test_CT01_envio_com_todos_os_campos_vazios(page):
    open_home(page)
    submit_contact_form(page)

    for field_name in ("Name", "Email", "Phone", "Subject", "Message"):
        matching_messages = page.get_by_text(
            re.compile(rf"(?=.*{re.escape(field_name)})(?=.*blank)", re.IGNORECASE)
        )
        expect(matching_messages.first).to_be_visible()


def test_CT02_telefone_abaixo_do_minimo(page):
    open_home(page)
    fill_contact_form(page, phone="1" * 10)
    submit_contact_form(page)

    expect(page.get_by_text(
        "Phone must be between 11 and 21 characters.",
        exact=True,
    )).to_be_visible()


def test_CT03_assunto_e_mensagem_abaixo_do_minimo(page):
    open_home(page)
    fill_contact_form(page, subject="Dúvi", message="A" * 19)
    submit_contact_form(page)

    expect(page.get_by_text(
        "Subject must be between 5 and 100 characters.",
        exact=True,
    )).to_be_visible()
    expect(page.get_by_text(
        "Message must be between 20 and 2000 characters.",
        exact=True,
    )).to_be_visible()


def test_CT04_email_malformado(page):
    open_home(page)
    fill_contact_form(page, email="bad")
    submit_contact_form(page)

    expect(page.get_by_text(
        re.compile(r"must be a well-formed email address", re.IGNORECASE)
    )).to_be_visible()


def test_CT05_envio_com_todos_os_dados_validos(page):
    open_home(page)
    fill_contact_form(page)
    submit_contact_form(page)

    expect_success(page, VALID_NAME, VALID_SUBJECT)


def test_CT06_telefone_no_limite_minimo(page):
    open_home(page)
    fill_contact_form(page, phone="1" * 11)
    submit_contact_form(page)

    expect_success(page, VALID_NAME, VALID_SUBJECT)


def test_CT07_telefone_no_limite_maximo(page):
    open_home(page)
    fill_contact_form(page, phone="1" * 21)
    submit_contact_form(page)

    expect_success(page, VALID_NAME, VALID_SUBJECT)


def test_CT08_telefone_acima_do_maximo(page):
    open_home(page)
    fill_contact_form(page, phone="1" * 22)
    submit_contact_form(page)

    expect(page.get_by_text(
        "Phone must be between 11 and 21 characters.",
        exact=True,
    )).to_be_visible()


def test_CT09_assunto_e_mensagem_nos_limites_minimos(page):
    subject = "A" * 5
    message = "A" * 20

    open_home(page)
    fill_contact_form(page, subject=subject, message=message)
    submit_contact_form(page)

    expect_success(page, VALID_NAME, subject)


def test_CT10_assunto_e_mensagem_nos_limites_maximos(page):
    subject = "A" * 100
    message = "A" * 2000

    open_home(page)
    fill_contact_form(page, subject=subject, message=message)
    submit_contact_form(page)

    expect_success(page, VALID_NAME, subject)


def test_CT11_assunto_e_mensagem_acima_dos_maximos(page):
    open_home(page)
    fill_contact_form(page, subject="A" * 101, message="A" * 2001)
    submit_contact_form(page)

    expect(page.get_by_text(
        "Subject must be between 5 and 100 characters.",
        exact=True,
    )).to_be_visible()
    expect(page.get_by_text(
        "Message must be between 20 and 2000 characters.",
        exact=True,
    )).to_be_visible()
