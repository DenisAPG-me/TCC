import re
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"

def test_TC01_login_empty_fields(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("link", name=re.compile("Sign in", re.IGNORECASE)).click()
    page.get_by_role("button", name=re.compile("Login", re.IGNORECASE)).click()
    
    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_be_visible()

def test_TC02_login_invalid_password(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("link", name=re.compile("Sign in", re.IGNORECASE)).click()
    
    page.get_by_label(re.compile("Email", re.IGNORECASE)).fill("customer@practicesoftwaretesting.com")
    page.get_by_label(re.compile("Password", re.IGNORECASE)).fill("wrongpassword")
    page.get_by_role("button", name=re.compile("Login", re.IGNORECASE)).click()
    
    expect(page.get_by_text("Invalid email or password")).to_be_visible()
    expect(page).not_to_have_url(re.compile("dashboard|account"))

def test_TC03_checkout_unauthenticated_redirects_to_login(page: Page):
    page.goto(BASE_URL)
    # Seleciona o primeiro produto disponível na listagem inicial
    page.locator(".card").first.click()
    page.get_by_role("button", name=re.compile("Add to cart", re.IGNORECASE)).click()
    
    # Vai para o carrinho e avança para o checkout
    page.get_by_role("link", name=re.compile("Cart", re.IGNORECASE)).click()
    page.get_by_role("button", name=re.compile("Proceed to checkout", re.IGNORECASE)).click()
    
    expect(page.get_by_text(re.compile("Sign in your account", re.IGNORECASE))).to_be_visible()
    expect(page.get_by_label(re.compile("Email", re.IGNORECASE))).to_be_visible()
    expect(page.get_by_label(re.compile("Password", re.IGNORECASE))).to_be_visible()

def test_TC04_successful_login_my_account(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("link", name=re.compile("Sign in", re.IGNORECASE)).click()
    
    page.get_by_label(re.compile("Email", re.IGNORECASE)).fill("customer@practicesoftwaretesting.com")
    page.get_by_label(re.compile("Password", re.IGNORECASE)).fill("welcome01")
    page.get_by_role("button", name=re.compile("Login", re.IGNORECASE)).click()
    
    # Verifica redirecionamento para a página My account e exibição do nome no menu/página
    expect(page).to_have_url(re.compile("account"))
    expect(page.get_by_role("heading", name=re.compile("My account", re.IGNORECASE))).to_be_visible()
    expect(page.locator("nav")).to_contain_text(re.compile("Jane Doe|Customer", re.IGNORECASE))

def test_TC05_checkout_address_mandatory_fields(page: Page):
    # Realiza login prévio
    page.goto(f"{BASE_URL}auth/login")
    page.get_by_label(re.compile("Email", re.IGNORECASE)).fill("customer@practicesoftwaretesting.com")
    page.get_by_label(re.compile("Password", re.IGNORECASE)).fill("welcome01")
    page.get_by_role("button", name=re.compile("Login", re.IGNORECASE)).click()
    
    # Adiciona produto e vai para checkout
    page.goto(BASE_URL)
    page.locator(".card").first.click()
    page.get_by_role("button", name=re.compile("Add to cart", re.IGNORECASE)).click()
    page.get_by_role("link", name=re.compile("Cart", re.IGNORECASE)).click()
    page.get_by_role("button", name=re.compile("Proceed to checkout", re.IGNORECASE)).click()
    
    # Avança para o passo de endereço se necessário
    if page.get_by_role("button", name=re.compile("Proceed to checkout", re.IGNORECASE)).is_visible():
        page.get_by_role("button", name=re.compile("Proceed to checkout", re.IGNORECASE)).click()
        
    # Tenta avançar com campos de endereço vazios
    proceed_btn = page.get_by_role("button", name=re.compile("Proceed to checkout|Next", re.IGNORECASE))
    proceed_btn.click()
    expect(page).not_to_have_url(re.compile("payment"))
    
    # Preenche os campos obrigatórios do endereço (país, CEP, número, rua, cidade, estado)
    page.get_by_label(re.compile("Street", re.IGNORECASE)).fill("Main Street 123")
    page.get_by_label(re.compile("City", re.IGNORECASE)).fill("New York")
    page.get_by_label(re.compile("State", re.IGNORECASE)).fill("NY")
    page.get_by_label(re.compile("Country", re.IGNORECASE)).fill("United States")
    page.get_by_label(re.compile("Postal code|ZIP", re.IGNORECASE)).fill("10001")
    
    proceed_btn.click()
    expect(page).to_have_url(re.compile("payment"))

def test_TC06_checkout_credit_card_payment_success(page: Page):
    # Realiza login
    page.goto(f"{BASE_URL}auth/login")
    page.get_by_label(re.compile("Email", re.IGNORECASE)).fill("customer@practicesoftwaretesting.com")
    page.get_by_label(re.compile("Password", re.IGNORECASE)).fill("welcome01")
    page.get_by_role("button", name=re.compile("Login", re.IGNORECASE)).click()
    
    # Adiciona produto, vai para o carrinho e prossegue até o pagamento
    page.goto(BASE_URL)
    page.locator(".card").first.click()
    page.get_by_role("button", name=re.compile("Add to cart", re.IGNORECASE)).click()
    page.get_by_role("link", name=re.compile("Cart", re.IGNORECASE)).click()
    
    # Processo de checkout (passos sucessivos)
    page.get_by_role("button", name=re.compile("Proceed to checkout", re.IGNORECASE)).click()
    if page.get_by_role("button", name=re.compile("Proceed to checkout", re.IGNORECASE)).is_visible():
        page.get_by_role("button", name=re.compile("Proceed to checkout", re.IGNORECASE)).click()
        
    # Preenche endereço se solicitado
    street_input = page.get_by_label(re.compile("Street", re.IGNORECASE))
    if street_input.is_visible() and not street_input.input_value():
        street_input.fill("Main Street 123")
        page.get_by_label(re.compile("City", re.IGNORECASE)).fill("New York")
        page.get_by_label(re.compile("State", re.IGNORECASE)).fill("NY")
        page.get_by_label(re.compile("Country", re.IGNORECASE)).fill("United States")
        page.get_by_label(re.compile("Postal code|ZIP", re.IGNORECASE)).fill("10001")
    
    # Avança para pagamento
    next_btn = page.get_by_role("button", name=re.compile("Proceed to checkout|Next", re.IGNORECASE))
    if next_btn.is_visible():
        next_btn.click()
        
    # Escolhe pagamento por cartão de crédito
    payment_select = page.get_by_label(re.compile("Payment method", re.IGNORECASE))
    if payment_select.is_visible():
        payment_select.select_option(label=re.compile("Credit Card", re.IGNORECASE))
    
    # Preenche dados fictícios válidos do cartão
    card_number = page.get_by_label(re.compile("Card number", re.IGNORECASE))
    if card_number.is_visible():
        card_number.fill("4242424242424242")
        page.get_by_label(re.compile("Expiration date", re.IGNORECASE)).fill("12/28")
        page.get_by_label(re.compile("CVV", re.IGNORECASE)).fill("123")
        page.get_by_label(re.compile("Cardholder name", re.IGNORECASE)).fill("Jane Doe")
        
    # Confirma o pagamento e o pedido
    page.get_by_role("button", name=re.compile("Confirm|Finish|Pay", re.IGNORECASE)).click()
    
    expect(page.get_by_text("Payment was successful")).to_be_visible()
    
    confirm_order_btn = page.get_by_role("button", name=re.compile("Confirm order|Place order", re.IGNORECASE))
    if confirm_order_btn.is_visible():
        confirm_order_btn.click()
        
    expect(page.get_by_text(re.compile(r"Thanks for your order! Your invoice number is INV-.*"))).to_be_visible()
