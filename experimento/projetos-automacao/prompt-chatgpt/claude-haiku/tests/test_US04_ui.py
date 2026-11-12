import re

from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

ROTULO_NOME = "Name"
ROTULO_EMAIL = "Email"
ROTULO_TELEFONE = "Phone"
ROTULO_ASSUNTO = "Subject"
ROTULO_MENSAGEM = "Message"
BOTAO_ENVIAR = "Submit"

NOME_VALIDO = "Maria Teste"
NOME_ACENTUADO = "João Ação"
EMAIL_VALIDO = "maria.teste@example.com"
EMAIL_MALFORMADO = "bad"
TELEFONE_VALIDO = "11987654321"
ASSUNTO_VALIDO = "Dúvida sobre reserva"
MENSAGEM_VALIDA = "Gostaria de saber sobre a disponibilidade de quartos."

MSG_TELEFONE = "Phone must be between 11 and 21 characters."
MSG_ASSUNTO = "Subject must be between 5 and 100 characters."
MSG_MENSAGEM = "Message must be between 20 and 2000 characters."
MSG_EMAIL = "must be a well-formed email address"


def _confirmacao(nome: str) -> str:
    return f"Thanks for getting in touch {nome}!"


def _submeter(page: Page, **campos: str) -> None:
    dados = {
        "nome": NOME_VALIDO,
        "email": EMAIL_VALIDO,
        "telefone": TELEFONE_VALIDO,
        "assunto": ASSUNTO_VALIDO,
        "mensagem": MENSAGEM_VALIDA,
    }
    dados.update(campos)
    page.goto(BASE_URL)
    page.get_by_label(ROTULO_NOME, exact=True).fill(dados["nome"])
    page.get_by_label(ROTULO_EMAIL, exact=True).fill(dados["email"])
    page.get_by_label(ROTULO_TELEFONE, exact=True).fill(dados["telefone"])
    page.get_by_label(ROTULO_ASSUNTO, exact=True).fill(dados["assunto"])
    page.get_by_label(ROTULO_MENSAGEM, exact=True).fill(dados["mensagem"])
    page.get_by_role("button", name=BOTAO_ENVIAR, exact=True).click()


def _erro_em_branco(page: Page, campo: str):
    return page.get_by_text(re.compile(rf"{campo}.*blank", re.IGNORECASE))


def _espera_confirmacao(page: Page, nome: str = NOME_VALIDO) -> None:
    expect(page.get_by_text(_confirmacao(nome))).to_be_visible()


def test_CT001_envio_vazio_exibe_mensagens_de_campo_em_branco(page: Page):
    _submeter(page, nome="", email="", telefone="", assunto="", mensagem="")
    for campo in ("Name", "Email", "Phone", "Subject", "Message"):
        expect(_erro_em_branco(page, campo)).to_be_visible()


def test_CT002_campos_somente_com_espacos_exibem_mensagens_de_campo_em_branco(page: Page):
    espacos = "   "
    _submeter(
        page,
        nome=espacos,
        email=espacos,
        telefone=espacos,
        assunto=espacos,
        mensagem=espacos,
    )
    for campo in ("Name", "Email", "Phone", "Subject", "Message"):
        expect(_erro_em_branco(page, campo)).to_be_visible()


def test_CT003_telefone_com_10_caracteres_exibe_erro_de_tamanho(page: Page):
    _submeter(page, telefone="1" * 10)
    expect(page.get_by_text(MSG_TELEFONE)).to_be_visible()
    expect(page.get_by_text(_confirmacao(NOME_VALIDO))).not_to_be_visible()


def test_CT004_telefone_com_11_caracteres_e_aceito(page: Page):
    _submeter(page, telefone="1" * 11)
    _espera_confirmacao(page)
    expect(page.get_by_text(MSG_TELEFONE)).not_to_be_visible()


def test_CT005_telefone_com_21_caracteres_e_aceito(page: Page):
    _submeter(page, telefone="1" * 21)
    _espera_confirmacao(page)
    expect(page.get_by_text(MSG_TELEFONE)).not_to_be_visible()


def test_CT006_telefone_com_22_caracteres_exibe_erro_de_tamanho(page: Page):
    _submeter(page, telefone="1" * 22)
    expect(page.get_by_text(MSG_TELEFONE)).to_be_visible()


def test_CT007_assunto_com_4_e_mensagem_com_19_caracteres_exibem_erros(page: Page):
    _submeter(page, assunto="a" * 4, mensagem="m" * 19)
    expect(page.get_by_text(MSG_ASSUNTO)).to_be_visible()
    expect(page.get_by_text(MSG_MENSAGEM)).to_be_visible()
    expect(page.get_by_text(_confirmacao(NOME_VALIDO))).not_to_be_visible()


def test_CT008_assunto_com_5_caracteres_e_aceito(page: Page):
    _submeter(page, assunto="a" * 5)
    _espera_confirmacao(page)
    expect(page.get_by_text(MSG_ASSUNTO)).not_to_be_visible()


def test_CT009_assunto_com_100_caracteres_e_aceito(page: Page):
    _submeter(page, assunto="a" * 100)
    _espera_confirmacao(page)
    expect(page.get_by_text(MSG_ASSUNTO)).not_to_be_visible()


def test_CT010_assunto_com_101_caracteres_exibe_erro_de_tamanho(page: Page):
    _submeter(page, assunto="a" * 101)
    expect(page.get_by_text(MSG_ASSUNTO)).to_be_visible()


def test_CT011_mensagem_com_20_caracteres_e_aceita(page: Page):
    _submeter(page, mensagem="m" * 20)
    _espera_confirmacao(page)
    expect(page.get_by_text(MSG_MENSAGEM)).not_to_be_visible()


def test_CT012_mensagem_com_2000_caracteres_e_aceita(page: Page):
    _submeter(page, mensagem="m" * 2000)
    _espera_confirmacao(page)
    expect(page.get_by_text(MSG_MENSAGEM)).not_to_be_visible()


def test_CT013_mensagem_com_2001_caracteres_exibe_erro_de_tamanho(page: Page):
    _submeter(page, mensagem="m" * 2001)
    expect(page.get_by_text(MSG_MENSAGEM)).to_be_visible()


def test_CT014_email_malformado_exibe_erro_de_formato(page: Page):
    _submeter(page, email=EMAIL_MALFORMADO)
    expect(page.get_by_text(MSG_EMAIL)).to_be_visible()
    expect(page.get_by_text(_confirmacao(NOME_VALIDO))).not_to_be_visible()


def test_CT015_dados_validos_exibem_confirmacao_com_nome_e_assunto(page: Page):
    _submeter(page)
    _espera_confirmacao(page)
    expect(page.get_by_text(ASSUNTO_VALIDO)).to_be_visible()


def test_CT016_nome_com_acentuacao_aparece_na_confirmacao(page: Page):
    _submeter(page, nome=NOME_ACENTUADO)
    _espera_confirmacao(page, NOME_ACENTUADO)
