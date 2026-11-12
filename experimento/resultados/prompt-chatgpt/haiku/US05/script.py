import re

from playwright.sync_api import Locator, Page, expect

BASE_URL = "https://automationintesting.online/"
ADMIN_URL = BASE_URL + "admin"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "password"
WRONG_PASSWORD = "senha-incorreta-123"
UPPERCASE_PASSWORD = "PASSWORD"
INVALID_CREDENTIALS_MESSAGE = "Invalid credentials"
USERNAME_LABEL = "Username"
PASSWORD_LABEL = "Password"
LOGIN_BUTTON_NAME = "Login"
LOGOUT_NAME = "Logout"
MENU_ITEMS = ["Rooms", "Report", "Branding", "Messages"]
ROOM_NUMBER = "101"
ROOM_TYPE = "Single"
HOME_URL_PATTERN = re.compile(r"^" + re.escape(BASE_URL.rstrip("/")) + r"/?(#/?)?$")
ADMIN_URL_PATTERN = re.compile(r"/admin/?$")


def nav_item(page: Page, name: str) -> Locator:
    return page.get_by_role("link", name=name, exact=True).or_(
        page.get_by_role("button", name=name, exact=True)
    )


def room_row(page: Page) -> Locator:
    return page.get_by_role("row").filter(has_text=ROOM_NUMBER).filter(has_text=ROOM_TYPE)


def open_login_page(page: Page) -> None:
    page.goto(ADMIN_URL)
    expect(page.get_by_label(PASSWORD_LABEL)).to_be_visible()


def submit_credentials(page: Page, username: str, password: str) -> None:
    page.get_by_label(USERNAME_LABEL).fill(username)
    page.get_by_label(PASSWORD_LABEL).fill(password)
    page.get_by_role("button", name=LOGIN_BUTTON_NAME, exact=True).click()


def login_as_admin(page: Page) -> None:
    open_login_page(page)
    submit_credentials(page, ADMIN_USER, ADMIN_PASSWORD)
    expect(room_row(page)).to_be_visible()


def logout(page: Page) -> None:
    nav_item(page, LOGOUT_NAME).click()


def test_CT001_login_campos_vazios_exibe_erro_e_permanece_na_tela_de_login(page: Page) -> None:
    open_login_page(page)
    submit_credentials(page, "", "")
    expect(page.get_by_text(INVALID_CREDENTIALS_MESSAGE)).to_be_visible()
    expect(page).to_have_url(ADMIN_URL_PATTERN)
    expect(page.get_by_label(PASSWORD_LABEL)).to_be_visible()


def test_CT002_login_senha_incorreta_exibe_invalid_credentials(page: Page) -> None:
    open_login_page(page)
    submit_credentials(page, ADMIN_USER, WRONG_PASSWORD)
    expect(page.get_by_text(INVALID_CREDENTIALS_MESSAGE)).to_be_visible()
    expect(page.get_by_label(PASSWORD_LABEL)).to_be_visible()


def test_CT003_login_valido_exibe_lista_de_quartos_com_quarto_101_single(page: Page) -> None:
    open_login_page(page)
    submit_credentials(page, ADMIN_USER, ADMIN_PASSWORD)
    expect(room_row(page)).to_be_visible()


def test_CT004_menu_autenticado_exibe_rooms_report_branding_messages(page: Page) -> None:
    login_as_admin(page)
    for item in MENU_ITEMS:
        expect(nav_item(page, item)).to_be_visible()


def test_CT005_logout_retorna_a_pagina_inicial_publica(page: Page) -> None:
    login_as_admin(page)
    logout(page)
    expect(page).to_have_url(HOME_URL_PATTERN)
    expect(nav_item(page, LOGOUT_NAME)).to_be_hidden()


def test_CT006_acesso_direto_apos_logout_exibe_tela_de_login(page: Page) -> None:
    login_as_admin(page)
    logout(page)
    page.goto(ADMIN_URL)
    expect(page.get_by_label(PASSWORD_LABEL)).to_be_visible()
    expect(room_row(page)).to_be_hidden()


def test_CT007_senha_em_caixa_alta_exibe_invalid_credentials(page: Page) -> None:
    open_login_page(page)
    submit_credentials(page, ADMIN_USER, UPPERCASE_PASSWORD)
    expect(page.get_by_text(INVALID_CREDENTIALS_MESSAGE)).to_be_visible()


def test_CT008_usuario_com_senha_vazia_exibe_erro_e_permanece_na_tela_de_login(page: Page) -> None:
    open_login_page(page)
    submit_credentials(page, ADMIN_USER, "")
    expect(page.get_by_text(INVALID_CREDENTIALS_MESSAGE)).to_be_visible()
    expect(page).to_have_url(ADMIN_URL_PATTERN)
