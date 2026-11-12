import re

from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"
CLAW_HAMMER = "Claw Hammer"
THOR_HAMMER = "Thor Hammer"
ADDED_MESSAGE = "Product added to shopping cart."
THOR_LIMIT_MESSAGE = "You can only have one Thor Hammer in the cart."


def parse_price(text: str) -> float:
    return round(float(re.sub(r"[^\d.]", "", text)), 2)


def open_product(page: Page, name: str) -> None:
    page.goto(BASE_URL)
    page.get_by_role("link", name=name).first.click()
    expect(page.get_by_role("heading", name=name)).to_be_visible()


def add_to_cart(page: Page, name: str, quantity: int) -> None:
    open_product(page, name)
    page.get_by_label("Quantity").fill(str(quantity))
    page.get_by_role("button", name="Add to cart").click()


def open_cart(page: Page) -> None:
    page.get_by_test_id("nav-cart").click()
    expect(page.get_by_role("heading", name="Shopping Cart")).to_be_visible()


def test_TC01_adicionar_3_unidades_exibe_confirmacao_e_badge(page: Page) -> None:
    add_to_cart(page, CLAW_HAMMER, 3)
    expect(page.get_by_text(ADDED_MESSAGE, exact=True)).to_be_visible()
    expect(page.get_by_test_id("cart-quantity")).to_have_text("3")


def test_TC02_total_linha_e_total_carrinho_igual_preco_x3(page: Page) -> None:
    add_to_cart(page, CLAW_HAMMER, 3)
    open_cart(page)
    expect(page.get_by_test_id("line-price")).to_be_visible()
    unit_price = parse_price(page.get_by_test_id("product-price").inner_text())
    line_total = parse_price(page.get_by_test_id("line-price").inner_text())
    expect.poll(lambda: parse_price(page.get_by_test_id("cart-total").inner_text())).to_equal(line_total)
    assert line_total == round(unit_price * 3, 2)


def test_TC03_alterar_quantidade_para_1_ajusta_total_ao_preco_unitario(page: Page) -> None:
    add_to_cart(page, CLAW_HAMMER, 3)
    open_cart(page)
    expect(page.get_by_test_id("product-quantity")).to_have_value("3")
    unit_price = parse_price(page.get_by_test_id("product-price").inner_text())
    page.get_by_test_id("product-quantity").fill("1")
    page.get_by_role("button", name="Update").click()
    expect(page.get_by_test_id("product-quantity")).to_have_value("1")
    expect.poll(lambda: parse_price(page.get_by_test_id("cart-total").inner_text())).to_equal(unit_price)


def test_TC04_adicionar_3_thor_hammer_exibe_mensagem_de_limite(page: Page) -> None:
    add_to_cart(page, THOR_HAMMER, 3)
    expect(page.get_by_text(THOR_LIMIT_MESSAGE, exact=True)).to_be_visible()


def test_TC05_tentativa_rejeitada_thor_hammer_nao_altera_carrinho(page: Page) -> None:
    add_to_cart(page, THOR_HAMMER, 3)
    expect(page.get_by_text(THOR_LIMIT_MESSAGE, exact=True)).to_be_visible()
    expect(page.get_by_test_id("cart-quantity")).to_have_text("0")


def test_TC06_adicionar_1_thor_hammer_e_aceito(page: Page) -> None:
    add_to_cart(page, THOR_HAMMER, 1)
    expect(page.get_by_text(ADDED_MESSAGE, exact=True)).to_be_visible()
    expect(page.get_by_test_id("cart-quantity")).to_have_text("1")
