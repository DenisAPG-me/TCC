import re
from datetime import date

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com"
EMAIL = "customer@practicesoftwaretesting.com"
PASSWORD = "welcome01"
WRONG_PASSWORD = "wrong-password-123"

ADDRESS = {
    "country": "Austria",
    "postal_code": "1010",
    "house_number": "12",
    "street": "Stephansplatz",
    "city": "Vienna",
    "state": "Vienna",
}
ADDRESS_TEXT_FIELDS = ["postal_code", "house_number", "street", "city", "state"]

CARD = {
    "credit_card_number": "4111-1111-1111-1111",
    "expiration_date": f"12/{date.today().year + 1}",
    "cvv": "123",
    "card_holder_name": "Jane Doe",
}


@pytest.fixture(scope="session", autouse=True)
def test_id_attribute(playwright):
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture
def app_url(pytestconfig):
    return (pytestconfig.getoption("base_url", default=None) or BASE_URL).rstrip("/")


def submit_credentials(page: Page, email: str, password: str):
    page.get_by_test_id("email").fill(email)
    page.get_by_test_id("password").fill(password)
    page.get_by_test_id("login-submit").click()


def login(page: Page, app_url: str):
    page.goto(f"{app_url}/auth/login")
    submit_credentials(page, EMAIL, PASSWORD)
    expect(page).to_have_url(re.compile(r"/account"))


def add_product_to_cart(page: Page, app_url: str):
    page.goto(f"{app_url}/")
    page.get_by_test_id(re.compile(r"^product-")).first.click()
    page.get_by_test_id("add-to-cart").click()
    expect(page.get_by_test_id("cart-quantity")).to_have_text("1")


def open_checkout(page: Page):
    page.get_by_test_id("nav-cart").click()
    page.get_by_test_id("proceed-1").click()


def go_to_address_step(page: Page, app_url: str):
    login(page, app_url)
    add_product_to_cart(page, app_url)
    open_checkout(page)
    page.get_by_test_id("proceed-2").click()
    expect(page.get_by_test_id("street")).to_be_visible()


def fill_field(page: Page, test_id: str, value: str):
    field = page.get_by_test_id(test_id)
    if field.evaluate("el => el.tagName") == "SELECT":
        field.select_option(label=value)
    else:
        field.fill(value)


def fill_address(page: Page, address: dict):
    for test_id, value in address.items():
        fill_field(page, test_id, value)


def go_to_payment_step(page: Page, app_url: str):
    go_to_address_step(page, app_url)
    fill_address(page, ADDRESS)
    page.get_by_test_id("proceed-3").click()
    expect(page.get_by_test_id("payment-method")).to_be_visible()


def test_ct01_login_formulario_vazio(page: Page, app_url):
    page.goto(f"{app_url}/auth/login")
    page.get_by_test_id("login-submit").click()

    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/auth/login"))


def test_ct02_login_senha_vazia(page: Page, app_url):
    page.goto(f"{app_url}/auth/login")
    page.get_by_test_id("email").fill(EMAIL)
    page.get_by_test_id("login-submit").click()

    expect(page.get_by_text("Password is required")).to_be_visible()
    expect(page.get_by_text("Email is required")).to_be_hidden()
    expect(page).to_have_url(re.compile(r"/auth/login"))


def test_ct03_login_senha_incorreta(page: Page, app_url):
    page.goto(f"{app_url}/auth/login")
    submit_credentials(page, EMAIL, WRONG_PASSWORD)

    expect(page.get_by_text("Invalid email or password")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/auth/login"))
    expect(page.get_by_test_id("nav-menu")).to_be_hidden()
    expect(page.get_by_test_id("nav-sign-in")).to_be_visible()


def test_ct04_checkout_sem_autenticacao_solicita_credenciais(page: Page, app_url):
    add_product_to_cart(page, app_url)
    open_checkout(page)

    expect(page.get_by_test_id("email")).to_be_visible()
    expect(page.get_by_test_id("password")).to_be_visible()
    expect(page.get_by_test_id("login-submit")).to_be_visible()


def test_ct05_autenticacao_no_checkout_permite_avancar(page: Page, app_url):
    add_product_to_cart(page, app_url)
    open_checkout(page)
    submit_credentials(page, EMAIL, PASSWORD)

    expect(page.get_by_test_id("proceed-2")).to_be_enabled()
    page.get_by_test_id("proceed-2").click()
    expect(page.get_by_test_id("street")).to_be_visible()


def test_ct06_login_valido_exibe_my_account_e_nome(page: Page, app_url):
    login(page, app_url)

    expect(page.get_by_test_id("page-title")).to_have_text("My account")
    expect(page.get_by_test_id("nav-menu")).to_have_text(re.compile(r"\w+"))
    expect(page.get_by_test_id("nav-menu")).not_to_have_text(re.compile(r"Sign in"))
    expect(page.get_by_test_id("nav-sign-in")).to_be_hidden()


def test_ct07_endereco_campos_obrigatorios_vazios(page: Page, app_url):
    go_to_address_step(page, app_url)
    for test_id in ADDRESS_TEXT_FIELDS:
        page.get_by_test_id(test_id).fill("")

    expect(page.get_by_test_id("proceed-3")).to_be_disabled()


def test_ct08_endereco_sem_cep(page: Page, app_url):
    go_to_address_step(page, app_url)
    fill_address(page, ADDRESS)
    page.get_by_test_id("postal_code").fill("")

    expect(page.get_by_test_id("proceed-3")).to_be_disabled()


def test_ct09_endereco_completo_avanca_para_pagamento(page: Page, app_url):
    go_to_address_step(page, app_url)
    fill_address(page, ADDRESS)

    expect(page.get_by_test_id("proceed-3")).to_be_enabled()
    page.get_by_test_id("proceed-3").click()
    expect(page.get_by_test_id("payment-method")).to_be_visible()


def test_ct10_confirmacao_desabilitada_sem_metodo_pagamento(page: Page, app_url):
    go_to_payment_step(page, app_url)

    expect(page.get_by_test_id("finish")).to_be_disabled()


def test_ct11_compra_com_cartao_de_credito(page: Page, app_url):
    go_to_payment_step(page, app_url)
    page.get_by_test_id("payment-method").select_option(label="Credit Card")
    for test_id, value in CARD.items():
        page.get_by_test_id(test_id).fill(value)

    page.get_by_test_id("finish").click()
    expect(page.get_by_text("Payment was successful")).to_be_visible()

    page.get_by_test_id("finish").click()
    expect(
        page.get_by_text(re.compile(r"Thanks for your order! Your invoice number is INV-\d+"))
    ).to_be_visible()
