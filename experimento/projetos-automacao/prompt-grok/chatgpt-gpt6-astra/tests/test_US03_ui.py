# Arquivo: test_compra.py
# Dependências: pytest, playwright e pytest-playwright.
# Preparação:
#   python -m pip install pytest playwright pytest-playwright
#   python -m playwright install chromium
# Execução:
#   pytest test_compra.py
#
# Todos os contratos de interface abaixo são suposições da User Story.
# Não foram verificados no sistema real.

import re
from datetime import date

from playwright.sync_api import Page, expect


BASE_URL = "https://practicesoftwaretesting.com/"
LOGIN_PATH = "auth/login"

EMAIL = "customer@practicesoftwaretesting.com"
PASSWORD = "welcome01"
WRONG_PASSWORD = "SenhaIncorreta_TC04!"

TIMEOUT_MS = 10_000

TEST_IDS = {
    "user_name": "user-menu-name",
    "product": "product-card",
    "cart_count": "cart-count",
    "address": "address-step",
    "payment": "payment-step",
    "confirmation": "order-confirmation",
}

LABELS = {
    "email": "Email",
    "password": "Password",
    "country": "Country",
    "postal_code": "Postal code",
    "number": "Number",
    "street": "Street",
    "city": "City",
    "state": "State",
    "payment_method": "Payment method",
    "card_number": "Card number",
    "expiration": "Expiration date",
    "cvv": "CVV",
    "cardholder": "Cardholder name",
}

BUTTONS = {
    "login": "Login",
    "add": "Add to cart",
    "checkout": "Proceed to checkout",
    "address_next": "Continue to payment",
    "pay": "Pay",
    "confirm": "Confirm order",
}

ADDRESS = {
    "country": "Brazil",
    "postal_code": "01310-100",
    "number": "1000",
    "street": "Avenida Paulista",
    "city": "São Paulo",
    "state": "São Paulo",
}

CARD_NUMBER = "4111111111111111"
CARD_CVV = "123"
CARDHOLDER = "CLIENTE TESTE"

INVOICE_PATTERN = re.compile(
    r"^Thanks for your order! Your invoice number is "
    r"INV-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$"
)


def open_login(page: Page) -> None:
    page.goto(BASE_URL + LOGIN_PATH)
    expect(page.get_by_label(LABELS["email"], exact=True)).to_be_visible(
        timeout=TIMEOUT_MS
    )
    expect(page.get_by_label(LABELS["password"], exact=True)).to_be_visible()


def submit_login(
    page: Page, email: str = "", password: str = ""
) -> None:
    page.get_by_label(LABELS["email"], exact=True).fill(email)
    page.get_by_label(LABELS["password"], exact=True).fill(password)
    page.get_by_role(
        "button", name=BUTTONS["login"], exact=True
    ).click()


def expect_no_session(page: Page) -> None:
    expect(page.get_by_test_id(TEST_IDS["user_name"])).to_have_count(0)
    # Navegação adicional verifica que o formulário continua acessível
    # sem um estado autenticado observável.
    open_login(page)
    expect(
        page.get_by_role("button", name=BUTTONS["login"], exact=True)
    ).to_be_visible()
    expect(page.get_by_test_id(TEST_IDS["user_name"])).to_have_count(0)


def login_successfully(page: Page) -> None:
    open_login(page)
    submit_login(page, EMAIL, PASSWORD)
    expect(
        page.get_by_role("heading", name="My account", exact=True)
    ).to_be_visible(timeout=TIMEOUT_MS)
    user_name = page.get_by_test_id(TEST_IDS["user_name"])
    expect(user_name).to_be_visible()
    expect(user_name).to_have_text(re.compile(r"\S"))


def add_product_and_start_checkout(page: Page) -> None:
    page.goto(BASE_URL)
    product = page.get_by_test_id(TEST_IDS["product"]).first
    expect(product).to_be_visible(timeout=TIMEOUT_MS)
    product.click()
    page.get_by_role(
        "button", name=BUTTONS["add"], exact=True
    ).click()
    expect(page.get_by_test_id(TEST_IDS["cart_count"])).to_have_text(
        "1", timeout=TIMEOUT_MS
    )
    page.get_by_role("link", name="Cart", exact=True).click()
    page.get_by_role(
        "button", name=BUTTONS["checkout"], exact=True
    ).click()


def reach_address(page: Page) -> None:
    login_successfully(page)
    add_product_and_start_checkout(page)
    expect(page.get_by_test_id(TEST_IDS["address"])).to_be_visible(
        timeout=TIMEOUT_MS
    )


def set_address_field(page: Page, field: str, value: str) -> None:
    step = page.get_by_test_id(TEST_IDS["address"])
    locator = step.get_by_label(LABELS[field], exact=True)
    if field == "country":
        if value:
            locator.select_option(label=value)
        else:
            locator.select_option(value="")
    else:
        locator.fill(value)


def fill_address(page: Page, missing: str = "") -> None:
    for field, value in ADDRESS.items():
        set_address_field(page, field, "" if field == missing else value)


def clear_address(page: Page) -> None:
    for field in ADDRESS:
        set_address_field(page, field, "")


def submit_address(page: Page) -> None:
    page.get_by_test_id(TEST_IDS["address"]).get_by_role(
        "button", name=BUTTONS["address_next"], exact=True
    ).click()


def expect_address_rejected(page: Page, missing_fields) -> None:
    step = page.get_by_test_id(TEST_IDS["address"])
    # Espera a validação ocorrer antes de verificar o bloqueio da etapa.
    for field in missing_fields:
        expect(
            step.get_by_label(LABELS[field], exact=True)
        ).to_have_attribute("aria-invalid", "true", timeout=TIMEOUT_MS)
    expect(step).to_be_visible()
    expect(page.get_by_test_id(TEST_IDS["payment"])).to_be_hidden()


def expect_payment_step(page: Page) -> None:
    expect(page.get_by_test_id(TEST_IDS["payment"])).to_be_visible(
        timeout=TIMEOUT_MS
    )
    expect(page.get_by_test_id(TEST_IDS["address"])).to_be_hidden()


def check_single_missing_address_field(page: Page, field: str) -> None:
    reach_address(page)
    fill_address(page, missing=field)
    submit_address(page)
    expect_address_rejected(page, [field])

    # Corrige somente o campo omitido para verificar que ele era
    # a única informação obrigatória pendente.
    set_address_field(page, field, ADDRESS[field])
    submit_address(page)
    expect_payment_step(page)


def test_TC01_login_vazio(page: Page) -> None:
    open_login(page)
    submit_login(page)
    expect(
        page.get_by_text("Email is required", exact=True)
    ).to_be_visible()
    expect(
        page.get_by_text("Password is required", exact=True)
    ).to_be_visible()


def test_TC02_login_sem_email(page: Page) -> None:
    open_login(page)
    submit_login(page, password=PASSWORD)
    expect(
        page.get_by_text("Email is required", exact=True)
    ).to_be_visible()
    expect_no_session(page)


def test_TC03_login_sem_senha(page: Page) -> None:
    open_login(page)
    submit_login(page, email=EMAIL)
    expect(
        page.get_by_text("Password is required", exact=True)
    ).to_be_visible()
    expect_no_session(page)


def test_TC04_senha_incorreta(page: Page) -> None:
    open_login(page)
    submit_login(page, EMAIL, WRONG_PASSWORD)
    expect(
        page.get_by_text("Invalid email or password", exact=True)
    ).to_be_visible(timeout=TIMEOUT_MS)
    expect_no_session(page)


def test_TC05_checkout_exige_autenticacao(page: Page) -> None:
    add_product_and_start_checkout(page)
    expect(
        page.get_by_label(LABELS["email"], exact=True)
    ).to_be_visible(timeout=TIMEOUT_MS)
    expect(
        page.get_by_label(LABELS["password"], exact=True)
    ).to_be_visible()
    expect(
        page.get_by_role("button", name=BUTTONS["login"], exact=True)
    ).to_be_visible()
    expect(page.get_by_test_id(TEST_IDS["user_name"])).to_have_count(0)


def test_TC06_login_com_sucesso(page: Page) -> None:
    login_successfully(page)


def test_TC07_endereco_totalmente_vazio(page: Page) -> None:
    reach_address(page)
    clear_address(page)
    submit_address(page)
    expect_address_rejected(page, ADDRESS.keys())


def test_TC08_endereco_sem_pais(page: Page) -> None:
    check_single_missing_address_field(page, "country")


def test_TC09_endereco_sem_cep(page: Page) -> None:
    check_single_missing_address_field(page, "postal_code")


def test_TC10_endereco_sem_numero(page: Page) -> None:
    check_single_missing_address_field(page, "number")


def test_TC11_endereco_sem_rua(page: Page) -> None:
    check_single_missing_address_field(page, "street")


def test_TC12_endereco_sem_cidade(page: Page) -> None:
    check_single_missing_address_field(page, "city")


def test_TC13_endereco_sem_estado(page: Page) -> None:
    check_single_missing_address_field(page, "state")


def test_TC14_corrigir_endereco_vazio_e_avancar(page: Page) -> None:
    reach_address(page)
    clear_address(page)
    submit_address(page)
    expect_address_rejected(page, ADDRESS.keys())

    fill_address(page)
    submit_address(page)
    expect_payment_step(page)


def test_TC15_pagar_com_cartao_e_confirmar_pedido(page: Page) -> None:
    reach_address(page)
    fill_address(page)
    submit_address(page)
    expect_payment_step(page)

    payment = page.get_by_test_id(TEST_IDS["payment"])
    payment.get_by_label(
        LABELS["payment_method"], exact=True
    ).select_option(label="Credit Card")

    today = date.today()
    expiration = f"{today.month:02d}/{today.year + 2}"

    payment.get_by_label(
        LABELS["card_number"], exact=True
    ).fill(CARD_NUMBER)
    payment.get_by_label(
        LABELS["expiration"], exact=True
    ).fill(expiration)
    payment.get_by_label(
        LABELS["cvv"], exact=True
    ).fill(CARD_CVV)
    payment.get_by_label(
        LABELS["cardholder"], exact=True
    ).fill(CARDHOLDER)
    payment.get_by_role(
        "button", name=BUTTONS["pay"], exact=True
    ).click()

    expect(
        page.get_by_text("Payment was successful", exact=True)
    ).to_be_visible(timeout=TIMEOUT_MS)

    page.get_by_role(
        "button", name=BUTTONS["confirm"], exact=True
    ).click()

    confirmation = page.get_by_test_id(TEST_IDS["confirmation"])
    expect(confirmation).to_be_visible(timeout=TIMEOUT_MS)
    expect(confirmation).to_have_text(
        INVOICE_PATTERN, timeout=TIMEOUT_MS
    )
