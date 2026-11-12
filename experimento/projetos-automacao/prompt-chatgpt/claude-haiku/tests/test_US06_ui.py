import re
import uuid

from playwright.sync_api import Browser, Locator, Page, expect

BASE_URL = "https://automationintesting.online/"
ADMIN_URL = f"{BASE_URL}admin"
MESSAGES_URL = f"{ADMIN_URL}/messages"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"
VISITOR_EMAIL = "visitante@example.com"
VISITOR_PHONE = "01234567890"
VISITOR_MESSAGE = "Gostaria de saber a disponibilidade de quartos para o próximo fim de semana."


def unique_text(prefix: str) -> str:
    return f"{prefix} {uuid.uuid4().hex[:8]}"


def messages_link(page: Page) -> Locator:
    return page.get_by_role("link", name=re.compile(r"Messages"))


def submit_contact_form(page: Page, name: str, subject: str, email: str = VISITOR_EMAIL) -> None:
    page.goto(BASE_URL)
    page.get_by_label("Name", exact=True).fill(name)
    page.get_by_label("Email", exact=True).fill(email)
    page.get_by_label("Phone", exact=True).fill(VISITOR_PHONE)
    page.get_by_label("Subject", exact=True).fill(subject)
    page.get_by_label("Message", exact=True).fill(VISITOR_MESSAGE)
    page.get_by_role("button", name="Submit").click()


def visitor_sends(
    browser: Browser, name: str, subject: str, email: str = VISITOR_EMAIL, confirmed: bool = True
) -> None:
    context = browser.new_context()
    try:
        page = context.new_page()
        submit_contact_form(page, name, subject, email)
        page.wait_for_load_state("networkidle")
        confirmation = page.get_by_text(f"Thanks for getting in touch {name}!", exact=True)
        if confirmed:
            expect(confirmation).to_be_visible()
        else:
            expect(confirmation).to_have_count(0)
    finally:
        context.close()


def admin_login(page: Page) -> None:
    page.goto(ADMIN_URL)
    page.get_by_label("Username").fill(ADMIN_USERNAME)
    page.get_by_label("Password").fill(ADMIN_PASSWORD)
    page.get_by_role("button", name="Login").click()
    expect(messages_link(page)).to_be_visible()


def admin_logout(page: Page) -> None:
    page.get_by_role("button", name="Logout").click()
    expect(page.get_by_label("Username")).to_be_visible()


def read_messages_count(page: Page) -> int:
    link = messages_link(page)
    expect(link).to_be_visible()
    match = re.search(r"\d+", link.inner_text())
    assert match is not None, "Contador ao lado de Messages não encontrado"
    return int(match.group())


def open_messages(page: Page) -> None:
    messages_link(page).click()


def message_item(page: Page, *texts: str) -> Locator:
    item = page.get_by_role("listitem")
    for text in texts:
        item = item.filter(has_text=text)
    return item


def test_CT001_contador_messages_visivel_apos_login(page: Page) -> None:
    admin_login(page)
    assert read_messages_count(page) >= 0


def test_CT002_login_com_senha_invalida_nao_exibe_contador(page: Page) -> None:
    page.goto(ADMIN_URL)
    page.get_by_label("Username").fill(ADMIN_USERNAME)
    page.get_by_label("Password").fill("senha-incorreta")
    page.get_by_role("button", name="Login").click()
    page.wait_for_load_state("networkidle")
    expect(page.get_by_label("Username")).to_be_visible()
    expect(messages_link(page)).to_have_count(0)


def test_CT003_envio_valido_exibe_confirmacao(page: Page) -> None:
    name = unique_text("Visitante Confirmacao")
    submit_contact_form(page, name, unique_text("Assunto"))
    expect(page.get_by_text(f"Thanks for getting in touch {name}!", exact=True)).to_be_visible()


def test_CT004_envio_sem_assunto_nao_exibe_confirmacao(browser: Browser) -> None:
    visitor_sends(browser, unique_text("Visitante Sem Assunto"), "", confirmed=False)


def test_CT005_confirmacao_preserva_nome_com_acentos(page: Page) -> None:
    name = unique_text("Ana Lúcia Gonçalves")
    submit_contact_form(page, name, unique_text("Reserva"))
    expect(page.get_by_text(f"Thanks for getting in touch {name}!", exact=True)).to_be_visible()


def test_CT006_contador_aumenta_uma_unidade_apos_envio(page: Page, browser: Browser) -> None:
    admin_login(page)
    before = read_messages_count(page)
    admin_logout(page)
    visitor_sends(browser, unique_text("Visitante Contador"), unique_text("Assunto"))
    admin_login(page)
    assert read_messages_count(page) == before + 1


def test_CT007_envio_com_email_invalido_nao_altera_contador(page: Page, browser: Browser) -> None:
    admin_login(page)
    before = read_messages_count(page)
    admin_logout(page)
    visitor_sends(
        browser,
        unique_text("Visitante Email Invalido"),
        unique_text("Assunto"),
        email="email-invalido",
        confirmed=False,
    )
    admin_login(page)
    assert read_messages_count(page) == before


def test_CT008_mensagem_recem_enviada_aparece_na_caixa(page: Page, browser: Browser) -> None:
    name = unique_text("Visitante Lista")
    subject = unique_text("Assunto Lista")
    visitor_sends(browser, name, subject)
    admin_login(page)
    open_messages(page)
    expect(message_item(page, name, subject)).to_be_visible()


def test_CT009_mensagem_com_acentos_aparece_corretamente(page: Page, browser: Browser) -> None:
    name = unique_text("Ângela Sá Pereira")
    subject = unique_text("Dúvida: café da manhã às 8h")
    visitor_sends(browser, name, subject)
    admin_login(page)
    open_messages(page)
    expect(message_item(page, name, subject)).to_be_visible()


def test_CT010_mensagem_nao_enviada_nao_aparece_na_caixa(page: Page, browser: Browser) -> None:
    subject = unique_text("Assunto Nao Enviado")
    visitor_sends(
        browser,
        unique_text("Visitante Invalido"),
        subject,
        email="email-invalido",
        confirmed=False,
    )
    admin_login(page)
    open_messages(page)
    page.wait_for_load_state("networkidle")
    expect(message_item(page, subject)).to_have_count(0)


def test_CT011_logout_exige_login_ao_abrir_caixa(page: Page) -> None:
    admin_login(page)
    admin_logout(page)
    page.goto(MESSAGES_URL)
    expect(page.get_by_label("Username")).to_be_visible()
    expect(messages_link(page)).to_have_count(0)


def test_CT012_acesso_direto_sem_login_exige_login(page: Page) -> None:
    page.goto(MESSAGES_URL)
    expect(page.get_by_label("Username")).to_be_visible()
    expect(message_item(page)).to_have_count(0)
