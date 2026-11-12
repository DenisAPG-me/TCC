import re
import uuid

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "password"
TELEFONE_VALIDO = "01234567890"
MENSAGEM_VALIDA = "Gostaria de saber sobre disponibilidade para o fim de semana."


def sufixo() -> str:
    return uuid.uuid4().hex[:6]


def login_admin(page: Page, usuario: str = ADMIN_USER, senha: str = ADMIN_PASSWORD) -> None:
    page.goto(BASE_URL + "admin")
    page.get_by_label("Username").fill(usuario)
    page.get_by_label("Password").fill(senha)
    page.get_by_role("button", name="Login").click()


def logout_admin(page: Page) -> None:
    page.get_by_role("link", name="Logout").click()


def contador_messages(page: Page) -> int:
    texto = page.get_by_role("link", name=re.compile("Messages")).inner_text()
    return int(re.search(r"\d+", texto).group())


def enviar_contato(
    page: Page,
    nome: str,
    email: str,
    assunto: str,
    mensagem: str,
    telefone: str = TELEFONE_VALIDO,
) -> None:
    page.goto(BASE_URL)
    page.get_by_label("Name").fill(nome)
    page.get_by_label("Email").fill(email)
    page.get_by_label("Phone").fill(telefone)
    page.get_by_label("Subject").fill(assunto)
    page.get_by_label("Message").fill(mensagem)
    page.get_by_role("button", name="Submit").click()


def test_CT01_admin_visualiza_contador_messages_apos_login(page: Page) -> None:
    login_admin(page)
    expect(page.get_by_role("link", name=re.compile("Messages"))).to_be_visible()
    assert contador_messages(page) >= 0


def test_CT02_visitante_recebe_confirmacao_ao_enviar_contato_valido(page: Page) -> None:
    nome = f"Visitante{sufixo()}"
    enviar_contato(
        page,
        nome,
        f"{nome.lower()}@exemplo.com",
        f"Reserva {sufixo()}",
        MENSAGEM_VALIDA,
    )
    expect(page.get_by_text(f"Thanks for getting in touch {nome}!")).to_be_visible()


def test_CT03_contador_messages_aumenta_em_uma_unidade_apos_envio(page: Page) -> None:
    nome = f"Visitante{sufixo()}"
    login_admin(page)
    antes = contador_messages(page)
    logout_admin(page)

    enviar_contato(
        page,
        nome,
        f"{nome.lower()}@exemplo.com",
        f"Reserva {sufixo()}",
        MENSAGEM_VALIDA,
    )
    expect(page.get_by_text(f"Thanks for getting in touch {nome}!")).to_be_visible()

    login_admin(page)
    depois = contador_messages(page)
    assert depois == antes + 1


def test_CT04_admin_ve_mensagem_recem_enviada_na_caixa(page: Page) -> None:
    nome = f"Visitante{sufixo()}"
    assunto = f"Reserva {sufixo()}"
    enviar_contato(page, nome, f"{nome.lower()}@exemplo.com", assunto, MENSAGEM_VALIDA)
    expect(page.get_by_text(f"Thanks for getting in touch {nome}!")).to_be_visible()

    login_admin(page)
    page.get_by_role("link", name=re.compile("Messages")).click()
    linha = page.get_by_role("row").filter(has_text=nome).filter(has_text=assunto)
    expect(linha).to_be_visible()


def test_CT05_acesso_direto_a_messages_apos_logout_exige_login(page: Page) -> None:
    login_admin(page)
    logout_admin(page)
    page.goto(BASE_URL + "admin/messages")
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_role("button", name="Login")).to_be_visible()


def test_CT06_login_com_senha_incorreta_nao_libera_painel(page: Page) -> None:
    login_admin(page, senha="senha-invalida")
    expect(page.get_by_role("button", name="Login")).to_be_visible()
    expect(page.get_by_role("link", name=re.compile("Messages"))).to_have_count(0)


def test_CT07_envio_sem_nome_e_rejeitado(page: Page) -> None:
    enviar_contato(page, "", f"{sufixo()}@exemplo.com", f"Reserva {sufixo()}", MENSAGEM_VALIDA)
    expect(page.get_by_text("Name may not be blank")).to_be_visible()
    expect(page.get_by_text(re.compile("Thanks for getting in touch"))).to_have_count(0)


def test_CT08_envio_com_email_invalido_e_rejeitado(page: Page) -> None:
    enviar_contato(page, f"Visitante{sufixo()}", "email-invalido", f"Reserva {sufixo()}", MENSAGEM_VALIDA)
    expect(page.get_by_text(re.compile("well-formed email"))).to_be_visible()
    expect(page.get_by_text(re.compile("Thanks for getting in touch"))).to_have_count(0)


def test_CT09_assunto_com_quatro_caracteres_e_rejeitado(page: Page) -> None:
    enviar_contato(page, f"Visitante{sufixo()}", f"{sufixo()}@exemplo.com", "Abcd", MENSAGEM_VALIDA)
    expect(page.get_by_text(re.compile(r"Subject .*between 5 and 100 characters"))).to_be_visible()
    expect(page.get_by_text(re.compile("Thanks for getting in touch"))).to_have_count(0)


def test_CT10_assunto_com_cinco_caracteres_e_aceito(page: Page) -> None:
    nome = f"Visitante{sufixo()}"
    enviar_contato(page, nome, f"{nome.lower()}@exemplo.com", "Preco", MENSAGEM_VALIDA)
    expect(page.get_by_text(f"Thanks for getting in touch {nome}!")).to_be_visible()


def test_CT11_mensagem_com_dezenove_caracteres_e_rejeitada(page: Page) -> None:
    enviar_contato(page, f"Visitante{sufixo()}", f"{sufixo()}@exemplo.com", f"Reserva {sufixo()}", "x" * 19)
    expect(page.get_by_text(re.compile(r"Message .*between 20 and 2000 characters"))).to_be_visible()
    expect(page.get_by_text(re.compile("Thanks for getting in touch"))).to_have_count(0)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
