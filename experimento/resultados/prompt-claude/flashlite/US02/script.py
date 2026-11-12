import re
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"


def test_ct01_adicionar_claw_hammer_com_quantidade_3_ao_carrinho(page: Page):
    page.goto(BASE_URL)
    page.get_by_text("Claw Hammer", exact=True).click()
    
    quantity_input = page.get_by_label("Quantity")
    quantity_input.fill("3")
    
    page.get_by_role("button", name=re.compile("Add to cart", re.IGNORECASE)).click()
    
    expect(page.get_by_text("Product added to shopping cart.")).toBeVisible()
    expect(page.locator("[data-test='nav-cart']")).to_contain_text("3")


def test_ct02_validar_total_da_linha_e_total_do_carrinho_com_3_unidades(page: Page):
    page.goto(BASE_URL)
    page.get_by_text("Claw Hammer", exact=True).click()
    
    quantity_input = page.get_by_label("Quantity")
    quantity_input.fill("3")
    
    page.get_by_role("button", name=re.compile("Add to cart", re.IGNORECASE)).click()
    expect(page.get_by_text("Product added to shopping cart.")).toBeVisible()
    
    page.locator("[data-test='nav-cart']").click()
    
    unit_price_text = page.locator("[data-test='product-price']").inner_text()
    unit_price = float(unit_price_text.replace("$", "").strip())
    
    line_total_text = page.locator("[data-test='line-price']").inner_text()
    line_total = float(line_total_text.replace("$", "").strip())
    
    cart_total_text = page.locator("[data-test='cart-total']").inner_text()
    cart_total = float(cart_total_text.replace("$", "").strip())
    
    assert line_total == unit_price * 3
    assert cart_total == line_total


def test_ct03_alterar_quantidade_no_carrinho_de_3_para_1(page: Page):
    page.goto(BASE_URL)
    page.get_by_text("Claw Hammer", exact=True).click()
    
    quantity_input = page.get_by_label("Quantity")
    quantity_input.fill("3")
    
    page.get_by_role("button", name=re.compile("Add to cart", re.IGNORECASE)).click()
    expect(page.get_by_text("Product added to shopping cart.")).toBeVisible()
    
    page.locator("[data-test='nav-cart']").click()
    
    unit_price_text = page.locator("[data-test='product-price']").inner_text()
    unit_price = float(unit_price_text.replace("$", "").strip())
    
    cart_quantity_input = page.locator("[data-test='product-quantity']")
    cart_quantity_input.fill("1")
    cart_quantity_input.press("Enter")
    
    cart_total_text = page.locator("[data-test='cart-total']").inner_text()
    cart_total = float(cart_total_text.replace("$", "").strip())
    
    assert cart_total == unit_price


def test_ct04_tentar_adicionar_3_unidades_de_thor_hammer_ao_carrinho(page: Page):
    page.goto(BASE_URL)
    page.get_by_text("Thor Hammer", exact=True).click()
    
    quantity_input = page.get_by_label("Quantity")
    quantity_input.fill("3")
    
    page.get_by_role("button", name=re.compile("Add to cart", re.IGNORECASE)).click()
    
    expect(page.get_by_text("You can only have one Thor Hammer in the cart.")).toBeVisible()
