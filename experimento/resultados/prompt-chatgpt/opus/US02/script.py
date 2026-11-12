import re
from decimal import Decimal

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"

PRODUCT_AVAILABLE = "Claw Hammer"
PRODUCT_LIMITED = "Thor Hammer"

MSG_ADDED = "Product added to shopping cart."
MSG_THOR_LIMIT = "You can only have one Thor Hammer in the cart."

TEST_ID_ATTRIBUTE = "data-test"
TEST_IDS = {
    "search_input": "search-query",
    "search_submit": "search-submit",
    "product_name": "product-name",
    "unit_price": "unit-price",
    "quantity": "quantity",
    "add_to_cart": "add-to-cart",
    "cart_badge": "cart-quantity",
    "nav_cart": "nav-cart",
    "cart_line_quantity": "product-quantity",
    "cart_line_total": "line-price",
    "cart_total": "cart-total",
}

DEFAULT_TIMEOUT_MS = 10_000

expect.set_options(timeout=DEFAULT_TIMEOUT_MS)


@pytest.fixture(scope="session", autouse=True)
def configure_test_id_attribute(playwright):
    playwright.selectors.set_test_id_attribute(TEST_ID_ATTRIBUTE)


def parse_amount(text: str) -> Decimal:
    match = re.search(r"\d+(?:\.\d+)?", text.replace(",", ""))
    assert match, f"Valor monetário não encontrado em: {text!r}"
    return Decimal(match.group(0)).quantize(Decimal("0.01"))


def amount_pattern(value: Decimal) -> re.Pattern:
    return re.compile(rf"^\s*\$?\s*{re.escape(f'{value:.2f}')}\s*$")


def open_product(page: Page, name: str) -> None:
    page.goto(BASE_URL)
    page.get_by_test_id(TEST_IDS["search_input"]).fill(name)
    page.get_by_test_id(TEST_IDS["search_submit"]).click()
    card = page.get_by_test_id(TEST_IDS["product_name"]).filter(
        has_text=re.compile(rf"^\s*{re.escape(name)}\s*$")
    )
    expect(card).to_have_count(1)
    card.click()
    expect(page.get_by_test_id(TEST_IDS["product_name"])).to_have_text(name)


def read_unit_price(page: Page) -> Decimal:
    unit_price = page.get_by_test_id(TEST_IDS["unit_price"])
    expect(unit_price).to_have_text(re.compile(r"\d"))
    return parse_amount(unit_price.inner_text())


def add_to_cart(page: Page, quantity: int) -> None:
    quantity_input = page.get_by_test_id(TEST_IDS["quantity"])
    quantity_input.fill(str(quantity))
    expect(quantity_input).to_have_value(str(quantity))
    page.get_by_test_id(TEST_IDS["add_to_cart"]).click()


def prepare_cart_with_three_units(page: Page) -> Decimal:
    open_product(page, PRODUCT_AVAILABLE)
    unit_price = read_unit_price(page)
    add_to_cart(page, 3)
    expect(page.get_by_test_id(TEST_IDS["cart_badge"])).to_have_text("3")
    page.get_by_test_id(TEST_IDS["nav_cart"]).click()
    expect(page.get_by_test_id(TEST_IDS["cart_line_quantity"])).to_have_count(1)
    expect(page.get_by_test_id(TEST_IDS["cart_line_quantity"])).to_have_value("3")
    return unit_price


def test_CT001_adicionar_tres_unidades_claw_hammer(page: Page):
    open_product(page, PRODUCT_AVAILABLE)
    add_to_cart(page, 3)

    expect(page.get_by_text(MSG_ADDED, exact=True)).to_be_visible()
    expect(page.get_by_test_id(TEST_IDS["cart_badge"])).to_have_text("3")


def test_CT002_totais_carrinho_com_tres_unidades(page: Page):
    unit_price = prepare_cart_with_three_units(page)
    expected_line_total = unit_price * 3

    line_total = page.get_by_test_id(TEST_IDS["cart_line_total"])
    cart_total = page.get_by_test_id(TEST_IDS["cart_total"])

    expect(line_total).to_have_text(amount_pattern(expected_line_total))
    expect(cart_total).to_have_text(amount_pattern(expected_line_total))
    assert parse_amount(cart_total.inner_text()) == parse_amount(line_total.inner_text())


def test_CT003_alterar_quantidade_carrinho_para_um(page: Page):
    unit_price = prepare_cart_with_three_units(page)

    quantity_input = page.get_by_test_id(TEST_IDS["cart_line_quantity"])
    quantity_input.fill("1")
    quantity_input.press("Tab")

    expect(quantity_input).to_have_value("1")
    expect(page.get_by_test_id(TEST_IDS["cart_total"])).to_have_text(amount_pattern(unit_price))


def test_CT004_bloquear_tres_unidades_thor_hammer(page: Page):
    open_product(page, PRODUCT_LIMITED)
    add_to_cart(page, 3)

    expect(page.get_by_text(MSG_THOR_LIMIT, exact=True)).to_be_visible()


def test_CT005_bloquear_duas_unidades_thor_hammer(page: Page):
    open_product(page, PRODUCT_LIMITED)
    add_to_cart(page, 2)

    expect(page.get_by_text(MSG_THOR_LIMIT, exact=True)).to_be_visible()
