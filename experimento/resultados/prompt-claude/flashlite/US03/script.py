import re
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"
DEMO_EMAIL = "customer@practicesoftwaretesting.com"
DEMO_PASSWORD = "welcome01"


def test_ct01_login_com_campos_vazios(page: Page) -> None:
    page.goto(BASE_URL)
    page.get_by_role("link", name=re.compile("Sign in", re.IGNORECASE)).click()
    page.get_by_role("button", name=re.compile("Login", re.IGNORECASE)).click()
    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_be_visible()


def test_ct02_login_senha_incorreta(page: Page) -> None:
    page.goto(BASE_URL)
    page.get_by_role("link", name=re.compile("Sign in", re.IGNORECASE)).click()
    page.get_by_label(re.compile("Email", re.IGNORECASE)).fill(DEMO_EMAIL)
    page.get_by_label(re.compile("Password", re.IGNORECASE)).fill("senhaerrada")
    page.get_by_role("button", name=re.compile("Login", re.IGNORECASE)).click()
    expect(page.get_by_text("Invalid email or password")).to_be_visible()
    expect(page.get_by_role("link", name=re.compile("Sign in", re.IGNORECASE))).to_be_visible()


def test_ct03_checkout_sem_autenticacao(page: Page) -> None:
    page.goto(BASE_URL)
    page.locator(".card").first.click()
    page.get_by_role("button", name=re.compile("Add to cart", re.IGNORECASE)).click()
    page.get_by_role("link", name=re.compile("Cart", re.IGNORECASE)).click()
    page.get_by_role("button", name=re.compile("Proceed to checkout", re.IGNORECASE)).click()
    expect(page.get_by_label(re.compile("Email", re.IGNORECASE))).to_be_visible()
    expect(page.get_by_label(re.compile("Password", re.IGNORECASE))).to_be_visible()


def test_ct04_visualizacao_my_account(page: Page) -> None:
    page.goto(BASE_URL)
    page.get_by_role("link", name=re.compile("Sign in", re.IGNORECASE)).click()
    page.get_by_label(re.compile("Email", re.IGNORECASE)).fill(DEMO_EMAIL)
    page.get_by_label(re.compile("Password", re.IGNORECASE)).fill(DEMO_PASSWORD)
    page.get_by_role("button", name=re.compile("Login", re.IGNORECASE)).click()
    expect(page.get_by_role("link", name=re.compile("My account", re.IGNORECASE))).to_be_visible()


def test_ct05_validacao_campos_endereco_checkout(page: Page) -> None:
    page.goto(BASE_URL)
    page.get_by_role("link", name=re.compile("Sign in", re.IGNORECASE)).click()
    page.get_by_label(re.compile("Email", re.IGNORECASE)).fill(DEMO_EMAIL)
    page.get_by_label(re.compile("Password", re.IGNORECASE)).fill(DEMO_PASSWORD)
    page.get_by_role("button", name=re.compile("Login", re.IGNORECASE)).click()

    page.goto(BASE_URL)
    page.locator(".card").first.click()
    page.get_by_role("button", name=re.compile("Add to cart", re.IGNORECASE)).click()
    page.get_by_role("link", name=re.compile("Cart", re.IGNORECASE)).click()
    page.get_by_role("button", name=re.compile("Proceed to checkout", re.IGNORECASE)).click()

    # Passo de login no checkout se necessário
    if page.get_by_label(re.compile("Email", re.IGNORECASE)).is_visible():
        page.get_by_label(re.compile("Email", re.IGNORECASE)).fill(DEMO_EMAIL)
        page.get_by_label(re.compile("Password", re.IGNORECASE)).fill(DEMO_PASSWORD)
        page.get_by_role("button", name=re.compile("Login", re.IGNORECASE)).click()

    page.get_by_role("button", name=re.compile("Proceed", re.IGNORECASE)).click()

    # Tenta avançar com campos vazios no endereço
    page.get_by_role("button", name=re.compile("Proceed", re.IGNORECASE)).click()
    expect(page.get_by_text(re.compile("required", re.IGNORECASE)).first).to_be_visible()

    # Preenche os campos obrigatórios: país, CEP, número, rua, cidade, estado
    page.get_by_label(re.compile("Address", re.IGNORECASE)).fill("Rua Teste")
    page.get_by_label(re.compile("City", re.IGNORECASE)).fill("Cidade Exemplo")
    page.get_by_label(re.compile("State", re.IGNORECASE)).fill("Estado Exemplo")
    page.get_by_label(re.compile("Country", re.IGNORECASE)).fill("Brasil")
    page.get_by_label(re.compile("Postal code", re.IGNORECASE)).fill("01000000")
    page.get_by_role("button", name=re.compile("Proceed", re.IGNORECASE)).click()


def test_ct06_pagamento_com_cartao_de_credito(page: Page) -> None:
    page.goto(BASE_URL)
    page.get_by_role("link", name=re.compile("Sign in", re.IGNORECASE)).click()
    page.get_by_label(re.compile("Email", re.IGNORECASE)).fill(DEMO_EMAIL)
    page.get_by_label(re.compile("Password", re.IGNORECASE)).fill(DEMO_PASSWORD)
    page.get_by_role("button", name=re.compile("Login", re.IGNORECASE)).click()

    page.goto(BASE_URL)
    page.locator(".card").first.click()
    page.get_by_role("button", name=re.compile("Add to cart", re.IGNORECASE)).click()
    page.get_by_role("link", name=re.compile("Cart", re.IGNORECASE)).click()
    page.get_by_role("button", name=re.compile("Proceed to checkout", re.IGNORECASE)).click()

    if page.get_by_label(re.compile("Email", re.IGNORECASE)).is_visible():
        page.get_by_label(re.compile("Email", re.IGNORECASE)).fill(DEMO_EMAIL)
        page.get_by_label(re.compile("Password", re.IGNORECASE)).fill(DEMO_PASSWORD)
        page.get_by_role("button", name=re.compile("Login", re.IGNORECASE)).click()

    # Avançar endereço
    page.get_by_role("button", name=re.compile("Proceed", re.IGNORECASE)).click()
    if page.get_by_label(re.compile("Address", re.IGNORECASE)).is_visible():
        page.get_by_label(re.compile("Address", re.IGNORECASE)).fill("Rua Teste")
        page.get_by_label(re.compile("City", re.IGNORECASE)).fill("Cidade Exemplo")
        page.get_by_label(re.compile("State", re.IGNORECASE)).fill("Estado Exemplo")
        page.get_by_label(re.compile("Country", re.IGNORECASE)).fill("Brasil")
        page.get_by_label(re.compile("Postal code", re.IGNORECASE)).fill("01000000")
        page.get_by_role("button", name=re.compile("Proceed", re.IGNORECASE)).click()

    # Selecionar pagamento com cartão de crédito e preencher dados fictícios válidos
    page.select_option("select[id*='payment'], select[name*='payment'], select", label=re.compile("Credit Card", re.IGNORECASE))
    page.get_by_label(re.compile("Card number", re.IGNORECASE)).fill("4242424242424242")
    page.get_by_label(re.compile("Expiration date", re.IGNORECASE)).fill("12/28")
    page.get_by_label(re.compile("CVV", re.IGNORECASE)).fill("123")
    page.get_by_label(re.compile("Card holder name", re.IGNORECASE)).fill("Cliente Teste")

    page.get_by_role("button", name=re.compile("Confirm", re.IGNORECASE)).click()

    expect(page.get_by_text("Payment was successful")).to_be_visible()
    page.get_by_role("button", name=re.compile("Confirm", re.IGNORECASE)).click()
    expect(page.get_by_text(re.compile("Thanks for your order! Your invoice number is INV-"))).to_be_visible()
