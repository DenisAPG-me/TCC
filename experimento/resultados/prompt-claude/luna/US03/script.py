import re

import pytest
from playwright.sync_api import expect


BASE_URL = "https://practicesoftwaretesting.com/"
DEMO_EMAIL = "customer@practicesoftwaretesting.com"
DEMO_PASSWORD = "welcome01"
WRONG_PASSWORD = "wrong-password"

ADDRESS = {
    "country": "United States",
    "postcode": "10001",
    "number": "123",
    "street": "Main Street",
    "city": "New York",
    "state": "NY",
}

CARD = {
    "number": "4111111111111111",
    "expiry": "12/2030",
    "cvv": "123",
}


def open_login(page):
    page.goto(BASE_URL)
    page.get_by_role("link", name=re.compile("sign in|login", re.I)).click()
    expect(page).to_have_url(re.compile(r".*/auth/login"))


def login(page, email=DEMO_EMAIL, password=DEMO_PASSWORD):
    open_login(page)
    page.get_by_label(re.compile("email", re.I)).fill(email)
    page.get_by_label(re.compile("password", re.I)).fill(password)
    page.get_by_role("button", name=re.compile("login|sign in", re.I)).click()


def add_product_to_cart(page):
    page.goto(BASE_URL)
    page.get_by_role("button", name=re.compile("add to cart", re.I)).first.click()
    page.get_by_role("link", name=re.compile("cart", re.I)).click()


def start_checkout(page):
    page.get_by_role("button", name=re.compile("proceed to checkout|checkout", re.I)).click()


def fill_address(page):
    fields = (
        (r"country", ADDRESS["country"]),
        (r"post.?code|postal.?code|zip", ADDRESS["postcode"]),
        (r"number", ADDRESS["number"]),
        (r"street|address", ADDRESS["street"]),
        (r"city", ADDRESS["city"]),
        (r"state|province", ADDRESS["state"]),
    )
    for label, value in fields:
        page.get_by_label(re.compile(label, re.I)).fill(value)


def continue_checkout(page):
    page.get_by_role("button", name=re.compile("continue|next", re.I)).click()


def complete_payment(page):
    page.get_by_label(re.compile("credit card", re.I)).check()
    page.get_by_label(re.compile("card number", re.I)).fill(CARD["number"])
    page.get_by_label(re.compile("expiry|expiration", re.I)).fill(CARD["expiry"])
    page.get_by_label(re.compile("cvv|cvc", re.I)).fill(CARD["cvv"])
    page.get_by_role("button", name=re.compile("confirm|pay", re.I)).click()


def authenticated_checkout_to_payment(page):
    login(page)
    expect(page.get_by_role("heading", name=re.compile("my account", re.I))).to_be_visible()
    add_product_to_cart(page)
    start_checkout(page)
    fill_address(page)
    continue_checkout(page)


def test_ct01_login_com_formulario_vazio(page):
    open_login(page)
    page.get_by_role("button", name=re.compile("login|sign in", re.I)).click()

    expect(page.get_by_text("Email is required", exact=True)).to_be_visible()
    expect(page.get_by_text("Password is required", exact=True)).to_be_visible()


def test_ct02_login_com_senha_incorreta(page):
    open_login(page)
    page.get_by_label(re.compile("email", re.I)).fill(DEMO_EMAIL)
    page.get_by_label(re.compile("password", re.I)).fill(WRONG_PASSWORD)
    page.get_by_role("button", name=re.compile("login|sign in", re.I)).click()

    expect(page.get_by_text("Invalid email or password", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name=re.compile("sign in|login", re.I))).to_be_visible()


def test_ct03_checkout_sem_autenticacao(page):
    add_product_to_cart(page)
    start_checkout(page)

    expect(page.get_by_label(re.compile("email", re.I))).to_be_visible()
    expect(page.get_by_label(re.compile("password", re.I))).to_be_visible()


def test_ct04_login_com_conta_de_demonstracao(page):
    login(page)

    expect(page.get_by_role("heading", name=re.compile("my account", re.I))).to_be_visible()
    expect(page.get_by_role("link", name=re.compile("customer", re.I))).to_be_visible()


def test_ct05_endereco_obrigatorio_incompleto(page):
    login(page)
    add_product_to_cart(page)
    start_checkout(page)

    continue_checkout(page)

    expect(page.get_by_label(re.compile("country", re.I))).to_be_visible()
    expect(page.get_by_role("heading", name=re.compile("address", re.I))).to_be_visible()


def test_ct06_endereco_completo_e_pagamento_com_cartao(page):
    authenticated_checkout_to_payment(page)
    complete_payment(page)

    expect(page.get_by_text("Payment was successful", exact=True)).to_be_visible()


def test_ct07_confirmacao_do_pedido_e_fatura(page):
    authenticated_checkout_to_payment(page)
    complete_payment(page)
    expect(page.get_by_text("Payment was successful", exact=True)).to_be_visible()

    page.get_by_role("button", name=re.compile("confirm order|place order|confirm", re.I)).click()

    expect(page.get_by_text("Thanks for your order!", exact=True)).to_be_visible()
    expect(page.get_by_text(re.compile(r"INV-[A-Za-z0-9-]+"))).to_be_visible()


def test_ct08_login_com_email_malformado(page):
    open_login(page)
    page.get_by_label(re.compile("email", re.I)).fill("email-invalido")
    page.get_by_label(re.compile("password", re.I)).fill(DEMO_PASSWORD)
    page.get_by_role("button", name=re.compile("login|sign in", re.I)).click()

    expect(page.get_by_text(re.compile("valid email|invalid email", re.I))).to_be_visible()
    expect(page.get_by_role("link", name=re.compile("sign in|login", re.I))).to_be_visible()
