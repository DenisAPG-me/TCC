import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online"

def test_ct01_login_empty_credentials(page: Page):
    page.goto(f"{BASE_URL}/admin")
    
    username_input = page.get_by_placeholder("Username")
    password_input = page.get_by_placeholder("Password")
    login_button = page.get_by_role("button", name="Login")
    
    username_input.fill("")
    password_input.fill("")
    login_button.click()
    
    expect(page.get_by_text("Invalid credentials")).toBeVisible()
    expect(page).to_have_url(f"{BASE_URL}/admin")

def test_ct02_login_incorrect_password(page: Page):
    page.goto(f"{BASE_URL}/admin")
    
    username_input = page.get_by_placeholder("Username")
    password_input = page.get_by_placeholder("Password")
    login_button = page.get_by_role("button", name="Login")
    
    username_input.fill("admin")
    password_input.fill("wrongpassword")
    login_button.click()
    
    expect(page.get_by_text("Invalid credentials")).toBeVisible()
    expect(page).to_have_url(f"{BASE_URL}/admin")

def test_ct03_login_success(page: Page):
    page.goto(f"{BASE_URL}/admin")
    
    username_input = page.get_by_placeholder("Username")
    password_input = page.get_by_placeholder("Password")
    login_button = page.get_by_role("button", name="Login")
    
    username_input.fill("admin")
    password_input.fill("password")
    login_button.click()
    
    expect(page.get_by_text("Rooms")).toBeVisible()
    expect(page.get_by_text("Report")).toBeVisible()
    expect(page.get_by_text("Branding")).toBeVisible()
    expect(page.get_by_text("Messages")).toBeVisible()
    
    expect(page.get_by_text("101")).toBeVisible()
    expect(page.get_by_text("Single")).toBeVisible()

def test_ct04_logout(page: Page):
    page.goto(f"{BASE_URL}/admin")
    
    username_input = page.get_by_placeholder("Username")
    password_input = page.get_by_placeholder("Password")
    login_button = page.get_by_role("button", name="Login")
    
    username_input.fill("admin")
    password_input.fill("password")
    login_button.click()
    
    expect(page.get_by_text("Rooms")).toBeVisible()
    
    logout_button = page.get_by_role("button", name="Logout")
    if logout_button.count() == 0:
        logout_button = page.get_by_text("Logout")
    logout_button.click()
    
    expect(page).to_have_url(f"{BASE_URL}/")

def test_ct05_direct_access_after_logout(page: Page):
    page.goto(f"{BASE_URL}/admin")
    
    username_input = page.get_by_placeholder("Username")
    password_input = page.get_by_placeholder("Password")
    login_button = page.get_by_role("button", name="Login")
    
    username_input.fill("admin")
    password_input.fill("password")
    login_button.click()
    
    expect(page.get_by_text("Rooms")).toBeVisible()
    
    logout_button = page.get_by_role("button", name="Logout")
    if logout_button.count() == 0:
        logout_button = page.get_by_text("Logout")
    logout_button.click()
    
    expect(page).to_have_url(f"{BASE_URL}/")
    
    page.goto(f"{BASE_URL}/admin")
    expect(page.get_by_placeholder("Username")).toBeVisible()
    expect(page.get_by_placeholder("Password")).toBeVisible()
