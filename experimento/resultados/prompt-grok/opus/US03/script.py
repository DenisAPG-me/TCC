import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"
DEMO_EMAIL = "customer@practicesoftwaretesting.com"
DEMO_PASSWORD = "welcome01"
WRONG_PASSWORD = "wrongPassword123"

ADDRESS = {
    "country": "Netherlands",
    "postal_code": "1234 AB",
    "house_number": "10",
    "street": "Test Street",
    "city": "Amsterdam",
    "state": "Noord-Holland",
}

CARD = {
    "credit_card_number": "0000-0000-0000-0000",
    "expiration_date": "12/2030",
    "cvv": "123",
    "card_holder_name": "Jane Doe",
}


@pytest.fixture(scope="session", autouse=True)
def _configure_test_id(playwright):
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture
def root(base_url):
    return (base_url or BASE_URL).rstrip("/")


def open_login(page: Page, root: str):
    page.goto(f"{root}/auth/login")
    expect(page.get_by_test_id("email")).to_be_visible()


def submit_login(page: Page, email: str, password: str):
    if email:
        page.get_by_test_id("email").fill(email)
    if password:
        page.get_by_test_id("password").fill(password)
    page.get_by_test_id("login-submit").click()


def login(page: Page, root: str):
    open_login(page, root)
    submit_login(page, DEMO_EMAIL, DEMO_PASSWORD)
    expect(page.get_by_role("heading", name="My account")).to_be_visible()


def add_product_to_cart(page: Page, root: str):
    page.goto(root)
    page.locator('[data-test^="product-"]').first.click()
    page.get_by_test_id("add-to-cart").click()
    expect(page.get_by_test_id("cart-quantity")).to_have_text("1")


def open_cart(page: Page):
    page.get_by_test_id("nav-cart").click()
    expect(page.get_by_test_id("proceed-1")).to_be_visible()


def go_to_address_step(page: Page, root: str):
    login(page, root)
    add_product_to_cart(page, root)
    open_cart(page)
    page.get_by_test_id("proceed-1").click()
    page.get_by_test_id("proceed-2").click()
    expect(page.get_by_test_id("street")).to_be_visible()


def set_field(page: Page, test_id: str, value: str):
    field = page.get_by_test_id(test_id)
    if field.evaluate("el => el.tagName.toLowerCase()") == "select":
        if value:
            field.select_option(label=value)
    else:
        field.fill(value)


def fill_address(page: Page, overrides: dict | None = None):
    data = {**ADDRESS, **(overrides or {})}
    for test_id, value in data.items():
        set_field(page, test_id, value)


def go_to_payment_step(page: Page, root: str):
    go_to_address_step(page, root)
    fill_address(page)
    page.get_by_test_id("proceed-3").click()
    expect(page.get_by_test_id("payment-method")).to_be_visible()


def assert_not_logged_in(page: Page):
    expect(page.get_by_test_id("nav-sign-in")).to_be_visible()
    expect(page.get_by_test_id("nav-menu")).to_have_count(0)


def test_TC01_login_formulario_vazio(page: Page, root):
    open_login(page, root)
    page.get_by_test_id("login-submit").click()
    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/auth/login"))


def test_TC02_login_apenas_email_senha_vazia(page: Page, root):
    open_login(page, root)
    submit_login(page, DEMO_EMAIL, "")
    expect(page.get_by_text("Password is required")).to_be_visible()
    expect(page.get_by_text("Email is required")).to_have_count(0)
    assert_not_logged_in(page)


def test_TC03_login_senha_incorreta(page: Page, root):
    open_login(page, root)
    submit_login(page, DEMO_EMAIL, WRONG_PASSWORD)
    expect(page.get_by_text("Invalid email or password")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/auth/login"))
    assert_not_logged_in(page)


def test_TC04_checkout_sem_autenticacao_exige_credenciais(page: Page, root):
    add_product_to_cart(page, root)
    open_cart(page)
    page.get_by_test_id("proceed-1").click()
    expect(page.get_by_test_id("email")).to_be_visible()
    expect(page.get_by_test_id("password")).to_be_visible()
    expect(page.get_by_test_id("login-submit")).to_be_visible()


def test_TC05_login_valido_exibe_my_account_e_nome(page: Page, root):
    login(page, root)
    expect(page).to_have_url(re.compile(r"/account"))
    nav_menu = page.get_by_test_id("nav-menu")
    expect(nav_menu).to_be_visible()
    expect(nav_menu).to_have_text(re.compile(r"\S+"))
    expect(page.get_by_test_id("nav-sign-in")).to_have_count(0)


def test_TC06_login_no_checkout_permite_prosseguir(page: Page, root):
    add_product_to_cart(page, root)
    open_cart(page)
    page.get_by_test_id("proceed-1").click()
    submit_login(page, DEMO_EMAIL, DEMO_PASSWORD)
    expect(page.get_by_test_id("nav-menu")).to_be_visible()
    page.get_by_test_id("proceed-2").click()
    expect(page.get_by_test_id("street")).to_be_visible()


def test_TC07_endereco_campos_obrigatorios_vazios(page: Page, root):
    go_to_address_step(page, root)
    fill_address(page, {key: "" for key in ADDRESS})
    expect(page.get_by_test_id("proceed-3")).to_be_disabled()
    expect(page.get_by_test_id("payment-method")).to_have_count(0)


def test_TC08_endereco_sem_cep(page: Page, root):
    go_to_address_step(page, root)
    fill_address(page, {"postal_code": ""})
    expect(page.get_by_test_id("proceed-3")).to_be_disabled()
    expect(page.get_by_test_id("payment-method")).to_have_count(0)


def test_TC09_endereco_completo_avanca_para_pagamento(page: Page, root):
    go_to_address_step(page, root)
    fill_address(page)
    expect(page.get_by_test_id("proceed-3")).to_be_enabled()
    page.get_by_test_id("proceed-3").click()
    expect(page.get_by_test_id("payment-method")).to_be_visible()


def test_TC10_pagamento_cartao_credito_e_confirmacao(page: Page, root):
    go_to_payment_step(page, root)
    page.get_by_test_id("payment-method").select_option(label="Credit Card")
    for test_id, value in CARD.items():
        page.get_by_test_id(test_id).fill(value)
    page.get_by_test_id("finish").click()
    expect(page.get_by_text("Payment was successful")).to_be_visible()
    page.get_by_test_id("finish").click()
    expect(
        page.get_by_text(re.compile(r"Thanks for your order! Your invoice number is INV-\S+"))
    ).to_be_visible()


def test_TC11_cartao_credito_sem_dados_nao_confirma(page: Page, root):
    go_to_payment_step(page, root)
    page.get_by_test_id("payment-method").select_option(label="Credit Card")
    expect(page.get_by_test_id("credit_card_number")).to_be_visible()
    expect(page.get_by_test_id("finish")).to_be_disabled()
    expect(page.get_by_text("Payment was successful")).to_have_count(0)
