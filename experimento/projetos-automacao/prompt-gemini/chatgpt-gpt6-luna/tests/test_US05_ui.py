import re

import pytest
from playwright.sync_api import Page, expect


BASE_URL = "https://automationintesting.online"


def open_login(page: Page) -> None:
    page.goto(f"{BASE_URL}/admin")


def login(page: Page, username: str = "admin", password: str = "password") -> None:
    page.get_by_label("Username").fill(username)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Login").click()


def test_CT_01_login_com_campos_vazios(page: Page) -> None:
    open_login(page)
    page.get_by_role("button", name="Login").click()

    expect(page.get_by_text("Invalid credentials")).to_be_visible()
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()


def test_CT_02_login_com_senha_incorreta(page: Page) -> None:
    open_login(page)
    login(page, username="admin", password="wrong-password")

    expect(page.get_by_text("Invalid credentials")).to_be_visible()


def test_CT_03_login_valido_exibe_lista_e_menu(page: Page) -> None:
    open_login(page)
    login(page)

    expect(page).to_have_url(re.compile(r"/admin/rooms/?$"))
    room_101 = page.get_by_role("row").filter(has_text="101")
    expect(room_101).to_contain_text("Single")

    for menu_item in ("Rooms", "Report", "Branding", "Messages"):
        expect(page.get_by_text(menu_item, exact=True)).to_be_visible()


def test_CT_04_logout_retorna_a_pagina_publica(page: Page) -> None:
    open_login(page)
    login(page)
    expect(page.get_by_role("button", name="Logout")).to_be_visible()

    page.get_by_role("button", name="Logout").click()

    expect(page).to_have_url(re.compile(r"^https://automationintesting\.online/?$"))


def test_CT_05_lista_de_quartos_requer_login_apos_logout(page: Page) -> None:
    open_login(page)
    login(page)
    page.get_by_role("button", name="Logout").click()

    page.goto(f"{BASE_URL}/admin/rooms")

    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()
