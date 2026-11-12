import re

from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"
ADMIN_URL = BASE_URL + "admin"
ROOMS_URL = BASE_URL + "admin/rooms"
VALID_USER = "admin"
VALID_PASSWORD = "password"
INVALID_CREDENTIALS = "Invalid credentials"


def open_login(page: Page) -> None:
    page.goto(ADMIN_URL)


def submit_login(page: Page, username: str, password: str) -> None:
    page.get_by_label("Username").fill(username)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Login").click()


def login_as_admin(page: Page) -> None:
    open_login(page)
    submit_login(page, VALID_USER, VALID_PASSWORD)
    expect(page).to_have_url(ROOMS_URL)


def logout(page: Page) -> None:
    page.get_by_role("link", name="Logout").or_(
        page.get_by_role("button", name="Logout")
    ).click()


def expect_login_error(page: Page) -> None:
    expect(page.get_by_text(INVALID_CREDENTIALS)).to_be_visible()
    expect(page.get_by_role("button", name="Login")).to_be_visible()
    expect(page).not_to_have_url(ROOMS_URL)


def test_TC01_login_campos_vazios_exibe_erro(page: Page):
    open_login(page)
    submit_login(page, "", "")
    expect_login_error(page)


def test_TC02_login_senha_incorreta_exibe_erro(page: Page):
    open_login(page)
    submit_login(page, VALID_USER, "senha-incorreta")
    expect_login_error(page)


def test_TC03_login_usuario_vazio_exibe_erro(page: Page):
    open_login(page)
    submit_login(page, "", VALID_PASSWORD)
    expect_login_error(page)


def test_TC04_login_usuario_inexistente_exibe_erro(page: Page):
    open_login(page)
    submit_login(page, "usuario-inexistente", VALID_PASSWORD)
    expect_login_error(page)


def test_TC05_login_senha_vazia_exibe_erro(page: Page):
    open_login(page)
    submit_login(page, VALID_USER, "")
    expect_login_error(page)


def test_TC06_login_valido_lista_quarto_101_single(page: Page):
    login_as_admin(page)
    expect(page.get_by_role("row", name=re.compile(r"101.*Single"))).to_be_visible()


def test_TC07_menu_exibe_rooms_report_branding_messages(page: Page):
    login_as_admin(page)
    for item in ["Rooms", "Report", "Branding", "Messages"]:
        expect(page.get_by_role("link", name=item)).to_be_visible()


def test_TC08_logout_retorna_home_publica(page: Page):
    login_as_admin(page)
    logout(page)
    expect(page).to_have_url(BASE_URL)


def test_TC09_acesso_direto_lista_quartos_apos_logout_exibe_login(page: Page):
    login_as_admin(page)
    logout(page)
    page.goto(ROOMS_URL)
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_role("button", name="Login")).to_be_visible()
