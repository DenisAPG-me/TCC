import re

import pytest
from playwright.sync_api import Page, expect

# URL base (pode ser sobrescrita com --base-url)
BASE_URL = "https://automationintesting.online/"

# Rotas (ROOMS_PATH é inferida)
ADMIN_PATH = "/admin"
ROOMS_PATH = "/admin/rooms"

# Credenciais
VALID_USERNAME = "admin"
VALID_PASSWORD = "password"
WRONG_PASSWORD = "senha-incorreta-123"

# Seletores e textos inferidos
USERNAME_LABEL = "Username"
PASSWORD_LABEL = "Password"
LOGIN_BUTTON_NAME = "Login"
LOGOUT_BUTTON_NAME = "Logout"
INVALID_CREDENTIALS_TEXT = "Invalid credentials"
MENU_LINKS = ("Rooms", "Report", "Branding", "Messages")
ROOM_LISTING_TEST_ID = "roomlisting"
ROOM_NUMBER = "101"
ROOM_TYPE = "Single"

UI_TIMEOUT_MS = 10_000
expect.set_options(timeout=UI_TIMEOUT_MS)


@pytest.fixture
def app_root(base_url):
    return (base_url or BASE_URL).rstrip("/")


def username_input(page: Page):
    return page.get_by_label(USERNAME_LABEL, exact=True)


def password_input(page: Page):
    return page.get_by_label(PASSWORD_LABEL, exact=True)


def login_button(page: Page):
    return page.get_by_role("button", name=LOGIN_BUTTON_NAME, exact=True)


def logout_button(page: Page):
    return page.get_by_role("button", name=LOGOUT_BUTTON_NAME, exact=True)


def room_listings(page: Page):
    return page.get_by_test_id(ROOM_LISTING_TEST_ID)


def expect_login_screen(page: Page):
    expect(username_input(page)).to_be_visible()
    expect(password_input(page)).to_be_visible()
    expect(login_button(page)).to_be_visible()


def open_login(page: Page, app_root: str):
    page.goto(app_root + ADMIN_PATH)
    expect_login_screen(page)


def submit_login(page: Page, username: str, password: str):
    username_input(page).fill(username)
    password_input(page).fill(password)
    login_button(page).click()


def login_as_admin(page: Page, app_root: str):
    open_login(page, app_root)
    submit_login(page, VALID_USERNAME, VALID_PASSWORD)
    expect(page).to_have_url(re.compile(re.escape(ROOMS_PATH) + r"/?$"))
    expect(logout_button(page)).to_be_visible()


def logout_to_home(page: Page, app_root: str):
    logout_button(page).click()
    expect(page).to_have_url(re.compile("^" + re.escape(app_root) + r"/?$"))


def test_CT001_login_com_usuario_e_senha_vazios(page: Page, app_root: str):
    open_login(page, app_root)

    submit_login(page, "", "")

    expect(page.get_by_text(INVALID_CREDENTIALS_TEXT)).to_be_visible()
    expect(page).to_have_url(re.compile(re.escape(ADMIN_PATH) + r"/?$"))
    expect_login_screen(page)


def test_CT002_login_com_admin_e_senha_incorreta(page: Page, app_root: str):
    open_login(page, app_root)

    submit_login(page, VALID_USERNAME, WRONG_PASSWORD)

    expect(page.get_by_text(INVALID_CREDENTIALS_TEXT)).to_be_visible()
    expect(logout_button(page)).to_have_count(0)


def test_CT003_login_com_admin_e_senha_vazia(page: Page, app_root: str):
    open_login(page, app_root)

    submit_login(page, VALID_USERNAME, "")

    expect(page.get_by_text(INVALID_CREDENTIALS_TEXT)).to_be_visible()
    expect_login_screen(page)


def test_CT004_login_valido_exibe_lista_de_quartos_e_menu(page: Page, app_root: str):
    login_as_admin(page, app_root)

    room_101 = room_listings(page).filter(has=page.get_by_text(ROOM_NUMBER, exact=True))
    expect(room_101.first).to_be_visible()
    expect(room_101.first).to_contain_text(re.compile(ROOM_TYPE, re.IGNORECASE))

    for link_name in MENU_LINKS:
        expect(page.get_by_role("link", name=link_name, exact=True)).to_be_visible()


def test_CT005_logout_retorna_a_pagina_inicial_publica(page: Page, app_root: str):
    login_as_admin(page, app_root)

    logout_to_home(page, app_root)

    expect(logout_button(page)).to_have_count(0)


def test_CT006_acesso_direto_a_lista_de_quartos_apos_logout(page: Page, app_root: str):
    login_as_admin(page, app_root)
    logout_to_home(page, app_root)

    page.goto(app_root + ROOMS_PATH)

    expect_login_screen(page)
    expect(room_listings(page)).to_have_count(0)
    expect(logout_button(page)).to_have_count(0)
