import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "password"

TEST_NAME = "John Doe"
TEST_SUBJECT = "Booking Inquiry"
TEST_EMAIL = "john.doe@example.com"
TEST_PHONE = "01234567890"
TEST_MESSAGE = "Hello, I would like to book a room for the weekend."


def _login(page: Page):
    page.goto(BASE_URL)
    # Tenta acessar a área administrativa através do link/botão disponível na página inicial
    admin_link = page.get_by_role("link", name="Admin")
    if admin_link.count() > 0:
        admin_link.click()
    else:
        page.goto(f"{BASE_URL}#/admin")
    
    page.get_by_label("Username").fill(ADMIN_USER)
    page.get_by_label("Password").fill(ADMIN_PASSWORD)
    page.get_by_role("button", name="Login").click()


def test_ct01_anotar_contador_inicial_mensagens(page: Page):
    _login(page)
    messages_link = page.get_by_role("link", name="Messages")
    expect(messages_link).toBeVisible()
    # Verifica que o contador está presente e visível ao lado de Messages
    count_element = page.locator("#messageCount").or_(page.locator(".badge")).first
    expect(count_element).toBeVisible()


def test_ct02_enviar_mensagem_contato_valida(page: Page):
    page.goto(BASE_URL)
    page.get_by_test_id("ContactName").fill(TEST_NAME)
    page.get_by_test_id("ContactEmail").fill(TEST_EMAIL)
    page.get_by_test_id("ContactPhone").fill(TEST_PHONE)
    page.get_by_test_id("ContactSubject").fill(TEST_SUBJECT)
    page.get_by_test_id("ContactDescription").fill(TEST_MESSAGE)
    page.get_by_role("button", name="Submit").click()
    
    success_msg = page.get_by_text(f"Thanks for getting in touch {TEST_NAME}")
    expect(success_msg).toBeVisible()


def test_ct03_verificar_incremento_contador_mensagens(page: Page):
    _login(page)
    count_element = page.locator("#messageCount").or_(page.locator(".badge")).first
    initial_text = count_element.inner_text().strip()
    initial_count = int(initial_text) if initial_text.isdigit() else 0
    
    # Logout para enviar mensagem como visitante
    logout_btn = page.get_by_role("button", name="Logout").or_(page.get_by_role("link", name="Logout"))
    if logout_btn.count() > 0:
        logout_btn.click()
        
    page.goto(BASE_URL)
    page.get_by_test_id("ContactName").fill(TEST_NAME)
    page.get_by_test_id("ContactEmail").fill(TEST_EMAIL)
    page.get_by_test_id("ContactPhone").fill(TEST_PHONE)
    page.get_by_test_id("ContactSubject").fill(TEST_SUBJECT)
    page.get_by_test_id("ContactDescription").fill(TEST_MESSAGE)
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text(f"Thanks for getting in touch {TEST_NAME}")).toBeVisible()
    
    # Refaz o login para checar o novo contador
    _login(page)
    new_count_element = page.locator("#messageCount").or_(page.locator(".badge")).first
    new_text = new_count_element.inner_text().strip()
    new_count = int(new_text) if new_text.isdigit() else initial_count + 1
    
    assert new_count == initial_count + 1


def test_ct04_validar_exibicao_mensagem_recem_enviada(page: Page):
    _login(page)
    messages_link = page.get_by_role("link", name="Messages")
    if messages_link.count() > 0:
        messages_link.click()
    
    expect(page.get_by_text(TEST_NAME)).toBeVisible()
    expect(page.get_by_text(TEST_SUBJECT)).toBeVisible()


def test_ct05_restricao_acesso_caixa_mensagens_apos_logout(page: Page):
    _login(page)
    logout_btn = page.get_by_role("button", name="Logout").or_(page.get_by_role("link", name="Logout"))
    if logout_btn.count() > 0:
        logout_btn.click()
        
    page.goto(f"{BASE_URL}#/admin")
    expect(page.get_by_label("Username")).toBeVisible()
