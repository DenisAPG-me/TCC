import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

@pytest.mark.playwright
def test_CT001_login_vazio(page: Page):
    page.goto(BASE_URL + "admin")
    login_button = page.get_by_role("button", name=re.compile("Login|Log In", re.IGNORECASE))
    login_button.click()
    error_message = page.get_by_text("Invalid credentials")
    expect(error_message).to_be_visible()
    expect(page).to_url(re.compile(r"/admin"))

@pytest.mark.playwright
def test_CT002_login_senha_incorreta(page: Page):
    page.goto(BASE_URL + "admin")
    username_input = page.get_by_label(re.compile("username", re.IGNORECASE)).or_(page.locator("#username"))
    password_input = page.get_by_label(re.compile("password", re.IGNORECASE)).or_(page.locator("#password"))
    
    username_input.fill("admin")
    password_input.fill("senha_errada")
    
    login_button = page.get_by_role("button", name=re.compile("Login|Log In", re.IGNORECASE))
    login_button.click()
    
    error_message = page.get_by_text("Invalid credentials")
    expect(error_message).to_be_visible()

@pytest.mark.playwright
def test_CT003_login_valido_e_painel(page: Page):
    page.goto(BASE_URL + "admin")
    username_input = page.get_by_label(re.compile("username", re.IGNORECASE)).or_(page.locator("#username"))
    password_input = page.get_by_label(re.compile("password", re.IGNORECASE)).or_(page.locator("#password"))
    
    username_input.fill("admin")
    password_input.fill("password")
    
    login_button = page.get_by_role("button", name=re.compile("Login|Log In", re.IGNORECASE))
    login_button.click()
    
    room_number = page.get_by_text("101")
    room_type = page.get_by_text("Single")
    expect(room_number).to_be_visible()
    expect(room_type).to_be_visible()
    
    expect(page.get_by_text("Rooms")).to_be_visible()
    expect(page.get_by_text("Report")).to_be_visible()
    expect(page.get_by_text("Branding")).to_be_visible()
    expect(page.get_by_text("Messages")).to_be_visible()

@pytest.mark.playwright
def test_CT004_logout(page: Page):
    page.goto(BASE_URL + "admin")
    username_input = page.get_by_label(re.compile("username", re.IGNORECASE)).or_(page.locator("#username"))
    password_input = page.get_by_label(re.compile("password", re.IGNORECASE)).or_(page.locator("#password"))
    
    username_input.fill("admin")
    password_input.fill("password")
    
    login_button = page.get_by_role("button", name=re.compile("Login|Log In", re.IGNORECASE))
    login_button.click()
    
    expect(page.get_by_text("Rooms")).to_be_visible()
    
    logout_element = page.get_by_role("link", name=re.compile("Logout", re.IGNORECASE)).or_(page.get_by_text("Logout"))
    logout_element.click()
    
    expect(page).to_url(re.compile(r"^https://automationintesting\.online/(?:index\.html)?$"))

@pytest.mark.playwright
def test_CT005_acesso_direto_apos_logout(page: Page):
    page.goto(BASE_URL + "admin")
    username_input = page.get_by_label(re.compile("username", re.IGNORECASE)).or_(page.locator("#username"))
    password_input = page.get_by_label(re.compile("password", re.IGNORECASE)).or_(page.locator("#password"))
    
    username_input.fill("admin")
    password_input.fill("password")
    
    login_button = page.get_by_role("button", name=re.compile("Login|Log In", re.IGNORECASE))
    login_button.click()
    
    expect(page.get_by_text("Rooms")).to_be_visible()
    
    logout_element = page.get_by_role("link", name=re.compile("Logout", re.IGNORECASE)).or_(page.get_by_text("Logout"))
    logout_element.click()
    
    page.goto(BASE_URL + "admin")
    
    login_btn_visible = page.get_by_role("button", name=re.compile("Login|Log In", re.IGNORECASE))
    expect(login_btn_visible).to_be_visible()
