import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"


def test_ct01_adicionar_produto_quantidade_personalizada(page: Page):
    page.goto(BASE_URL)
    page.get_by_text("Claw Hammer").first.click()
    
    quantity_input = page.get_by_label("Quantity")
    quantity_input.fill("3")
    
    page.get_by_role("button", name="Add to cart").click()
    
    expect(page.get_by_text("Product added to shopping cart.")).toBeVisible()
    expect(page.get_by_test_id("nav-cart")).to_have_text("3")


def test_ct02_validar_total_linha_e_carrinho(page: Page):
    page.goto(BASE_URL)
    page.get_by_text("Claw Hammer").first.click()
    
    quantity_input = page.get_by_label("Quantity")
    quantity_input.fill("3")
    page.get_by_role("button", name="Add to cart").click()
    
    page.get_by_test_id("nav-cart").click()
    
    unit_price_text = page.get_by_test_id("product-price").inner_text()
    unit_price = float(unit_price_text.replace("$", "").strip())
    
    line_total_text = page.get_by_test_id("line-price").inner_text()
    line_total = float(line_total_text.replace("$", "").strip())
    
    cart_total_text = page.get_by_test_id("cart-total").inner_text()
    cart_total = float(cart_total_text.replace("$", "").strip())
    
    assert line_total == unit_price * 3
    assert cart_total == line_total


def test_ct03_reduzir_quantidade_no_carrinho(page: Page):
    page.goto(BASE_URL)
    page.get_by_text("Claw Hammer").first.click()
    
    quantity_input = page.get_by_label("Quantity")
    quantity_input.fill("3")
    page.get_by_role("button", name="Add to cart").click()
    
    page.get_by_test_id("nav-cart").click()
    
    unit_price_text = page.get_by_test_id("product-price").inner_text()
    unit_price = float(unit_price_text.replace("$", "").strip())
    
    cart_quantity_input = page.get_by_test_id("product-quantity")
    cart_quantity_input.fill("1")
    cart_quantity_input.press("Enter")
    
    cart_total_text = page.get_by_test_id("cart-total").inner_text()
    cart_total = float(cart_total_text.replace("$", "").strip())
    
    assert cart_total == unit_price


def test_ct04_adicionar_mais_de_uma_unidade_thor_hammer(page: Page):
    page.goto(BASE_URL)
    page.get_by_text("Thor Hammer").first.click()
    
    quantity_input = page.get_by_label("Quantity")
    quantity_input.fill("3")
    
    page.get_by_role("button", name="Add to cart").click()
    
    expect(page.get_by_text("You can only have one Thor Hammer in the cart.")).toBeVisible()
