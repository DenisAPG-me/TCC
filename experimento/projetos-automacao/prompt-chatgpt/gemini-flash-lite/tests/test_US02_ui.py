import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"


def test_CT001_adicionar_produto_com_quantidade_especifica(page: Page) -> None:
    page.goto(BASE_URL)
    page.get_by_text("Claw Hammer").first.click()
    quantity_input = page.get_by_label("Quantity")
    quantity_input.fill("3")
    page.get_by_role("button", name="Add to cart").click()
    expect(page.get_by_text("Product added to shopping cart.")).to_be_visible()
    expect(page.locator("[data-test='nav-cart']")).to_contain_text("3")


def test_CT002_verificar_total_da_linha_e_do_carrinho(page: Page) -> None:
    page.goto(BASE_URL)
    page.get_by_text("Claw Hammer").first.click()
    page.get_by_label("Quantity").fill("3")
    page.get_by_role("button", name="Add to cart").click()
    page.locator("[data-test='nav-cart']").click()
    
    unit_price_text = page.locator("data-test='product-price'").inner_text()
    unit_price = float(unit_price_text.replace("$", "").strip())
    
    line_total_text = page.locator("data-test='line-total'").inner_text()
    line_total = float(line_total_text.replace("$", "").strip())
    
    cart_total_text = page.locator("data-test='cart-total'").inner_text()
    cart_total = float(cart_total_text.replace("$", "").strip())
    
    assert line_total == unit_price * 3
    assert cart_total == line_total


def test_CT003_alterar_quantidade_no_carrinho_para_um(page: Page) -> None:
    page.goto(BASE_URL)
    page.get_by_text("Claw Hammer").first.click()
    page.get_by_label("Quantity").fill("3")
    page.get_by_role("button", name="Add to cart").click()
    page.locator("[data-test='nav-cart']").click()
    
    unit_price_text = page.locator("data-test='product-price'").inner_text()
    unit_price = float(unit_price_text.replace("$", "").strip())
    
    quantity_input = page.locator("data-test='product-quantity'")
    quantity_input.fill("1")
    
    cart_total_text = page.locator("data-test='cart-total'").inner_text()
    cart_total = float(cart_total_text.replace("$", "").strip())
    
    assert cart_total == unit_price


def test_CT004_tentar_adicionar_mais_de_uma_unidade_thor_hammer(page: Page) -> None:
    page.goto(BASE_URL)
    page.get_by_text("Thor Hammer").first.click()
    page.get_by_label("Quantity").fill("3")
    page.get_by_role("button", name="Add to cart").click()
    expect(page.get_by_text("You can only have one Thor Hammer in the cart.")).to_be_visible()
