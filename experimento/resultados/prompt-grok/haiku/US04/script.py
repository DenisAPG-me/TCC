import re

from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

BLANK_RE = re.compile(r"(empty|blank|branco|vazio)", re.IGNORECASE)
PHONE_ERROR = "Phone must be between 11 and 21 characters."
SUBJECT_ERROR = "Subject must be between 5 and 100 characters."
MESSAGE_ERROR = "Message must be between 20 and 2000 characters."
EMAIL_ERROR = "must be a well-formed email address"

VALID = {
    "name": "Maria Silva",
    "email": "maria@example.com",
    "phone": "11987654321",
    "subject": "Dúvida reserva",
    "message": "Gostaria de saber sobre o café da manhã.",
}


def _submit(page: Page, base_url, **overrides):
    data = {**VALID, **overrides}
    page.goto(base_url or BASE_URL)
    page.get_by_label("Name").fill(data["name"])
    page.get_by_label("Email").fill(data["email"])
    page.get_by_label("Phone").fill(data["phone"])
    page.get_by_label("Subject").fill(data["subject"])
    page.get_by_label("Message").fill(data["message"])
    page.get_by_role("button", name="Submit").click()


def _assert_success(page: Page, name: str, subject: str):
    expect(page.get_by_text(f"Thanks for getting in touch {name}!")).to_be_visible()
    expect(page.get_by_text(subject)).to_be_visible()


def test_TC01_envio_vazio_exibe_mensagens_de_campos_obrigatorios(page: Page, base_url):
    _submit(page, base_url, name="", email="", phone="", subject="", message="")
    expect(page.get_by_text(BLANK_RE)).to_have_count(5)


def test_TC02_email_vazio_exibe_mensagem_de_campo_obrigatorio(page: Page, base_url):
    _submit(page, base_url, email="")
    expect(page.get_by_text(BLANK_RE)).to_have_count(1)


def test_TC03_telefone_com_10_caracteres_exibe_erro(page: Page, base_url):
    _submit(page, base_url, phone="1" * 10)
    expect(page.get_by_text(PHONE_ERROR, exact=True)).to_be_visible()


def test_TC04_telefone_com_11_caracteres_e_aceito(page: Page, base_url):
    _submit(page, base_url, phone="1" * 11)
    _assert_success(page, VALID["name"], VALID["subject"])


def test_TC05_telefone_com_21_caracteres_e_aceito(page: Page, base_url):
    _submit(page, base_url, phone="1" * 21)
    _assert_success(page, VALID["name"], VALID["subject"])


def test_TC06_telefone_com_22_caracteres_exibe_erro(page: Page, base_url):
    _submit(page, base_url, phone="1" * 22)
    expect(page.get_by_text(PHONE_ERROR, exact=True)).to_be_visible()


def test_TC07_assunto_com_4_caracteres_exibe_erro(page: Page, base_url):
    _submit(page, base_url, subject="Ajud")
    expect(page.get_by_text(SUBJECT_ERROR, exact=True)).to_be_visible()


def test_TC08_assunto_com_5_e_mensagem_com_20_caracteres_sao_aceitos(page: Page, base_url):
    _submit(page, base_url, subject="Preco", message="Mensagem curta aqui!")
    _assert_success(page, VALID["name"], "Preco")


def test_TC09_assunto_com_101_caracteres_exibe_erro(page: Page, base_url):
    _submit(page, base_url, subject="A" * 101)
    expect(page.get_by_text(SUBJECT_ERROR, exact=True)).to_be_visible()


def test_TC10_mensagem_com_19_caracteres_exibe_erro(page: Page, base_url):
    _submit(page, base_url, message="Mensagem curta aqui")
    expect(page.get_by_text(MESSAGE_ERROR, exact=True)).to_be_visible()


def test_TC11_mensagem_com_2001_caracteres_exibe_erro(page: Page, base_url):
    _submit(page, base_url, message="a" * 2001)
    expect(page.get_by_text(MESSAGE_ERROR, exact=True)).to_be_visible()


def test_TC12_mensagem_com_2000_caracteres_e_aceita(page: Page, base_url):
    _submit(page, base_url, message="a" * 2000)
    _assert_success(page, VALID["name"], VALID["subject"])


def test_TC13_assunto_e_mensagem_abaixo_do_minimo_exibem_ambos_erros(page: Page, base_url):
    _submit(page, base_url, subject="Ajud", message="Mensagem curta aqui")
    expect(page.get_by_text(SUBJECT_ERROR, exact=True)).to_be_visible()
    expect(page.get_by_text(MESSAGE_ERROR, exact=True)).to_be_visible()


def test_TC14_email_bad_exibe_erro_de_formato(page: Page, base_url):
    _submit(page, base_url, email="bad")
    expect(page.get_by_text(EMAIL_ERROR)).to_be_visible()


def test_TC15_email_sem_arroba_exibe_erro_de_formato(page: Page, base_url):
    _submit(page, base_url, email="usuario.exemplo.com")
    expect(page.get_by_text(EMAIL_ERROR)).to_be_visible()


def test_TC16_todos_os_campos_validos_exibem_confirmacao(page: Page, base_url):
    _submit(page, base_url)
    _assert_success(page, VALID["name"], VALID["subject"])


def test_TC17_nome_com_acentos_aparece_na_confirmacao(page: Page, base_url):
    name = "José da Silva Ação"
    _submit(page, base_url, name=name)
    _assert_success(page, name, VALID["subject"])
