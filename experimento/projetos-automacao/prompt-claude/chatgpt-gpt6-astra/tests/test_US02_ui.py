import re
from decimal import Decimal

from playwright.sync_api import Page, Locator, expect


BASE_URL = "https://practicesoftwaretesting.com/"
USERNAME = None
PASSWORD = None

REGULAR_PRODUCT = "Claw Hammer"
RESTRICTED_PRODUCT = "Thor Hammer"
INITIAL_QUANTITY = 3
MINIMUM_QUANTITY = 1

SUCCESS_MESSAGE = "Product added to shopping cart."
RESTRICTION_MESSAGE = "You can only have one Thor Hammer in the cart."

QUANTITY_LABEL = "Quantity"
ADD_BUTTON_NAME = "Add to cart"

CART_LINK_ID = "cart-link"
CART_BADGE_ID = "cart-quantity"
CART_TABLE_ID = "cart-table"
ROW_QUANTITY_ID = "quantity"
UNIT_PRICE_ID = "unit-price"
LINE_TOTAL_ID = "line-total"
CART_TOTAL_ID = "cart-total"

UI_TIMEOUT_MS = 15_000
NAVIGATION_TIMEOUT_MS = 30_000

# Aceita "$12.34" ou "$ 12.34", incluindo espaços nas extremidades.
MONEY_PATTERN = re.compile(r"^\s*\$\s*(\d+\.\d{2})\s*$")


def open_product(page: Page, product_name: str) -> None:
    page.set_default_timeout(UI_TIMEOUT_MS)
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)

    page.goto(BASE_URL, wait_until="domcontentloaded")
    product_link = page.get_by_role(
        "link",
        name=re.compile(re.escape(product_name), re.IGNORECASE),
    )
    expect(product_link).to_have_count(1, timeout=UI_TIMEOUT_MS)
    product_link.click()

    expect(
        page.get_by_label(QUANTITY_LABEL, exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)


def submit_quantity(page: Page, quantity: int) -> None:
    quantity_input = page.get_by_label(QUANTITY_LABEL, exact=True)
    quantity_input.fill(str(quantity))
    expect(quantity_input).to_have_value(str(quantity))

    page.get_by_role(
        "button", name=ADD_BUTTON_NAME, exact=True
    ).click()


def expect_addition_success(page: Page, quantity: int) -> None:
    expect(
        page.get_by_text(SUCCESS_MESSAGE, exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)

    expect(
        page.get_by_test_id(CART_BADGE_ID)
    ).to_have_text(str(quantity), timeout=UI_TIMEOUT_MS)


def open_cart_row(page: Page, product_name: str) -> Locator:
    page.get_by_test_id(CART_LINK_ID).click()

    cart_table = page.get_by_test_id(CART_TABLE_ID)
    expect(cart_table).to_be_visible(timeout=UI_TIMEOUT_MS)

    row = cart_table.get_by_role("row").filter(
        has_text=re.compile(re.escape(product_name))
    )
    expect(row).to_have_count(1, timeout=UI_TIMEOUT_MS)
    expect(row).to_be_visible(timeout=UI_TIMEOUT_MS)
    return row


def prepare_cart(page: Page, product_name: str, quantity: int) -> Locator:
    open_product(page, product_name)
    submit_quantity(page, quantity)
    expect_addition_success(page, quantity)
    return open_cart_row(page, product_name)


def read_money(locator: Locator) -> Decimal:
    expect(locator).to_have_text(MONEY_PATTERN, timeout=UI_TIMEOUT_MS)
    text = locator.inner_text()
    match = MONEY_PATTERN.fullmatch(text)

    if match is None:
        raise ValueError(f"Formato monetário inesperado: {text!r}")

    return Decimal(match.group(1))


def expect_money(locator: Locator, amount: Decimal) -> None:
    formatted_amount = format(amount, ".2f")
    expected_pattern = re.compile(
        r"^\s*\$\s*" + re.escape(formatted_amount) + r"\s*$"
    )
    expect(locator).to_have_text(
        expected_pattern, timeout=UI_TIMEOUT_MS
    )


def test_ct01_adicionar_tres_unidades(page: Page) -> None:
    open_product(page, REGULAR_PRODUCT)
    submit_quantity(page, INITIAL_QUANTITY)

    expect(
        page.get_by_text(SUCCESS_MESSAGE, exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(
        page.get_by_test_id(CART_BADGE_ID)
    ).to_have_text(str(INITIAL_QUANTITY), timeout=UI_TIMEOUT_MS)


def test_ct02_conferir_totais_de_tres_unidades(page: Page) -> None:
    row = prepare_cart(page, REGULAR_PRODUCT, INITIAL_QUANTITY)

    expect(
        row.get_by_test_id(ROW_QUANTITY_ID)
    ).to_have_value(str(INITIAL_QUANTITY), timeout=UI_TIMEOUT_MS)

    unit_price = read_money(row.get_by_test_id(UNIT_PRICE_ID))
    expected_total = unit_price * Decimal(INITIAL_QUANTITY)

    expect_money(row.get_by_test_id(LINE_TOTAL_ID), expected_total)
    expect_money(page.get_by_test_id(CART_TOTAL_ID), expected_total)


def test_ct03_reduzir_quantidade_para_uma_unidade(page: Page) -> None:
    row = prepare_cart(page, REGULAR_PRODUCT, INITIAL_QUANTITY)
    quantity_input = row.get_by_test_id(ROW_QUANTITY_ID)
    unit_price = read_money(row.get_by_test_id(UNIT_PRICE_ID))

    # Confirma o estado anterior para verificar uma alteração real.
    expect(quantity_input).to_have_value(str(INITIAL_QUANTITY))
    expect_money(
        page.get_by_test_id(CART_TOTAL_ID),
        unit_price * Decimal(INITIAL_QUANTITY),
    )

    quantity_input.fill(str(MINIMUM_QUANTITY))
    quantity_input.press("Tab")

    expect(quantity_input).to_have_value(
        str(MINIMUM_QUANTITY), timeout=UI_TIMEOUT_MS
    )
    expect_money(page.get_by_test_id(CART_TOTAL_ID), unit_price)


def test_ct04_rejeitar_tres_unidades_de_thor_hammer(page: Page) -> None:
    open_product(page, RESTRICTED_PRODUCT)
    submit_quantity(page, INITIAL_QUANTITY)

    expect(
        page.get_by_text(RESTRICTION_MESSAGE, exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)


def test_ct05_aceitar_uma_unidade_de_thor_hammer(page: Page) -> None:
    open_product(page, RESTRICTED_PRODUCT)
    submit_quantity(page, MINIMUM_QUANTITY)

    expect(
        page.get_by_text(SUCCESS_MESSAGE, exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(
        page.get_by_test_id(CART_BADGE_ID)
    ).to_have_text(str(MINIMUM_QUANTITY), timeout=UI_TIMEOUT_MS)

    row = open_cart_row(page, RESTRICTED_PRODUCT)
    expect(
        row.get_by_test_id(ROW_QUANTITY_ID)
    ).to_have_value(str(MINIMUM_QUANTITY), timeout=UI_TIMEOUT_MS)
