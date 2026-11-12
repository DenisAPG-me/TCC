import re

from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online"
USUARIO_ADMIN = "admin"
SENHA_ADMIN = "password"
SENHA_INCORRETA = "senha_incorreta"
MENSAGEM_ERRO_LOGIN = "Invalid credentials"
QUARTO_ESPERADO = "101"
TIPO_QUARTO_ESPERADO = "Single"
MENU_ESPERADO = ["Rooms", "Report", "Branding", "Messages"]


def _abrir_login(page: Page) -> None:
    page.goto(f"{BASE_URL}/admin")
    expect(page.get_by_label("Username")).to_be_visible()


def _submeter_login(page: Page, usuario: str, senha: str) -> None:
    page.get_by_label("Username").fill(usuario)
    page.get_by_label("Password").fill(senha)
    page.get_by_role("button", name="Login").click()


def _fazer_login(page: Page) -> None:
    _abrir_login(page)
    _submeter_login(page, USUARIO_ADMIN, SENHA_ADMIN)
    expect(page).to_have_url(re.compile(r"/admin/rooms"))


def _fazer_logout(page: Page) -> None:
    page.get_by_role("link", name="Logout").click()
    expect(page).to_have_url(re.compile(rf"^{re.escape(BASE_URL)}/?$"))


def test_ct01_login_com_usuario_e_senha_vazios(page: Page) -> None:
    _abrir_login(page)
    _submeter_login(page, "", "")
    expect(page.get_by_text(MENSAGEM_ERRO_LOGIN)).to_be_visible()
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/admin/?$"))


def test_ct02_login_com_senha_incorreta(page: Page) -> None:
    _abrir_login(page)
    _submeter_login(page, USUARIO_ADMIN, SENHA_INCORRETA)
    expect(page.get_by_text(MENSAGEM_ERRO_LOGIN)).to_be_visible()
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/admin/?$"))


def test_ct03_login_com_senha_e_usuario_vazio(page: Page) -> None:
    _abrir_login(page)
    _submeter_login(page, "", SENHA_ADMIN)
    expect(page.get_by_text(MENSAGEM_ERRO_LOGIN)).to_be_visible()
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/admin/?$"))


def test_ct04_login_com_senha_em_caixa_diferente(page: Page) -> None:
    _abrir_login(page)
    _submeter_login(page, USUARIO_ADMIN, SENHA_ADMIN.upper())
    expect(page.get_by_text(MENSAGEM_ERRO_LOGIN)).to_be_visible()
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/admin/?$"))


def test_ct05_login_com_credenciais_validas(page: Page) -> None:
    _abrir_login(page)
    _submeter_login(page, USUARIO_ADMIN, SENHA_ADMIN)
    expect(page).to_have_url(re.compile(r"/admin/rooms"))
    expect(
        page.get_by_role("row")
        .filter(has_text=QUARTO_ESPERADO)
        .filter(has_text=TIPO_QUARTO_ESPERADO)
    ).to_be_visible()
    for item in MENU_ESPERADO:
        expect(page.get_by_role("link", name=item, exact=True)).to_be_visible()


def test_ct06_logout_retorna_home_publica(page: Page) -> None:
    _fazer_login(page)
    _fazer_logout(page)
    expect(page.get_by_label("Username")).to_have_count(0)


def test_ct07_acesso_direto_lista_quartos_apos_logout(page: Page) -> None:
    _fazer_login(page)
    _fazer_logout(page)
    page.goto(f"{BASE_URL}/admin/rooms")
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page).not_to_have_url(re.compile(r"/admin/rooms"))
