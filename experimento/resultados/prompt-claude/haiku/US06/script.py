import re
import uuid

from playwright.sync_api import Browser, Page, expect

BASE_URL = "https://automationintesting.online/"
ADMIN_USUARIO = "admin"
ADMIN_SENHA = "password"
EMAIL_VALIDO = "visitante.teste@example.com"
EMAIL_INVALIDO = "email-invalido"
TELEFONE_VALIDO = "01234567890"
MENSAGEM_VALIDA = "Gostaria de saber a disponibilidade de quartos para o proximo fim de semana."
CONFIRMACAO = "Thanks for getting in touch"


def gerar_nome_e_assunto() -> tuple[str, str]:
    sufixo = uuid.uuid4().hex[:8]
    return f"Visitante {sufixo}", f"Assunto {sufixo}"


def preencher_contato(
    page: Page,
    nome: str,
    assunto: str,
    email: str = EMAIL_VALIDO,
    mensagem: str = MENSAGEM_VALIDA,
) -> None:
    page.goto(BASE_URL)
    page.get_by_label("Name", exact=True).fill(nome)
    page.get_by_label("Email", exact=True).fill(email)
    page.get_by_label("Phone", exact=True).fill(TELEFONE_VALIDO)
    page.get_by_label("Subject", exact=True).fill(assunto)
    page.get_by_label("Message", exact=True).fill(mensagem)
    page.get_by_role("button", name="Submit").click()


def enviar_contato_visitante(browser: Browser, nome: str, assunto: str) -> None:
    contexto = browser.new_context()
    visitante = contexto.new_page()
    preencher_contato(visitante, nome, assunto)
    expect(visitante.get_by_text(f"{CONFIRMACAO} {nome}!")).to_be_visible()
    contexto.close()


def fazer_login_admin(page: Page) -> None:
    page.goto(f"{BASE_URL}admin")
    page.get_by_label("Username", exact=True).fill(ADMIN_USUARIO)
    page.get_by_label("Password", exact=True).fill(ADMIN_SENHA)
    page.get_by_role("button", name="Login").click()


def ler_contador_mensagens(page: Page) -> int:
    texto = page.get_by_role("link", name=re.compile("Messages")).inner_text()
    return int(re.search(r"\d+", texto).group())


def ler_contador_em_nova_sessao(browser: Browser) -> int:
    contexto = browser.new_context()
    admin = contexto.new_page()
    fazer_login_admin(admin)
    contador = ler_contador_mensagens(admin)
    contexto.close()
    return contador


def abrir_caixa_mensagens(page: Page) -> None:
    page.get_by_role("link", name=re.compile("Messages")).click()


def test_ct01_contador_messages_exibe_numero_apos_login(page: Page) -> None:
    fazer_login_admin(page)
    expect(page.get_by_role("link", name=re.compile("Messages"))).to_be_visible()
    assert ler_contador_mensagens(page) >= 0


def test_ct02_formulario_valido_exibe_confirmacao(page: Page) -> None:
    nome, assunto = gerar_nome_e_assunto()
    preencher_contato(page, nome, assunto)
    expect(page.get_by_text(f"{CONFIRMACAO} {nome}!")).to_be_visible()


def test_ct03_contador_aumenta_uma_unidade_apos_envio(page: Page, browser: Browser) -> None:
    fazer_login_admin(page)
    contador_antes = ler_contador_mensagens(page)

    nome, assunto = gerar_nome_e_assunto()
    enviar_contato_visitante(browser, nome, assunto)

    assert ler_contador_em_nova_sessao(browser) == contador_antes + 1


def test_ct04_mensagem_recem_enviada_aparece_na_caixa(page: Page, browser: Browser) -> None:
    nome, assunto = gerar_nome_e_assunto()
    enviar_contato_visitante(browser, nome, assunto)

    fazer_login_admin(page)
    abrir_caixa_mensagens(page)
    linha = page.get_by_role("row").filter(has_text=nome).filter(has_text=assunto)
    expect(linha).to_be_visible()


def test_ct05_apos_logout_caixa_exige_login(page: Page) -> None:
    fazer_login_admin(page)
    page.get_by_role("link", name="Logout").click()
    page.goto(f"{BASE_URL}admin/messages")
    expect(page.get_by_label("Username", exact=True)).to_be_visible()


def test_ct06_formulario_vazio_nao_exibe_confirmacao(page: Page) -> None:
    page.goto(BASE_URL)
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_label("Name", exact=True)).to_be_visible()
    expect(page.get_by_text(CONFIRMACAO)).to_have_count(0)


def test_ct07_nome_com_acentos_aparece_na_confirmacao(page: Page) -> None:
    nome = "José Conceição"
    _, assunto = gerar_nome_e_assunto()
    preencher_contato(page, nome, assunto)
    expect(page.get_by_text(f"{CONFIRMACAO} {nome}!")).to_be_visible()


def test_ct08_email_invalido_nao_incrementa_contador(page: Page, browser: Browser) -> None:
    fazer_login_admin(page)
    contador_antes = ler_contador_mensagens(page)

    nome, assunto = gerar_nome_e_assunto()
    contexto = browser.new_context()
    visitante = contexto.new_page()
    preencher_contato(visitante, nome, assunto, email=EMAIL_INVALIDO)
    visitante.wait_for_load_state("networkidle")
    expect(visitante.get_by_text(CONFIRMACAO)).to_have_count(0)
    contexto.close()

    assert ler_contador_em_nova_sessao(browser) == contador_antes
