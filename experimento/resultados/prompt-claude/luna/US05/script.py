import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"
LOGIN_URL = f"{BASE_URL}admin"
ROOMS_URL = f"{BASE_URL}admin/rooms"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"
INVALID_PASSWORD = "incorrect"


def _login(page: Page) -> None:
    page.goto(LOGIN_URL)
    page.get_by_label("Username").fill(ADMIN_USERNAME)
    page.get_by_label("Password").fill(ADMIN_PASSWORD)
    page.get_by_role("button", name="Login").click()


def test_ct01_login_com_campos_vazios(page: Page) -> None:
    page.goto(LOGIN_URL)
    page.get_by_role("button", name="Login").click()

    expect(page.get_by_text("Invalid credentials", exact=True)).to_be_visible()
    expect(page).to_have_url(LOGIN_URL)


def test_ct02_login_com_senha_incorreta(page: Page) -> None:
    page.goto(LOGIN_URL)
    page.get_by_label("Username").fill(ADMIN_USERNAME)
    page.get_by_label("Password").fill(INVALID_PASSWORD)
    page.get_by_role("button", name="Login").click()

    expect(page.get_by_text("Invalid credentials", exact=True)).to_be_visible()
    expect(page).to_have_url(LOGIN_URL)


def test_ct03_login_com_credenciais_validas(page: Page) -> None:
    _login(page)

    expect(page).to_have_url(ROOMS_URL)
    expect(page.get_by_text("101", exact=True)).to_be_visible()
    expect(page.get_by_text("Single", exact=True)).to_be_visible()

    for menu_item in ("Rooms", "Report", "Branding", "Messages"):
        expect(page.get_by_text(menu_item, exact=True)).to_be_visible()


def test_ct04_logout_retorna_a_pagina_publica(page: Page) -> None:
    _login(page)
    page.get_by_role("link", name="Logout").click()

    expect(page).to_have_url(BASE_URL)


def test_ct05_acesso_direto_apos_logout_exige_login(page: Page) -> None:
    _login(page)
    page.get_by_role("link", name="Logout").click()
    expect(page).to_have_url(BASE_URL)

    page.goto(ROOMS_URL)

    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()
    expect(page.get_by_role("button", name="Login")).to_be_visible()
