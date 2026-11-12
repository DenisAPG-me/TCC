import re
from decimal import Decimal

from playwright.sync_api import Page, Locator, expect


BASE_URL = "https://practicesoftwaretesting.com/"
TIMEOUT_MS = 10_000
MONEY_PATTERN = re.compile(r"^\$\d+\.\d{2}$")

expect.set_options(timeout=TIMEOUT_MS)


def open_product(page: Page, product_name: str) -> None:
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.get_by_role("link", name=product_name, exact=True).click()
    expect(
        page.get_by_role("heading", name=product_name, exact=True)
    ).to_be_visible()


def add_quantity(page: Page, quantity: int) -> None:
    quantity_input = page.get_by_label("Quantity", exact=True)
    quantity_input.fill(str(quantity))
    expect(quantity_input).to_have_value(str(quantity))
    page.get_by_role("button", name="Add to cart", exact=True).click()


def expect_added(page: Page, quantity: int) -> None:
    expect(
        page.get_by_text("Product added to shopping cart.", exact=True)
    ).to_be_visible()
    expect(page.get_by_test_id("cart-quantity")).to_have_text(str(quantity))


def open_cart_row(page: Page, product_name: str) -> Locator:
    page.get_by_role("link", name="Cart", exact=True).click()
    row = page.get_by_role("row").filter(
        has=page.get_by_text(product_name, exact=True)
    )
    expect(row).to_have_count(1)
    expect(row).to_be_visible()
    return row


def read_money(locator: Locator) -> Decimal:
    expect(locator).to_be_visible()
    expect(locator).to_have_text(MONEY_PATTERN)
    return Decimal(locator.inner_text().strip().removeprefix("$"))


def money_text(amount: Decimal) -> str:
    return f"${amount:.2f}"


def prepare_claw_hammer_cart(page: Page) -> Locator:
    open_product(page, "Claw Hammer")
    add_quantity(page, 3)
    expect_added(page, 3)
    row = open_cart_row(page, "Claw Hammer")
    expect(row.get_by_label("Quantity", exact=True)).to_have_value("3")
    return row


def test_TC01_adicionar_tres_unidades(page: Page) -> None:
    open_product(page, "Claw Hammer")
    add_quantity(page, 3)
    expect_added(page, 3)


def test_TC02_calcular_totais_para_tres_unidades(page: Page) -> None:
    row = prepare_claw_hammer_cart(page)
    unit_price = read_money(row.get_by_test_id("unit-price"))
    expected_total = unit_price * Decimal("3")

    expect(row.get_by_test_id("line-total")).to_have_text(
        money_text(expected_total)
    )
    expect(page.get_by_test_id("cart-total")).to_have_text(
        money_text(expected_total)
    )


def test_TC03_reduzir_quantidade_para_uma_unidade(page: Page) -> None:
    row = prepare_claw_hammer_cart(page)
    unit_price = read_money(row.get_by_test_id("unit-price"))

    # Confirma o estado inicial antes de verificar a transição.
    expect(page.get_by_test_id("cart-total")).to_have_text(
        money_text(unit_price * Decimal("3"))
    )

    quantity_input = row.get_by_label("Quantity", exact=True)
    quantity_input.fill("1")
    quantity_input.press("Tab")

    expect(quantity_input).to_have_value("1")
    expect(page.get_by_test_id("cart-total")).to_have_text(
        money_text(unit_price)
    )


def test_TC04_rejeitar_tres_unidades_de_thor_hammer(page: Page) -> None:
    open_product(page, "Thor Hammer")
    add_quantity(page, 3)

    expect(
        page.get_by_text(
            "You can only have one Thor Hammer in the cart.",
            exact=True,
        )
    ).to_be_visible()


def test_TC05_aceitar_uma_unidade_de_thor_hammer(page: Page) -> None:
    # Expectativa inferida: o limite de uma unidade é inclusivo.
    open_product(page, "Thor Hammer")
    add_quantity(page, 1)

    row = open_cart_row(page, "Thor Hammer")
    expect(row.get_by_label("Quantity", exact=True)).to_have_value("1")
