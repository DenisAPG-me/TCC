import re
import uuid

from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online"
ADMIN_URL = f"{BASE_URL}/admin"
MESSAGES_URL = f"{BASE_URL}/admin/message"

ADMIN_USER = "admin"
ADMIN_PASSWORD = "password"
INVALID_PASSWORD = "senha-errada"

VISITOR_PHONE = "01234567890"
VISITOR_DESCRIPTION = "Gostaria de saber a disponibilidade de quartos para o próximo feriado."
INVALID_EMAIL = "email-invalido"
MIN_SUBJECT = "Quart"
SHORT_SUBJECT = "Quar"
MIN_DESCRIPTION = "Mensagem de 20 chars"


def unique_visitor():
    suffix = uuid.uuid4().hex[:8]
    return {
        "name": f"Visitante {suffix}",
        "email": f"visitante.{suffix}@example.com",
        "phone": VISITOR_PHONE,
        "subject": f"Reserva {suffix}",
        "description": VISITOR_DESCRIPTION,
    }


def fill_contact_form(page: Page, data: dict):
    page.goto(BASE_URL)
    page.get_by_test_id("ContactName").fill(data["name"])
    page.get_by_test_id("ContactEmail").fill(data["email"])
    page.get_by_test_id("ContactPhone").fill(data["phone"])
    page.get_by_test_id("ContactSubject").fill(data["subject"])
    page.get_by_test_id("ContactDescription").fill(data["description"])
    page.get_by_role("button", name="Submit").click()


def send_valid_message(page: Page, data: dict):
    fill_contact_form(page, data)
    expect(page.get_by_text(f"Thanks for getting in touch {data['name']}!")).to_be_visible()


def login(page: Page, password: str = ADMIN_PASSWORD):
    page.goto(ADMIN_URL)
    page.get_by_label("Username").fill(ADMIN_USER)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Login").click()


def logout(page: Page):
    page.get_by_role("button", name="Logout").click()
    expect(page.get_by_role("button", name="Logout")).to_be_hidden()


def messages_link(page: Page):
    return page.get_by_role("link", name=re.compile(r"Messages"))


def read_messages_count(page: Page) -> int:
    link = messages_link(page)
    expect(link).to_have_text(re.compile(r"\d+"))
    return int(re.search(r"\d+", link.inner_text()).group())


def expect_login_form(page: Page):
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()
    expect(page.get_by_role("button", name="Login")).to_be_visible()


def expect_no_confirmation(page: Page):
    expect(page.get_by_text("Thanks for getting in touch")).to_have_count(0)


def test_ct01_painel_exibe_contador_de_messages(page: Page):
    login(page)
    expect(messages_link(page)).to_be_visible()
    count = read_messages_count(page)
    assert count >= 0


def test_ct02_envio_valido_exibe_confirmacao(page: Page):
    data = unique_visitor()
    fill_contact_form(page, data)
    expect(page.get_by_text(f"Thanks for getting in touch {data['name']}!")).to_be_visible()


def test_ct03_contador_incrementa_apos_envio(page: Page):
    login(page)
    count_before = read_messages_count(page)
    logout(page)

    send_valid_message(page, unique_visitor())

    login(page)
    expect(messages_link(page)).to_have_text(re.compile(rf"\b{count_before + 1}\b"))
    assert read_messages_count(page) == count_before + 1


def test_ct04_mensagem_aparece_na_caixa_com_nome_e_assunto(page: Page):
    data = unique_visitor()
    send_valid_message(page, data)

    login(page)
    messages_link(page).click()

    row = (
        page.get_by_test_id(re.compile(r"^message\d+$"))
        .filter(has_text=data["name"])
        .filter(has_text=data["subject"])
    )
    expect(row).to_have_count(1)
    expect(row).to_be_visible()


def test_ct05_logout_bloqueia_acesso_direto_a_caixa(page: Page):
    login(page)
    expect(messages_link(page)).to_be_visible()
    logout(page)

    page.goto(MESSAGES_URL)
    expect_login_form(page)
    expect(page.get_by_test_id(re.compile(r"^message\d+$"))).to_have_count(0)


def test_ct06_envio_com_formulario_vazio_rejeitado(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_role("alert")).to_be_visible()
    expect_no_confirmation(page)


def test_ct07_envio_com_email_invalido_rejeitado(page: Page):
    data = unique_visitor()
    data["email"] = INVALID_EMAIL
    fill_contact_form(page, data)
    expect(page.get_by_role("alert")).to_contain_text(re.compile(r"email", re.IGNORECASE))
    expect_no_confirmation(page)


def test_ct08_envio_com_tamanhos_minimos_aceito(page: Page):
    data = unique_visitor()
    data["subject"] = MIN_SUBJECT
    data["description"] = MIN_DESCRIPTION
    assert len(data["subject"]) == 5
    assert len(data["description"]) == 20
    fill_contact_form(page, data)
    expect(page.get_by_text(f"Thanks for getting in touch {data['name']}!")).to_be_visible()


def test_ct09_envio_com_assunto_curto_rejeitado(page: Page):
    data = unique_visitor()
    data["subject"] = SHORT_SUBJECT
    assert len(data["subject"]) == 4
    fill_contact_form(page, data)
    expect(page.get_by_role("alert")).to_contain_text(re.compile(r"Subject", re.IGNORECASE))
    expect_no_confirmation(page)


def test_ct10_login_com_senha_invalida_nao_exibe_messages(page: Page):
    login(page, password=INVALID_PASSWORD)
    expect_login_form(page)
    expect(messages_link(page)).to_have_count(0)


def test_ct11_acesso_direto_sem_login_solicita_autenticacao(page: Page):
    page.goto(MESSAGES_URL)
    expect_login_form(page)
    expect(page.get_by_test_id(re.compile(r"^message\d+$"))).to_have_count(0)
