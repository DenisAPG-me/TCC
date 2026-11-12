import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

def login_admin(page: Page):
    page.goto(f"{BASE_URL}admin")
    page.get_by_label("Username").fill("admin")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()

def test_TC01_anotar_contador_inicial_mensagens(page: Page):
    login_admin(page)
    messages_indicator = page.get_by_text("Messages")
    expect(messages_indicator).to_be_visible()

def test_TC02_envio_mensagem_formulario_contato(page: Page):
    page.goto(BASE_URL)
    page.get_by_label("Name").fill("Visitante Teste")
    page.get_by_label("Email").fill("visitante@teste.com")
    page.get_by_label("Phone").fill("12345678901")
    page.get_by_label("Subject").fill("Reserva de Quarto")
    page.get_by_label("Message").fill("Gostaria de obter mais informações sobre a disponibilidade.")
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("Thanks for getting in touch Visitante Teste!")).to_be_visible()

def test_TC03_verificar_incremento_contador_mensagens(page: Page):
    login_admin(page)
    messages_badge = page.locator(".badge, [class*='message']").first
    expect(messages_badge).to_be_visible()

def test_TC04_verificar_mensagem_na_lista_admin(page: Page):
    login_admin(page)
    page.get_by_role("link", name="Messages").click()
    expect(page.get_by_text("Visitante Teste")).to_be_visible()
    expect(page.get_by_text("Reserva de Quarto")).to_be_visible()

def test_TC05_logout_e_restricao_acesso(page: Page):
    login_admin(page)
    logout_button = page.get_by_role("button", name="Logout")
    if logout_button.is_visible():
        logout_button.click()
    page.goto(f"{BASE_URL}admin")
    expect(page.get_by_label("Username")).to_be_visible()
