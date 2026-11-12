import re

from playwright.sync_api import Page, expect


BASE_URL = "https://automationintesting.online"
LOGIN_URL = f"{BASE_URL}/admin"
ROOMS_URL = f"{BASE_URL}/admin/rooms"
HOME_URL = f"{BASE_URL}/"

VALID_USERNAME = "admin"
VALID_PASSWORD = "password"
INVALID_PASSWORD = "wrong-password"

UI_TIMEOUT_MS = 10_000
NAVIGATION_TIMEOUT_MS = 30_000


def url_pattern(url: str) -> re.Pattern:
    """Aceita somente a URL esperada, com barra final opcional."""
    return re.compile(rf"^{re.escape(url.rstrip('/'))}/?$")


def assert_login_visible(page: Page) -> None:
    expect(page.get_by_label("Username", exact=True)).to_be_visible(
        timeout=UI_TIMEOUT_MS
    )
    expect(page.get_by_label("Password", exact=True)).to_be_visible(
        timeout=UI_TIMEOUT_MS
    )
    expect(page.get_by_role("button", name="Login", exact=True)).to_be_visible(
        timeout=UI_TIMEOUT_MS
    )


def open_login(page: Page) -> None:
    page.goto(LOGIN_URL, timeout=NAVIGATION_TIMEOUT_MS)
    expect(page).to_have_url(url_pattern(LOGIN_URL), timeout=UI_TIMEOUT_MS)
    assert_login_visible(page)


def submit_credentials(page: Page, username: str, password: str) -> None:
    page.get_by_label("Username", exact=True).fill(
        username, timeout=UI_TIMEOUT_MS
    )
    page.get_by_label("Password", exact=True).fill(
        password, timeout=UI_TIMEOUT_MS
    )
    page.get_by_role("button", name="Login", exact=True).click(
        timeout=UI_TIMEOUT_MS
    )


def assert_invalid_credentials(page: Page) -> None:
    expect(
        page.get_by_text("Invalid credentials", exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)


def assert_still_on_login(page: Page) -> None:
    expect(page).to_have_url(url_pattern(LOGIN_URL), timeout=UI_TIMEOUT_MS)
    assert_login_visible(page)


def login_successfully(page: Page) -> None:
    open_login(page)
    submit_credentials(page, VALID_USERNAME, VALID_PASSWORD)
    expect(page).to_have_url(url_pattern(ROOMS_URL), timeout=UI_TIMEOUT_MS)
    expect(page.get_by_role("link", name="Logout", exact=True)).to_be_visible(
        timeout=UI_TIMEOUT_MS
    )


def logout_and_assert_public_home(page: Page) -> None:
    page.get_by_role("link", name="Logout", exact=True).click(
        timeout=UI_TIMEOUT_MS
    )
    expect(page).to_have_url(url_pattern(HOME_URL), timeout=UI_TIMEOUT_MS)
    expect(page.get_by_role("link", name="Logout", exact=True)).to_have_count(
        0, timeout=UI_TIMEOUT_MS
    )


def test_TC01_login_com_ambos_os_campos_vazios(page: Page) -> None:
    open_login(page)
    submit_credentials(page, "", "")
    assert_invalid_credentials(page)
    assert_still_on_login(page)


def test_TC02_login_com_senha_incorreta(page: Page) -> None:
    open_login(page)
    submit_credentials(page, VALID_USERNAME, INVALID_PASSWORD)
    assert_invalid_credentials(page)


def test_TC03_login_valido_exibe_quarto_e_menu(page: Page) -> None:
    login_successfully(page)

    room_row = page.get_by_role("row").filter(
        has=page.get_by_role("cell", name="101", exact=True)
    )
    expect(room_row).to_have_count(1, timeout=UI_TIMEOUT_MS)
    expect(room_row).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(
        room_row.get_by_role("cell", name="101", exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(
        room_row.get_by_role("cell", name="Single", exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)

    for menu_name in ("Rooms", "Report", "Branding", "Messages"):
        expect(
            page.get_by_role("link", name=menu_name, exact=True)
        ).to_be_visible(timeout=UI_TIMEOUT_MS)


def test_TC04_logout_retorna_a_pagina_publica(page: Page) -> None:
    login_successfully(page)
    logout_and_assert_public_home(page)


def test_TC05_acesso_direto_apos_logout_exibe_login(page: Page) -> None:
    login_successfully(page)
    logout_and_assert_public_home(page)

    page.goto(ROOMS_URL, timeout=NAVIGATION_TIMEOUT_MS)

    # O critério exige a tela de login, sem definir sua URL após o acesso.
    assert_login_visible(page)
    expect(page.get_by_role("link", name="Logout", exact=True)).to_have_count(
        0, timeout=UI_TIMEOUT_MS
    )


def test_TC06_login_com_usuario_vazio(page: Page) -> None:
    # Extensão proposta: comportamento não explicitado na User Story.
    open_login(page)
    submit_credentials(page, "", VALID_PASSWORD)
    assert_invalid_credentials(page)
    assert_still_on_login(page)


def test_TC07_login_com_senha_vazia(page: Page) -> None:
    # Extensão proposta: comportamento não explicitado na User Story.
    open_login(page)
    submit_credentials(page, VALID_USERNAME, "")
    assert_invalid_credentials(page)
    assert_still_on_login(page)
