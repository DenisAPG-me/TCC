BASE_URL = "https://automationintesting.online/"

import re
from pathlib import Path
from urllib.parse import urljoin

import pytest
from playwright.sync_api import Page, expect


LOGIN_URL = urljoin(BASE_URL, "admin")
ROOMS_URL = urljoin(BASE_URL, "admin/rooms")
PUBLIC_HOME_URL = BASE_URL

VALID_USERNAME = "admin"
VALID_PASSWORD = "password"
INVALID_PASSWORD = "senha-incorreta"


def url_pattern(url: str) -> re.Pattern:
    """Aceita somente a URL esperada, com barra final opcional."""
    return re.compile(r"^" + re.escape(url.rstrip("/")) + r"/?$")


def assert_login_screen(page: Page) -> None:
    expect(page).to_have_url(url_pattern(LOGIN_URL))
    expect(page.get_by_label("Username", exact=True)).to_be_visible()
    expect(page.get_by_label("Password", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Login", exact=True)).to_be_visible()


def open_login(page: Page) -> None:
    page.goto(LOGIN_URL)
    assert_login_screen(page)


def submit_credentials(page: Page, username: str, password: str) -> None:
    page.get_by_label("Username", exact=True).fill(username)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Login", exact=True).click()


def login_successfully(page: Page) -> None:
    open_login(page)
    submit_credentials(page, VALID_USERNAME, VALID_PASSWORD)
    expect(page).to_have_url(url_pattern(ROOMS_URL))
    expect(page.get_by_role("button", name="Logout", exact=True)).to_be_visible()


def logout(page: Page) -> None:
    page.get_by_role("button", name="Logout", exact=True).click()
    expect(page).to_have_url(url_pattern(PUBLIC_HOME_URL))
    expect(page.get_by_role("main")).to_be_visible()


def test_CT01_login_com_usuario_e_senha_vazios(page: Page) -> None:
    open_login(page)

    submit_credentials(page, "", "")

    expect(page.get_by_text("Invalid credentials", exact=True)).to_be_visible()
    assert_login_screen(page)


def test_CT02_login_com_senha_incorreta(page: Page) -> None:
    open_login(page)

    submit_credentials(page, VALID_USERNAME, INVALID_PASSWORD)

    expect(page.get_by_text("Invalid credentials", exact=True)).to_be_visible()


def test_CT03_login_valido_exibe_quartos_e_menu(page: Page) -> None:
    login_successfully(page)

    room_row = page.get_by_role("row").filter(
        has=page.get_by_role("cell", name="101", exact=True)
    )
    expect(room_row).to_have_count(1)
    expect(room_row).to_be_visible()
    expect(room_row.get_by_role("cell", name="101", exact=True)).to_be_visible()
    expect(room_row.get_by_role("cell", name="Single", exact=True)).to_be_visible()

    navigation = page.get_by_role("navigation")
    expect(navigation).to_be_visible()

    for menu_item in ("Rooms", "Report", "Branding", "Messages"):
        expect(
            navigation.get_by_role("link", name=menu_item, exact=True)
        ).to_be_visible()


def test_CT04_logout_retorna_a_pagina_publica(page: Page) -> None:
    login_successfully(page)

    logout(page)


def test_CT05_acesso_direto_a_quartos_apos_logout_exige_login(page: Page) -> None:
    login_successfully(page)
    logout(page)

    # Mantém o contexto existente para verificar a sessão após o logout.
    page.goto(ROOMS_URL)

    assert_login_screen(page)


if __name__ == "__main__":
    raise SystemExit(pytest.main([str(Path(__file__).resolve())]))
