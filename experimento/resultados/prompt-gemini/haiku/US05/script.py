import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online"
ADMIN_URL = f"{BASE_URL}/admin"
ROOMS_URL = f"{BASE_URL}/admin/rooms"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "password"


def fazer_login(page: Page, usuario: str, senha: str) -> None:
    page.goto(ADMIN_URL)
    page.get_by_label("Username").fill(usuario)
    page.get_by_label("Password").fill(senha)
    page.get_by_role("button", name="Login").click()


def verificar_tela_login(page: Page) -> None:
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()
    expect(page.get_by_role("button", name="Login")).to_be_visible()


def test_CT01_login_com_campos_vazios_exibe_erro(page: Page) -> None:
    fazer_login(page, "", "")
    expect(page.get_by_text("Invalid credentials")).to_be_visible()
    verificar_tela_login(page)


def test_CT02_login_com_usuario_preenchido_e_senha_vazia_exibe_erro(page: Page) -> None:
    fazer_login(page, ADMIN_USER, "")
    expect(page.get_by_text("Invalid credentials")).to_be_visible()
    verificar_tela_login(page)


def test_CT03_login_com_usuario_vazio_e_senha_preenchida_exibe_erro(page: Page) -> None:
    fazer_login(page, "", ADMIN_PASSWORD)
    expect(page.get_by_text("Invalid credentials")).to_be_visible()
    verificar_tela_login(page)


def test_CT04_login_com_senha_incorreta_exibe_erro(page: Page) -> None:
    fazer_login(page, ADMIN_USER, "senha-incorreta")
    expect(page.get_by_text("Invalid credentials")).to_be_visible()
    verificar_tela_login(page)


def test_CT05_login_com_usuario_inexistente_exibe_erro(page: Page) -> None:
    fazer_login(page, "usuario-inexistente", ADMIN_PASSWORD)
    expect(page.get_by_text("Invalid credentials")).to_be_visible()
    verificar_tela_login(page)


def test_CT06_login_com_senha_em_caixa_diferente_exibe_erro(page: Page) -> None:
    fazer_login(page, ADMIN_USER, "Password")
    expect(page.get_by_text("Invalid credentials")).to_be_visible()
    verificar_tela_login(page)


def test_CT07_login_com_senha_com_espaco_extra_exibe_erro(page: Page) -> None:
    fazer_login(page, ADMIN_USER, "password ")
    expect(page.get_by_text("Invalid credentials")).to_be_visible()
    verificar_tela_login(page)


def test_CT08_login_valido_exibe_lista_de_quartos_e_menu(page: Page) -> None:
    fazer_login(page, ADMIN_USER, ADMIN_PASSWORD)
    expect(page).to_have_url(re.compile(r"/admin/rooms/?$"))
    expect(
        page.get_by_role("row").filter(has_text="101").filter(has_text="Single")
    ).to_be_visible()
    for item in ["Rooms", "Report", "Branding", "Messages"]:
        expect(page.get_by_role("link", name=item, exact=True)).to_be_visible()


def test_CT09_logout_retorna_a_pagina_inicial_publica(page: Page) -> None:
    fazer_login(page, ADMIN_USER, ADMIN_PASSWORD)
    page.get_by_text("Logout", exact=True).click()
    expect(page).to_have_url(re.compile(rf"^{re.escape(BASE_URL)}/?$"))


def test_CT10_acesso_direto_a_lista_de_quartos_apos_logout_exibe_login(page: Page) -> None:
    fazer_login(page, ADMIN_USER, ADMIN_PASSWORD)
    page.get_by_text("Logout", exact=True).click()
    expect(page).to_have_url(re.compile(rf"^{re.escape(BASE_URL)}/?$"))
    page.goto(ROOMS_URL)
    verificar_tela_login(page)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
