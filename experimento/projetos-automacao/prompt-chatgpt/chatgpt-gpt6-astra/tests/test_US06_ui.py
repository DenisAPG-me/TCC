import re
from contextlib import contextmanager
from uuid import uuid4

import pytest
from playwright.sync_api import expect, sync_playwright


BASE_URL = "https://automationintesting.online/"

# Valores explícitos na User Story.
ADMIN_PATH = "/admin"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"
CONFIRMATION_TEMPLATE = "Thanks for getting in touch {name}!"

# Valores inferidos: ajustar se a interface real apresentar outro contrato.
MESSAGES_PATH = "/admin/#/messages"
UI_TIMEOUT_MS = 15_000

UI = {
    "username_label": "Username",
    "password_label": "Password",
    "login_button": "Login",
    "logout_button": "Logout",
    "messages_link_pattern": r"^Messages\b",
    "counter_test_id": "message-count",
    "name_label": "Name",
    "email_label": "Email",
    "phone_label": "Phone",
    "subject_label": "Subject",
    "message_label": "Message",
    "submit_button": "Submit",
}

CONTACT_DEFAULTS = {
    "name_prefix": "Visitante Teste",
    "subject_prefix": "Consulta sobre hospedagem",
    "email": "visitante.teste@example.com",
    "phone": "11987654321",
    "message": (
        "Olá, gostaria de receber informações sobre a hospedagem "
        "e os serviços disponíveis na pousada."
    ),
}

COUNTER_PATTERN = re.compile(r"^\s*[0-9]+\s*$")


def absolute_url(path):
    return f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}"


@pytest.fixture(scope="session")
def chromium_browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            yield browser
        finally:
            browser.close()


@contextmanager
def isolated_page(browser):
    context = browser.new_context()
    try:
        context.set_default_timeout(UI_TIMEOUT_MS)
        context.set_default_navigation_timeout(UI_TIMEOUT_MS)
        page = context.new_page()
        yield page
    finally:
        context.close()


@pytest.fixture
def admin_page(chromium_browser):
    with isolated_page(chromium_browser) as page:
        yield page


@pytest.fixture
def visitor_page(chromium_browser):
    with isolated_page(chromium_browser) as page:
        yield page


def messages_link(page):
    return page.get_by_role(
        "link",
        name=re.compile(UI["messages_link_pattern"]),
    )


def message_counter(page):
    return messages_link(page).get_by_test_id(UI["counter_test_id"])


def assert_login_requested(page):
    expect(
        page.get_by_label(UI["username_label"], exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(
        page.get_by_label(UI["password_label"], exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(
        page.get_by_role("button", name=UI["login_button"], exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)


def login(page):
    page.goto(absolute_url(ADMIN_PATH))
    assert_login_requested(page)
    page.get_by_label(UI["username_label"], exact=True).fill(
        ADMIN_USERNAME
    )
    page.get_by_label(UI["password_label"], exact=True).fill(
        ADMIN_PASSWORD
    )
    page.get_by_role(
        "button", name=UI["login_button"], exact=True
    ).click()
    expect(messages_link(page)).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(
        page.get_by_role("button", name=UI["logout_button"], exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)


def logout(page):
    page.get_by_role(
        "button", name=UI["logout_button"], exact=True
    ).click()
    assert_login_requested(page)


def read_counter(page):
    counter = message_counter(page)
    expect(counter).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(counter).to_have_text(
        COUNTER_PATTERN, timeout=UI_TIMEOUT_MS
    )
    return int(counter.inner_text().strip())


def new_contact():
    unique_id = uuid4().hex[:12]
    return {
        "name": f"{CONTACT_DEFAULTS['name_prefix']} {unique_id}",
        "subject": f"{CONTACT_DEFAULTS['subject_prefix']} {unique_id}",
        "email": CONTACT_DEFAULTS["email"],
        "phone": CONTACT_DEFAULTS["phone"],
        "message": CONTACT_DEFAULTS["message"],
    }


def submit_contact(page, contact):
    page.goto(BASE_URL)
    for field in ("name", "email", "phone", "subject", "message"):
        page.get_by_label(
            UI[f"{field}_label"], exact=True
        ).fill(contact[field])

    page.get_by_role(
        "button", name=UI["submit_button"], exact=True
    ).click()


def assert_contact_confirmation(page, contact):
    confirmation = CONFIRMATION_TEMPLATE.format(name=contact["name"])
    expect(
        page.get_by_text(confirmation, exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)


def open_messages(page):
    messages_link(page).click()
    expect(page).to_have_url(
        absolute_url(MESSAGES_PATH), timeout=UI_TIMEOUT_MS
    )


def test_CT001_registrar_contador_de_mensagens(admin_page):
    login(admin_page)

    recorded_count = read_counter(admin_page)

    assert recorded_count >= 0, (
        f"O contador deve ser não negativo; recebido: {recorded_count}"
    )


def test_CT002_confirmar_envio_do_visitante(visitor_page):
    contact = new_contact()

    submit_contact(visitor_page, contact)

    assert_contact_confirmation(visitor_page, contact)


def test_CT003_incrementar_contador_apos_envio(
    admin_page, visitor_page
):
    login(admin_page)
    recorded_count = read_counter(admin_page)
    logout(admin_page)

    contact = new_contact()
    submit_contact(visitor_page, contact)
    assert_contact_confirmation(visitor_page, contact)

    login(admin_page)
    expected_count = recorded_count + 1

    expect(message_counter(admin_page)).to_have_text(
        re.compile(rf"^\s*{expected_count}\s*$"),
        timeout=UI_TIMEOUT_MS,
    )
    assert read_counter(admin_page) == expected_count


def test_CT004_localizar_mensagem_na_caixa(admin_page, visitor_page):
    contact = new_contact()
    submit_contact(visitor_page, contact)
    assert_contact_confirmation(visitor_page, contact)

    login(admin_page)
    open_messages(admin_page)

    matching_row = admin_page.get_by_role("row").filter(
        has=admin_page.get_by_role(
            "cell", name=contact["name"], exact=True
        )
    ).filter(
        has=admin_page.get_by_role(
            "cell", name=contact["subject"], exact=True
        )
    )

    expect(matching_row).to_have_count(1, timeout=UI_TIMEOUT_MS)
    expect(
        matching_row.get_by_role(
            "cell", name=contact["name"], exact=True
        )
    ).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(
        matching_row.get_by_role(
            "cell", name=contact["subject"], exact=True
        )
    ).to_be_visible(timeout=UI_TIMEOUT_MS)


def test_CT005_exigir_login_apos_logout(admin_page):
    login(admin_page)
    open_messages(admin_page)
    logout(admin_page)

    # Preserva o contexto para verificar o efeito do logout na sessão.
    admin_page.goto(absolute_url(MESSAGES_PATH))

    assert_login_requested(admin_page)
