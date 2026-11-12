import re
import sys
from decimal import Decimal

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"

ADDED_MSG = "Product added to shopping cart."
THOR_MSG = "You can only have one Thor Hammer in the cart."


@pytest.fixture(scope="session", autouse=True)
def _test_id_attribute(playwright):
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture
def app_url(pytestconfig):
    return pytestconfig.getoption("base_url", None) or BASE_URL


def to_decimal(text: str) -> Decimal:
    return Decimal(re.sub(r"[^\d.]", "", text))


def money(value: Decimal) -> re.Pattern:
    return re.compile(rf"^\s*\$?\s*{re.escape(f'{value:.2f}')}\s*$")


def open_product(page: Page, app_url: str, name: str) -> Decimal:
    page.goto(app_url)
    page.get_by_test_id("search-query").fill(name)
    page.get_by_test_id("search-submit").click()
    page.get_by_role("heading", name=name, exact=True).first.click()
    expect(page.get_by_test_id("product-name")).to_have_text(name)
    unit_price = page.get_by_test_id("unit-price")
    expect(unit_price).to_have_text(re.compile(r"\d"))
    return to_decimal(unit_price.inner_text())


def add_to_cart(page: Page, quantity: int) -> None:
    page.get_by_test_id("quantity").fill(str(quantity))
    page.get_by_role("button", name="Add to cart").click()


def add_claw_hammers(page: Page, app_url: str, quantity: int) -> Decimal:
    unit_price = open_product(page, app_url, "Claw Hammer")
    add_to_cart(page, quantity)
    expect(page.get_by_text(ADDED_MSG)).to_be_visible()
    expect(page.get_by_test_id("cart-quantity")).to_have_text(str(quantity))
    return unit_price


def open_cart(page: Page) -> None:
    page.get_by_test_id("nav-cart").click()
    expect(page).to_have_url(re.compile(r"/checkout"))


def test_ct01_add_three_claw_hammers_shows_confirmation_and_badge(page: Page, app_url):
    open_product(page, app_url, "Claw Hammer")
    add_to_cart(page, 3)
    expect(page.get_by_text(ADDED_MSG)).to_be_visible()
    expect(page.get_by_test_id("cart-quantity")).to_have_text("3")


def test_ct02_cart_line_total_and_cart_total_for_three_units(page: Page, app_url):
    unit_price = add_claw_hammers(page, app_url, 3)
    open_cart(page)
    expect(page.get_by_test_id("product-quantity")).to_have_value("3")
    expect(page.get_by_test_id("line-price")).to_have_text(money(unit_price * 3))
    expect(page.get_by_test_id("cart-total")).to_have_text(money(unit_price * 3))


def test_ct03_change_quantity_from_three_to_one_updates_total(page: Page, app_url):
    unit_price = add_claw_hammers(page, app_url, 3)
    open_cart(page)
    expect(page.get_by_test_id("cart-total")).to_have_text(money(unit_price * 3))
    quantity = page.get_by_test_id("product-quantity")
    quantity.fill("1")
    quantity.press("Tab")
    expect(page.get_by_test_id("line-price")).to_have_text(money(unit_price))
    expect(page.get_by_test_id("cart-total")).to_have_text(money(unit_price))


def test_ct04_thor_hammer_three_units_is_rejected(page: Page, app_url):
    open_product(page, app_url, "Thor Hammer")
    add_to_cart(page, 3)
    expect(page.get_by_text(THOR_MSG)).to_be_visible()


def test_ct05_thor_hammer_single_unit_is_added(page: Page, app_url):
    open_product(page, app_url, "Thor Hammer")
    add_to_cart(page, 1)
    expect(page.get_by_text(ADDED_MSG)).to_be_visible()
    expect(page.get_by_test_id("cart-quantity")).to_have_text("1")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
