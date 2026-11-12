import re
from decimal import Decimal

import pytest
from playwright.sync_api import expect, sync_playwright


BASE_URL = "https://practicesoftwaretesting.com/"

# Valores inferidos que podem exigir ajuste no sistema real.
PRODUCT_AVAILABLE = "Claw Hammer"
PRODUCT_RESTRICTED = "Thor Hammer"
TEST_ID_ATTRIBUTE = "data-test"
ACTION_TIMEOUT_MS = 15_000
NAVIGATION_TIMEOUT_MS = 30_000

UI = {
    "product_title_test_id": "product-name",
    "quantity_label": "Quantity",
    "add_button_name": "Add to cart",
    "cart_link_test_id": "nav-cart",
    "cart_count_test_id": "cart-quantity",
    "unit_price_test_id": "product-price",
    "line_total_test_id": "line-price",
    "cart_total_test_id": "cart-total",
}

SUCCESS_MESSAGE = "Product added to shopping cart."
RESTRICTION_MESSAGE = "You can only have one Thor Hammer in the cart."

# Exige símbolo $, duas casas decimais e agrupamento válido, se presente.
MONEY_PATTERN = re.compile(
    r"^\s*\$\s*(?P<amount>"
    r"(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)\.[0-9]{2}"
    r")\s*$"
)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        playwright.selectors.set_test_id_attribute(TEST_ID_ATTRIBUTE)
        instance = playwright.chromium.launch(headless=True)
        try:
            yield instance
        finally:
            instance.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(locale="en-US")
    try:
        instance = context.new_page()
        instance.set_default_timeout(ACTION_TIMEOUT_MS)
        instance.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
        yield instance
    finally:
        context.close()


def open_product(page, product_name):
    response = page.goto(BASE_URL, wait_until="domcontentloaded")
    assert response is not None, "A navegação inicial não retornou resposta HTTP."
    assert response.ok, (
        f"Falha ao abrir a loja: HTTP {response.status}."
    )

    product = page.get_by_text(product_name, exact=True)
    expect(product).to_be_visible(timeout=ACTION_TIMEOUT_MS)
    product.click()

    title = page.get_by_test_id(UI["product_title_test_id"])
    expect(title).to_be_visible(timeout=ACTION_TIMEOUT_MS)
    expect(title).to_have_text(product_name, timeout=ACTION_TIMEOUT_MS)


def submit_quantity(page, quantity):
    field = page.get_by_label(UI["quantity_label"], exact=True)
    expect(field).to_be_editable(timeout=ACTION_TIMEOUT_MS)
    field.fill(str(quantity))
    expect(field).to_have_value(str(quantity), timeout=ACTION_TIMEOUT_MS)
    page.get_by_role(
        "button", name=UI["add_button_name"], exact=True
    ).click()


def expect_success(page):
    expect(
        page.get_by_text(SUCCESS_MESSAGE, exact=True)
    ).to_be_visible(timeout=ACTION_TIMEOUT_MS)


def prepare_cart_with_three_units(page):
    open_product(page, PRODUCT_AVAILABLE)
    submit_quantity(page, 3)
    expect_success(page)
    expect(
        page.get_by_test_id(UI["cart_count_test_id"])
    ).to_have_text("3", timeout=ACTION_TIMEOUT_MS)


def open_cart_row(page, product_name):
    page.get_by_test_id(UI["cart_link_test_id"]).click()

    row = page.get_by_role("row").filter(
        has=page.get_by_text(product_name, exact=True)
    )
    expect(row).to_have_count(1, timeout=ACTION_TIMEOUT_MS)
    expect(row).to_be_visible(timeout=ACTION_TIMEOUT_MS)
    return row


def read_money(locator):
    expect(locator).to_be_visible(timeout=ACTION_TIMEOUT_MS)
    expect(locator).to_have_text(
        MONEY_PATTERN, timeout=ACTION_TIMEOUT_MS
    )
    text = locator.inner_text()
    match = MONEY_PATTERN.fullmatch(text)
    assert match is not None, f"Formato monetário inesperado: {text!r}"
    return Decimal(match.group("amount").replace(",", ""))


def expected_money_pattern(value):
    plain = format(value, ".2f")
    grouped = format(value, ",.2f")
    alternatives = "|".join(
        re.escape(text) for text in sorted({plain, grouped})
    )
    return re.compile(r"^\s*\$\s*(?:" + alternatives + r")\s*$")


def expect_money(locator, expected):
    expect(locator).to_be_visible(timeout=ACTION_TIMEOUT_MS)
    expect(locator).to_have_text(
        expected_money_pattern(expected),
        timeout=ACTION_TIMEOUT_MS,
    )


def test_CT001_adicionar_tres_unidades(page):
    open_product(page, PRODUCT_AVAILABLE)

    submit_quantity(page, 3)

    expect_success(page)
    expect(
        page.get_by_test_id(UI["cart_count_test_id"])
    ).to_have_text("3", timeout=ACTION_TIMEOUT_MS)


def test_CT002_calcular_totais_para_tres_unidades(page):
    prepare_cart_with_three_units(page)
    row = open_cart_row(page, PRODUCT_AVAILABLE)

    expect(
        row.get_by_label(UI["quantity_label"], exact=True)
    ).to_have_value("3", timeout=ACTION_TIMEOUT_MS)

    unit_price = read_money(
        row.get_by_test_id(UI["unit_price_test_id"])
    )
    expected_total = unit_price * Decimal("3")

    line_total_locator = row.get_by_test_id(UI["line_total_test_id"])
    expect_money(line_total_locator, expected_total)
    line_total = read_money(line_total_locator)
    assert line_total == expected_total

    cart_total_locator = page.get_by_test_id(UI["cart_total_test_id"])
    expect_money(cart_total_locator, line_total)
    assert read_money(cart_total_locator) == line_total


def test_CT003_reduzir_quantidade_para_uma_unidade(page):
    prepare_cart_with_three_units(page)
    row = open_cart_row(page, PRODUCT_AVAILABLE)

    quantity = row.get_by_label(UI["quantity_label"], exact=True)
    expect(quantity).to_have_value("3", timeout=ACTION_TIMEOUT_MS)

    unit_price = read_money(
        row.get_by_test_id(UI["unit_price_test_id"])
    )
    cart_total = page.get_by_test_id(UI["cart_total_test_id"])
    expect_money(cart_total, unit_price * Decimal("3"))

    quantity.fill("1")
    quantity.press("Tab")

    expect(quantity).to_have_value("1", timeout=ACTION_TIMEOUT_MS)
    expect_money(cart_total, unit_price)
    assert read_money(cart_total) == unit_price


def test_CT004_restringir_tres_unidades_de_thor_hammer(page):
    open_product(page, PRODUCT_RESTRICTED)

    submit_quantity(page, 3)

    expect(
        page.get_by_text(RESTRICTION_MESSAGE, exact=True)
    ).to_be_visible(timeout=ACTION_TIMEOUT_MS)
