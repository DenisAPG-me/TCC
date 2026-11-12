import re

import pytest
from playwright.sync_api import expect

BASE_URL = "https://practicesoftwaretesting.com"
LOGIN_URL = f"{BASE_URL}/#/auth/login"
DEMO_EMAIL = "customer@practicesoftwaretesting.com"
DEMO_PASSWORD = "welcome01"
WRONG_PASSWORD = "senha-incorreta"
UNREGISTERED_EMAIL = "inexistente@practicesoftwaretesting.com"
USER_NAME = "Jane Doe"
ADDRESS = {
    "Street": "Main Street",
    "City": "New York",
    "State": "NY",
    "Postcode": "10001",
    "Building number": "100",
}
COUNTRY = "United States"
CARD = {"holder": "John Doe", "number": "4111111111111111", "expiry": "12/2030", "cvv": "123"}
INVALID_CARD_NUMBER = "1234567890123456"
EXPIRED_CARD_EXPIRY = "01/2020"
NEXT_STEP_BUTTON = "Proceed to payment"
CONFIRM_BUTTON = "Confirm"
CONFIRM_ORDER_BUTTON = "Confirm order"
INVOICE_TEXT = re.compile(r"Thanks for your order! Your invoice number is INV-")


def _submit_login(page, email, password):
    page.get_by_label("Email address").fill(email)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Login", exact=True).click()


def _login(page, email, password):
    page.goto(LOGIN_URL)
    _submit_login(page, email, password)


def _add_product_to_cart(page):
    page.goto(BASE_URL)
    page.locator('[data-test="product-name"]').first.click()
    page.get_by_role("button", name="Add to cart").click()
    expect(page.get_by_text("Product added to shopping cart.")).to_be_visible()


def _go_to_checkout(page):
    page.locator('[data-test="nav-cart"]').click()
    page.get_by_role("button", name="Proceed to checkout").click()


def _start_checkout_as_customer(page):
    _login(page, DEMO_EMAIL, DEMO_PASSWORD)
    _add_product_to_cart(page)
    _go_to_checkout(page)


def _fill_address(page):
    for label, value in ADDRESS.items():
        page.get_by_label(label).fill(value)
    page.get_by_label("Country").select_option(COUNTRY)


def _proceed_to_payment(page):
    _fill_address(page)
    page.get_by_role("button", name=NEXT_STEP_BUTTON).click()
    expect(page.get_by_label("Payment method")).to_be_visible()


def _fill_credit_card(page, number, expiry):
    page.get_by_label("Payment method").select_option("Credit Card")
    page.get_by_label("Card number").fill(number)
    page.get_by_label(re.compile("expir", re.IGNORECASE)).fill(expiry)
    page.get_by_label("CVV").fill(CARD["cvv"])
    page.get_by_label("Card holder name").fill(CARD["holder"])


def test_CT01_login_vazio_exibe_mensagens_obrigatorias(page):
    page.goto(LOGIN_URL)
    page.get_by_role("button", name="Login", exact=True).click()
    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_be_visible()


def test_CT02_login_somente_com_senha_exibe_erro_de_email(page):
    page.goto(LOGIN_URL)
    page.get_by_label("Password", exact=True).fill(DEMO_PASSWORD)
    page.get_by_role("button", name="Login", exact=True).click()
    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_have_count(0)


def test_CT03_login_somente_com_email_exibe_erro_de_senha(page):
    page.goto(LOGIN_URL)
    page.get_by_label("Email address").fill(DEMO_EMAIL)
    page.get_by_role("button", name="Login", exact=True).click()
    expect(page.get_by_text("Password is required")).to_be_visible()
    expect(page.get_by_text("Email is required")).to_have_count(0)


def test_CT04_login_com_senha_incorreta_exibe_erro_e_mantem_sem_sessao(page):
    _login(page, DEMO_EMAIL, WRONG_PASSWORD)
    expect(page.get_by_text("Invalid email or password")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/auth/login"))
    expect(page.get_by_role("button", name="Login", exact=True)).to_be_visible()


def test_CT05_login_com_email_nao_cadastrado_exibe_erro(page):
    _login(page, UNREGISTERED_EMAIL, DEMO_PASSWORD)
    expect(page.get_by_text("Invalid email or password")).to_be_visible()
    expect(page.get_by_role("button", name="Login", exact=True)).to_be_visible()


def test_CT06_login_valido_exibe_my_account_com_nome_no_menu(page):
    _login(page, DEMO_EMAIL, DEMO_PASSWORD)
    expect(page.get_by_role("navigation").get_by_text(USER_NAME)).to_be_visible()
    page.get_by_role("navigation").get_by_text(USER_NAME).click()
    page.get_by_text("My account", exact=True).click()
    expect(page.get_by_role("heading", name="My account")).to_be_visible()


def test_CT07_checkout_sem_autenticacao_exige_email_e_senha(page):
    _add_product_to_cart(page)
    _go_to_checkout(page)
    expect(page.get_by_label("Email address")).to_be_visible()
    expect(page.get_by_label("Password", exact=True)).to_be_visible()


def test_CT08_endereço_com_campos_obrigatorios_vazios_bloqueia_avanco(page):
    _start_checkout_as_customer(page)
    for label in ADDRESS:
        page.get_by_label(label).fill("")
    page.get_by_label("Country").select_option("")
    page.get_by_role("button", name=NEXT_STEP_BUTTON).click()
    expect(page.get_by_label("Street")).to_be_visible()
    expect(page.get_by_label("Payment method")).to_have_count(0)


def test_CT09_endereco_completo_permite_avancar_para_pagamento(page):
    _start_checkout_as_customer(page)
    _proceed_to_payment(page)


def test_CT10_cep_vazio_isolado_bloqueia_avanco_para_pagamento(page):
    _start_checkout_as_customer(page)
    _fill_address(page)
    page.get_by_label("Postcode").fill("")
    page.get_by_role("button", name=NEXT_STEP_BUTTON).click()
    expect(page.get_by_label("Street")).to_be_visible()
    expect(page.get_by_label("Payment method")).to_have_count(0)


def test_CT11_pagamento_com_cartao_valido_exibe_sucesso(page):
    _start_checkout_as_customer(page)
    _proceed_to_payment(page)
    _fill_credit_card(page, CARD["number"], CARD["expiry"])
    page.get_by_role("button", name=CONFIRM_BUTTON, exact=True).click()
    expect(page.get_by_text("Payment was successful")).to_be_visible()


def test_CT12_confirmacao_do_pedido_exibe_numero_da_fatura(page):
    _start_checkout_as_customer(page)
    _proceed_to_payment(page)
    _fill_credit_card(page, CARD["number"], CARD["expiry"])
    page.get_by_role("button", name=CONFIRM_BUTTON, exact=True).click()
    expect(page.get_by_text("Payment was successful")).to_be_visible()
    page.get_by_role("button", name=CONFIRM_ORDER_BUTTON).click()
    expect(page.get_by_text(INVOICE_TEXT)).to_be_visible()


def test_CT13_cartao_com_numero_invalido_nao_e_aprovado(page):
    _start_checkout_as_customer(page)
    _proceed_to_payment(page)
    _fill_credit_card(page, INVALID_CARD_NUMBER, CARD["expiry"])
    page.get_by_role("button", name=CONFIRM_BUTTON, exact=True).click()
    expect(page.get_by_text("Payment was successful")).to_have_count(0)
    expect(page.get_by_label("Payment method")).to_be_visible()


def test_CT14_cartao_com_validade_expirada_nao_e_aprovado(page):
    _start_checkout_as_customer(page)
    _proceed_to_payment(page)
    _fill_credit_card(page, CARD["number"], EXPIRED_CARD_EXPIRY)
    page.get_by_role("button", name=CONFIRM_BUTTON, exact=True).click()
    expect(page.get_by_text("Payment was successful")).to_have_count(0)


def test_CT15_fluxo_ponta_a_ponta_de_compra_com_cartao(page):
    _add_product_to_cart(page)
    _go_to_checkout(page)
    _submit_login(page, DEMO_EMAIL, DEMO_PASSWORD)
    expect(page.get_by_role("navigation").get_by_text(USER_NAME)).to_be_visible()
    _go_to_checkout(page)
    _proceed_to_payment(page)
    _fill_credit_card(page, CARD["number"], CARD["expiry"])
    page.get_by_role("button", name=CONFIRM_BUTTON, exact=True).click()
    expect(page.get_by_text("Payment was successful")).to_be_visible()
    page.get_by_role("button", name=CONFIRM_ORDER_BUTTON).click()
    expect(page.get_by_text(INVOICE_TEXT)).to_be_visible()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
