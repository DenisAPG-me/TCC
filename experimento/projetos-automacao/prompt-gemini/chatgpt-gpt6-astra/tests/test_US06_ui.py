"""
Arquivo: test_mensagens.py

Instalação:
    pip install pytest playwright pytest-playwright
    python -m playwright install chromium

Execução sequencial:
    python -m pytest test_mensagens.py --browser chromium -v

Os seletores são hipóteses documentadas e precisam ser confirmados
na aplicação antes da execução.
"""

import re
from dataclasses import dataclass
from uuid import uuid4

from playwright.sync_api import Page, expect


BASE_URL = "https://automationintesting.online"
ADMIN_URL = f"{BASE_URL}/admin"
UI_TIMEOUT_MS = 15_000

expect.set_options(timeout=UI_TIMEOUT_MS)


@dataclass(frozen=True)
class Mensagem:
    nome: str
    email: str
    telefone: str
    assunto: str
    texto: str


def nova_mensagem(prefixo_nome: str = "Visitante Teste") -> Mensagem:
    identificador = uuid4().hex[:12]
    return Mensagem(
        nome=f"{prefixo_nome} {identificador}",
        email=f"visitante.{identificador}@example.com",
        telefone="11987654321",
        assunto=f"Consulta de hospedagem {identificador}",
        texto=(
            "Gostaria de informações sobre disponibilidade e tarifas "
            f"para uma estadia de duas noites. Referência {identificador}."
        ),
    )


def link_messages(page: Page):
    return page.get_by_role(
        "link",
        name=re.compile(r"^Messages\b"),
    )


def contador_messages(page: Page):
    return link_messages(page).locator(".badge")


def tabela_messages(page: Page):
    return page.get_by_role("table", name="Messages", exact=True)


def verificar_login_visivel(page: Page) -> None:
    expect(page.get_by_label("Username", exact=True)).to_be_visible()
    expect(page.get_by_label("Password", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Login", exact=True)).to_be_visible()


def autenticar(page: Page) -> None:
    page.goto(ADMIN_URL)
    verificar_login_visivel(page)
    page.get_by_label("Username", exact=True).fill("admin")
    page.get_by_label("Password", exact=True).fill("password")
    page.get_by_role("button", name="Login", exact=True).click()
    expect(link_messages(page)).to_be_visible()
    expect(page.get_by_role("button", name="Logout", exact=True)).to_be_visible()


def sair(page: Page) -> None:
    page.get_by_role("button", name="Logout", exact=True).click()
    # Confirma o término do logout mesmo se ele levar à página inicial.
    page.goto(ADMIN_URL)
    verificar_login_visivel(page)


def registrar_contador(page: Page) -> int:
    contador = contador_messages(page)
    expect(contador).to_be_visible()
    expect(contador).to_have_text(re.compile(r"^\s*[0-9]+\s*$"))
    return int(contador.inner_text().strip())


def verificar_contador(page: Page, esperado: int) -> None:
    expect(contador_messages(page)).to_have_text(
        re.compile(rf"^\s*{esperado}\s*$")
    )


def enviar_mensagem(page: Page, mensagem: Mensagem) -> None:
    page.goto(f"{BASE_URL}/")
    page.get_by_label("Name", exact=True).fill(mensagem.nome)
    page.get_by_label("Email", exact=True).fill(mensagem.email)
    page.get_by_label("Phone", exact=True).fill(mensagem.telefone)
    page.get_by_label("Subject", exact=True).fill(mensagem.assunto)
    page.get_by_label("Message", exact=True).fill(mensagem.texto)
    page.get_by_role("button", name="Submit", exact=True).click()


def verificar_confirmacao(page: Page, mensagem: Mensagem) -> None:
    expect(
        page.get_by_text(
            f"Thanks for getting in touch {mensagem.nome}!",
            exact=True,
        )
    ).to_be_visible()


def abrir_messages(page: Page) -> str:
    link_messages(page).click()
    expect(tabela_messages(page)).to_be_visible()
    return page.url


def test_CT01_registrar_contador_de_mensagens(page: Page) -> None:
    autenticar(page)

    contador_inicial = registrar_contador(page)

    verificar_contador(page, contador_inicial)


def test_CT02_confirmar_envio_valido(page: Page) -> None:
    mensagem = nova_mensagem()

    enviar_mensagem(page, mensagem)

    verificar_confirmacao(page, mensagem)


def test_CT03_incrementar_contador_apos_envio(page: Page) -> None:
    autenticar(page)
    contador_inicial = registrar_contador(page)
    sair(page)

    mensagem = nova_mensagem()
    enviar_mensagem(page, mensagem)
    verificar_confirmacao(page, mensagem)

    autenticar(page)

    verificar_contador(page, contador_inicial + 1)


def test_CT04_exibir_remetente_e_assunto_na_mesma_linha(page: Page) -> None:
    mensagem = nova_mensagem()
    enviar_mensagem(page, mensagem)
    verificar_confirmacao(page, mensagem)

    autenticar(page)
    abrir_messages(page)

    linha = (
        tabela_messages(page)
        .get_by_role("row")
        .filter(
            has=page.get_by_role(
                "cell", name=mensagem.nome, exact=True
            )
        )
        .filter(
            has=page.get_by_role(
                "cell", name=mensagem.assunto, exact=True
            )
        )
    )

    expect(linha).to_have_count(1)
    expect(
        linha.get_by_role("cell", name=mensagem.nome, exact=True)
    ).to_be_visible()
    expect(
        linha.get_by_role("cell", name=mensagem.assunto, exact=True)
    ).to_be_visible()


def test_CT05_exigir_login_no_acesso_direto_apos_logout(page: Page) -> None:
    autenticar(page)
    url_messages = abrir_messages(page)
    sair(page)

    page.goto(url_messages)

    verificar_login_visivel(page)
    expect(tabela_messages(page)).not_to_be_visible()


def test_CT06_preservar_nome_com_acentos_e_apostrofo(page: Page) -> None:
    mensagem = nova_mensagem(prefixo_nome="João D'Ávila")

    enviar_mensagem(page, mensagem)

    verificar_confirmacao(page, mensagem)


def test_CT07_incrementar_em_dois_envios_consecutivos(page: Page) -> None:
    autenticar(page)
    contador_inicial = registrar_contador(page)

    for incremento in (1, 2):
        sair(page)

        mensagem = nova_mensagem()
        enviar_mensagem(page, mensagem)
        verificar_confirmacao(page, mensagem)

        autenticar(page)
        verificar_contador(page, contador_inicial + incremento)


if __name__ == "__main__":
    import sys

    import pytest

    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))
