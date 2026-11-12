from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

NOME_VALIDO = "Maria Teste"
EMAIL_VALIDO = "maria.teste@example.com"
TELEFONE_VALIDO = "11999999999"
ASSUNTO_VALIDO = "Dúvida sobre reserva"
MENSAGEM_VALIDA = "Gostaria de saber mais sobre a pousada e as tarifas."

TELEFONE_10_CARACTERES = "1" * 10
TELEFONE_11_CARACTERES = "1" * 11
TELEFONE_21_CARACTERES = "1" * 21
TELEFONE_22_CARACTERES = "1" * 22

ASSUNTO_4_CARACTERES = "A" * 4
ASSUNTO_5_CARACTERES = "A" * 5
ASSUNTO_100_CARACTERES = "A" * 100
ASSUNTO_101_CARACTERES = "A" * 101

MENSAGEM_19_CARACTERES = "M" * 19
MENSAGEM_20_CARACTERES = "M" * 20
MENSAGEM_2000_CARACTERES = "M" * 2000
MENSAGEM_2001_CARACTERES = "M" * 2001

EMAIL_MALFORMADO = "bad"

MSG_NOME_OBRIGATORIO = "Name may not be blank"
MSG_EMAIL_OBRIGATORIO = "Email may not be blank"
MSG_TELEFONE_OBRIGATORIO = "Phone may not be blank"
MSG_ASSUNTO_OBRIGATORIO = "Subject may not be blank"
MSG_MENSAGEM_OBRIGATORIA = "Message may not be blank"
MSG_TELEFONE_TAMANHO = "Phone must be between 11 and 21 characters."
MSG_ASSUNTO_TAMANHO = "Subject must be between 5 and 100 characters."
MSG_MENSAGEM_TAMANHO = "Message must be between 20 and 2000 characters."
MSG_EMAIL_INVALIDO = "must be a well-formed email address"
MSG_AGRADECIMENTO = f"Thanks for getting in touch {NOME_VALIDO}!"


def preencher_formulario(
    page: Page,
    nome: str = NOME_VALIDO,
    email: str = EMAIL_VALIDO,
    telefone: str = TELEFONE_VALIDO,
    assunto: str = ASSUNTO_VALIDO,
    mensagem: str = MENSAGEM_VALIDA,
) -> None:
    page.get_by_label("Name", exact=True).fill(nome)
    page.get_by_label("Email", exact=True).fill(email)
    page.get_by_label("Phone", exact=True).fill(telefone)
    page.get_by_label("Subject", exact=True).fill(assunto)
    page.get_by_label("Message", exact=True).fill(mensagem)


def enviar_formulario(page: Page) -> None:
    page.get_by_role("button", name="Submit", exact=True).click()


def test_ct01_formulario_vazio_exibe_mensagens_de_campos_obrigatorios(page: Page) -> None:
    page.goto(BASE_URL)
    preencher_formulario(page, "", "", "", "", "")
    enviar_formulario(page)

    expect(page.get_by_text(MSG_NOME_OBRIGATORIO)).to_be_visible()
    expect(page.get_by_text(MSG_EMAIL_OBRIGATORIO)).to_be_visible()
    expect(page.get_by_text(MSG_TELEFONE_OBRIGATORIO)).to_be_visible()
    expect(page.get_by_text(MSG_ASSUNTO_OBRIGATORIO)).to_be_visible()
    expect(page.get_by_text(MSG_MENSAGEM_OBRIGATORIA)).to_be_visible()


def test_ct02_telefone_com_10_caracteres_e_rejeitado(page: Page) -> None:
    page.goto(BASE_URL)
    preencher_formulario(page, telefone=TELEFONE_10_CARACTERES)
    enviar_formulario(page)

    expect(page.get_by_text(MSG_TELEFONE_TAMANHO)).to_be_visible()


def test_ct03_telefone_com_11_caracteres_limite_inferior_e_aceito(page: Page) -> None:
    page.goto(BASE_URL)
    preencher_formulario(page, telefone=TELEFONE_11_CARACTERES)
    enviar_formulario(page)

    expect(page.get_by_text(MSG_AGRADECIMENTO)).to_be_visible()


def test_ct04_telefone_com_21_caracteres_limite_superior_e_aceito(page: Page) -> None:
    page.goto(BASE_URL)
    preencher_formulario(page, telefone=TELEFONE_21_CARACTERES)
    enviar_formulario(page)

    expect(page.get_by_text(MSG_AGRADECIMENTO)).to_be_visible()


def test_ct05_telefone_com_22_caracteres_e_rejeitado(page: Page) -> None:
    page.goto(BASE_URL)
    preencher_formulario(page, telefone=TELEFONE_22_CARACTERES)
    enviar_formulario(page)

    expect(page.get_by_text(MSG_TELEFONE_TAMANHO)).to_be_visible()


def test_ct06_assunto_com_4_e_mensagem_com_19_caracteres_sao_rejeitados(page: Page) -> None:
    page.goto(BASE_URL)
    preencher_formulario(page, assunto=ASSUNTO_4_CARACTERES, mensagem=MENSAGEM_19_CARACTERES)
    enviar_formulario(page)

    expect(page.get_by_text(MSG_ASSUNTO_TAMANHO)).to_be_visible()
    expect(page.get_by_text(MSG_MENSAGEM_TAMANHO)).to_be_visible()


def test_ct07_assunto_com_5_e_mensagem_com_20_caracteres_limites_inferiores_sao_aceitos(page: Page) -> None:
    page.goto(BASE_URL)
    preencher_formulario(page, assunto=ASSUNTO_5_CARACTERES, mensagem=MENSAGEM_20_CARACTERES)
    enviar_formulario(page)

    expect(page.get_by_text(MSG_AGRADECIMENTO)).to_be_visible()


def test_ct08_assunto_com_100_e_mensagem_com_2000_caracteres_limites_superiores_sao_aceitos(page: Page) -> None:
    page.goto(BASE_URL)
    preencher_formulario(page, assunto=ASSUNTO_100_CARACTERES, mensagem=MENSAGEM_2000_CARACTERES)
    enviar_formulario(page)

    expect(page.get_by_text(MSG_AGRADECIMENTO)).to_be_visible()


def test_ct09_assunto_com_101_e_mensagem_com_2001_caracteres_sao_rejeitados(page: Page) -> None:
    page.goto(BASE_URL)
    preencher_formulario(page, assunto=ASSUNTO_101_CARACTERES, mensagem=MENSAGEM_2001_CARACTERES)
    enviar_formulario(page)

    expect(page.get_by_text(MSG_ASSUNTO_TAMANHO)).to_be_visible()
    expect(page.get_by_text(MSG_MENSAGEM_TAMANHO)).to_be_visible()


def test_ct10_email_malformado_e_rejeitado(page: Page) -> None:
    page.goto(BASE_URL)
    preencher_formulario(page, email=EMAIL_MALFORMADO)
    enviar_formulario(page)

    expect(page.get_by_text(MSG_EMAIL_INVALIDO)).to_be_visible()


def test_ct11_dados_validos_geram_confirmacao_com_nome_e_assunto(page: Page) -> None:
    page.goto(BASE_URL)
    preencher_formulario(page)
    enviar_formulario(page)

    expect(page.get_by_text(MSG_AGRADECIMENTO)).to_be_visible()
    expect(page.get_by_text(ASSUNTO_VALIDO)).to_be_visible()
