import re

import pytest
from playwright.sync_api import Page, expect


BASE_URL = "https://practicesoftwaretesting.com/"
CLAW_HAMMER = "Claw Hammer"
THOR_HAMMER = "Thor Hammer"
QUANTITY_TO_ADD = "3"
QUANTITY_TO_EDIT = "1"
ADDED_MESSAGE = "Product added to shopping cart."
THOR_LIMIT_MESSAGE = "You can only have one Thor Hammer in the cart."


def open_product(page: Page, product_name: str) -> None:
    page.goto(BASE_URL)
    search = page.get_by_placeholder("Search")
    expect(search).to_be_visible()
    search.fill(product_name)
    search.press("Enter")
    product_link = page.get_by_text(product_name, exact=True).first
    expect(product_link).to_be_visible()
    product_link.click()


def set_product_quantity(page: Page, quantity: str) -> None:
    quantity_input = page.get_by_role("spinbutton")
    expect(quantity_input).to_be_visible()
    quantity_input.fill(quantity)


def add_product_to_cart(page: Page) -> None:
    page.get_by_role("button", name=re.compile("Add to cart", re.IGNORECASE)).click()


def open_cart(page: Page) -> None:
    page.get_by_role("link", name=re.compile("cart", re.IGNORECASE)).click()


def money_to_cents(text: str) -> int:
    normalized = re.sub(r"[^\d,.\-]", "", text).strip()
    if "," in normalized and "." in normalized:
        if normalized.rfind(",") > normalized.rfind("."):
            normalized = normalized.replace(".", "").replace(",", ".")
        else:
            normalized = normalized.replace(",", "")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")
    return round(float(normalized) * 100)


def product_row(page: Page, product_name: str):
    row = page.get_by_role("row").filter(has_text=product_name)
    expect(row).to_be_visible()
    return row


def row_price_cents(row) -> int:
    cells = row.get_by_role("cell")
    expect(cells.nth(1)).to_be_visible()
    return money_to_cents(cells.nth(1).inner_text())


def row_total_cents(row) -> int:
    cells = row.get_by_role("cell")
    expect(cells.nth(3)).to_be_visible()
    return money_to_cents(cells.nth(3).inner_text())


def cart_total_cents(page: Page) -> int:
    total_text = page.get_by_text(re.compile(r"Total", re.IGNORECASE)).last
    expect(total_text).to_be_visible()
    return money_to_cents(total_text.inner_text())


def test_ct01_adicionar_tres_unidades_de_claw_hammer(page: Page) -> None:
    open_product(page, CLAW_HAMMER)
    set_product_quantity(page, QUANTITY_TO_ADD)
    add_product_to_cart(page)

    expect(page.get_by_text(ADDED_MESSAGE, exact=True)).to_be_visible()
    cart_link = page.get_by_role("link", name=re.compile("cart", re.IGNORECASE))
    expect(cart_link).to_contain_text("3")


def test_ct02_conferir_totais_com_tres_unidades(page: Page) -> None:
    open_product(page, CLAW_HAMMER)
    set_product_quantity(page, QUANTITY_TO_ADD)
    add_product_to_cart(page)
    open_cart(page)

    row = product_row(page, CLAW_HAMMER)
    unit_price = row_price_cents(row)
    expected_total = unit_price * 3

    expect(row.get_by_role("spinbutton")).to_have_value("3")
    assert row_total_cents(row) == expected_total
    assert cart_total_cents(page) == expected_total


def test_ct03_alterar_quantidade_no_carrinho_para_uma_unidade(page: Page) -> None:
    open_product(page, CLAW_HAMMER)
    set_product_quantity(page, QUANTITY_TO_ADD)
    add_product_to_cart(page)
    open_cart(page)

    row = product_row(page, CLAW_HAMMER)
    unit_price = row_price_cents(row)
    quantity_input = row.get_by_role("spinbutton")
    quantity_input.fill(QUANTITY_TO_EDIT)
    quantity_input.press("Enter")

    expect(quantity_input).to_have_value("1")
    expect.poll(lambda: cart_total_cents(page)).to_be(unit_price)


def test_ct04_impedir_tres_unidades_de_thor_hammer(page: Page) -> None:
    open_product(page, THOR_HAMMER)
    set_product_quantity(page, QUANTITY_TO_ADD)
    add_product_to_cart(page)

    expect(page.get_by_text(THOR_LIMIT_MESSAGE, exact=True)).to_be_visible()
