import os

import pytest
from playwright.sync_api import expect


BASE_URL = os.getenv("BASE_URL", "https://automationintesting.online/").rstrip("/")
LOGIN_URL = f"{BASE_URL}/admin"
ROOMS_URL = f"{BASE_URL}/admin/rooms"

VALID_USERNAME = "admin"
VALID_PASSWORD = "password"
INVALID_PASSWORD = "incorrect-password"

LOGIN_USERNAME_LABEL = "Username"
LOGIN_PASSWORD_LABEL = "Password"
LOGIN_BUTTON_NAME = "Login"
LOGOUT_BUTTON_NAME = "Logout"
INVALID_CREDENTIALS_TEXT = "Invalid credentials"
PUBLIC_HOME_TITLE = "Shady Meadows B&B"


def open_login(page):
    page.goto(LOGIN_URL)
    expect(page.get_by_label(LOGIN_USERNAME_LABEL)).to_be_visible()
    expect(page.get_by_label(LOGIN_PASSWORD_LABEL)).to_be_visible()


def login(page, username=VALID_USERNAME, password=VALID_PASSWORD):
    page.get_by_label(LOGIN_USERNAME_LABEL).fill(username)
    page.get_by_label(LOGIN_PASSWORD_LABEL).fill(password)
    page.get_by_role("button", name=LOGIN_BUTTON_NAME).click()


def assert_invalid_login(page):
    expect(page.get_by_text(INVALID_CREDENTIALS_TEXT, exact=True)).to_be_visible()
    expect(page.get_by_label(LOGIN_USERNAME_LABEL)).to_be_visible()
    expect(page.get_by_label(LOGIN_PASSWORD_LABEL)).to_be_visible()


def authenticate(page):
    open_login(page)
    login(page)
    expect(page).to_have_url(ROOMS_URL)


def test_CT001_login_com_credenciais_vazias(page):
    open_login(page)
    page.get_by_role("button", name=LOGIN_BUTTON_NAME).click()

    assert_invalid_login(page)
    expect(page).to_have_url(LOGIN_URL)


def test_CT002_login_com_senha_incorreta(page):
    open_login(page)
    login(page, username=VALID_USERNAME, password=INVALID_PASSWORD)

    assert_invalid_login(page)


def test_CT003_login_valido_e_conteudo_do_painel(page):
    authenticate(page)

    expect(page.get_by_text("101", exact=True)).to_be_visible()
    expect(page.get_by_text("Single", exact=True)).to_be_visible()

    for menu_item in ("Rooms", "Report", "Branding", "Messages"):
        expect(page.get_by_text(menu_item, exact=True)).to_be_visible()


def test_CT004_logout_retorna_a_pagina_inicial_publica(page):
    authenticate(page)
    page.get_by_role("button", name=LOGOUT_BUTTON_NAME).click()

    expect(page).to_have_url(BASE_URL + "/")
    expect(page).to_have_title(PUBLIC_HOME_TITLE)


def test_CT005_acesso_a_quartos_apos_logout_exige_novo_login(page):
    authenticate(page)
    page.get_by_role("button", name=LOGOUT_BUTTON_NAME).click()
    expect(page).to_have_url(BASE_URL + "/")
    expect(page).to_have_title(PUBLIC_HOME_TITLE)

    page.goto(ROOMS_URL)

    expect(page).to_have_url(LOGIN_URL)
    expect(page.get_by_label(LOGIN_USERNAME_LABEL)).to_be_visible()
    expect(page.get_by_label(LOGIN_PASSWORD_LABEL)).to_be_visible()
