import re
from datetime import date

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"
LOGIN_URL = f"{BASE_URL}auth/login"
CHECKOUT_URL = f"{BASE_URL}checkout"

USER_EMAIL = "customer@practicesoftwaretesting.com"
USER_PASSWORD = "welcome01"
USER_NAME = "Jane Doe"
WRONG_PASSWORD = "senhaErrada123"

ADDRESS = {
    "country": "Brazil",
    "postal_code": "01001-000",
    "house_number": "100",
    "street": "Rua Exemplo",
    "city": "Sao Paulo",
    "state": "SP",
}

CARD_NUMBER = "0000-0000-0000-0000"
INVALID_CARD_NUMBER = "1234"
CARD_EXPIRATION = f"{date.today().month:02d}/{date.today().year + 2}"
CARD_CVV = "123"
CARD_HOLDER = "Jane Doe"

expect.set_options(timeout=15_000)


@pytest.fixture(scope="session", autouse=True)
def configure_test_id(playwright):
    playwright.selectors.set_test_id_attribute("data-test")


def login(page: Page, email: str = USER_EMAIL, password: str = USER_PASSWORD):
    page.goto(LOGIN_URL)
    page.get_by_test_id("email").fill(email)
    page.get_by_test_id("password").fill(password)
    page.get_by_test_id("login-submit").click()


def login_successfully(page: Page):
    login(page)
    expect(page).to_have_url(re.compile(r"/account$"))


def add_product_to_cart(page: Page):
    page.goto(BASE_URL)
    page.get_by_test_id("product-name").first.click()
    page.get_by_test_id("add-to-cart").click()
    expect(page.get_by_test_id("cart-quantity")).to_have_text("1")


def go_to_address_step(page: Page):
    login_successfully(page)
    add_product_to_cart(page)
    page.goto(CHECKOUT_URL)
    page.get_by_test_id("proceed-1").click()
    page.get_by_test_id("proceed-2").click()
    expect(page.get_by_test_id("street")).to_be_visible()


def fill_address(page: Page, address: dict):
    for field, value in address.items():
        page.get_by_test_id(field).fill(value)


def go_to_payment_step(page: Page):
    go_to_address_step(page)
    fill_address(page, ADDRESS)
    page.get_by_test_id("proceed-3").click()
    expect(page.get_by_test_id("payment-method")).to_be_visible()


def fill_credit_card(page: Page, card_number: str):
    page.get_by_test_id("payment-method").select_option(label="Credit Card")
    page.get_by_test_id("credit_card_number").fill(card_number)
    page.get_by_test_id("expiration_date").fill(CARD_EXPIRATION)
    page.get_by_test_id("cvv").fill(CARD_CVV)
    page.get_by_test_id("card_holder_name").fill(CARD_HOLDER)


def test_ct01_login_com_formulario_vazio(page: Page):
    page.goto(LOGIN_URL)
    page.get_by_test_id("login-submit").click()

    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/auth/login"))


def test_ct02_login_apenas_com_senha_preenchida(page: Page):
    login(page, email="", password=USER_PASSWORD)

    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_have_count(0)
    expect(page).to_have_url(re.compile(r"/auth/login"))


def test_ct03_login_com_senha_incorreta(page: Page):
    login(page, password=WRONG_PASSWORD)

    expect(page.get_by_text("Invalid email or password")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/auth/login"))
    expect(page.get_by_test_id("nav-sign-in")).to_be_visible()
    expect(page.get_by_test_id("nav-menu")).to_have_count(0)


def test_ct04_checkout_sem_autenticacao_solicita_credenciais(page: Page):
    add_product_to_cart(page)
    page.goto(CHECKOUT_URL)
    page.get_by_test_id("proceed-1").click()

    expect(page.get_by_test_id("email")).to_be_visible()
    expect(page.get_by_test_id("password")).to_be_visible()
    expect(page.get_by_test_id("login-submit")).to_be_visible()


def test_ct05_autenticacao_no_checkout_permite_prosseguir(page: Page):
    add_product_to_cart(page)
    page.goto(CHECKOUT_URL)
    page.get_by_test_id("proceed-1").click()
    page.get_by_test_id("email").fill(USER_EMAIL)
    page.get_by_test_id("password").fill(USER_PASSWORD)
    page.get_by_test_id("login-submit").click()

    expect(page.get_by_text(re.compile("already logged in"))).to_be_visible()
    page.get_by_test_id("proceed-2").click()
    expect(page.get_by_test_id("street")).to_be_visible()


def test_ct06_login_com_conta_de_demonstracao(page: Page):
    login(page)

    expect(page).to_have_url(re.compile(r"/account$"))
    expect(page.get_by_test_id("page-title")).to_have_text("My account")
    expect(page.get_by_test_id("nav-menu")).to_contain_text(USER_NAME)


def test_ct07_endereco_com_campos_obrigatorios_vazios(page: Page):
    go_to_address_step(page)
    fill_address(page, {field: "" for field in ADDRESS})

    expect(page.get_by_test_id("proceed-3")).to_be_disabled()
    expect(page.get_by_test_id("payment-method")).to_have_count(0)


def test_ct08_endereco_apenas_com_cep_vazio(page: Page):
    go_to_address_step(page)
    fill_address(page, {**ADDRESS, "postal_code": ""})

    expect(page.get_by_test_id("proceed-3")).to_be_disabled()


def test_ct09_endereco_completo_permite_avancar_para_pagamento(page: Page):
    go_to_address_step(page)
    fill_address(page, ADDRESS)

    expect(page.get_by_test_id("proceed-3")).to_be_enabled()
    page.get_by_test_id("proceed-3").click()
    expect(page.get_by_test_id("payment-method")).to_be_visible()


def test_ct10_pagamento_com_cartao_valido_e_confirmacao_do_pedido(page: Page):
    go_to_payment_step(page)
    fill_credit_card(page, CARD_NUMBER)

    page.get_by_test_id("finish").click()
    expect(page.get_by_test_id("payment-success-message")).to_have_text("Payment was successful")

    page.get_by_test_id("finish").click()
    expect(
        page.get_by_text(re.compile(r"Thanks for your order! Your invoice number is INV-\d+"))
    ).to_be_visible()


def test_ct11_pagamento_com_numero_de_cartao_invalido(page: Page):
    go_to_payment_step(page)
    fill_credit_card(page, INVALID_CARD_NUMBER)

    expect(page.get_by_test_id("finish")).to_be_disabled()
    expect(page.get_by_text("Payment was successful")).to_have_count(0)
