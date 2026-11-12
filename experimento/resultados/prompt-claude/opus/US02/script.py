import re
from decimal import Decimal

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com"
PRODUCT_NAME = "Claw Hammer"
LIMITED_PRODUCT_NAME = "Thor Hammer"
QUANTITY = 3
UPDATED_QUANTITY = 1
MIN_QUANTITY = 1
MSG_PRODUCT_ADDED = "Product added to shopping cart."
MSG_THOR_LIMIT = "You can only have one Thor Hammer in the cart."
TIMEOUT = 15000


@pytest.fixture(scope="session", autouse=True)
def configure_test_id_attribute(playwright):
    playwright.selectors.set_test_id_attribute("data-test")


def open_product(page: Page, name: str) -> None:
    page.goto(f"{BASE_URL}/")
    page.get_by_test_id("search-query").fill(name)
    page.get_by_test_id("search-submit").click()
    card = page.get_by_test_id("product-name").filter(
        has_text=re.compile(rf"^\s*{re.escape(name)}\s*$")
    ).first
    expect(card).to_be_visible(timeout=TIMEOUT)
    card.click()
    expect(page.get_by_test_id("product-name")).to_have_text(name, timeout=TIMEOUT)


def get_unit_price(page: Page) -> Decimal:
    price = page.get_by_test_id("unit-price")
    expect(price).to_have_text(re.compile(r"\d+\.\d{2}"), timeout=TIMEOUT)
    return Decimal(re.search(r"\d+\.\d{2}", price.inner_text()).group())


def add_to_cart(page: Page, quantity: int) -> None:
    page.get_by_test_id("quantity").fill(str(quantity))
    page.get_by_test_id("add-to-cart").click()


def open_cart(page: Page) -> None:
    page.get_by_test_id("nav-cart").click()
    expect(page).to_have_url(re.compile(r"/checkout"), timeout=TIMEOUT)


def money(value: Decimal) -> re.Pattern:
    return re.compile(rf"^\s*\$?\s*{re.escape(f'{value:.2f}')}\s*$")


def test_ct01_adicionar_tres_unidades_ao_carrinho(page: Page):
    open_product(page, PRODUCT_NAME)
    add_to_cart(page, QUANTITY)

    expect(page.get_by_text(MSG_PRODUCT_ADDED)).to_be_visible(timeout=TIMEOUT)
    expect(page.get_by_test_id("cart-quantity")).to_have_text(str(QUANTITY), timeout=TIMEOUT)


def test_ct02_validar_total_da_linha_e_do_carrinho(page: Page):
    open_product(page, PRODUCT_NAME)
    unit_price = get_unit_price(page)
    add_to_cart(page, QUANTITY)
    expect(page.get_by_test_id("cart-quantity")).to_have_text(str(QUANTITY), timeout=TIMEOUT)

    open_cart(page)

    expected_line_total = unit_price * QUANTITY
    expect(page.get_by_test_id("product-title")).to_contain_text(PRODUCT_NAME, timeout=TIMEOUT)
    expect(page.get_by_test_id("product-quantity")).to_have_value(str(QUANTITY), timeout=TIMEOUT)
    expect(page.get_by_test_id("line-price")).to_have_text(money(expected_line_total), timeout=TIMEOUT)
    expect(page.get_by_test_id("cart-total")).to_have_text(money(expected_line_total), timeout=TIMEOUT)


def test_ct03_alterar_quantidade_no_carrinho_para_um(page: Page):
    open_product(page, PRODUCT_NAME)
    unit_price = get_unit_price(page)
    add_to_cart(page, QUANTITY)
    expect(page.get_by_test_id("cart-quantity")).to_have_text(str(QUANTITY), timeout=TIMEOUT)

    open_cart(page)
    expect(page.get_by_test_id("cart-total")).to_have_text(money(unit_price * QUANTITY), timeout=TIMEOUT)

    quantity_input = page.get_by_test_id("product-quantity")
    quantity_input.fill(str(UPDATED_QUANTITY))
    quantity_input.press("Tab")

    expect(page.get_by_test_id("line-price")).to_have_text(money(unit_price), timeout=TIMEOUT)
    expect(page.get_by_test_id("cart-total")).to_have_text(money(unit_price), timeout=TIMEOUT)


def test_ct04_bloquear_tres_unidades_de_thor_hammer(page: Page):
    open_product(page, LIMITED_PRODUCT_NAME)
    add_to_cart(page, QUANTITY)

    expect(page.get_by_text(MSG_THOR_LIMIT)).to_be_visible(timeout=TIMEOUT)
    expect(page.get_by_text(MSG_PRODUCT_ADDED)).not_to_be_visible()


def test_ct05_adicionar_quantidade_minima(page: Page):
    open_product(page, PRODUCT_NAME)
    unit_price = get_unit_price(page)
    add_to_cart(page, MIN_QUANTITY)

    expect(page.get_by_text(MSG_PRODUCT_ADDED)).to_be_visible(timeout=TIMEOUT)
    expect(page.get_by_test_id("cart-quantity")).to_have_text(str(MIN_QUANTITY), timeout=TIMEOUT)

    open_cart(page)
    expect(page.get_by_test_id("cart-total")).to_have_text(money(unit_price), timeout=TIMEOUT)


def test_ct06_adicionar_uma_unidade_de_thor_hammer(page: Page):
    open_product(page, LIMITED_PRODUCT_NAME)
    add_to_cart(page, MIN_QUANTITY)

    expect(page.get_by_text(MSG_PRODUCT_ADDED)).to_be_visible(timeout=TIMEOUT)
    expect(page.get_by_test_id("cart-quantity")).to_have_text(str(MIN_QUANTITY), timeout=TIMEOUT)
    expect(page.get_by_text(MSG_THOR_LIMIT)).not_to_be_visible()
