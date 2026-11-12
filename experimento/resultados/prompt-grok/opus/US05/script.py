import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"
ADMIN_PATH = "/admin"
ROOMS_PATH = "/admin/rooms"
VALID_USER = "admin"
VALID_PASSWORD = "password"
WRONG_PASSWORD = "wrongpass"
INVALID_CREDENTIALS_MSG = "Invalid credentials"
ADMIN_MENU_ITEMS = ["Rooms", "Report", "Branding", "Messages"]


@pytest.fixture
def app_url(base_url):
    return (base_url or BASE_URL).rstrip("/")


def username_field(page: Page):
    return page.get_by_label("Username").or_(page.locator("#username"))


def password_field(page: Page):
    return page.get_by_label("Password").or_(page.locator("#password"))


def login_button(page: Page):
    return page.get_by_role("button", name="Login", exact=True)


def logout_control(page: Page):
    return page.get_by_role("button", name="Logout").or_(
        page.get_by_role("link", name="Logout")
    )


def open_login(page: Page, app_url: str):
    page.goto(f"{app_url}{ADMIN_PATH}")
    expect(login_button(page)).to_be_visible()


def submit_login(page: Page, username: str, password: str):
    username_field(page).first.fill(username)
    password_field(page).first.fill(password)
    login_button(page).click()


def login_as_admin(page: Page, app_url: str):
    open_login(page, app_url)
    submit_login(page, VALID_USER, VALID_PASSWORD)
    expect(page).to_have_url(re.compile(re.escape(ROOMS_PATH)))


def expect_login_screen(page: Page):
    expect(username_field(page).first).to_be_visible()
    expect(password_field(page).first).to_be_visible()
    expect(login_button(page)).to_be_visible()


def expect_invalid_credentials(page: Page):
    expect(page.get_by_text(INVALID_CREDENTIALS_MSG)).to_be_visible()
    expect_login_screen(page)
    expect(page.get_by_role("link", name="Messages", exact=True)).to_have_count(0)


def test_TC01_login_com_usuario_e_senha_vazios(page: Page, app_url):
    open_login(page, app_url)
    submit_login(page, "", "")
    expect_invalid_credentials(page)


def test_TC02_login_admin_com_senha_incorreta(page: Page, app_url):
    open_login(page, app_url)
    submit_login(page, VALID_USER, WRONG_PASSWORD)
    expect_invalid_credentials(page)


def test_TC03_login_valido_exibe_lista_de_quartos_e_menu(page: Page, app_url):
    open_login(page, app_url)
    submit_login(page, VALID_USER, VALID_PASSWORD)
    expect(page).to_have_url(re.compile(re.escape(ROOMS_PATH)))
    expect(page.get_by_text("101", exact=True).first).to_be_visible()
    expect(page.get_by_text("Single", exact=True).first).to_be_visible()
    for item in ADMIN_MENU_ITEMS:
        expect(page.get_by_role("link", name=item, exact=True).first).to_be_visible()


def test_TC04_logout_retorna_para_pagina_inicial_publica(page: Page, app_url):
    login_as_admin(page, app_url)
    logout_control(page).first.click()
    expect(page).to_have_url(re.compile(rf"^{re.escape(app_url)}/?(#.*)?$"))
    expect(login_button(page)).to_have_count(0)
    expect(page.get_by_role("link", name="Messages", exact=True)).to_have_count(0)


def test_TC05_acesso_direto_a_lista_de_quartos_apos_logout(page: Page, app_url):
    login_as_admin(page, app_url)
    logout_control(page).first.click()
    expect(page).to_have_url(re.compile(rf"^{re.escape(app_url)}/?(#.*)?$"))
    page.goto(f"{app_url}{ROOMS_PATH}")
    expect_login_screen(page)
    expect(page.get_by_role("link", name="Messages", exact=True)).to_have_count(0)
    expect(logout_control(page)).to_have_count(0)


def test_TC06_login_admin_com_senha_vazia(page: Page, app_url):
    open_login(page, app_url)
    submit_login(page, VALID_USER, "")
    expect_invalid_credentials(page)


def test_TC07_login_com_senha_em_maiusculas(page: Page, app_url):
    open_login(page, app_url)
    submit_login(page, VALID_USER, VALID_PASSWORD.upper())
    expect_invalid_credentials(page)


def test_TC08_login_com_usuario_vazio_e_senha_correta(page: Page, app_url):
    open_login(page, app_url)
    submit_login(page, "", VALID_PASSWORD)
    expect_invalid_credentials(page)


def test_TC09_acesso_direto_a_lista_de_quartos_sem_autenticacao(page: Page, app_url):
    page.goto(f"{app_url}{ROOMS_PATH}")
    expect_login_screen(page)
    expect(page.get_by_role("link", name="Messages", exact=True)).to_have_count(0)
    expect(logout_control(page)).to_have_count(0)
