import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"

def test_TC01_adicionar_quantidade_valida_ao_carrinho(page: Page):
    page.goto(BASE_URL)
    page.get_by_text("Claw Hammer").first.click()
    
    quantity_input = page.get_by_label("Quantity")
    quantity_input.fill("3")
    
    page.get_by_role("button", name="Add to cart").click()
    
    expect(page.get_by_text("Product added to shopping cart.")).toBeVisible()
    expect(page.locator("[data-test='nav-cart']")).to_contain_text("3")

def test_TC02_validar_calculo_total_linha_e_carrinho(page: Page):
    page.goto(BASE_URL)
    page.get_by_text("Claw Hammer").first.click()
    
    quantity_input = page.get_by_label("Quantity")
    quantity_input.fill("3")
    page.get_by_role("button", name="Add to cart").click()
    
    page.get_by_test_id("nav-cart").click()
    
    unit_price = float(page.locator("data-test='product-price'").inner_text().replace("$", ""))
    line_total = float(page.locator("data-test='line-price'").inner_text().replace("$", ""))
    cart_total = float(page.locator("data-test='cart-total'").inner_text().replace("$", ""))
    
    assert line_total == unit_price * 3
    assert cart_total == line_total

def test_TC03_alterar_quantidade_no_carrinho(page: Page):
    page.goto(BASE_URL)
    page.get_by_text("Claw Hammer").first.click()
    
    quantity_input = page.get_by_label("Quantity")
    quantity_input.fill("3")
    page.get_by_role("button", name="Add to cart").click()
    
    page.get_by_test_id("nav-cart").click()
    
    unit_price = float(page.locator("data-test='product-price'").inner_text().replace("$", ""))
    
    cart_quantity_input = page.get_by_role("spinbutton", name="Quantity")
    cart_quantity_input.fill("1")
    
    cart_total = float(page.locator("data-test='cart-total'").inner_text().replace("$", ""))
    assert cart_total == unit_price

def test_TC04_tentar_adicionar_mais_de_uma_unidade_thor_hammer(page: Page):
    page.goto(BASE_URL)
    page.get_by_text("Thor Hammer").first.click()
    
    quantity_input = page.get_by_label("Quantity")
    quantity_input.fill("3")
    
    page.get_by_role("button", name="Add to cart").click()
    
    expect(page.get_by_text("You can only have one Thor Hammer in the cart.")).toBeVisible()
