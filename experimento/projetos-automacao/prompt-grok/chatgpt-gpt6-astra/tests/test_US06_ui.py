import re
from uuid import uuid4

import pytest
from playwright.sync_api import Page, expect


BASE_URL = "https://automationintesting.online"
ADMIN_PATH = "/admin"
MESSAGES_PATH = "/admin/messages"
UI_TIMEOUT_MS = 15_000

pytestmark = pytest.mark.browser_context_args(
    storage_state={"cookies": [], "origins": []}
)


def open_path(page: Page, path: str) -> None:
    page.goto(f"{BASE_URL.rstrip('/')}{path}")


def messages_link(page: Page):
    return page.get_by_role(
        "link", name=re.compile(r"^Messages\b")
    )


def message_counter(page: Page):
    return messages_link(page).get_by_test_id("message-count")


def expect_login_form(page: Page) -> None:
    expect(page.get_by_label("Username", exact=True)).to_be_visible(
        timeout=UI_TIMEOUT_MS
    )
    expect(page.get_by_label("Password", exact=True)).to_be_visible(
        timeout=UI_TIMEOUT_MS
    )
    expect(page.get_by_role("button", name="Login", exact=True)).to_be_visible(
        timeout=UI_TIMEOUT_MS
    )


def login(page: Page) -> None:
    open_path(page, ADMIN_PATH)
    expect_login_form(page)
    page.get_by_label("Username", exact=True).fill("admin")
    page.get_by_label("Password", exact=True).fill("password")
    page.get_by_role("button", name="Login", exact=True).click()
    expect(messages_link(page)).to_be_visible(timeout=UI_TIMEOUT_MS)


def logout(page: Page) -> None:
    page.get_by_role("button", name="Logout", exact=True).click()
    expect_login_form(page)


def read_counter(page: Page) -> int:
    counter = message_counter(page)
    expect(counter).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(counter).to_have_text(
        re.compile(r"^\s*[0-9]+\s*$"),
        timeout=UI_TIMEOUT_MS,
    )
    return int(counter.inner_text().strip())


def make_contact(case_id: str, accented: bool = False) -> dict:
    token = uuid4().hex[:12]
    name = (
        f"João da Conceição {token}"
        if accented
        else f"Visitante Teste {token}"
    )
    return {
        "name": name,
        "email": f"visitante.{token}@example.com",
        "phone": "11987654321",
        "subject": f"Consulta {case_id} {token}",
        "message": (
            "Olá, gostaria de receber informações sobre a disponibilidade "
            f"de quartos para duas pessoas. Referência {token}."
        ),
    }


def submit_contact(page: Page, contact: dict) -> None:
    open_path(page, "/")
    page.get_by_label("Name", exact=True).fill(contact["name"])
    page.get_by_label("Email", exact=True).fill(contact["email"])
    page.get_by_label("Phone", exact=True).fill(contact["phone"])
    page.get_by_label("Subject", exact=True).fill(contact["subject"])
    page.get_by_label("Message", exact=True).fill(contact["message"])
    page.get_by_role("button", name="Submit", exact=True).click()

    expect(
        page.get_by_text(
            f"Thanks for getting in touch {contact['name']}!",
            exact=True,
        )
    ).to_be_visible(timeout=UI_TIMEOUT_MS)


def open_messages(page: Page) -> None:
    messages_link(page).click()
    expect(page).to_have_url(
        re.compile(
            rf"^{re.escape(BASE_URL.rstrip('/') + MESSAGES_PATH)}/?"
            rf"(?:[?#].*)?$"
        ),
        timeout=UI_TIMEOUT_MS,
    )


def expect_contact_in_list(page: Page, contact: dict) -> None:
    row = page.get_by_role("row").filter(
        has=page.get_by_text(contact["subject"], exact=True)
    )
    expect(row).to_have_count(1, timeout=UI_TIMEOUT_MS)
    expect(row).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(
        row.get_by_text(contact["name"], exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(
        row.get_by_text(contact["subject"], exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)


def test_TC01_registrar_contador_inicial(page: Page) -> None:
    login(page)
    initial_count = read_counter(page)

    # Confirma que o valor registrado corresponde ao exibido.
    expect(message_counter(page)).to_have_text(
        re.compile(rf"^\s*{initial_count}\s*$"),
        timeout=UI_TIMEOUT_MS,
    )


def test_TC02_confirmar_envio_valido(page: Page) -> None:
    contact = make_contact("TC02")
    submit_contact(page, contact)


def test_TC03_incrementar_contador_apos_envio(page: Page) -> None:
    login(page)
    initial_count = read_counter(page)
    logout(page)

    contact = make_contact("TC03")
    submit_contact(page, contact)

    login(page)
    expect(message_counter(page)).to_have_text(
        re.compile(rf"^\s*{initial_count + 1}\s*$"),
        timeout=UI_TIMEOUT_MS,
    )


def test_TC04_exibir_remetente_e_assunto(page: Page) -> None:
    contact = make_contact("TC04")
    submit_contact(page, contact)

    login(page)
    open_messages(page)
    expect_contact_in_list(page, contact)


def test_TC05_bloquear_acesso_direto_apos_logout(page: Page) -> None:
    login(page)
    open_messages(page)
    logout(page)

    open_path(page, MESSAGES_PATH)
    expect_login_form(page)


def test_TC06_bloquear_acesso_sem_autenticacao(page: Page) -> None:
    open_path(page, MESSAGES_PATH)
    expect_login_form(page)


def test_TC07_preservar_nome_com_acentos_e_espacos(page: Page) -> None:
    contact = make_contact("TC07", accented=True)
    submit_contact(page, contact)

    login(page)
    open_messages(page)
    expect_contact_in_list(page, contact)
