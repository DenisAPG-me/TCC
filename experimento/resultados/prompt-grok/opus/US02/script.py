import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"

CLAW_HAMMER = "Claw Hammer"
THOR_HAMMER = "Thor Hammer"
MSG_ADDED = "Product added to shopping cart."
MSG_THOR_LIMIT = "You can only have one Thor Hammer in the cart."


@pytest.fixture(scope="session", autouse=True)
def configure_test_id(playwright):
    playwright.selectors.set_test_id_attribute("data-test")


def parse_price(text: str) -> float:
    match = re.search(r"\d+(?:[.,]\d+)?", text.replace(",", ""))
    assert match, f"Preço não encontrado em: {text!r}"
    return float(match.group(0))


def price_pattern(value: float) -> re.Pattern:
    return re.compile(rf"^\s*\$?\s*{re.escape(f'{value:.2f}')}\s*$")


def open_product(page: Page, name: str) -> None:
    page.goto(BASE_URL)
    page.get_by_test_id("search-query").fill(name)
    page.get_by_test_id("search-submit").click()
    page.get_by_test_id("product-name").filter(
        has_text=re.compile(rf"^\s*{re.escape(name)}\s*$")
    ).first.click()
    expect(page.get_by_role("heading", name=name, exact=True)).to_be_visible()


def set_quantity_and_add(page: Page, quantity: int) -> None:
    page.get_by_test_id("quantity").fill(str(quantity))
    page.get_by_role("button", name="Add to cart").click()


def get_unit_price(page: Page) -> float:
    unit_price = page.get_by_test_id("unit-price")
    expect(unit_price).to_have_text(re.compile(r"\d"))
    return parse_price(unit_price.inner_text())


def add_claw_hammer_x3(page: Page) -> float:
    open_product(page, CLAW_HAMMER)
    unit_price = get_unit_price(page)
    set_quantity_and_add(page, 3)
    expect(page.get_by_text(MSG_ADDED)).to_be_visible()
    expect(page.get_by_test_id("cart-quantity")).to_have_text("3")
    return unit_price


def open_cart(page: Page) -> None:
    page.get_by_test_id("nav-cart").click()
    expect(page).to_have_url(re.compile(r"/checkout"))
    expect(page.get_by_test_id("cart-total")).to_be_visible()


def test_TC01_add_claw_hammer_quantity_3(page: Page):
    open_product(page, CLAW_HAMMER)
    set_quantity_and_add(page, 3)

    expect(page.get_by_text(MSG_ADDED)).to_be_visible()
    expect(page.get_by_test_id("cart-quantity")).to_have_text("3")


def test_TC02_cart_line_total_and_cart_total_for_3_units(page: Page):
    unit_price = add_claw_hammer_x3(page)
    open_cart(page)

    expect(page.get_by_test_id("product-quantity")).to_have_value("3")
    expected_line_total = round(unit_price * 3, 2)
    expect(page.get_by_test_id("line-price")).to_have_text(price_pattern(expected_line_total))
    expect(page.get_by_test_id("cart-total")).to_have_text(price_pattern(expected_line_total))

    line_total = parse_price(page.get_by_test_id("line-price").inner_text())
    cart_total = parse_price(page.get_by_test_id("cart-total").inner_text())
    assert cart_total == line_total


def test_TC03_change_cart_quantity_from_3_to_1(page: Page):
    unit_price = add_claw_hammer_x3(page)
    open_cart(page)

    quantity_input = page.get_by_test_id("product-quantity")
    expect(quantity_input).to_have_value("3")
    quantity_input.fill("1")
    quantity_input.press("Tab")

    expect(quantity_input).to_have_value("1")
    expect(page.get_by_test_id("cart-total")).to_have_text(price_pattern(unit_price))


def test_TC04_thor_hammer_cannot_add_3_units(page: Page):
    open_product(page, THOR_HAMMER)
    set_quantity_and_add(page, 3)

    expect(page.get_by_text(MSG_THOR_LIMIT)).to_be_visible()
    expect(page.get_by_test_id("cart-quantity")).not_to_have_text("3")


def test_TC05_thor_hammer_add_single_unit_allowed(page: Page):
    open_product(page, THOR_HAMMER)
    set_quantity_and_add(page, 1)

    expect(page.get_by_text(MSG_ADDED)).to_be_visible()
    expect(page.get_by_test_id("cart-quantity")).to_have_text("1")
