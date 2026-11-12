import re
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"

def test_CT001_validacao_campos_obrigatorios_login(page: Page):
    page.goto(BASE_URL + "#/auth/login")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_be_visible()

def test_CT002_tentativa_login_senha_incorreta(page: Page):
    page.goto(BASE_URL + "#/auth/login")
    page.get_by_label("E-mail Address").fill("customer@practicesoftwaretesting.com")
    page.get_by_label("Password").fill("senhaerrada")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_text("Invalid email or password")).to_be_visible()
    expect(page).not_to_have_url(re.compile(r".*/account"))

def test_CT003_checkout_sem_autenticacao(page: Page):
    page.goto(BASE_URL)
    page.locator(".card").first.click()
    page.get_by_role("button", name="Add to cart").click()
    page.get_by_role("link", name=re.compile(r"Cart")).click()
    page.get_by_role("button", name="Proceed to checkout").click()
    expect(page).to_have_url(re.compile(r".*/auth/login"))

def test_CT004_visualizacao_my_account_apos_login(page: Page):
    page.goto(BASE_URL + "#/auth/login")
    page.get_by_label("E-mail Address").fill("customer@practicesoftwaretesting.com")
    page.get_by_label("Password").fill("welcome01")
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(re.compile(r".*/account"))
    expect(page.get_by_role("navigation")).to_contain_text("Jane Doe")

def test_CT005_validacao_campos_endereco_checkout(page: Page):
    page.goto(BASE_URL + "#/auth/login")
    page.get_by_label("E-mail Address").fill("customer@practicesoftwaretesting.com")
    page.get_by_label("Password").fill("welcome01")
    page.get_by_role("button", name="Login").click()
    
    page.goto(BASE_URL)
    page.locator(".card").first.click()
    page.get_by_role("button", name="Add to cart").click()
    page.get_by_role("link", name=re.compile(r"Cart")).click()
    page.get_by_role("button", name="Proceed to checkout").click()
    page.get_by_role("button", name="Proceed to checkout").click()
    
    page.get_by_role("button", name="Proceed to checkout").click()
    expect(page.get_by_text("Address is required")).to_be_visible()
    
    page.get_by_label("Country").fill("United States")
    page.get_by_label("State").fill("California")
    page.get_by_label("City").fill("Beverly Hills")
    page.get_by_label("Street").fill("Rodeo Drive")
    page.get_by_label("Postcode").fill("90210")
    page.get_by_label("Number").fill("123")
    
    page.get_by_role("button", name="Proceed to checkout").click()
    expect(page).not_to_have_url(re.compile(r".*/checkout.*address"))

def test_CT006_conclusao_compra_cartao_credito(page: Page):
    page.goto(BASE_URL + "#/auth/login")
    page.get_by_label("E-mail Address").fill("customer@practicesoftwaretesting.com")
    page.get_by_label("Password").fill("welcome01")
    page.get_by_role("button", name="Login").click()
    
    page.goto(BASE_URL)
    page.locator(".card").first.click()
    page.get_by_role("button", name="Add to cart").click()
    page.get_by_role("link", name=re.compile(r"Cart")).click()
    page.get_by_role("button", name="Proceed to checkout").click()
    page.get_by_role("button", name="Proceed to checkout").click()
    
    page.get_by_label("Country").fill("United States")
    page.get_by_label("State").fill("California")
    page.get_by_label("City").fill("Beverly Hills")
    page.get_by_label("Street").fill("Rodeo Drive")
    page.get_by_label("Postcode").fill("90210")
    page.get_by_label("Number").fill("123")
    page.get_by_role("button", name="Proceed to checkout").click()
    
    page.get_by_label("Payment Method").select_option("Credit Card")
    page.get_by_label("Credit Card Number").fill("4242424242424242")
    page.get_by_label("Expiration Date").fill("12/28")
    page.get_by_label("CVV").fill("123")
    page.get_by_label("Card Holder Name").fill("Jane Doe")
    
    page.get_by_role("button", name="Confirm").click()
    expect(page.get_by_text("Payment was successful")).to_be_visible()
    
    page.get_by_role("button", name="Confirm").click()
    expect(page.get_by_text(re.compile(r"Thanks for your order! Your invoice number is INV-.*"))).to_be_visible()
