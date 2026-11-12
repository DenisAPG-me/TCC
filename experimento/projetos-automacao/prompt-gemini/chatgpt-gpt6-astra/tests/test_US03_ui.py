from datetime import date
import re
import sys

import pytest
from playwright.sync_api import Page, expect


BASE_URL = "https://practicesoftwaretesting.com/"
EMAIL = "customer@practicesoftwaretesting.com"
PASSWORD = "welcome01"
WRONG_PASSWORD = "senha-incorreta-CT02!"
USER_NAME = "Jane Doe"

TIMEOUT_MS = 15_000
expect.set_options(timeout=TIMEOUT_MS)

ADDRESS = {
    "Country": "Brazil",
    "Postal code": "01310-100",
    "Number": "100",
    "Street": "Avenida Paulista",
    "City": "Sao Paulo",
    "State": "Sao Paulo",
}

CARD_NUMBER = "4111111111111111"
CARD_CVV = "123"
CARD_EXPIRATION = f"12/{date.today().year + 3}"


def visit(page: Page, path: str) -> None:
    # O pytest-playwright aplica --base-url ao contexto quando informado.
    page.set_default_timeout(TIMEOUT_MS)
    configured_base_url = page.context.base_url
    base_url = configured_base_url or BASE_URL
    page.goto(
        f"{base_url.rstrip('/')}/{path.lstrip('/')}",
        wait_until="domcontentloaded",
    )


def login(page: Page) -> None:
    visit(page, "/auth/login")
    page.get_by_label("Email", exact=True).fill(EMAIL)
    page.get_by_label("Password", exact=True).fill(PASSWORD)
    page.get_by_role("button", name="Login", exact=True).click()
    expect(
        page.get_by_role("heading", name="My account", exact=True)
    ).to_be_visible()
    expect(page.get_by_test_id("user-menu")).to_contain_text(USER_NAME)


def add_product(page: Page) -> None:
    visit(page, "/")
    product = page.get_by_test_id("product-card").first
    expect(product).to_be_visible()
    product.click()
    page.get_by_role("button", name="Add to cart", exact=True).click()
    expect(page.get_by_test_id("cart-quantity")).to_have_text("1")


def open_checkout(page: Page) -> None:
    visit(page, "/checkout")
    expect(page.get_by_test_id("cart-item")).to_have_count(1)
    page.get_by_role(
        "button", name="Proceed to checkout", exact=True
    ).click()


def reach_address(page: Page) -> None:
    login(page)
    add_product(page)
    open_checkout(page)
    page.get_by_role("button", name="Continue", exact=True).click()
    expect(page.get_by_test_id("checkout-address")).to_be_visible()


def fill_address(page: Page, empty_fields=()) -> None:
    address = page.get_by_test_id("checkout-address")
    empty_fields = set(empty_fields)
    for label, value in ADDRESS.items():
        address.get_by_label(label, exact=True).fill(
            "" if label in empty_fields else value
        )


def assert_address_blocked(page: Page) -> None:
    address = page.get_by_test_id("checkout-address")
    address.get_by_role(
        "button", name="Proceed to payment", exact=True
    ).click()
    expect(address).to_be_visible()
    expect(page.get_by_test_id("checkout-payment")).to_be_hidden()
    expect(
        address.get_by_role(
            "button", name="Proceed to payment", exact=True
        )
    ).to_be_visible()


def check_single_missing_field(page: Page, field: str) -> None:
    reach_address(page)
    fill_address(page, empty_fields=(field,))
    expect(
        page.get_by_test_id("checkout-address").get_by_label(
            field, exact=True
        )
    ).to_have_value("")
    assert_address_blocked(page)


def advance_to_payment(page: Page) -> None:
    address = page.get_by_test_id("checkout-address")
    address.get_by_role(
        "button", name="Proceed to payment", exact=True
    ).click()
    expect(page.get_by_test_id("checkout-payment")).to_be_visible()
    expect(address).to_be_hidden()


def reach_payment(page: Page) -> None:
    reach_address(page)
    fill_address(page)
    advance_to_payment(page)


def pay_by_credit_card(page: Page) -> None:
    payment = page.get_by_test_id("checkout-payment")
    payment.get_by_label("Payment method", exact=True).select_option(
        label="Credit card"
    )
    payment.get_by_label("Card holder name", exact=True).fill(USER_NAME)
    payment.get_by_label("Card number", exact=True).fill(CARD_NUMBER)
    payment.get_by_label("Expiration date", exact=True).fill(
        CARD_EXPIRATION
    )
    payment.get_by_label("CVV", exact=True).fill(CARD_CVV)
    payment.get_by_role(
        "button", name="Confirm payment", exact=True
    ).click()
    expect(
        page.get_by_text("Payment was successful", exact=True)
    ).to_be_visible()


def test_CT01_login_formulario_vazio(page: Page) -> None:
    visit(page, "/auth/login")
    page.get_by_label("Email", exact=True).fill("")
    page.get_by_label("Password", exact=True).fill("")
    page.get_by_role("button", name="Login", exact=True).click()

    expect(
        page.get_by_text("Email is required", exact=True)
    ).to_be_visible()
    expect(
        page.get_by_text("Password is required", exact=True)
    ).to_be_visible()


def test_CT02_login_senha_incorreta_sem_sessao(page: Page) -> None:
    visit(page, "/auth/login")
    page.get_by_label("Email", exact=True).fill(EMAIL)
    page.get_by_label("Password", exact=True).fill(WRONG_PASSWORD)
    page.get_by_role("button", name="Login", exact=True).click()

    expect(
        page.get_by_text("Invalid email or password", exact=True)
    ).to_be_visible()
    expect(page).to_have_url(re.compile(r"/auth/login/?(?:[?#].*)?$"))
    expect(page.get_by_test_id("user-menu")).to_be_hidden()
    expect(
        page.get_by_role("link", name="Sign in", exact=True)
    ).to_be_visible()

    visit(page, "/account")
    expect(page).to_have_url(re.compile(r"/auth/login/?(?:[?#].*)?$"))
    expect(page.get_by_label("Email", exact=True)).to_be_visible()
    expect(page.get_by_label("Password", exact=True)).to_be_visible()
    expect(
        page.get_by_role("heading", name="My account", exact=True)
    ).to_be_hidden()


def test_CT03_checkout_solicita_autenticacao(page: Page) -> None:
    add_product(page)
    open_checkout(page)

    login_step = page.get_by_test_id("checkout-login")
    expect(login_step).to_be_visible()
    expect(login_step.get_by_label("Email", exact=True)).to_be_visible()
    expect(
        login_step.get_by_label("Password", exact=True)
    ).to_be_visible()
    expect(page.get_by_test_id("checkout-payment")).to_be_hidden()


def test_CT04_login_valido_exibe_conta_e_nome(page: Page) -> None:
    login(page)


def test_CT05_endereco_todos_obrigatorios_vazios(page: Page) -> None:
    reach_address(page)
    fill_address(page, empty_fields=ADDRESS.keys())
    assert_address_blocked(page)


def test_CT06_endereco_sem_pais(page: Page) -> None:
    check_single_missing_field(page, "Country")


def test_CT07_endereco_sem_cep(page: Page) -> None:
    check_single_missing_field(page, "Postal code")


def test_CT08_endereco_sem_numero(page: Page) -> None:
    check_single_missing_field(page, "Number")


def test_CT09_endereco_sem_rua(page: Page) -> None:
    check_single_missing_field(page, "Street")


def test_CT10_endereco_sem_cidade(page: Page) -> None:
    check_single_missing_field(page, "City")


def test_CT11_endereco_sem_estado(page: Page) -> None:
    check_single_missing_field(page, "State")


def test_CT12_corrigir_endereco_permite_avancar(page: Page) -> None:
    reach_address(page)
    fill_address(page, empty_fields=ADDRESS.keys())
    assert_address_blocked(page)

    fill_address(page)
    advance_to_payment(page)


def test_CT13_pagamento_cartao_ficticio_valido(page: Page) -> None:
    reach_payment(page)
    pay_by_credit_card(page)


def test_CT14_confirmacao_pedido_com_numero_fatura(page: Page) -> None:
    reach_payment(page)
    pay_by_credit_card(page)

    page.get_by_role(
        "button", name="Confirm order", exact=True
    ).click()

    confirmation = page.get_by_test_id("order-confirmation")
    expect(confirmation).to_be_visible()
    expect(confirmation).to_contain_text(
        re.compile(
            r"Thanks for your order!\s+"
            r"Your invoice number is INV-[^\s.]+"
        )
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))
