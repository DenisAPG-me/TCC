import re
import uuid
from urllib.parse import urljoin

from playwright.sync_api import Page, expect

# ---------------------------------------------------------------------------
# Configuração e valores inferidos (ajustar se o sistema real divergir)
# ---------------------------------------------------------------------------
BASE_URL = "https://automationintesting.online/"
ADMIN_PATH = "admin"
MESSAGES_PATH = "admin/message"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

UI_TIMEOUT_MS = 15_000

LOGIN_USERNAME_LABEL = "Username"
LOGIN_PASSWORD_LABEL = "Password"
LOGIN_BUTTON_NAME = "Login"
LOGOUT_BUTTON_NAME = "Logout"

MESSAGES_LINK_NAME = re.compile(r"^\s*Messages\b")
MESSAGES_LINK_TEXT = re.compile(r"^\s*Messages\s*\d+\s*$")
MESSAGES_COUNT_PATTERN = re.compile(r"Messages\s*(\d+)")
MESSAGE_ROW_TEST_ID = re.compile(r"^message\d+$")

CONTACT_TEST_IDS = {
    "name": "ContactName",
    "email": "ContactEmail",
    "phone": "ContactPhone",
    "subject": "ContactSubject",
    "message": "ContactDescription",
}
CONTACT_SUBMIT_NAME = "Submit"

CONFIRMATION_TEMPLATE = "Thanks for getting in touch {name}!"
CONFIRMATION_PREFIX = "Thanks for getting in touch"
BLANK_FIELD_ERRORS = ("Name may not be blank", "Subject may not be blank")

SPECIAL_NAME = "José D'Ávila-Núñez"

expect.set_options(timeout=UI_TIMEOUT_MS)


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def url(path: str = "") -> str:
    return urljoin(BASE_URL, path)


def build_contact(name: str | None = None) -> dict:
    suffix = uuid.uuid4().hex[:8]
    return {
        "name": name if name is not None else f"Visitante {suffix}",
        "email": f"visitante.{suffix}@example.com",
        "phone": "01234567890",
        "subject": f"Reserva teste {suffix}",
        "message": f"Gostaria de informações sobre disponibilidade. Ref {suffix}.",
    }


def submit_contact(page: Page, contact: dict) -> None:
    page.goto(url())
    for field, test_id in CONTACT_TEST_IDS.items():
        page.get_by_test_id(test_id).fill(contact[field])
    page.get_by_role("button", name=CONTACT_SUBMIT_NAME).click()
    expect(
        page.get_by_text(CONFIRMATION_TEMPLATE.format(name=contact["name"]), exact=True)
    ).to_be_visible()


def login(page: Page) -> None:
    page.goto(url(ADMIN_PATH))
    page.get_by_label(LOGIN_USERNAME_LABEL).fill(ADMIN_USERNAME)
    page.get_by_label(LOGIN_PASSWORD_LABEL).fill(ADMIN_PASSWORD)
    page.get_by_role("button", name=LOGIN_BUTTON_NAME).click()
    expect(page.get_by_role("button", name=LOGOUT_BUTTON_NAME)).to_be_visible()


def logout(page: Page) -> None:
    page.get_by_role("button", name=LOGOUT_BUTTON_NAME).click()
    expect(page.get_by_role("button", name=LOGOUT_BUTTON_NAME)).to_have_count(0)


def read_messages_count(page: Page) -> int:
    link = page.get_by_role("link", name=MESSAGES_LINK_NAME)
    expect(link).to_have_text(MESSAGES_LINK_TEXT)
    match = MESSAGES_COUNT_PATTERN.search(link.inner_text())
    assert match is not None, f"Número não encontrado no link Messages: {link.inner_text()!r}"
    return int(match.group(1))


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------
def test_CT001_contador_messages_exibido_apos_login(page: Page) -> None:
    login(page)

    count = read_messages_count(page)

    assert count >= 0


def test_CT002_envio_valido_exibe_confirmacao_com_nome(page: Page) -> None:
    contact = build_contact()
    page.goto(url())
    for field, test_id in CONTACT_TEST_IDS.items():
        page.get_by_test_id(test_id).fill(contact[field])
    page.get_by_role("button", name=CONTACT_SUBMIT_NAME).click()

    expect(
        page.get_by_text(CONFIRMATION_TEMPLATE.format(name=contact["name"]), exact=True)
    ).to_be_visible()


def test_CT003_envio_vazio_nao_exibe_confirmacao(page: Page) -> None:
    page.goto(url())
    expect(page.get_by_test_id(CONTACT_TEST_IDS["name"])).to_be_visible()

    page.get_by_role("button", name=CONTACT_SUBMIT_NAME).click()

    for error_text in BLANK_FIELD_ERRORS:
        expect(page.get_by_text(error_text)).to_be_visible()
    expect(page.get_by_text(CONFIRMATION_PREFIX)).to_have_count(0)
    expect(page.get_by_test_id(CONTACT_TEST_IDS["name"])).to_be_visible()


def test_CT004_confirmacao_preserva_nome_com_caracteres_especiais(page: Page) -> None:
    contact = build_contact(name=SPECIAL_NAME)
    page.goto(url())
    for field, test_id in CONTACT_TEST_IDS.items():
        page.get_by_test_id(test_id).fill(contact[field])
    page.get_by_role("button", name=CONTACT_SUBMIT_NAME).click()

    expect(
        page.get_by_text(CONFIRMATION_TEMPLATE.format(name=SPECIAL_NAME), exact=True)
    ).to_be_visible()


def test_CT005_contador_messages_aumenta_uma_unidade_apos_envio(page: Page) -> None:
    login(page)
    count_before = read_messages_count(page)
    logout(page)

    submit_contact(page, build_contact())

    login(page)
    count_after = read_messages_count(page)

    assert count_after == count_before + 1, (
        f"Esperado {count_before + 1}, obtido {count_after}"
    )


def test_CT006_mensagem_recem_enviada_aparece_na_lista(page: Page) -> None:
    contact = build_contact()
    submit_contact(page, contact)

    login(page)
    page.get_by_role("link", name=MESSAGES_LINK_NAME).click()
    expect(page).to_have_url(re.compile(re.escape(url(MESSAGES_PATH))))

    row = page.get_by_test_id(MESSAGE_ROW_TEST_ID).filter(has_text=contact["subject"])
    expect(row).to_have_count(1)
    expect(row).to_contain_text(contact["name"])
    expect(row).to_contain_text(contact["subject"])


def test_CT007_acesso_direto_apos_logout_solicita_login(page: Page) -> None:
    login(page)
    logout(page)

    page.goto(url(MESSAGES_PATH))

    expect(page.get_by_label(LOGIN_USERNAME_LABEL)).to_be_visible()
    expect(page.get_by_label(LOGIN_PASSWORD_LABEL)).to_be_visible()
    expect(page.get_by_role("button", name=LOGIN_BUTTON_NAME)).to_be_visible()
    expect(page.get_by_test_id(MESSAGE_ROW_TEST_ID)).to_have_count(0)
    expect(page.get_by_role("button", name=LOGOUT_BUTTON_NAME)).to_have_count(0)
