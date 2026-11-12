import pytest
from playwright.sync_api import Page as _page, expect

BASE_URL = "https://automationintesting.online/"
ADMIN_USER = "admin"
ADMIN_PASS = "password"


def test_ct01_login_com_credenciais_vazias(page: _page) -> None:
    page.goto(f"{BASE_URL}admin")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_text("Invalid credentials")).to_be_visible()
    expect(page.get_by_role("textbox", name="Username")).to_be_visible()


def test_ct02_login_com_senha_incorreta(page: _page) -> None:
    page.goto(f"{BASE_URL}admin")
    page.get_by_role("textbox", name="Username").fill(ADMIN_USER)
    page.get_by_role("textbox", name="Password").fill("wrongpassword")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_text("Invalid credentials")).to_be_visible()
    expect(page.get_by_role("textbox", name="Username")).to_be_visible()


def test_ct03_login_com_credenciais_validas(page: _page) -> None:
    page.goto(f"{BASE_URL}admin")
    page.get_by_role("textbox", name="Username").fill(ADMIN_USER)
    page.get_by_role("textbox", name="Password").fill(ADMIN_PASS)
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_text("101")).to_be_visible()
    expect(page.get_by_text("Single")).to_be_visible()
    expect(page.get_by_role("link", name="Rooms")).to_be_visible()
    expect(page.get_by_role("link", name="Report")).to_be_visible()
    expect(page.get_by_role("link", name="Branding")).to_be_visible()
    expect(page.get_by_role("link", name="Messages")).to_be_visible()


def test_ct04_realizar_logout(page: _page) -> None:
    page.goto(f"{BASE_URL}admin")
    page.get_by_role("textbox", name="Username").fill(ADMIN_USER)
    page.get_by_role("textbox", name="Password").fill(ADMIN_PASS)
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_role("link", name="Rooms")).to_be_visible()
    page.get_by_role("button", name="Logout").click()
    expect(page.get_by_role("button", name="Login")).to_be_visible()


def test_ct05_acesso_direto_apos_logout(page: _page) -> None:
    page.goto(f"{BASE_URL}admin")
    page.get_by_role("textbox", name="Username").fill(ADMIN_USER)
    page.get_by_role("textbox", name="Password").fill(ADMIN_PASS)
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_role("link", name="Rooms")).to_be_visible()
    page.get_by_role("button", name="Logout").click()
    page.goto(f"{BASE_URL}admin")
    expect(page.get_by_role("button", name="Login")).to_be_visible()
