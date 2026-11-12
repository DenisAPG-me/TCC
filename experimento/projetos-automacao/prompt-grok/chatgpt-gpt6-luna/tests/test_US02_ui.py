import re
from decimal import Decimal
from urllib.parse import quote

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"


def _base_url(request):
    return request.config.getoption("--base-url") or BASE_URL


def _open_product(page: Page, base_url: str, name: str):
    page.goto(base_url)
    product_link = page.get_by_role("link", name=re.compile(re.escape(name), re.I))
    if product_link.count():
        product_link.first.click()
    else:
        page.goto(base_url.rstrip("/") + "/product/" + quote(name.lower().replace(" ", "-")))
    expect(page.get_by_text(re.compile(re.escape(name), re.I)).first).to_be_visible()


def _set_quantity(page: Page, quantity: int):
    field = page.get_by_label(re.compile("quantity", re.I))
    if field.count() == 0:
        field = page.locator('input[type="number"]')
    expect(field.first).to_be_visible()
    field.first.fill(str(quantity))


def _add_to_cart(page: Page):
    page.get_by_role("button", name=re.compile("add to cart", re.I)).click()


def _open_cart(page: Page):
    cart = page.get_by_role("link", name=re.compile("shopping cart|cart", re.I))
    if cart.count() == 0:
        cart = page.get_by_role("button", name=re.compile("shopping cart|cart", re.I))
    cart.first.click()


def _cart_count(page: Page):
    indicator = page.get_by_test_id("cart-count")
    if indicator.count() == 0:
        indicator = page.locator('[aria-label*="cart" i] [class*="badge"], [class*="cart"] [class*="badge"]')
    expect(indicator.first).to_be_visible()
    return int(re.search(r"\d+", indicator.first.inner_text()).group())


def _money(text: str) -> Decimal:
    value = re.sub(r"[^\d,.\-]", "", text)
    if "," in value and "." in value:
        value = value.replace(",", "")
    elif "," in value:
        value = value.replace(",", ".")
    return Decimal(value)


def _cart_row(page: Page, name: str):
    row = page.get_by_role("row", name=re.compile(re.escape(name), re.I))
    if row.count():
        return row.first
    return page.locator("tr, [role='row']").filter(
        has=page.get_by_text(re.compile(re.escape(name), re.I))
    ).first


def _line_values(page: Page, name: str):
    row = _cart_row(page, name)
    expect(row).to_be_visible()
    quantity = row.locator('input[type="number"]')
    if quantity.count() == 0:
        quantity = row.get_by_label(re.compile("quantity", re.I))
    expect(quantity.first).to_be_visible()
    qty = int(quantity.first.input_value())

    cells = row.locator("td, [role='cell']")
    texts = [cells.nth(i).inner_text() for i in range(cells.count())]
    numbers = [_money(t) for t in texts if re.search(r"\d", t)]
    assert len(numbers) >= 2, f"Não foi possível identificar preço e total na linha: {texts}"
    unit_price = numbers[0]
    line_total = numbers[-1]
    return row, quantity.first, unit_price, line_total, qty


def _cart_total(page: Page) -> Decimal:
    total_label = page.get_by_text(re.compile(r"(cart\s*)?total", re.I))
    expect(total_label.last).to_be_visible()
    return _money(total_label.last.inner_text())


def _prepare_three_units(page: Page, base_url: str, name: str):
    _open_product(page, base_url, name)
    _set_quantity(page, 3)
    _add_to_cart(page)
    expect(page.get_by_text("Product added to shopping cart.", exact=True)).to_be_visible()
    _open_cart(page)
    expect(page.get_by_text(re.compile(re.escape(name), re.I)).first).to_be_visible()


def test_TC01_adicionar_tres_unidades_de_claw_hammer(page: Page, request):
    _open_product(page, _base_url(request), "Claw Hammer")
    _set_quantity(page, 3)
    _add_to_cart(page)
    expect(page.get_by_text("Product added to shopping cart.", exact=True)).to_be_visible()
    expect(page.get_by_text(re.compile(r"\b3\b")).first).to_be_visible()
    assert _cart_count(page) == 3


def test_TC02_totais_com_tres_unidades(page: Page, request):
    _prepare_three_units(page, _base_url(request), "Claw Hammer")
    _, _, unit_price, line_total, quantity = _line_values(page, "Claw Hammer")
    assert quantity == 3
    assert line_total == unit_price * 3
    assert _cart_total(page) == line_total


def test_TC03_alterar_quantidade_para_uma_unidade(page: Page, request):
    _prepare_three_units(page, _base_url(request), "Claw Hammer")
    _, quantity_field, unit_price, _, _ = _line_values(page, "Claw Hammer")
    quantity_field.fill("1")
    quantity_field.press("Enter")
    expect(quantity_field).to_have_value("1")
    expect(page.get_by_text(re.compile(re.escape("Claw Hammer"), re.I)).first).to_be_visible()
    assert _cart_total(page) == unit_price


def test_TC04_bloquear_tres_unidades_de_thor_hammer(page: Page, request):
    _open_product(page, _base_url(request), "Thor Hammer")
    _set_quantity(page, 3)
    _add_to_cart(page)
    expect(
        page.get_by_text(
            "You can only have one Thor Hammer in the cart.",
            exact=True,
        )
    ).to_be_visible()


def test_TC05_adicionar_uma_unidade_de_claw_hammer(page: Page, request):
    _open_product(page, _base_url(request), "Claw Hammer")
    _set_quantity(page, 1)
    _add_to_cart(page)
    expect(page.get_by_text("Product added to shopping cart.", exact=True)).to_be_visible()
    assert _cart_count(page) == 1
    _open_cart(page)
    _, _, unit_price, line_total, quantity = _line_values(page, "Claw Hammer")
    assert quantity == 1
    assert line_total == unit_price
    assert _cart_total(page) == unit_price
