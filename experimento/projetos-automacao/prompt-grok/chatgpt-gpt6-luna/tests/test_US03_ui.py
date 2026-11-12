import re

import pytest
from playwright.sync_api import expect


BASE_URL = "https://practicesoftwaretesting.com/"
EMAIL = "customer@practicesoftwaretesting.com"
PASSWORD = "welcome01"
WRONG_PASSWORD = "wrong-password"

ADDRESS = {
    "ZIP": "12345",
    "Number": "10",
    "Street": "Main Street",
    "City": "Austin",
    "State": "Texas",
}

CARD = {
    "Cardholder name": "Jane Doe",
    "Card number": "4111111111111111",
    "Expiry date": "12/30",
    "CVV": "123",
}


def open_login(page):
    page.goto(BASE_URL + "auth/login")


def login(page):
    open_login(page)
    page.get_by_label(re.compile("email", re.I)).fill(EMAIL)
    page.get_by_label(re.compile("password", re.I)).fill(PASSWORD)
    page.get_by_role("button", name=re.compile(r"sign in|login", re.I)).click()


def add_product_and_open_checkout(page):
    page.goto(BASE_URL)
    page.get_by_role("button", name=re.compile("add to cart", re.I)).first.click()
    page.get_by_role("link", name=re.compile("cart", re.I)).click()
    page.get_by_role("button", name=re.compile("proceed to checkout|checkout", re.I)).click()


def fill_address(page, omit=None):
    omit = omit or set()
    for label, value in ADDRESS.items():
        if label not in omit:
            page.get_by_label(re.compile(re.escape(label), re.I)).fill(value)

    country = page.get_by_label(re.compile("country", re.I))
    if "Country" not in omit:
        country.select_option(label=re.compile("united states", re.I)) if False else country.select_option(label="United States")

    page.get_by_role("button", name=re.compile("continue|next|payment", re.I)).click()


def is_payment_step(page):
    return page.get_by_text(re.compile("payment", re.I)).first


def test_TC01_login_empty_form_shows_required_messages(page):
    open_login(page)
    page.get_by_role("button", name=re.compile(r"sign in|login", re.I)).click()
    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_be_visible()


def test_TC02_wrong_password_rejected_without_session(page):
    open_login(page)
    page.get_by_label(re.compile("email", re.I)).fill(EMAIL)
    page.get_by_label(re.compile("password", re.I)).fill(WRONG_PASSWORD)
    page.get_by_role("button", name=re.compile(r"sign in|login", re.I)).click()
    expect(page.get_by_text("Invalid email or password")).to_be_visible()
    expect(page.get_by_role("link", name=re.compile("my account", re.I))).not_to_be_visible()


def test_TC03_unauthenticated_checkout_requests_credentials(page):
    add_product_and_open_checkout(page)
    expect(page.get_by_label(re.compile("email", re.I))).to_be_visible()
    expect(page.get_by_label(re.compile("password", re.I))).to_be_visible()


def test_TC04_valid_login_shows_account_and_user_name(page):
    login(page)
    expect(page.get_by_text("My account")).to_be_visible()
    expect(page.get_by_text(re.compile("Jane Doe", re.I))).to_be_visible()


def test_TC05_empty_address_cannot_advance_to_payment(page):
    login(page)
    add_product_and_open_checkout(page)
    expect(page.get_by_label(re.compile("email", re.I))).to_be_visible()
    page.get_by_label(re.compile("email", re.I)).fill(EMAIL)
    page.get_by_label(re.compile("password", re.I)).fill(PASSWORD)
    page.get_by_role("button", name=re.compile(r"sign in|login", re.I)).click()

    payment = is_payment_step(page)
    fill_address(page, omit=set(ADDRESS) | {"Country"})
    expect(payment).not_to_be_visible()


def test_TC06_complete_address_advances_to_payment(page):
    login(page)
    add_product_and_open_checkout(page)
    if page.get_by_label(re.compile("email", re.I)).is_visible():
        page.get_by_label(re.compile("email", re.I)).fill(EMAIL)
        page.get_by_label(re.compile("password", re.I)).fill(PASSWORD)
        page.get_by_role("button", name=re.compile(r"sign in|login", re.I)).click()

    fill_address(page)
    expect(is_payment_step(page)).to_be_visible()


def test_TC07_credit_card_payment_and_order_confirmation(page):
    login(page)
    add_product_and_open_checkout(page)
    if page.get_by_label(re.compile("email", re.I)).is_visible():
        page.get_by_label(re.compile("email", re.I)).fill(EMAIL)
        page.get_by_label(re.compile("password", re.I)).fill(PASSWORD)
        page.get_by_role("button", name=re.compile(r"sign in|login", re.I)).click()

    fill_address(page)
    expect(is_payment_step(page)).to_be_visible()
    page.get_by_label(re.compile("credit card", re.I)).check()

    for label, value in CARD.items():
        page.get_by_label(re.compile(re.escape(label), re.I)).fill(value)

    page.get_by_role("button", name=re.compile("confirm|pay", re.I)).click()
    expect(page.get_by_text("Payment was successful")).to_be_visible()

    page.get_by_role("button", name=re.compile("confirm order|place order|complete order", re.I)).click()
    expect(page.get_by_text(re.compile(
        r"Thanks for your order! Your invoice number is INV-",
        re.I,
    ))).to_be_visible()


def test_TC08_missing_zip_prevents_payment_step(page):
    login(page)
    add_product_and_open_checkout(page)
    if page.get_by_label(re.compile("email", re.I)).is_visible():
        page.get_by_label(re.compile("email", re.I)).fill(EMAIL)
        page.get_by_label(re.compile("password", re.I)).fill(PASSWORD)
        page.get_by_role("button", name=re.compile(r"sign in|login", re.I)).click()

    payment = is_payment_step(page)
    fill_address(page, omit={"ZIP"})
    expect(payment).not_to_be_visible()


def test_TC09_missing_country_prevents_payment_step(page):
    login(page)
    add_product_and_open_checkout(page)
    if page.get_by_label(re.compile("email", re.I)).is_visible():
        page.get_by_label(re.compile("email", re.I)).fill(EMAIL)
        page.get_by_label(re.compile("password", re.I)).fill(PASSWORD)
        page.get_by_role("button", name=re.compile(r"sign in|login", re.I)).click()

    payment = is_payment_step(page)
    fill_address(page, omit={"Country"})
    expect(payment).not_to_be_visible()
