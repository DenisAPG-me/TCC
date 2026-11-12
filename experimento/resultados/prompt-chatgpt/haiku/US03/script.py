import re

import pytest
from playwright.sync_api import Browser, Page, expect, sync_playwright

BASE_URL = "https://practicesoftwaretesting.com/"
DEMO_EMAIL = "customer@practicesoftwaretesting.com"
DEMO_PASSWORD = "welcome01"
WRONG_PASSWORD = "senha-incorreta-123"
DEMO_USER_NAME = "Jane Doe"
COUNTRY = "Canada"
ADDRESS_DATA = {
    "Street": "Main Street 1",
    "House number": "100",
    "Postcode": "12345",
    "City": "Springfield",
    "State": "Illinois",
}
PAYMENT_METHOD = "Credit Card"
CARD_DATA = {
    "Card number": "4111 1111 1111 1111",
    "Expiry date": "12/30",
    "CVV": "123",
    "Card holder name": "Test Customer",
}
PRODUCT_CARD_SELECTOR = ".card"
TIMEOUT_MS = 15000

EMAIL_LABEL = re.compile(r"E-?mail", re.IGNORECASE)
PASSWORD_LABEL = re.compile(r"Password", re.IGNORECASE)
SIGN_IN_LINK = re.compile(r"Sign in", re.IGNORECASE)
LOGIN_BUTTON = re.compile(r"^Login$", re.IGNORECASE)
CART_LINK = re.compile(r"Cart", re.IGNORECASE)
ADD_TO_CART_BUTTON = re.compile(r"Add to cart", re.IGNORECASE)
PROCEED_CHECKOUT_BUTTON = re.compile(r"Proceed to checkout", re.IGNORECASE)
PROCEED_PAYMENT_BUTTON = re.compile(r"Proceed to payment", re.IGNORECASE)
PAYMENT_CONFIRM_BUTTON = re.compile(r"Confirm payment", re.IGNORECASE)
ORDER_CONFIRM_BUTTON = re.compile(r"Confirm order", re.IGNORECASE)
MY_ACCOUNT_HEADING = re.compile(r"My account", re.IGNORECASE)
INVOICE_MESSAGE = re.compile(r"Thanks for your order! Your invoice number is INV-\S+")


@pytest.fixture(scope="session")
def chromium_browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def web_page(chromium_browser: Browser):
    context = chromium_browser.new_context()
    context.set_default_timeout(TIMEOUT_MS)
    page = context.new_page()
    yield page
    context.close()


def open_home(page: Page) -> None:
    page.goto(BASE_URL)
    expect(page.get_by_role("link", name=SIGN_IN_LINK)).to_be_visible()


def go_to_login(page: Page) -> None:
    open_home(page)
    page.get_by_role("link", name=SIGN_IN_LINK).click()
    expect(page.get_by_label(PASSWORD_LABEL)).to_be_visible()


def submit_login(page: Page, email: str, password: str) -> None:
    page.get_by_label(EMAIL_LABEL).fill(email)
    page.get_by_label(PASSWORD_LABEL).fill(password)
    page.get_by_role("button", name=LOGIN_BUTTON).click()


def add_first_product_to_cart(page: Page) -> None:
    open_home(page)
    page.locator(PRODUCT_CARD_SELECTOR).first.click()
    page.get_by_role("button", name=ADD_TO_CART_BUTTON).click()


def go_to_checkout_from_cart(page: Page) -> None:
    add_first_product_to_cart(page)
    page.get_by_role("link", name=CART_LINK).click()
    page.get_by_role("button", name=PROCEED_CHECKOUT_BUTTON).click()


def reach_address_step(page: Page) -> None:
    go_to_checkout_from_cart(page)
    submit_login(page, DEMO_EMAIL, DEMO_PASSWORD)
    expect(page.get_by_label("Street", exact=True)).to_be_visible()


def fill_address(page: Page, omit: str = "") -> None:
    page.get_by_label("Country", exact=True).select_option(label=COUNTRY)
    for label, value in ADDRESS_DATA.items():
        if label != omit:
            page.get_by_label(label, exact=True).fill(value)


def reach_payment_step(page: Page) -> None:
    reach_address_step(page)
    fill_address(page)
    page.get_by_role("button", name=PROCEED_PAYMENT_BUTTON).click()
    expect(page.get_by_label("Payment method", exact=True)).to_be_visible()


def choose_credit_card(page: Page) -> None:
    page.get_by_label("Payment method", exact=True).select_option(label=PAYMENT_METHOD)


def fill_card(page: Page) -> None:
    for label, value in CARD_DATA.items():
        page.get_by_label(label, exact=True).fill(value)


def test_CT001_login_formulario_vazio_exibe_mensagens_obrigatorias(web_page: Page) -> None:
    go_to_login(web_page)
    web_page.get_by_role("button", name=LOGIN_BUTTON).click()
    expect(web_page.get_by_text("Email is required")).to_be_visible()
    expect(web_page.get_by_text("Password is required")).to_be_visible()


def test_CT002_login_somente_email_exibe_senha_obrigatoria(web_page: Page) -> None:
    go_to_login(web_page)
    web_page.get_by_label(EMAIL_LABEL).fill(DEMO_EMAIL)
    web_page.get_by_role("button", name=LOGIN_BUTTON).click()
    expect(web_page.get_by_text("Password is required")).to_be_visible()
    expect(web_page.get_by_text("Email is required")).to_have_count(0)


def test_CT003_login_senha_incorreta_nao_cria_sessao(web_page: Page) -> None:
    go_to_login(web_page)
    submit_login(web_page, DEMO_EMAIL, WRONG_PASSWORD)
    expect(web_page.get_by_text("Invalid email or password")).to_be_visible()
    expect(web_page.get_by_label(PASSWORD_LABEL)).to_be_visible()
    expect(web_page.get_by_role("heading", name=MY_ACCOUNT_HEADING)).to_have_count(0)
    expect(web_page.get_by_role("navigation").get_by_text(DEMO_USER_NAME)).to_have_count(0)


def test_CT004_checkout_sem_autenticacao_exige_login(web_page: Page) -> None:
    go_to_checkout_from_cart(web_page)
    expect(web_page.get_by_label(EMAIL_LABEL)).to_be_visible()
    expect(web_page.get_by_label(PASSWORD_LABEL)).to_be_visible()


def test_CT005_login_valido_exibe_my_account_com_nome_no_menu(web_page: Page) -> None:
    go_to_login(web_page)
    submit_login(web_page, DEMO_EMAIL, DEMO_PASSWORD)
    expect(web_page.get_by_role("heading", name=MY_ACCOUNT_HEADING)).to_be_visible()
    expect(web_page.get_by_role("navigation").get_by_text(DEMO_USER_NAME)).to_be_visible()


def test_CT006_endereco_campos_vazios_nao_avanca_para_pagamento(web_page: Page) -> None:
    reach_address_step(web_page)
    web_page.get_by_role("button", name=PROCEED_PAYMENT_BUTTON).click()
    expect(web_page.get_by_label("Payment method", exact=True)).to_have_count(0)
    expect(web_page.get_by_label("Street", exact=True)).to_be_visible()


def test_CT007_endereco_sem_estado_nao_avanca_para_pagamento(web_page: Page) -> None:
    reach_address_step(web_page)
    fill_address(web_page, omit="State")
    web_page.get_by_role("button", name=PROCEED_PAYMENT_BUTTON).click()
    expect(web_page.get_by_label("Payment method", exact=True)).to_have_count(0)
    expect(web_page.get_by_label("State", exact=True)).to_be_visible()


def test_CT008_endereco_completo_avanca_para_pagamento(web_page: Page) -> None:
    reach_address_step(web_page)
    fill_address(web_page)
    web_page.get_by_role("button", name=PROCEED_PAYMENT_BUTTON).click()
    expect(web_page.get_by_label("Payment method", exact=True)).to_be_visible()


def test_CT009_pagamento_cartao_credito_dados_validos_exibe_sucesso(web_page: Page) -> None:
    reach_payment_step(web_page)
    choose_credit_card(web_page)
    fill_card(web_page)
    web_page.get_by_role("button", name=PAYMENT_CONFIRM_BUTTON).click()
    expect(web_page.get_by_text("Payment was successful")).to_be_visible()


def test_CT010_confirmar_pedido_exibe_numero_da_fatura(web_page: Page) -> None:
    reach_payment_step(web_page)
    choose_credit_card(web_page)
    fill_card(web_page)
    web_page.get_by_role("button", name=PAYMENT_CONFIRM_BUTTON).click()
    expect(web_page.get_by_text("Payment was successful")).to_be_visible()
    web_page.get_by_role("button", name=ORDER_CONFIRM_BUTTON).click()
    expect(web_page.get_by_text(INVOICE_MESSAGE)).to_be_visible()


def test_CT011_pagamento_sem_dados_do_cartao_nao_exibe_sucesso(web_page: Page) -> None:
    reach_payment_step(web_page)
    choose_credit_card(web_page)
    web_page.get_by_role("button", name=PAYMENT_CONFIRM_BUTTON).click()
    expect(web_page.get_by_text("Payment was successful")).to_have_count(0)
    expect(web_page.get_by_label("Card number", exact=True)).to_be_visible()
