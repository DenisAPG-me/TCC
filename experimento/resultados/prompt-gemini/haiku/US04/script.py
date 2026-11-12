import re

from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

NOME = "Maria Silva"
EMAIL = "maria@exemplo.com"
TELEFONE = "11999999999"
ASSUNTO = "Dúvida sobre reserva"
MENSAGEM = "Gostaria de saber sobre disponibilidade para o fim de semana."


def enviar_formulario(
    page: Page,
    nome: str = NOME,
    email: str = EMAIL,
    telefone: str = TELEFONE,
    assunto: str = ASSUNTO,
    mensagem: str = MENSAGEM,
) -> None:
    page.goto(BASE_URL)
    page.get_by_label("Name", exact=True).fill(nome)
    page.get_by_label("Email", exact=True).fill(email)
    page.get_by_label("Phone", exact=True).fill(telefone)
    page.get_by_label("Subject", exact=True).fill(assunto)
    page.get_by_label("Message", exact=True).fill(mensagem)
    page.get_by_role("button", name="Submit").click()


def verificar_confirmacao(page: Page, nome: str, assunto: str) -> None:
    expect(page.get_by_text(f"Thanks for getting in touch {nome}!")).to_be_visible()
    expect(page.get_by_text(assunto)).to_be_visible()


def test_CT01_envio_vazio_exibe_mensagens_de_campos_obrigatorios(page: Page) -> None:
    enviar_formulario(page, "", "", "", "", "")
    for campo in ["Name", "Email", "Phone", "Subject", "Message"]:
        expect(page.get_by_text(re.compile(rf"{campo}.*blank"))).to_be_visible()


def test_CT02_telefone_com_10_caracteres_exibe_erro(page: Page) -> None:
    enviar_formulario(page, telefone="1" + "9" * 9)
    expect(page.get_by_text("Phone must be between 11 and 21 characters.")).to_be_visible()


def test_CT03_telefone_com_11_caracteres_e_aceito(page: Page) -> None:
    enviar_formulario(page, telefone="1" + "9" * 10)
    verificar_confirmacao(page, NOME, ASSUNTO)


def test_CT04_telefone_com_21_caracteres_e_aceito(page: Page) -> None:
    enviar_formulario(page, telefone="1" + "9" * 20)
    verificar_confirmacao(page, NOME, ASSUNTO)


def test_CT05_telefone_com_22_caracteres_exibe_erro(page: Page) -> None:
    enviar_formulario(page, telefone="1" + "9" * 21)
    expect(page.get_by_text("Phone must be between 11 and 21 characters.")).to_be_visible()


def test_CT06_assunto_com_4_caracteres_exibe_erro(page: Page) -> None:
    enviar_formulario(page, assunto="Dica")
    expect(page.get_by_text("Subject must be between 5 and 100 characters.")).to_be_visible()


def test_CT07_assunto_com_5_caracteres_e_aceito(page: Page) -> None:
    enviar_formulario(page, assunto="Preço")
    verificar_confirmacao(page, NOME, "Preço")


def test_CT08_assunto_com_101_caracteres_exibe_erro(page: Page) -> None:
    enviar_formulario(page, assunto="a" * 101)
    expect(page.get_by_text("Subject must be between 5 and 100 characters.")).to_be_visible()


def test_CT09_mensagem_com_19_caracteres_exibe_erro(page: Page) -> None:
    enviar_formulario(page, mensagem="a" * 19)
    expect(page.get_by_text("Message must be between 20 and 2000 characters.")).to_be_visible()


def test_CT10_mensagem_com_20_caracteres_e_aceita(page: Page) -> None:
    enviar_formulario(page, mensagem="a" * 20)
    verificar_confirmacao(page, NOME, ASSUNTO)


def test_CT11_mensagem_com_2001_caracteres_exibe_erro(page: Page) -> None:
    enviar_formulario(page, mensagem="a" * 2001)
    expect(page.get_by_text("Message must be between 20 and 2000 characters.")).to_be_visible()


def test_CT12_email_malformado_exibe_erro(page: Page) -> None:
    enviar_formulario(page, email="bad")
    expect(page.get_by_text("must be a well-formed email address")).to_be_visible()


def test_CT13_dados_validos_enviam_mensagem_com_confirmacao(page: Page) -> None:
    enviar_formulario(page)
    verificar_confirmacao(page, NOME, ASSUNTO)
