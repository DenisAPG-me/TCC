import re
from datetime import date
from urllib.parse import urljoin

import pytest
from playwright.sync_api import expect, sync_playwright


BASE_URL = "https://practicesoftwaretesting.com/"

# Valores fornecidos explicitamente pela User Story.
DEMO_EMAIL = "customer@practicesoftwaretesting.com"
DEMO_PASSWORD = "welcome01"

EXPECTED_MESSAGES = {
    "email_required": "Email is required",
    "password_required": "Password is required",
    "invalid_login": "Invalid email or password",
    "account": "My account",
    "payment_success": "Payment was successful",
}

# Detalhes inferidos, centralizados para eventual ajuste.
ROUTES = {
    "login": "/auth/login",
    "account": "/account",
    "checkout": "/checkout",
}

UI = {
    "test_id_attribute": "data-test",
    "product_cards_css": '[data-test^="product-"]',
    "user_menu": "nav-menu",
    "cart_quantity": "cart-quantity",
    "cart_next": "proceed-1",
    "authentication_next": "proceed-2",
    "address_next": "proceed-3",
    "email": "Email",
    "password": "Password",
    "login_button": "Login",
    "sign_in_link": "Sign in",
    "add_to_cart": "Add to cart",
    "payment_method": "Payment method",
    "credit_card_option": "Credit Card",
    "card_number": "Credit card number",
    "expiration": "Expiration date",
    "cvv": "CVV",
    "card_holder": "Card holder name",
    "confirm_payment": "Confirm",
    "confirm_order": "Confirm order",
}

EXPECTED_USER_NAME = "Jane Doe"
WRONG_PASSWORD = "SenhaIncorreta_CT002!2026"

ADDRESS_LABELS = {
    "country": "Country",
    "postal_code": "Postal code",
    "number": "Number",
    "street": "Street",
    "city": "City",
    "state": "State",
}

ADDRESS_VALUES = {
    "country": "Brazil",
    "postal_code": "01310-100",
    "number": "1000",
    "street": "Avenida Paulista",
    "city": "Sao Paulo",
    "state": "Sao Paulo",
}

CARD_VALUES = {
    "number": "4111111111111111",
    "expiration": f"12/{date.today().year + 3}",
    "cvv": "123",
    "holder": EXPECTED_USER_NAME,
}

INVOICE_MESSAGE_PATTERN = re.compile(
    r"^Thanks for your order! Your invoice number is INV-\S+$"
)

ACTION_TIMEOUT_MS = 15_000
NAVIGATION_TIMEOUT_MS = 30_000
ASSERTION_TIMEOUT_MS = 15_000


def absolute_url(route):
    return urljoin(BASE_URL, route)


def route_pattern(route):
    return re.compile(
        re.escape(absolute_url(route)) + r"/?(?:[?#].*)?$"
    )


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        playwright.selectors.set_test_id_attribute(
            UI["test_id_attribute"]
        )
        expect.set_options(timeout=ASSERTION_TIMEOUT_MS)
        instance = playwright.chromium.launch(headless=True)
        try:
            yield instance
        finally:
            instance.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(locale="en-US")
    try:
        current_page = context.new_page()
        current_page.set_default_timeout(ACTION_TIMEOUT_MS)
        current_page.set_default_navigation_timeout(
            NAVIGATION_TIMEOUT_MS
        )
        yield current_page
    finally:
        context.close()


def open_login(page):
    page.goto(
        absolute_url(ROUTES["login"]),
        wait_until="domcontentloaded",
    )
    expect(page.get_by_label(UI["email"], exact=True)).to_be_visible()
    expect(
        page.get_by_label(UI["password"], exact=True)
    ).to_be_visible()


def submit_login(page, email, password):
    page.get_by_label(UI["email"], exact=True).fill(email)
    page.get_by_label(UI["password"], exact=True).fill(password)
    page.get_by_role(
        "button", name=UI["login_button"], exact=True
    ).click()


def assert_account_visible(page):
    expect(page).to_have_url(route_pattern(ROUTES["account"]))
    expect(
        page.get_by_role(
            "heading",
            name=EXPECTED_MESSAGES["account"],
            exact=True,
        )
    ).to_be_visible()
    menu = page.get_by_test_id(UI["user_menu"])
    expect(menu).to_be_visible()
    expect(menu).to_have_text(EXPECTED_USER_NAME)


def login_demo_account(page):
    open_login(page)
    submit_login(page, DEMO_EMAIL, DEMO_PASSWORD)
    assert_account_visible(page)


def add_one_product_and_open_checkout(page):
    page.goto(BASE_URL, wait_until="domcontentloaded")
    product = page.locator(UI["product_cards_css"]).first
    expect(product).to_be_visible()
    product.click()

    add_button = page.get_by_role(
        "button", name=UI["add_to_cart"], exact=True
    )
    expect(add_button).to_be_enabled()
    add_button.click()

    expect(
        page.get_by_test_id(UI["cart_quantity"])
    ).to_have_text("1")

    page.goto(
        absolute_url(ROUTES["checkout"]),
        wait_until="domcontentloaded",
    )
    expect(page.get_by_test_id(UI["cart_next"])).to_be_visible()


def address_field(page, field_name):
    return page.get_by_label(
        ADDRESS_LABELS[field_name], exact=True
    )


def payment_method(page):
    return page.get_by_label(UI["payment_method"], exact=True)


def prepare_address_step(page):
    login_demo_account(page)
    add_one_product_and_open_checkout(page)
    page.get_by_test_id(UI["cart_next"]).click()
    page.get_by_test_id(UI["authentication_next"]).click()

    for field_name in ADDRESS_LABELS:
        expect(address_field(page, field_name)).to_be_visible()

    expect(payment_method(page)).not_to_be_visible()


def fill_address(page, values):
    for field_name in ADDRESS_LABELS:
        address_field(page, field_name).fill(values[field_name])


def advance_from_address(page):
    button = page.get_by_test_id(UI["address_next"])
    expect(button).to_be_enabled()
    button.click()


def assert_address_step_retained(page):
    for field_name in ADDRESS_LABELS:
        expect(address_field(page, field_name)).to_be_visible()

    expect(page.get_by_test_id(UI["address_next"])).to_be_visible()
    expect(payment_method(page)).not_to_be_visible()


def prepare_payment_step(page):
    prepare_address_step(page)
    fill_address(page, ADDRESS_VALUES)
    advance_from_address(page)
    expect(payment_method(page)).to_be_visible()


def test_CT001_enviar_login_vazio(page):
    open_login(page)
    submit_login(page, "", "")

    expect(
        page.get_by_text(
            EXPECTED_MESSAGES["email_required"], exact=True
        )
    ).to_be_visible()
    expect(
        page.get_by_text(
            EXPECTED_MESSAGES["password_required"], exact=True
        )
    ).to_be_visible()


def test_CT002_rejeitar_senha_incorreta(page):
    open_login(page)
    submit_login(page, DEMO_EMAIL, WRONG_PASSWORD)

    expect(
        page.get_by_text(
            EXPECTED_MESSAGES["invalid_login"], exact=True
        )
    ).to_be_visible()
    expect(page).to_have_url(route_pattern(ROUTES["login"]))
    expect(
        page.get_by_role(
            "link", name=UI["sign_in_link"], exact=True
        )
    ).to_be_visible()
    expect(page.get_by_test_id(UI["user_menu"])).not_to_be_visible()
    expect(
        page.get_by_label(UI["password"], exact=True)
    ).to_be_visible()


def test_CT003_exigir_autenticacao_no_checkout(page):
    add_one_product_and_open_checkout(page)
    page.get_by_test_id(UI["cart_next"]).click()

    expect(page.get_by_label(UI["email"], exact=True)).to_be_visible()
    expect(
        page.get_by_label(UI["password"], exact=True)
    ).to_be_visible()
    expect(
        page.get_by_role(
            "button", name=UI["login_button"], exact=True
        )
    ).to_be_visible()
    expect(payment_method(page)).not_to_be_visible()


def test_CT004_entrar_com_conta_de_demonstracao(page):
    open_login(page)
    submit_login(page, DEMO_EMAIL, DEMO_PASSWORD)

    assert_account_visible(page)


def test_CT005_validar_campos_obrigatorios_do_endereco(page):
    prepare_address_step(page)

    empty_address = {
        field_name: "" for field_name in ADDRESS_LABELS
    }
    fill_address(page, empty_address)
    advance_from_address(page)
    assert_address_step_retained(page)

    for field_name in ADDRESS_LABELS:
        expect(address_field(page, field_name)).to_have_value("")

    # Cada tentativa deixa exatamente um campo obrigatório vazio.
    # O laço pertence a um único caso, sem parametrização do pytest.
    for missing_field in ADDRESS_LABELS:
        incomplete_address = dict(ADDRESS_VALUES)
        incomplete_address[missing_field] = ""
        fill_address(page, incomplete_address)

        advance_from_address(page)
        assert_address_step_retained(page)
        expect(
            address_field(page, missing_field)
        ).to_have_value("")

    fill_address(page, ADDRESS_VALUES)
    advance_from_address(page)
    expect(payment_method(page)).to_be_visible()


def test_CT006_pagar_com_cartao_e_confirmar_pedido(page):
    prepare_payment_step(page)

    payment_method(page).select_option(
        label=UI["credit_card_option"]
    )
    expect(
        payment_method(page).locator("option:checked")
    ).to_have_text(UI["credit_card_option"])

    page.get_by_label(UI["card_number"], exact=True).fill(
        CARD_VALUES["number"]
    )
    page.get_by_label(UI["expiration"], exact=True).fill(
        CARD_VALUES["expiration"]
    )
    page.get_by_label(UI["cvv"], exact=True).fill(
        CARD_VALUES["cvv"]
    )
    page.get_by_label(UI["card_holder"], exact=True).fill(
        CARD_VALUES["holder"]
    )

    page.get_by_role(
        "button", name=UI["confirm_payment"], exact=True
    ).click()

    expect(
        page.get_by_text(
            EXPECTED_MESSAGES["payment_success"], exact=True
        )
    ).to_be_visible()

    confirm_order = page.get_by_role(
        "button", name=UI["confirm_order"], exact=True
    )
    expect(confirm_order).to_be_enabled()
    confirm_order.click()

    confirmation = page.get_by_text(INVOICE_MESSAGE_PATTERN)
    expect(confirmation).to_be_visible()
    expect(confirmation).to_have_text(INVOICE_MESSAGE_PATTERN)
