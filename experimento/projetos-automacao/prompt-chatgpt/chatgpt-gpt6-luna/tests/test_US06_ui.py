import re
import uuid

import pytest
from playwright.sync_api import expect


# Valores inferidos e centralizados para facilitar ajustes antes do uso real.
BASE_URL = "https://automationintesting.online/"
ADMIN_PATH = "/admin"
MESSAGES_PATH = "/admin/messages"
LOGOUT_PATH = "/admin/logout"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"
REQUEST_TIMEOUT_MS = 10_000


def unique_value(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def fill_contact_form(page, name, subject):
    page.goto(BASE_URL)
    page.get_by_label(re.compile(r"name", re.IGNORECASE)).fill(name)
    page.get_by_label(re.compile(r"email", re.IGNORECASE)).fill(
        f"{unique_value('visitor')}@example.com"
    )
    page.get_by_label(re.compile(r"phone", re.IGNORECASE)).fill("+1 202 555 0147")
    page.get_by_label(re.compile(r"subject", re.IGNORECASE)).fill(subject)
    page.get_by_label(re.compile(r"message", re.IGNORECASE)).fill(
        f"Message for {subject}"
    )


def submit_contact_form(page, name, subject):
    fill_contact_form(page, name, subject)
    page.get_by_role("button", name=re.compile(r"submit|send", re.IGNORECASE)).click()


def login_as_admin(page):
    page.goto(f"{BASE_URL.rstrip('/')}{ADMIN_PATH}")
    page.get_by_label(re.compile(r"username", re.IGNORECASE)).fill(ADMIN_USERNAME)
    page.get_by_label(re.compile(r"password", re.IGNORECASE)).fill(ADMIN_PASSWORD)
    page.get_by_role("button", name=re.compile(r"login|log in", re.IGNORECASE)).click()
    expect(page.get_by_role("link", name=re.compile(r"messages", re.IGNORECASE))).to_be_visible()


def read_messages_count(page):
    messages_item = page.get_by_role(
        "link", name=re.compile(r"messages", re.IGNORECASE)
    )
    expect(messages_item).to_be_visible()
    match = re.search(r"\d+", messages_item.inner_text())
    assert match is not None, "Não foi encontrado número no item Messages"
    return int(match.group(0))


def open_messages(page):
    page.goto(f"{BASE_URL.rstrip('/')}{MESSAGES_PATH}")
    expect(page.get_by_text(re.compile(r"messages", re.IGNORECASE)).first).to_be_visible()


def test_CT001_enviar_mensagem_valida_exibe_confirmacao(page):
    name = unique_value("Visitor")
    subject = unique_value("Subject")

    submit_contact_form(page, name, subject)

    expect(page.get_by_text(f"Thanks for getting in touch {name}!", exact=True)).to_be_visible(
        timeout=REQUEST_TIMEOUT_MS
    )


def test_CT002_contador_aumenta_apos_envio_de_mensagem(page):
    login_as_admin(page)
    count_before = read_messages_count(page)

    page.goto(BASE_URL)
    name = unique_value("Visitor")
    subject = unique_value("Subject")
    submit_contact_form(page, name, subject)
    expect(page.get_by_text(f"Thanks for getting in touch {name}!", exact=True)).to_be_visible(
        timeout=REQUEST_TIMEOUT_MS
    )

    login_as_admin(page)
    count_after = read_messages_count(page)
    assert count_after == count_before + 1


def test_CT003_mensagem_enviada_aparece_na_caixa_de_mensagens(page):
    name = unique_value("Visitor")
    subject = unique_value("Subject")
    submit_contact_form(page, name, subject)
    expect(page.get_by_text(f"Thanks for getting in touch {name}!", exact=True)).to_be_visible(
        timeout=REQUEST_TIMEOUT_MS
    )

    login_as_admin(page)
    open_messages(page)

    expect(page.get_by_text(name, exact=True)).to_be_visible(timeout=REQUEST_TIMEOUT_MS)
    expect(page.get_by_text(subject, exact=True)).to_be_visible(timeout=REQUEST_TIMEOUT_MS)


def test_CT004_caixa_de_mensagens_solicita_login_apos_logout(page):
    login_as_admin(page)

    page.goto(f"{BASE_URL.rstrip('/')}{LOGOUT_PATH}")
    page.goto(f"{BASE_URL.rstrip('/')}{MESSAGES_PATH}")

    expect(page.get_by_label(re.compile(r"username", re.IGNORECASE))).to_be_visible(
        timeout=REQUEST_TIMEOUT_MS
    )
    expect(page.get_by_label(re.compile(r"password", re.IGNORECASE))).to_be_visible(
        timeout=REQUEST_TIMEOUT_MS
    )
