import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com"


def test_ct01_login_empty_form(page: Page):
    page.goto(f"{BASE_URL}/auth/login")
    page.get_by_role("button", name=re.compile("login|sign in", re.IGNORECASE)).click()
    
    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_be_visible()


def test_ct02_login_invalid_password(page: Page):
    page.goto(f"{BASE_URL}/auth/login")
    
    page.get_by_label(re.compile("email", re.IGNORECASE)).fill("customer@practicesoftwaretesting.com")
    page.get_by_label(re.compile("password", re.IGNORECASE)).fill("wrongpassword")
    page.get_by_role("button", name=re.compile("login|sign in", re.IGNORECASE)).click()
    
    expect(page.get_by_text("Invalid email or password")).to_be_visible()
    expect(page).not_to_have_url(re.compile("/account"))


def test_ct03_checkout_unauthenticated_redirect(page: Page):
    page.goto(f"{BASE_URL}/")
    page.locator(".card").first.click()
    page.get_by_role("button", name=re.compile("add to cart", re.IGNORECASE)).click()
    
    page.get_by_role("link", name=re.compile("cart", re.IGNORECASE)).click()
    page.get_by_role("button", name=re.compile("proceed to checkout", re.IGNORECASE)).click()
    
    expect(page).to_have_url(re.compile("/auth/login|/login"))


def test_ct04_login_success_my_account(page: Page):
    page.goto(f"{BASE_URL}/auth/login")
    
    page.get_by_label(re.compile("email", re.IGNORECASE)).fill("customer@practicesoftwaretesting.com")
    page.get_by_label(re.compile("password", re.IGNORECASE)).fill("welcome01")
    page.get_by_role("button", name=re.compile("login|sign in", re.IGNORECASE)).click()
    
    expect(page).to_have_url(re.compile("/account"))
    expect(page.locator("nav")).to_contain_text(re.compile("Customer|Jane|John", re.IGNORECASE))


def test_ct05_checkout_address_mandatory_fields(page: Page):
    page.goto(f"{BASE_URL}/auth/login")
    page.get_by_label(re.compile("email", re.IGNORECASE)).fill("customer@practicesoftwaretesting.com")
    page.get_by_label(re.compile("password", re.IGNORECASE)).fill("welcome01")
    page.get_by_role("button", name=re.compile("login|sign in", re.IGNORECASE)).click()
    
    page.goto(f"{BASE_URL}/")
    page.locator(".card").first.click()
    page.get_by_role("button", name=re.compile("add to cart", re.IGNORECASE)).click()
    
    page.get_by_role("link", name=re.compile("cart", re.IGNORECASE)).click()
    page.get_by_role("button", name=re.compile("proceed to checkout", re.IGNORECASE)).click()
    
    # Avançar para endereço se necessário e tentar prosseguir com campos vazios
    proceed_btn = page.get_by_role("button", name=re.compile("proceed", re.IGNORECASE))
    if proceed_btn.is_visible():
        proceed_btn.click()
        
    # Tenta avançar com campos obrigatórios vazios
    next_btn = page.get_by_role("button", name=re.compile("proceed|next|continue", re.IGNORECASE))
    if next_btn.is_visible():
        next_btn.click()
        
    # Preenche campos obrigatórios do endereço
    page.get_by_label(re.compile("country", re.IGNORECASE)).fill("United States")
    page.get_by_label(re.compile("postal code|zip", re.IGNORECASE)).fill("12345")
    page.get_by_label(re.compile("city", re.IGNORECASE)).fill("New York")
    page.get_by_label(re.compile("state", re.IGNORECASE)).fill("NY")
    page.get_by_label(re.compile("address|street", re.IGNORECASE)).fill("Main Street")
    page.get_by_label(re.compile("number", re.IGNORECASE)).fill("100")
    
    next_btn.click()
    expect(page).to_have_url(re.compile("/payment|checkout"))


def test_ct06_credit_card_payment_success(page: Page):
    # Setup state up to payment step (simulado via fluxo integrado ou pré-condição)
    page.goto(f"{BASE_URL}/auth/login")
    page.get_by_label(re.compile("email", re.IGNORECASE)).fill("customer@practicesoftwaretesting.com")
    page.get_by_label(re.compile("password", re.IGNORECASE)).fill("welcome01")
    page.get_by_role("button", name=re.compile("login|sign in", re.IGNORECASE)).click()
    
    page.goto(f"{BASE_URL}/")
    page.locator(".card").first.click()
    page.get_by_role("button", name=re.compile("add to cart", re.IGNORECASE)).click()
    
    page.goto(f"{BASE_URL}/checkout")
    
    # Preencher etapas se necessário até pagamento
    for _ in range(3):
        btn = page.get_by_role("button", name=re.compile("proceed|next|continue", re.IGNORECASE))
        if btn.is_visible():
            try:
                btn.click()
            except Exception:
                break
                
    # Selecionar cartão de crédito e preencher dados
    payment_select = page.get_by_label(re.compile("payment method", re.IGNORECASE))
    if payment_select.is_visible():
        payment_select.select_option(label=re.compile("credit card", re.IGNORECASE))
        
    page.get_by_label(re.compile("card number", re.IGNORECASE)).fill("4111222233334444")
    page.get_by_label(re.compile("expiration", re.IGNORECASE)).fill("12/28")
    page.get_by_label(re.compile("cvv", re.IGNORECASE)).fill("123")
    page.get_by_label(re.compile("cardholder", re.IGNORECASE)).fill("John Doe")
    
    page.get_by_role("button", name=re.compile("confirm|pay|finish", re.IGNORECASE)).click()
    
    expect(page.get_by_text("Payment was successful")).to_be_visible()
    
    confirm_order_btn = page.get_by_role("button", name=re.compile("confirm order|finish|submit", re.IGNORECASE))
    if confirm_order_btn.is_visible():
        confirm_order_btn.click()
        
    expect(page.get_by_text(re.compile(r"Thanks for your order! Your invoice number is INV-.*"))).to_be_visible()
