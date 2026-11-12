import uuid

import pytest
from playwright.sync_api import expect


BASE_URL = "https://automationintesting.online/"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

TEST_ID = uuid.uuid4().hex[:8]
VISITOR_NAME = f"Visitante {TEST_ID}"
VISITOR_EMAIL = f"visitante-{TEST_ID}@example.com"
VISITOR_PHONE = "11999999999"
VISITOR_SUBJECT = f"Assunto {TEST_ID}"
VISITOR_MESSAGE = f"Mensagem de teste {TEST_ID}"

ADMIN_URL = f"{BASE_URL}admin"
MESSAGES_URL = f"{ADMIN_URL}/messages"


def login(page):
    page.goto(ADMIN_URL)
    page.get_by_label("Username").fill(ADMIN_USERNAME)
    page.get_by_label("Password").fill(ADMIN_PASSWORD)
    page.get_by_role("button", name="Login").click()


def fill_contact_form(page, name=VISITOR_NAME, subject=VISITOR_SUBJECT):
    page.goto(BASE_URL)
    page.get_by_label("Name").fill(name)
    page.get_by_label("Email").fill(VISITOR_EMAIL)
    page.get_by_label("Phone").fill(VISITOR_PHONE)
    page.get_by_label("Subject").fill(subject)
    page.get_by_label("Message").fill(VISITOR_MESSAGE)


def submit_contact_form(page):
    page.get_by_role("button", name="Submit").click()


def read_messages_count(page):
    messages_link = page.get_by_role("link", name="Messages")
    expect(messages_link).to_be_visible()
    label = messages_link.inner_text()
    digits = "".join(character for character in label if character.isdigit())
    assert digits, f"Não foi possível encontrar o contador no texto: {label!r}"
    return int(digits)


def test_ct01_enviar_mensagem_valida_como_visitante(page):
    fill_contact_form(page)
    submit_contact_form(page)

    expect(
        page.get_by_text(f"Thanks for getting in touch {VISITOR_NAME}!", exact=True)
    ).to_be_visible()


def test_ct02_conferir_incremento_e_mensagem_recebida(page):
    login(page)
    count_before = read_messages_count(page)

    fill_contact_form(page)
    submit_contact_form(page)
    expect(
        page.get_by_text(f"Thanks for getting in touch {VISITOR_NAME}!", exact=True)
    ).to_be_visible()

    login(page)
    count_after = read_messages_count(page)
    assert count_after == count_before + 1

    page.get_by_role("link", name="Messages").click()
    expect(page.get_by_text(VISITOR_NAME, exact=True)).to_be_visible()
    expect(page.get_by_text(VISITOR_SUBJECT, exact=True)).to_be_visible()


def test_ct03_bloquear_envio_sem_nome(page):
    fill_contact_form(page, name="")
    submit_contact_form(page)

    expect(
        page.get_by_text(f"Thanks for getting in touch {VISITOR_NAME}!", exact=True)
    ).to_have_count(0)


def test_ct04_bloquear_envio_sem_assunto(page):
    fill_contact_form(page, subject="")
    submit_contact_form(page)

    expect(
        page.get_by_text(f"Thanks for getting in touch {VISITOR_NAME}!", exact=True)
    ).to_have_count(0)


def test_ct05_solicitar_login_apos_logout(page):
    login(page)
    page.get_by_role("link", name="Logout").click()
    page.goto(MESSAGES_URL)

    expect(page).to_have_url(f"{ADMIN_URL}/")
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()
