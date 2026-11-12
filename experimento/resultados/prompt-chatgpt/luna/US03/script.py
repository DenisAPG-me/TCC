import re

import pytest
from playwright.sync_api import expect


# Valores inferidos a partir da User Story; ajuste se o ambiente real diferir.
BASE_URL = "https://practicesoftwaretesting.com/"
LOGIN_PATH = "/auth/login"
DEMO_EMAIL = "customer@practicesoftwaretesting.com"
DEMO_PASSWORD = "welcome01"
INVALID_PASSWORD = "incorrect-password"

ADDRESS = {
    "country": "United States",
    "postal_code": "94105",
    "number": "123",
    "street": "Market Street",
    "city": "San Francisco",
    "state": "California",
}

CARD = {
    "number": "4111111111111111",
    "expiration": "12/30",
    "cvv": "123",
    "holder": "Test Customer",
}


def open_login(page):
    page.goto(f"{BASE_URL.rstrip('/')}{LOGIN_PATH}")
    expect(page.get_by_label("Email")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()


def login_as_demo_user(page):
    open_login(page)
    page.get_by_label("Email").fill(DEMO_EMAIL)
    page.get_by_label("Password").fill(DEMO_PASSWORD)
    page.get_by_role("button", name="Login").click()


def add_product_to_cart(page):
    page.goto(BASE_URL)
    page.get_by_role("button", name="Add to cart").first.click()
    expect(page.get_by_role("link", name=re.compile("Cart", re.IGNORECASE))).to_be_visible()


def open_cart(page):
    page.get_by_role("link", name=re.compile("Cart", re.IGNORECASE)).click()
    expect(page.get_by_role("button", name=re.compile("Proceed to checkout", re.IGNORECASE))).to_be_visible()


def proceed_from_cart(page):
    open_cart(page)
    page.get_by_role("button", name=re.compile("Proceed to checkout", re.IGNORECASE)).click()


def fill_address(page):
    page.get_by_label("Country").select_option(label=ADDRESS["country"])
    page.get_by_label("Postal code").fill(ADDRESS["postal_code"])
    page.get_by_label("Number").fill(ADDRESS["number"])
    page.get_by_label("Street").fill(ADDRESS["street"])
    page.get_by_label("City").fill(ADDRESS["city"])
    page.get_by_label("State").fill(ADDRESS["state"])


def advance_to_payment(page):
    page.get_by_role("button", name=re.compile("Continue|Next|Payment", re.IGNORECASE)).click()
    expect(page.get_by_text(re.compile("Payment", re.IGNORECASE)).first).to_be_visible()


def fill_credit_card(page):
    page.get_by_label("Credit Card").check()
    page.get_by_label("Card number").fill(CARD["number"])
    page.get_by_label("Expiration date").fill(CARD["expiration"])
    page.get_by_label("CVV").fill(CARD["cvv"])
    page.get_by_label("Card holder").fill(CARD["holder"])


def test_CT001_envio_do_login_vazio(page):
    open_login(page)

    page.get_by_role("button", name="Login").click()

    expect(page.get_by_text("Email is required", exact=True)).to_be_visible()
    expect(page.get_by_text("Password is required", exact=True)).to_be_visible()


def test_CT002_login_com_senha_incorreta(page):
    open_login(page)
    page.get_by_label("Email").fill(DEMO_EMAIL)
    page.get_by_label("Password").fill(INVALID_PASSWORD)

    page.get_by_role("button", name="Login").click()

    expect(page.get_by_text("Invalid email or password", exact=True)).to_be_visible()
    expect(page.get_by_label("Email")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()
    expect(page.get_by_text("My account", exact=True)).to_have_count(0)


def test_CT003_checkout_sem_autenticacao(page):
    add_product_to_cart(page)
    proceed_from_cart(page)

    expect(page.get_by_label("Email")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()


def test_CT004_login_bem_sucedido(page):
    login_as_demo_user(page)

    expect(page.get_by_text("My account", exact=True)).to_be_visible()
    expect(page.get_by_role("navigation").get_by_text("Jane Doe", exact=True)).to_be_visible()


def test_CT005_validacao_e_preenchimento_do_endereco(page):
    login_as_demo_user(page)
    add_product_to_cart(page)
    proceed_from_cart(page)

    expect(page.get_by_label("Country")).to_be_visible()
    page.get_by_role("button", name=re.compile("Continue|Next|Payment", re.IGNORECASE)).click()

    expect(page.get_by_label("Country")).to_be_visible()
    expect(page.get_by_label("Postal code")).to_be_visible()
    expect(page.get_by_label("Number")).to_be_visible()

    fill_address(page)
    advance_to_payment(page)


def test_CT006_pagamento_e_confirmacao_do_pedido(page):
    login_as_demo_user(page)
    add_product_to_cart(page)
    proceed_from_cart(page)

    fill_address(page)
    advance_to_payment(page)
    fill_credit_card(page)

    page.get_by_role("button", name=re.compile("Confirm|Pay", re.IGNORECASE)).click()
    expect(page.get_by_text("Payment was successful", exact=True)).to_be_visible()

    page.get_by_role("button", name=re.compile("Confirm order|Place order", re.IGNORECASE)).click()
    expect(page.get_by_text("Thanks for your order!", exact=True)).to_be_visible()
    expect(page.get_by_text(re.compile(r"INV-[A-Za-z0-9-]+"))).to_be_visible()
