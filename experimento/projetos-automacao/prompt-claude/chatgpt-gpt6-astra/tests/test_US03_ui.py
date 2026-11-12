import re

from playwright.sync_api import Page, expect


BASE_URL = "https://practicesoftwaretesting.com/"
EMAIL = "customer@practicesoftwaretesting.com"
PASSWORD = "welcome01"
WRONG_PASSWORD = "senha-incorreta-CT04!"
EXPECTED_USER_NAME = "Jane Doe"

LOGIN_PATH = "/auth/login"
ACCOUNT_PATH = "/account"
CHECKOUT_PATH = "/checkout"
TIMEOUT_MS = 15_000

ADDRESS = {
    "country": "Brazil",
    "postal_code": "01310-100",
    "number": "100",
    "street": "Avenida Paulista",
    "city": "Sao Paulo",
    "state": "SP",
}

CARD = {
    "number": "4111111111111111",
    "expiration": "12/2035",
    "cvv": "123",
    "holder": "Jane Doe",
}

TEST_IDS = {
    "user_menu": "nav-menu",
    "product": "product-card",
    "add_to_cart": "add-to-cart",
    "cart_quantity": "cart-quantity",
    "cart_item": "cart-item",
    "cart_continue": "proceed-to-checkout",
    "sign_in_panel": "checkout-sign-in",
    "sign_in_continue": "proceed-to-address",
    "address_panel": "checkout-address",
    "address_continue": "proceed-to-payment",
    "country": "country",
    "postal_code": "postal-code",
    "number": "house-number",
    "street": "street",
    "city": "city",
    "state": "state",
    "payment_panel": "checkout-payment",
    "payment_method": "payment-method",
    "card_number": "credit-card-number",
    "card_expiration": "expiration-date",
    "card_cvv": "cvv",
    "card_holder": "card-holder-name",
    "payment_confirm": "confirm-payment",
    "order_confirm": "confirm-order",
}

EMAIL_REQUIRED = "Email is required"
PASSWORD_REQUIRED = "Password is required"
INVALID_LOGIN = "Invalid email or password"
PAYMENT_SUCCESS = "Payment was successful"

LOGIN_URL_PATTERN = re.compile(
    re.escape(BASE_URL.rstrip("/") + LOGIN_PATH)
    + r"/?(?:[?#].*)?$"
)
ACCOUNT_URL_PATTERN = re.compile(
    re.escape(BASE_URL.rstrip("/") + ACCOUNT_PATH)
    + r"/?(?:[?#].*)?$"
)
INVOICE_PATTERN = re.compile(
    r"^Thanks for your order! Your invoice number is INV-\S+$"
)

expect.set_options(timeout=TIMEOUT_MS)


def element(page: Page, key: str):
    return page.get_by_test_id(TEST_IDS[key])


def navigate(page: Page, path: str = "") -> None:
    page.set_default_timeout(TIMEOUT_MS)
    page.set_default_navigation_timeout(TIMEOUT_MS)
    page.goto(
        BASE_URL.rstrip("/") + "/" + path.lstrip("/"),
        wait_until="domcontentloaded",
    )


def open_login(page: Page) -> None:
    navigate(page, LOGIN_PATH)
    expect(page.get_by_label("Email", exact=True)).to_be_visible()
    expect(page.get_by_label("Password", exact=True)).to_be_visible()


def submit_login(page: Page, email: str, password: str) -> None:
    page.get_by_label("Email", exact=True).fill(email)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Login", exact=True).click()


def login(page: Page) -> None:
    open_login(page)
    submit_login(page, EMAIL, PASSWORD)
    expect(page).to_have_url(ACCOUNT_URL_PATTERN)
    expect(
        page.get_by_role("heading", name="My account", exact=True)
    ).to_be_visible()
    expect(element(page, "user_menu")).to_have_text(EXPECTED_USER_NAME)


def add_product_and_open_checkout(page: Page) -> None:
    navigate(page)
    product = element(page, "product").first
    expect(product).to_be_visible()
    product.click()

    element(page, "add_to_cart").click()
    expect(element(page, "cart_quantity")).to_have_text("1")

    navigate(page, CHECKOUT_PATH)
    expect(element(page, "cart_item")).to_have_count(1)
    element(page, "cart_continue").click()


def open_address(page: Page) -> None:
    login(page)
    add_product_and_open_checkout(page)
    expect(element(page, "sign_in_continue")).to_be_visible()
    element(page, "sign_in_continue").click()
    expect(element(page, "address_panel")).to_be_visible()
    expect(element(page, "payment_panel")).to_be_hidden()


def clear_address(page: Page) -> None:
    for field in ADDRESS:
        element(page, field).fill("")
    element(page, "state").press("Tab")


def verify_empty_address_blocks_payment(page: Page) -> None:
    clear_address(page)
    button = element(page, "address_continue")
    expect(button).to_be_visible()

    # Sistemas podem bloquear pelo botão ou validar após o clique.
    if button.is_enabled():
        button.click()
    else:
        expect(button).to_be_disabled()

    expect(element(page, "address_panel")).to_be_visible()
    expect(element(page, "payment_panel")).to_be_hidden()
    for field in ADDRESS:
        expect(element(page, field)).to_have_value("")


def fill_address_and_continue(page: Page) -> None:
    for field, value in ADDRESS.items():
        element(page, field).fill(value)

    button = element(page, "address_continue")
    expect(button).to_be_enabled()
    button.click()

    expect(element(page, "payment_panel")).to_be_visible()
    expect(element(page, "payment_method")).to_be_visible()


def test_ct01_login_vazio(page: Page) -> None:
    open_login(page)
    submit_login(page, "", "")

    expect(page.get_by_text(EMAIL_REQUIRED, exact=True)).to_be_visible()
    expect(page.get_by_text(PASSWORD_REQUIRED, exact=True)).to_be_visible()


def test_ct02_login_sem_email(page: Page) -> None:
    open_login(page)
    submit_login(page, "", PASSWORD)

    expect(page.get_by_text(EMAIL_REQUIRED, exact=True)).to_be_visible()
    expect(page.get_by_text(PASSWORD_REQUIRED, exact=True)).to_be_hidden()


def test_ct03_login_sem_senha(page: Page) -> None:
    open_login(page)
    submit_login(page, EMAIL, "")

    expect(page.get_by_text(PASSWORD_REQUIRED, exact=True)).to_be_visible()
    expect(page.get_by_text(EMAIL_REQUIRED, exact=True)).to_be_hidden()


def test_ct04_senha_incorreta_sem_sessao(page: Page) -> None:
    open_login(page)
    submit_login(page, EMAIL, WRONG_PASSWORD)

    expect(page.get_by_text(INVALID_LOGIN, exact=True)).to_be_visible()
    expect(page).to_have_url(LOGIN_URL_PATTERN)
    expect(page.get_by_role("button", name="Login", exact=True)).to_be_visible()

    navigate(page, ACCOUNT_PATH)
    expect(page).to_have_url(LOGIN_URL_PATTERN)
    expect(page.get_by_label("Email", exact=True)).to_be_visible()
    expect(page.get_by_label("Password", exact=True)).to_be_visible()
    expect(
        page.get_by_role("heading", name="My account", exact=True)
    ).to_be_hidden()


def test_ct05_checkout_exige_login(page: Page) -> None:
    add_product_and_open_checkout(page)

    panel = element(page, "sign_in_panel")
    expect(panel).to_be_visible()
    expect(panel.get_by_label("Email", exact=True)).to_be_visible()
    expect(panel.get_by_label("Password", exact=True)).to_be_visible()
    expect(
        panel.get_by_role("button", name="Login", exact=True)
    ).to_be_visible()


def test_ct06_login_com_credenciais_validas(page: Page) -> None:
    open_login(page)
    submit_login(page, EMAIL, PASSWORD)

    expect(page).to_have_url(ACCOUNT_URL_PATTERN)
    expect(
        page.get_by_role("heading", name="My account", exact=True)
    ).to_be_visible()
    expect(element(page, "user_menu")).to_be_visible()
    expect(element(page, "user_menu")).to_have_text(EXPECTED_USER_NAME)


def test_ct07_endereco_vazio_bloqueia_pagamento(page: Page) -> None:
    open_address(page)
    verify_empty_address_blocks_payment(page)


def test_ct08_endereco_preenchido_libera_pagamento(page: Page) -> None:
    open_address(page)
    verify_empty_address_blocks_payment(page)
    fill_address_and_continue(page)

    expect(element(page, "payment_panel")).to_be_visible()
    expect(element(page, "payment_method")).to_be_enabled()


def test_ct09_compra_com_cartao_de_credito(page: Page) -> None:
    open_address(page)
    fill_address_and_continue(page)

    element(page, "payment_method").select_option(label="Credit Card")
    element(page, "card_number").fill(CARD["number"])
    element(page, "card_expiration").fill(CARD["expiration"])
    element(page, "card_cvv").fill(CARD["cvv"])
    element(page, "card_holder").fill(CARD["holder"])

    payment_button = element(page, "payment_confirm")
    expect(payment_button).to_be_enabled()
    payment_button.click()

    expect(
        page.get_by_text(PAYMENT_SUCCESS, exact=True)
    ).to_be_visible()

    order_button = element(page, "order_confirm")
    expect(order_button).to_be_enabled()
    order_button.click()

    confirmation = page.get_by_text(INVOICE_PATTERN)
    expect(confirmation).to_be_visible()
    expect(confirmation).to_have_text(INVOICE_PATTERN)
