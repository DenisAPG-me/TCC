import re

import pytest
from playwright.sync_api import Page, expect

# Configurações e valores inferidos (ajustar conforme o sistema real)
BASE_URL = "https://practicesoftwaretesting.com"
TEST_ID_ATTRIBUTE = "data-test"
EXPECT_TIMEOUT_MS = 15000

CUSTOMER_EMAIL = "customer@practicesoftwaretesting.com"
CUSTOMER_PASSWORD = "welcome01"
CUSTOMER_NAME = "Jane Doe"
WRONG_PASSWORD = "senhaIncorreta123"

PRODUCT_NAME = "Combination Pliers"

LOGIN_PATH = "/auth/login"
ACCOUNT_URL_PATTERN = re.compile(r"/account/?$")
LOGIN_URL_PATTERN = re.compile(r"/auth/login/?$")

MSG_EMAIL_REQUIRED = "Email is required"
MSG_PASSWORD_REQUIRED = "Password is required"
MSG_INVALID_LOGIN = "Invalid email or password"
MSG_MY_ACCOUNT = "My account"
MSG_PAYMENT_SUCCESS = "Payment was successful"
ORDER_CONFIRMATION_PATTERN = re.compile(
    r"Thanks for your order! Your invoice number is INV-[A-Za-z0-9]+"
)

TID = {
    "email": "email",
    "password": "password",
    "login_submit": "login-submit",
    "email_error": "email-error",
    "password_error": "password-error",
    "login_error": "login-error",
    "nav_menu": "nav-menu",
    "nav_sign_in": "nav-sign-in",
    "nav_cart": "nav-cart",
    "cart_quantity": "cart-quantity",
    "page_title": "page-title",
    "product_name": "product-name",
    "add_to_cart": "add-to-cart",
    "cart_product_title": "product-title",
    "proceed_cart": "proceed-1",
    "proceed_sign_in": "proceed-2",
    "proceed_address": "proceed-3",
    "payment_method": "payment-method",
    "credit_card_number": "credit_card_number",
    "expiration_date": "expiration_date",
    "cvv": "cvv",
    "card_holder_name": "card_holder_name",
    "finish": "finish",
    "payment_success": "payment-success-message",
}

ADDRESS = {
    "country": "Netherlands",
    "postal_code": "1012 NX",
    "house_number": "1",
    "street": "Kalverstraat",
    "city": "Amsterdam",
    "state": "Noord-Holland",
}

CREDIT_CARD = {
    "payment_method_label": "Credit Card",
    "credit_card_number": "4111-1111-1111-1111",
    "expiration_date": "12/2030",
    "cvv": "123",
    "card_holder_name": "Jane Doe",
}

expect.set_options(timeout=EXPECT_TIMEOUT_MS)


@pytest.fixture(scope="session", autouse=True)
def configure_test_id_attribute(playwright):
    playwright.selectors.set_test_id_attribute(TEST_ID_ATTRIBUTE)


@pytest.fixture
def app_url(base_url):
    return (base_url or BASE_URL).rstrip("/")


def submit_login(page: Page, app_url: str, email: str = "", password: str = ""):
    page.goto(f"{app_url}{LOGIN_PATH}")
    if email:
        page.get_by_test_id(TID["email"]).fill(email)
    if password:
        page.get_by_test_id(TID["password"]).fill(password)
    page.get_by_test_id(TID["login_submit"]).click()


def login_as_customer(page: Page, app_url: str):
    submit_login(page, app_url, CUSTOMER_EMAIL, CUSTOMER_PASSWORD)
    expect(page).to_have_url(ACCOUNT_URL_PATTERN)


def add_product_to_cart(page: Page, app_url: str):
    page.goto(f"{app_url}/")
    page.get_by_test_id(TID["product_name"]).filter(has_text=PRODUCT_NAME).first.click()
    expect(page.get_by_test_id(TID["product_name"])).to_have_text(PRODUCT_NAME)
    page.get_by_test_id(TID["add_to_cart"]).click()
    expect(page.get_by_test_id(TID["cart_quantity"])).to_have_text("1")


def proceed_from_cart(page: Page):
    page.get_by_test_id(TID["nav_cart"]).click()
    expect(
        page.get_by_test_id(TID["cart_product_title"]).filter(has_text=PRODUCT_NAME)
    ).to_be_visible()
    page.get_by_test_id(TID["proceed_cart"]).click()


def go_to_address_step(page: Page, app_url: str):
    login_as_customer(page, app_url)
    add_product_to_cart(page, app_url)
    proceed_from_cart(page)
    page.get_by_test_id(TID["proceed_sign_in"]).click()
    expect(page.get_by_test_id("street")).to_be_visible()


def set_address_field(page: Page, field: str, value: str):
    locator = page.get_by_test_id(field)
    if locator.evaluate("e => e.tagName") == "SELECT":
        if value:
            locator.select_option(label=value)
        else:
            locator.select_option(value="")
    else:
        locator.fill(value)


def fill_address(page: Page, values: dict):
    for field, value in values.items():
        set_address_field(page, field, value)


def go_to_payment_step(page: Page, app_url: str):
    go_to_address_step(page, app_url)
    fill_address(page, ADDRESS)
    proceed = page.get_by_test_id(TID["proceed_address"])
    expect(proceed).to_be_enabled()
    proceed.click()
    expect(page.get_by_test_id(TID["payment_method"])).to_be_visible()


def test_CT001_login_formulario_vazio_exibe_mensagens(page: Page, app_url):
    submit_login(page, app_url)

    expect(page.get_by_test_id(TID["email_error"])).to_contain_text(MSG_EMAIL_REQUIRED)
    expect(page.get_by_test_id(TID["password_error"])).to_contain_text(MSG_PASSWORD_REQUIRED)
    expect(page).to_have_url(LOGIN_URL_PATTERN)


def test_CT002_login_somente_email_exige_senha(page: Page, app_url):
    submit_login(page, app_url, email=CUSTOMER_EMAIL)

    expect(page.get_by_test_id(TID["password_error"])).to_contain_text(MSG_PASSWORD_REQUIRED)
    expect(page.get_by_text(MSG_EMAIL_REQUIRED)).to_have_count(0)
    expect(page).to_have_url(LOGIN_URL_PATTERN)


def test_CT003_login_senha_incorreta_sem_sessao(page: Page, app_url):
    submit_login(page, app_url, CUSTOMER_EMAIL, WRONG_PASSWORD)

    expect(page.get_by_test_id(TID["login_error"])).to_contain_text(MSG_INVALID_LOGIN)
    expect(page).to_have_url(LOGIN_URL_PATTERN)
    expect(page.get_by_test_id(TID["nav_sign_in"])).to_be_visible()
    expect(page.get_by_test_id(TID["nav_menu"])).to_have_count(0)


def test_CT004_checkout_sem_autenticacao_solicita_credenciais(page: Page, app_url):
    add_product_to_cart(page, app_url)
    proceed_from_cart(page)

    expect(page.get_by_test_id(TID["email"])).to_be_visible()
    expect(page.get_by_test_id(TID["password"])).to_be_visible()
    expect(page.get_by_test_id(TID["login_submit"])).to_be_visible()
    expect(page.get_by_test_id(TID["nav_menu"])).to_have_count(0)


def test_CT005_login_valido_exibe_my_account_com_nome(page: Page, app_url):
    login_as_customer(page, app_url)

    expect(page.get_by_test_id(TID["page_title"])).to_have_text(MSG_MY_ACCOUNT)
    expect(page.get_by_test_id(TID["nav_menu"])).to_contain_text(CUSTOMER_NAME)


def test_CT006_endereco_campos_vazios_bloqueia_avanco(page: Page, app_url):
    go_to_address_step(page, app_url)

    fill_address(page, {field: "" for field in ADDRESS})

    expect(page.get_by_test_id(TID["proceed_address"])).to_be_disabled()
    expect(page.get_by_test_id(TID["payment_method"])).to_have_count(0)


def test_CT007_endereco_sem_cep_bloqueia_avanco(page: Page, app_url):
    go_to_address_step(page, app_url)

    fill_address(page, ADDRESS)
    set_address_field(page, "postal_code", "")

    expect(page.get_by_test_id(TID["proceed_address"])).to_be_disabled()
    expect(page.get_by_test_id(TID["payment_method"])).to_have_count(0)


def test_CT008_endereco_completo_permite_avancar(page: Page, app_url):
    go_to_address_step(page, app_url)

    fill_address(page, ADDRESS)
    proceed = page.get_by_test_id(TID["proceed_address"])
    expect(proceed).to_be_enabled()
    proceed.click()

    expect(page.get_by_test_id(TID["payment_method"])).to_be_visible()


def test_CT009_pagamento_cartao_credito_finaliza_pedido(page: Page, app_url):
    go_to_payment_step(page, app_url)

    page.get_by_test_id(TID["payment_method"]).select_option(
        label=CREDIT_CARD["payment_method_label"]
    )
    page.get_by_test_id(TID["credit_card_number"]).fill(CREDIT_CARD["credit_card_number"])
    page.get_by_test_id(TID["expiration_date"]).fill(CREDIT_CARD["expiration_date"])
    page.get_by_test_id(TID["cvv"]).fill(CREDIT_CARD["cvv"])
    page.get_by_test_id(TID["card_holder_name"]).fill(CREDIT_CARD["card_holder_name"])

    finish = page.get_by_test_id(TID["finish"])
    expect(finish).to_be_enabled()
    finish.click()
    expect(page.get_by_test_id(TID["payment_success"])).to_contain_text(MSG_PAYMENT_SUCCESS)

    finish.click()
    expect(page.get_by_text(ORDER_CONFIRMATION_PATTERN)).to_be_visible()
