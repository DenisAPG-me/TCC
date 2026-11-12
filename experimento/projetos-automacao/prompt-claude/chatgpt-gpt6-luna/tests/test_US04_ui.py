from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

NOME_VALIDO = "Ana Silva"
EMAIL_VALIDO = "ana.silva@example.com"
TELEFONE_VALIDO = "11987654321"
ASSUNTO_VALIDO = "Dúvida sobre reservas"
MENSAGEM_VALIDA = "Gostaria de saber mais sobre as opções de reserva disponíveis."


def abrir_pagina(page: Page) -> None:
    page.goto(BASE_URL)


def preencher_formulario(
    page: Page,
    *,
    nome: str = NOME_VALIDO,
    email: str = EMAIL_VALIDO,
    telefone: str = TELEFONE_VALIDO,
    assunto: str = ASSUNTO_VALIDO,
    mensagem: str = MENSAGEM_VALIDA,
) -> None:
    page.get_by_label("Name").fill(nome)
    page.get_by_label("Email").fill(email)
    page.get_by_label("Phone").fill(telefone)
    page.get_by_label("Subject").fill(assunto)
    page.get_by_label("Message").fill(mensagem)


def enviar_formulario(page: Page) -> None:
    page.get_by_role("button", name="Submit").click()


def test_ct01_enviar_formulario_vazio(page: Page) -> None:
    abrir_pagina(page)
    enviar_formulario(page)

    for campo in ("Name", "Email", "Phone", "Subject", "Message"):
        expect(page.get_by_text(campo, exact=False)).to_be_visible()
        expect(page.get_by_text("required", exact=False)).to_be_visible()


def test_ct02_telefone_abaixo_do_minimo(page: Page) -> None:
    abrir_pagina(page)
    preencher_formulario(page, telefone="1234567890")
    enviar_formulario(page)

    expect(
        page.get_by_text("Phone must be between 11 and 21 characters.", exact=True)
    ).to_be_visible()


def test_ct03_assunto_e_mensagem_abaixo_do_minimo(page: Page) -> None:
    abrir_pagina(page)
    preencher_formulario(page, assunto="abc", mensagem="1234567890123456789")
    enviar_formulario(page)

    expect(
        page.get_by_text("Subject must be between 5 and 100 characters.", exact=True)
    ).to_be_visible()
    expect(
        page.get_by_text("Message must be between 20 and 2000 characters.", exact=True)
    ).to_be_visible()


def test_ct04_email_malformado(page: Page) -> None:
    abrir_pagina(page)
    preencher_formulario(page, email="bad")
    enviar_formulario(page)

    expect(
        page.get_by_text("must be a well-formed email address", exact=False)
    ).to_be_visible()


def test_ct05_enviar_mensagem_valida(page: Page) -> None:
    abrir_pagina(page)
    preencher_formulario(page)
    enviar_formulario(page)

    expect(
        page.get_by_text(
            f"Thanks for getting in touch {NOME_VALIDO}!",
            exact=True,
        )
    ).to_be_visible()
    expect(page.get_by_text(ASSUNTO_VALIDO, exact=True)).to_be_visible()
