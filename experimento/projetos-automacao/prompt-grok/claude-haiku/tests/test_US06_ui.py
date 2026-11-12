import re
import uuid
from urllib.parse import urljoin

from playwright.sync_api import expect

BASE_URL = "https://automationintesting.online/"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "password"
CONFIRMATION_PREFIX = "Thanks for getting in touch"


def _url(path=""):
    return urljoin(BASE_URL, path)


def _make_data(**overrides):
    uid = uuid.uuid4().hex[:8]
    data = {
        "name": f"Visitante {uid}",
        "email": f"visitante.{uid}@example.com",
        "phone": "11999999999",
        "subject": f"Assunto {uid}",
        "message": "Mensagem automatizada de teste.",
    }
    data.update(overrides)
    return data


def _send_as_visitor(browser, data):
    context = browser.new_context()
    visitor = context.new_page()
    visitor.goto(_url())
    visitor.get_by_label("Name", exact=True).fill(data["name"])
    visitor.get_by_label("Email", exact=True).fill(data["email"])
    visitor.get_by_label("Phone", exact=True).fill(data["phone"])
    visitor.get_by_label("Subject", exact=True).fill(data["subject"])
    visitor.get_by_label("Message", exact=True).fill(data["message"])
    visitor.get_by_role("button", name="Submit").click()
    return visitor, context


def _login_admin(page, user=ADMIN_USER, password=ADMIN_PASSWORD):
    page.goto(_url("admin"))
    page.get_by_label("Username", exact=True).fill(user)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Login").click()


def _logout_admin(page):
    page.get_by_role("button", name="Logout").click()
    expect(page.get_by_label("Username", exact=True)).to_be_visible()


def _messages_link(page):
    return page.get_by_role("link", name=re.compile("Messages"))


def _read_messages_count(page):
    link = _messages_link(page)
    expect(link).to_contain_text(re.compile(r"\d+"))
    return int(re.search(r"\d+", link.inner_text()).group())


def _admin_messages_count(page):
    _login_admin(page)
    count = _read_messages_count(page)
    _logout_admin(page)
    return count


def _open_messages(page):
    _messages_link(page).click()
    expect(page).to_have_url(re.compile(r"/admin/messages"))


def test_TC01_login_valido_exibe_contador_de_messages(page):
    _login_admin(page)
    count = _read_messages_count(page)
    assert count >= 0


def test_TC02_envio_valido_exibe_confirmacao_com_nome(browser):
    data = _make_data()
    visitor, context = _send_as_visitor(browser, data)
    expect(visitor.get_by_text(f"{CONFIRMATION_PREFIX} {data['name']}!")).to_be_visible()
    context.close()


def test_TC03_contador_aumenta_uma_unidade_apos_envio(page, browser):
    before = _admin_messages_count(page)
    data = _make_data()
    visitor, context = _send_as_visitor(browser, data)
    expect(visitor.get_by_text(f"{CONFIRMATION_PREFIX} {data['name']}!")).to_be_visible()
    context.close()
    after = _admin_messages_count(page)
    assert after == before + 1


def test_TC04_mensagem_aparece_na_caixa_com_nome_e_assunto(page, browser):
    data = _make_data()
    visitor, context = _send_as_visitor(browser, data)
    expect(visitor.get_by_text(f"{CONFIRMATION_PREFIX} {data['name']}!")).to_be_visible()
    context.close()
    _login_admin(page)
    _open_messages(page)
    row = page.get_by_role("row").filter(has_text=data["subject"])
    expect(row).to_have_count(1)
    expect(row).to_contain_text(data["name"])


def test_TC05_apos_logout_acesso_direto_a_messages_exige_login(page):
    _login_admin(page)
    _logout_admin(page)
    page.goto(_url("admin/messages"))
    expect(page.get_by_label("Username", exact=True)).to_be_visible()
    expect(_messages_link(page)).to_have_count(0)


def test_TC06_login_com_senha_invalida_nao_acessa_painel(page):
    _login_admin(page, password="senha-invalida")
    expect(page.get_by_role("button", name="Login")).to_be_visible()
    expect(_messages_link(page)).to_have_count(0)


def test_TC07_envio_sem_nome_nao_confirma_e_nao_altera_contador(page, browser):
    before = _admin_messages_count(page)
    visitor, context = _send_as_visitor(browser, _make_data(name=""))
    expect(visitor.get_by_text(CONFIRMATION_PREFIX)).to_have_count(0)
    context.close()
    after = _admin_messages_count(page)
    assert after == before


def test_TC08_envio_sem_assunto_nao_exibe_confirmacao(browser):
    visitor, context = _send_as_visitor(browser, _make_data(subject=""))
    expect(visitor.get_by_text(CONFIRMATION_PREFIX)).to_have_count(0)
    context.close()


def test_TC09_nome_e_assunto_com_acentos_aparecem_corretamente(page, browser):
    uid = uuid.uuid4().hex[:8]
    data = _make_data(name="José Álvaro Ñandú", subject=f"Reserva – ação & cia {uid}")
    visitor, context = _send_as_visitor(browser, data)
    expect(visitor.get_by_text(f"{CONFIRMATION_PREFIX} {data['name']}!")).to_be_visible()
    context.close()
    _login_admin(page)
    _open_messages(page)
    row = page.get_by_role("row").filter(has_text=data["subject"])
    expect(row).to_have_count(1)
    expect(row).to_contain_text(data["name"])
