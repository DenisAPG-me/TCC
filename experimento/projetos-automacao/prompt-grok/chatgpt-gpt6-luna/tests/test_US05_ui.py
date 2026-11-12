import os

import pytest
from playwright.sync_api import expect

BASE_URL = os.getenv("BASE_URL", "https://automationintesting.online/")
LOGIN_URL = f"{BASE_URL.rstrip('/')}/admin"
ROOMS_URL = f"{BASE_URL.rstrip('/')}/admin/rooms"


def open_login(page):
    page.goto(LOGIN_URL)
    expect(page.get_by_role("textbox", name="Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()


def submit_login(page, username, password):
    page.get_by_role("textbox", name="Username").fill(username)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Login").click()


def expect_login_error(page):
    expect(page.get_by_text("Invalid credentials", exact=True)).to_be_visible()
    expect(page.get_by_role("textbox", name="Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()


def login_as_admin(page):
    open_login(page)
    submit_login(page, "admin", "password")


def test_TC01_empty_credentials_show_error(page):
    open_login(page)
    submit_login(page, "", "")
    expect_login_error(page)


def test_TC02_wrong_password_shows_error(page):
    open_login(page)
    submit_login(page, "admin", "incorrect-password")
    expect_login_error(page)


def test_TC03_valid_login_shows_rooms_and_menu(page):
    login_as_admin(page)

    expect(page.get_by_text("101", exact=True)).to_be_visible()
    expect(page.get_by_text("Single", exact=True)).to_be_visible()

    for menu_item in ("Rooms", "Report", "Branding", "Messages"):
        expect(page.get_by_text(menu_item, exact=True)).to_be_visible()


def test_TC04_logout_returns_to_public_home(page):
    login_as_admin(page)
    expect(page.get_by_text("Logout", exact=True)).to_be_visible()
    page.get_by_text("Logout", exact=True).click()

    expect(page).to_have_url(BASE_URL)
    expect(page).not_to_have_url(ROOMS_URL)


def test_TC05_direct_room_list_after_logout_requires_login(page):
    login_as_admin(page)
    page.get_by_text("Logout", exact=True).click()
    expect(page).to_have_url(BASE_URL)

    page.goto(ROOMS_URL)
    expect(page.get_by_role("textbox", name="Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()


def test_TC06_valid_username_empty_password_shows_error(page):
    open_login(page)
    submit_login(page, "admin", "")
    expect_login_error(page)


def test_TC07_empty_username_valid_password_shows_error(page):
    open_login(page)
    submit_login(page, "", "password")
    expect_login_error(page)
