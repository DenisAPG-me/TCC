import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online"

ADMIN_USER = "admin"
ADMIN_PASSWORD = "password"
INVALID_CREDENTIALS_MSG = "Invalid credentials"


@pytest.fixture
def app_url(base_url):
    return (base_url or BASE_URL).rstrip("/")


def open_login(page: Page, app_url: str) -> None:
    page.goto(f"{app_url}/admin")
    expect(page.get_by_role("button", name="Login")).to_be_visible()


def submit_login(page: Page, username: str, password: str) -> None:
    page.get_by_label("Username").fill(username)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Login").click()


def login_as_admin(page: Page, app_url: str) -> None:
    open_login(page, app_url)
    submit_login(page, ADMIN_USER, ADMIN_PASSWORD)
    expect(page).to_have_url(re.compile(r"/admin/rooms/?$"))


def logout(page: Page) -> None:
    page.get_by_role("navigation").get_by_text("Logout", exact=True).click()


def expect_login_screen(page: Page) -> None:
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_label("Password", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Login")).to_be_visible()


def test_ct01_login_com_usuario_e_senha_vazios(page: Page, app_url: str):
    open_login(page, app_url)
    submit_login(page, "", "")

    expect(page.get_by_text(INVALID_CREDENTIALS_MSG)).to_be_visible()
    expect(page).to_have_url(re.compile(r"/admin/?$"))
    expect_login_screen(page)


def test_ct02_login_com_senha_incorreta(page: Page, app_url: str):
    open_login(page, app_url)
    submit_login(page, ADMIN_USER, "senhaErrada123")

    expect(page.get_by_text(INVALID_CREDENTIALS_MSG)).to_be_visible()
    expect_login_screen(page)


def test_ct03_login_com_senha_em_caixa_diferente(page: Page, app_url: str):
    open_login(page, app_url)
    submit_login(page, ADMIN_USER, "Password")

    expect(page.get_by_text(INVALID_CREDENTIALS_MSG)).to_be_visible()
    expect_login_screen(page)


def test_ct04_login_com_usuario_admin_e_senha_vazia(page: Page, app_url: str):
    open_login(page, app_url)
    submit_login(page, ADMIN_USER, "")

    expect(page.get_by_text(INVALID_CREDENTIALS_MSG)).to_be_visible()
    expect(page).to_have_url(re.compile(r"/admin/?$"))
    expect_login_screen(page)


def test_ct05_login_valido_exibe_quarto_101_single(page: Page, app_url: str):
    login_as_admin(page, app_url)

    room_101 = page.get_by_test_id("roomlisting").filter(has_text="101")
    expect(room_101).to_have_count(1)
    expect(room_101).to_contain_text(re.compile(r"single", re.IGNORECASE))


def test_ct06_login_valido_exibe_menu_do_painel(page: Page, app_url: str):
    login_as_admin(page, app_url)

    nav = page.get_by_role("navigation")
    for item in ("Rooms", "Report", "Branding", "Messages"):
        expect(nav.get_by_role("link", name=item, exact=True)).to_be_visible()


def test_ct07_logout_retorna_a_pagina_inicial(page: Page, app_url: str):
    login_as_admin(page, app_url)
    logout(page)

    expect(page).to_have_url(re.compile(rf"^{re.escape(app_url)}/?$"))
    expect(page.get_by_role("button", name="Login")).to_have_count(0)


def test_ct08_acesso_direto_a_quartos_apos_logout_exige_login(page: Page, app_url: str):
    login_as_admin(page, app_url)
    logout(page)
    expect(page).to_have_url(re.compile(rf"^{re.escape(app_url)}/?$"))

    page.goto(f"{app_url}/admin/rooms")

    expect_login_screen(page)
    expect(page.get_by_test_id("roomlisting")).to_have_count(0)


def test_ct09_acesso_direto_a_quartos_sem_autenticacao_exige_login(page: Page, app_url: str):
    page.goto(f"{app_url}/admin/rooms")

    expect_login_screen(page)
    expect(page.get_by_test_id("roomlisting")).to_have_count(0)
