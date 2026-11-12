import re
from decimal import Decimal

import pytest
from playwright.sync_api import expect


BASE_URL = "https://practicesoftwaretesting.com/"
ADD_CONFIRMATION = "Product added to shopping cart."
THOR_LIMIT_MESSAGE = "You can only have one Thor Hammer in the cart."


def _find_product(page, product_name):
    page.goto(BASE_URL)
    search = page.get_by_placeholder("Search")
    search.fill(product_name)
    search.press("Enter")
    product = page.get_by_text(product_name, exact=True).first
    expect(product).to_be_visible()
    product.click()
    expect(page.get_by_role("button", name=re.compile("Add to cart", re.I))).to_be_visible()


def _quantity_input(page):
    field = page.locator('input[type="number"]').first
    expect(field).to_be_visible()
    return field


def _add_product(page, product_name, quantity):
    _find_product(page, product_name)
    _quantity_input(page).fill(str(quantity))
    page.get_by_role("button", name=re.compile("Add to cart", re.I)).click()


def _open_cart(page):
    cart_link = page.get_by_role(
        "link", name=re.compile(r"cart|carrinho", re.I)
    ).first
    if cart_link.count() == 0:
        cart_link = page.get_by_role(
            "button", name=re.compile(r"cart|carrinho", re.I)
        ).first
    expect(cart_link).to_be_visible()
    cart_link.click()


def _cart_indicator(page):
    test_id_indicator = page.locator('[data-test="nav-cart"]')
    if test_id_indicator.count():
        return test_id_indicator
    return page.get_by_role(
        "link", name=re.compile(r"cart|carrinho", re.I)
    ).first


def _number_from_text(value):
    cleaned = re.sub(r"[^\d,.\-]", "", value).strip()
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    return Decimal(cleaned)


def _product_row(page, product_name):
    row = page.get_by_role("row").filter(has_text=product_name).first
    if row.count() == 0:
        row = page.locator("tr").filter(has_text=product_name).first
    expect(row).to_be_visible()
    return row


def _price_from_row(row):
    cells = row.get_by_role("cell")
    if cells.count() == 0:
        cells = row.locator("td")
    # Suposição: a primeira célula monetária da linha contém o preço unitário.
    for index in range(cells.count()):
        value = cells.nth(index).inner_text()
        if re.search(r"\d", value) and re.search(r"[$€£]|,\d{2}|\.\d{2}", value):
            return _number_from_text(value)
    raise AssertionError("Preço unitário não encontrado na linha do produto.")


def _line_total_from_row(row):
    cells = row.get_by_role("cell")
    if cells.count() == 0:
        cells = row.locator("td")
    monetary_values = []
    for index in range(cells.count()):
        value = cells.nth(index).inner_text()
        if re.search(r"\d", value) and re.search(r"[$€£]|,\d{2}|\.\d{2}", value):
            monetary_values.append(_number_from_text(value))
    if not monetary_values:
        raise AssertionError("Total da linha não encontrado.")
    return monetary_values[-1]


def _cart_total(page):
    total_text = page.get_by_text(re.compile(r"Total", re.I)).last
    expect(total_text).to_be_visible()
    return _number_from_text(total_text.inner_text())


def test_CT_01_adicionar_tres_unidades_de_claw_hammer(page):
    _add_product(page, "Claw Hammer", 3)

    expect(page.get_by_text(ADD_CONFIRMATION, exact=True)).to_be_visible()
    expect(_cart_indicator(page)).to_contain_text("3")


def test_CT_02_totais_do_carrinho_com_tres_unidades(page):
    _add_product(page, "Claw Hammer", 3)
    _open_cart(page)

    row = _product_row(page, "Claw Hammer")
    unit_price = _price_from_row(row)
    expected_total = unit_price * 3

    expect(row).to_contain_text("3")
    assert _line_total_from_row(row) == expected_total
    assert _cart_total(page) == expected_total


def test_CT_03_alterar_quantidade_no_carrinho_para_um(page):
    _add_product(page, "Claw Hammer", 3)
    _open_cart(page)

    row = _product_row(page, "Claw Hammer")
    unit_price = _price_from_row(row)
    quantity = row.locator('input[type="number"]').first
    expect(quantity).to_be_visible()
    quantity.fill("1")
    quantity.press("Enter")

    expect(quantity).to_have_value("1")
    assert _cart_total(page) == unit_price


def test_CT_04_rejeitar_tres_unidades_de_thor_hammer(page):
    _find_product(page, "Thor Hammer")
    _quantity_input(page).fill("3")
    page.get_by_role("button", name=re.compile("Add to cart", re.I)).click()

    expect(page.get_by_text(THOR_LIMIT_MESSAGE, exact=True)).to_be_visible()
