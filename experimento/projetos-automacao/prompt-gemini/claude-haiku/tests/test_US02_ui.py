import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com"

CONFIRMATION_MSG = "Product added to shopping cart."
THOR_HAMMER_MSG = "You can only have one Thor Hammer in the cart."

CART_BADGE = '[data-test="cart-quantity"]'
UNIT_PRICE = '[data-test="unit-price"]'
LINE_PRICE = '[data-test="line-price"]'
CART_TOTAL = '[data-test="cart-total"]'


def money(value: float) -> re.Pattern:
    text = f"{value:.2f}"
    return re.compile(rf"^\D*{re.escape(text)}\s*$")


def parse_money(text: str) -> float:
    return float(re.sub(r"[^\d.]", "", text))


def open_product(page: Page, name: str) -> None:
    page.goto(BASE_URL)
    page.get_by_role("link", name=name).click()
    expect(page.get_by_role("heading", name=name)).to_be_visible()


def read_unit_price(page: Page) -> float:
    price = page.locator(UNIT_PRICE)
    expect(price).not_to_be_empty()
    return parse_money(price.inner_text())


def add_to_cart(page: Page, quantity: str | None = None) -> None:
    if quantity is not None:
        page.get_by_label("Quantity").fill(quantity)
    page.get_by_role("button", name="Add to cart").click()


def open_cart(page: Page) -> None:
    page.get_by_role("link", name=re.compile("Cart")).click()
    expect(page.get_by_role("spinbutton")).to_be_visible()


def test_TC01_adicionar_3_claw_hammer_exibe_confirmacao_e_badge(page: Page):
    open_product(page, "Claw Hammer")
    add_to_cart(page, "3")
    expect(page.get_by_text(CONFIRMATION_MSG)).to_be_visible()
    expect(page.locator(CART_BADGE)).to_have_text("3")


def test_TC02_linha_e_total_do_carrinho_igual_preco_vezes_3(page: Page):
    open_product(page, "Claw Hammer")
    unit = read_unit_price(page)
    add_to_cart(page, "3")
    expect(page.get_by_text(CONFIRMATION_MSG)).to_be_visible()
    open_cart(page)
    expected = round(unit * 3, 2)
    expect(page.locator(LINE_PRICE)).to_have_text(money(expected))
    expect(page.locator(CART_TOTAL)).to_have_text(money(expected))


def test_TC03_alterar_quantidade_para_1_total_igual_preco_unitario(page: Page):
    open_product(page, "Claw Hammer")
    unit = read_unit_price(page)
    add_to_cart(page, "3")
    expect(page.get_by_text(CONFIRMATION_MSG)).to_be_visible()
    open_cart(page)
    page.get_by_role("spinbutton").fill("1")
    page.get_by_role("button", name="Update").click()
    expect(page.locator(CART_TOTAL)).to_have_text(money(unit))


def test_TC04_thor_hammer_3_unidades_exibe_mensagem_de_limite(page: Page):
    open_product(page, "Thor Hammer")
    add_to_cart(page, "3")
    expect(page.get_by_text(THOR_HAMMER_MSG)).to_be_visible()


def test_TC05_quantidade_padrao_1_ao_adicionar_sem_alterar(page: Page):
    open_product(page, "Claw Hammer")
    expect(page.get_by_label("Quantity")).to_have_value("1")
    add_to_cart(page)
    expect(page.get_by_text(CONFIRMATION_MSG)).to_be_visible()
    expect(page.locator(CART_BADGE)).to_have_text("1")


def test_TC06_quantidade_zero_nao_adiciona_ao_carrinho(page: Page):
    open_product(page, "Claw Hammer")
    add_to_cart(page, "0")
    expect(page.get_by_text(CONFIRMATION_MSG)).to_have_count(0)


def test_TC07_thor_hammer_1_unidade_e_aceito(page: Page):
    open_product(page, "Thor Hammer")
    add_to_cart(page, "1")
    expect(page.get_by_text(CONFIRMATION_MSG)).to_be_visible()
    expect(page.locator(CART_BADGE)).to_have_text("1")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
