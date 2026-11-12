import re
from decimal import Decimal, ROUND_HALF_UP

from playwright.sync_api import Page, expect


BASE_URL = "https://practicesoftwaretesting.com/"

# Seletores inferidos da User Story; podem precisar de ajuste no site real.
PRODUCT_PRICE_SELECTOR = ".product-price"
CART_COUNT_SELECTOR = "#cart-count"
CART_ITEM_SELECTOR = ".cart-item"
LINE_TOTAL_SELECTOR = ".line-total"
CART_TOTAL_SELECTOR = "#cart-total"
QUANTITY_LABEL = "Quantity"
ADD_TO_CART_BUTTON = "Add to cart"
CART_LINK = "Cart"
ADD_CONFIRMATION = "Product added to shopping cart."
THOR_LIMIT_MESSAGE = "You can only have one Thor Hammer in the cart."


def _open_product(page: Page, product_name: str) -> Decimal:
    page.goto(BASE_URL)
    product_link = page.get_by_role("link", name=product_name, exact=True)
    expect(product_link).to_be_visible()
    product_link.click()

    price_text = page.locator(PRODUCT_PRICE_SELECTOR).first.inner_text()
    return _money_from_text(price_text)


def _set_product_quantity(page: Page, quantity: int) -> None:
    quantity_input = page.get_by_label(QUANTITY_LABEL)
    expect(quantity_input).to_be_visible()
    quantity_input.fill(str(quantity))


def _add_to_cart(page: Page) -> None:
    page.get_by_role("button", name=ADD_TO_CART_BUTTON, exact=True).click()


def _open_cart(page: Page) -> None:
    page.get_by_role("link", name=re.compile(CART_LINK, re.IGNORECASE)).click()


def _money_from_text(value: str) -> Decimal:
    match = re.search(r"-?\d[\d,.]*", value)
    assert match is not None, f"Não foi possível extrair um valor monetário de: {value!r}"
    normalized = match.group(0).replace(",", "")
    return Decimal(normalized).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _cart_item(page: Page, product_name: str):
    item = page.locator(CART_ITEM_SELECTOR).filter(has_text=product_name)
    expect(item).to_have_count(1)
    return item


def test_CT001_adicionar_tres_unidades_de_claw_hammer(page: Page) -> None:
    _open_product(page, "Claw Hammer")
    _set_product_quantity(page, 3)
    _add_to_cart(page)

    expect(page.get_by_text(ADD_CONFIRMATION, exact=True)).to_be_visible()
    expect(page.locator(CART_COUNT_SELECTOR)).to_have_text("3")


def test_CT002_conferir_totais_com_tres_unidades(page: Page) -> None:
    unit_price = _open_product(page, "Claw Hammer")
    _set_product_quantity(page, 3)
    _add_to_cart(page)
    expect(page.get_by_text(ADD_CONFIRMATION, exact=True)).to_be_visible()

    _open_cart(page)
    item = _cart_item(page, "Claw Hammer")

    line_total = _money_from_text(item.locator(LINE_TOTAL_SELECTOR).inner_text())
    cart_total = _money_from_text(page.locator(CART_TOTAL_SELECTOR).inner_text())
    expected_total = (unit_price * 3).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    assert line_total == expected_total
    assert cart_total == line_total


def test_CT003_atualizar_quantidade_no_carrinho(page: Page) -> None:
    unit_price = _open_product(page, "Claw Hammer")
    _set_product_quantity(page, 3)
    _add_to_cart(page)
    expect(page.get_by_text(ADD_CONFIRMATION, exact=True)).to_be_visible()

    _open_cart(page)
    item = _cart_item(page, "Claw Hammer")
    quantity_input = item.get_by_label(QUANTITY_LABEL)
    quantity_input.fill("1")
    quantity_input.press("Enter")

    expected_total = unit_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    expect(quantity_input).to_have_value("1")
    expect(page.locator(CART_TOTAL_SELECTOR)).to_have_text(
        re.compile(re.escape(f"{expected_total:.2f}"))
    )


def test_CT004_impedir_tres_unidades_de_thor_hammer(page: Page) -> None:
    _open_product(page, "Thor Hammer")
    _set_product_quantity(page, 3)
    _add_to_cart(page)

    expect(page.get_by_text(THOR_LIMIT_MESSAGE, exact=True)).to_be_visible()
