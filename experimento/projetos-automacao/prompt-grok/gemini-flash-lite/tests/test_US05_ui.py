import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online"

def test_TC01_empty_credentials(page: Page):
    page.goto(f"{BASE_URL}/admin")
    
    # Tentativa de login com campos vazios
    # Assumindo campos de input de usuário e senha e botão de login
    page.get_by_label("Username").fill("")
    page.get_by_label("Password").fill("")
    page.get_by_role("button", name="Login").click()
    
    # Validação de que a mensagem de erro é exibida e continua na tela de login
    expect(page.get_by_text("Invalid credentials")).to_be_visible()
    expect(page).to_have_url(f"{BASE_URL}/admin")

def test_TC02_incorrect_password(page: Page):
    page.goto(f"{BASE_URL}/admin")
    
    # Tentativa de login com senha incorreta
    page.get_by_label("Username").fill("admin")
    page.get_by_label("Password").fill("wrongpassword")
    page.get_by_role("button", name="Login").click()
    
    # Validação de que a mensagem de erro é exibida
    expect(page.get_by_text("Invalid credentials")).to_be_visible()

def test_TC03_successful_login(page: Page):
    page.goto(f"{BASE_URL}/admin")
    
    # Login com credenciais válidas
    page.get_by_label("Username").fill("admin")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()
    
    # Validação da lista de quartos, quarto 101 do tipo Single e menu completo
    expect(page.get_by_text("101")).to_be_visible()
    expect(page.get_by_text("Single")).to_be_visible()
    expect(page.get_by_text("Rooms")).to_be_visible()
    expect(page.get_by_text("Report")).to_be_visible()
    expect(page.get_by_text("Branding")).to_be_visible()
    expect(page.get_by_text("Messages")).to_be_visible()

def test_TC04_logout(page: Page):
    page.goto(f"{BASE_URL}/admin")
    
    # Realiza login para depois fazer logout
    page.get_by_label("Username").fill("admin")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()
    
    # Clica em Logout
    page.get_by_role("link", name="Logout").click()
    
    # Valida retorno à página inicial pública
    expect(page).to_have_url(f"{BASE_URL}/")

def test_TC05_direct_access_after_logout(page: Page):
    page.goto(f"{BASE_URL}/admin")
    
    # Login e posterior logout
    page.get_by_label("Username").fill("admin")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()
    page.get_by_role("link", name="Logout").click()
    
    # Tenta acessar diretamente a área administrativa restrita
    page.goto(f"{BASE_URL}/admin")
    
    # Valida que é redirecionado ou vê novamente a tela de login
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()
