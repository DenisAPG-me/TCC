import re
from urllib.parse import urljoin

import pytest
from playwright.sync_api import expect, sync_playwright


BASE_URL = "https://automationintesting.online/"

# Valores explícitos na User Story.
USERNAME = "admin"
PASSWORD = "password"
ERROR_MESSAGE = "Invalid credentials"
ROOM_NUMBER = "101"
ROOM_TYPE = "Single"
MENU_ITEMS = ("Rooms", "Report", "Branding", "Messages")

# Suposições de implementação centralizadas para eventual ajuste.
LOGIN_PATH = "/admin"
ROOMS_PATH = "/admin/rooms"
PUBLIC_HOME_PATH = "/"
USERNAME_LABEL = "Username"
PASSWORD_LABEL = "Password"
LOGIN_BUTTON_NAME = "Login"
LOGOUT_BUTTON_NAME = "Logout"
INVALID_PASSWORD = "senha-incorreta-ct002"
NAVIGATION_ROLE = "navigation"
PUBLIC_CONTENT_ROLE = "main"
ROOM_ROW_ROLE = "row"
ROOM_CELL_ROLE = "cell"
ACTION_TIMEOUT_MS = 10_000
NAVIGATION_TIMEOUT_MS = 30_000
ASSERTION_TIMEOUT_MS = 10_000


def absolute_url(path):
    return urljoin(BASE_URL, path)


def expected_url(path):
    """Aceita somente a URL esperada, com barra final opcional."""
    normalized = absolute_url(path).rstrip("/")
    return re.compile(r"^" + re.escape(normalized) + r"/?$")


@pytest.fixture(scope="session")
def chromium_browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture
def ui_page(chromium_browser):
    context = chromium_browser.new_context()
    try:
        page = context.new_page()
        page.set_default_timeout(ACTION_TIMEOUT_MS)
        page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
        yield page
    finally:
        context.close()


def assert_login_screen(page):
    expect(page).to_have_url(
        expected_url(LOGIN_PATH), timeout=ASSERTION_TIMEOUT_MS
    )
    expect(
        page.get_by_label(USERNAME_LABEL, exact=True)
    ).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)
    expect(
        page.get_by_label(PASSWORD_LABEL, exact=True)
    ).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)
    expect(
        page.get_by_role("button", name=LOGIN_BUTTON_NAME, exact=True)
    ).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)


def open_login(page):
    page.goto(absolute_url(LOGIN_PATH), wait_until="domcontentloaded")
    assert_login_screen(page)


def submit_credentials(page, username, password):
    page.get_by_label(USERNAME_LABEL, exact=True).fill(username)
    page.get_by_label(PASSWORD_LABEL, exact=True).fill(password)
    page.get_by_role(
        "button", name=LOGIN_BUTTON_NAME, exact=True
    ).click()


def assert_invalid_credentials(page):
    expect(
        page.get_by_text(ERROR_MESSAGE, exact=True)
    ).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)


def authenticate(page):
    open_login(page)
    submit_credentials(page, USERNAME, PASSWORD)
    expect(page).to_have_url(
        expected_url(ROOMS_PATH), timeout=ASSERTION_TIMEOUT_MS
    )
    expect(
        page.get_by_role("button", name=LOGOUT_BUTTON_NAME, exact=True)
    ).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)


def assert_public_home(page):
    expect(page).to_have_url(
        expected_url(PUBLIC_HOME_PATH), timeout=ASSERTION_TIMEOUT_MS
    )
    expect(
        page.get_by_role(PUBLIC_CONTENT_ROLE)
    ).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)


def logout(page):
    page.get_by_role(
        "button", name=LOGOUT_BUTTON_NAME, exact=True
    ).click()


def test_CT001_enviar_credenciais_vazias(ui_page):
    open_login(ui_page)

    submit_credentials(ui_page, "", "")

    assert_invalid_credentials(ui_page)
    assert_login_screen(ui_page)


def test_CT002_rejeitar_senha_incorreta(ui_page):
    open_login(ui_page)

    submit_credentials(ui_page, USERNAME, INVALID_PASSWORD)

    assert_invalid_credentials(ui_page)


def test_CT003_acessar_quartos_com_credenciais_validas(ui_page):
    open_login(ui_page)

    submit_credentials(ui_page, USERNAME, PASSWORD)

    expect(ui_page).to_have_url(
        expected_url(ROOMS_PATH), timeout=ASSERTION_TIMEOUT_MS
    )

    room_row = ui_page.get_by_role(ROOM_ROW_ROLE).filter(
        has=ui_page.get_by_role(
            ROOM_CELL_ROLE, name=ROOM_NUMBER, exact=True
        )
    )
    expect(room_row).to_have_count(1, timeout=ASSERTION_TIMEOUT_MS)
    expect(room_row).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)
    expect(
        room_row.get_by_role(
            ROOM_CELL_ROLE, name=ROOM_NUMBER, exact=True
        )
    ).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)
    expect(
        room_row.get_by_role(
            ROOM_CELL_ROLE, name=ROOM_TYPE, exact=True
        )
    ).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)

    navigation = ui_page.get_by_role(NAVIGATION_ROLE)
    for item in MENU_ITEMS:
        expect(
            navigation.get_by_role("link", name=item, exact=True)
        ).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)


def test_CT004_sair_do_painel(ui_page):
    authenticate(ui_page)

    logout(ui_page)

    assert_public_home(ui_page)


def test_CT005_impedir_acesso_direto_apos_logout(ui_page):
    authenticate(ui_page)
    logout(ui_page)
    assert_public_home(ui_page)

    ui_page.goto(
        absolute_url(ROOMS_PATH), wait_until="domcontentloaded"
    )

    assert_login_screen(ui_page)
