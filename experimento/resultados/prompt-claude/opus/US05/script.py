import re

from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online"
ADMIN_URL = f"{BASE_URL}/admin"
ADMIN_ROOMS_URL = f"{BASE_URL}/admin/rooms"

VALID_USERNAME = "admin"
VALID_PASSWORD = "password"
WRONG_PASSWORD = "senhaErrada123"
UPPERCASE_PASSWORD = "PASSWORD"
TRAILING_SPACE_PASSWORD = "password "

ERROR_MESSAGE = "Invalid credentials"
EXPECTED_ROOM_NUMBER = "101"
EXPECTED_ROOM_TYPE = "Single"
ADMIN_MENU_ITEMS = ["Rooms", "Report", "Branding", "Messages"]

HOME_URL_PATTERN = re.compile(r"^https://automationintesting\.online/?$")
ROOMS_URL_PATTERN = re.compile(r".*/admin/rooms/?$")
ADMIN_LOGIN_URL_PATTERN = re.compile(r".*/admin/?$")


def username_field(page: Page):
    return page.get_by_label("Username")


def password_field(page: Page):
    return page.get_by_label("Password")


def login_button(page: Page):
    return page.get_by_role("button", name="Login")


def logout_button(page: Page):
    return page.get_by_role("button", name="Logout")


def submit_login(page: Page, username: str, password: str) -> None:
    page.goto(ADMIN_URL)
    expect(login_button(page)).to_be_visible()
    username_field(page).fill(username)
    password_field(page).fill(password)
    login_button(page).click()


def login_as_admin(page: Page) -> None:
    submit_login(page, VALID_USERNAME, VALID_PASSWORD)
    expect(page).to_have_url(ROOMS_URL_PATTERN)
    expect(logout_button(page)).to_be_visible()


def assert_login_screen(page: Page) -> None:
    expect(username_field(page)).to_be_visible()
    expect(password_field(page)).to_be_visible()
    expect(login_button(page)).to_be_visible()


def assert_invalid_credentials(page: Page) -> None:
    expect(page.get_by_text(ERROR_MESSAGE)).to_be_visible()
    assert_login_screen(page)
    expect(logout_button(page)).to_have_count(0)


def test_ct01_login_com_usuario_e_senha_vazios(page: Page):
    submit_login(page, "", "")
    assert_invalid_credentials(page)
    expect(page).to_have_url(ADMIN_LOGIN_URL_PATTERN)


def test_ct02_login_com_senha_incorreta(page: Page):
    submit_login(page, VALID_USERNAME, WRONG_PASSWORD)
    assert_invalid_credentials(page)


def test_ct03_login_com_senha_vazia(page: Page):
    submit_login(page, VALID_USERNAME, "")
    assert_invalid_credentials(page)


def test_ct04_login_com_senha_em_caixa_alta(page: Page):
    submit_login(page, VALID_USERNAME, UPPERCASE_PASSWORD)
    assert_invalid_credentials(page)
    expect(page.get_by_role("link", name="Branding", exact=True)).to_have_count(0)


def test_ct05_login_com_senha_com_espaco_final(page: Page):
    submit_login(page, VALID_USERNAME, TRAILING_SPACE_PASSWORD)
    assert_invalid_credentials(page)
    expect(page.get_by_role("link", name="Branding", exact=True)).to_have_count(0)


def test_ct06_login_valido_exibe_quarto_101_single(page: Page):
    login_as_admin(page)
    room_row = page.get_by_test_id("roomlisting").filter(
        has=page.get_by_text(EXPECTED_ROOM_NUMBER, exact=True)
    )
    expect(room_row.first).to_be_visible()
    expect(room_row.first).to_contain_text(
        re.compile(EXPECTED_ROOM_TYPE, re.IGNORECASE)
    )


def test_ct07_login_valido_exibe_menu_do_painel(page: Page):
    login_as_admin(page)
    for item in ADMIN_MENU_ITEMS:
        expect(page.get_by_role("link", name=item, exact=True)).to_be_visible()
    expect(logout_button(page)).to_be_visible()


def test_ct08_logout_retorna_para_pagina_inicial(page: Page):
    login_as_admin(page)
    logout_button(page).click()
    expect(page).to_have_url(HOME_URL_PATTERN)
    expect(logout_button(page)).to_have_count(0)
    expect(page.get_by_role("link", name="Branding", exact=True)).to_have_count(0)


def test_ct09_acesso_direto_aos_quartos_apos_logout_exige_login(page: Page):
    login_as_admin(page)
    logout_button(page).click()
    expect(page).to_have_url(HOME_URL_PATTERN)
    page.goto(ADMIN_ROOMS_URL)
    assert_login_screen(page)
    expect(page.get_by_test_id("roomlisting")).to_have_count(0)
    expect(logout_button(page)).to_have_count(0)


def test_ct10_acesso_direto_aos_quartos_sem_login_exige_login(page: Page):
    page.goto(ADMIN_ROOMS_URL)
    assert_login_screen(page)
    expect(page.get_by_test_id("roomlisting")).to_have_count(0)
    expect(logout_button(page)).to_have_count(0)
