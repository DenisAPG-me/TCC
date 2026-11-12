import re
from uuid import uuid4

from playwright.sync_api import Page, expect


BASE_URL = "https://automationintesting.online"
ADMIN_URL = f"{BASE_URL}/admin"
MESSAGES_URL = f"{BASE_URL}/admin/messages"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

CONTACT_NAME = "Visitante Teste"
CONTACT_EMAIL = "visitante.teste@example.com"
CONTACT_PHONE = "11987654321"
CONTACT_SUBJECT_PREFIX = "Consulta de hospedagem"
CONTACT_BODY = (
    "Ola, gostaria de consultar a disponibilidade de hospedagem "
    "para duas pessoas no proximo mes."
)
INVALID_EMAIL = "email-invalido"

UI_TIMEOUT_MS = 15_000
NAVIGATION_TIMEOUT_MS = 30_000

MESSAGES_NAME = re.compile(r"^Messages\b", re.IGNORECASE)
COUNTER_PATTERN = re.compile(
    r"^\s*Messages\s+(?:[0-9]+|\(\s*[0-9]+\s*\))\s*$",
    re.IGNORECASE,
)


def configure(page: Page) -> None:
    page.set_default_timeout(UI_TIMEOUT_MS)
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)


def navigate(page: Page, url: str) -> None:
    page.goto(url, wait_until="domcontentloaded")


def new_contact() -> dict[str, str]:
    return {
        "name": CONTACT_NAME,
        "email": CONTACT_EMAIL,
        "phone": CONTACT_PHONE,
        "subject": f"{CONTACT_SUBJECT_PREFIX} {uuid4().hex[:12]}",
        "message": CONTACT_BODY,
    }


def messages_link(page: Page):
    return page.get_by_role("link", name=MESSAGES_NAME)


def expect_login(page: Page) -> None:
    expect(
        page.get_by_label("Username", exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(page.get_by_label("Password", exact=True)).to_be_visible(
        timeout=UI_TIMEOUT_MS
    )
    expect(
        page.get_by_role("button", name="Login", exact=True)
    ).to_be_visible(timeout=UI_TIMEOUT_MS)


def login(page: Page) -> None:
    navigate(page, ADMIN_URL)
    expect_login(page)
    page.get_by_label("Username", exact=True).fill(ADMIN_USERNAME)
    page.get_by_label("Password", exact=True).fill(ADMIN_PASSWORD)
    page.get_by_role("button", name="Login", exact=True).click()
    expect(messages_link(page)).to_be_visible(timeout=UI_TIMEOUT_MS)


def logout(page: Page) -> None:
    page.get_by_role("button", name="Logout", exact=True).click()
    expect_login(page)


def read_counter(page: Page) -> int:
    link = messages_link(page)
    expect(link).to_have_text(COUNTER_PATTERN, timeout=UI_TIMEOUT_MS)
    text = link.inner_text()
    match = re.fullmatch(COUNTER_PATTERN, text)
    if match is None:
        raise AssertionError(f"Formato inesperado do contador: {text!r}")
    return int(re.search(r"[0-9]+", match.group(0)).group(0))


def expect_counter(page: Page, expected: int) -> None:
    pattern = re.compile(
        rf"^\s*Messages\s+(?:{expected}|\(\s*{expected}\s*\))\s*$",
        re.IGNORECASE,
    )
    expect(messages_link(page)).to_have_text(
        pattern, timeout=UI_TIMEOUT_MS
    )


def confirmation(page: Page, contact: dict[str, str]):
    return page.get_by_text(
        f"Thanks for getting in touch {contact['name']}!",
        exact=True,
    )


def fill_contact(page: Page, contact: dict[str, str]) -> None:
    navigate(page, f"{BASE_URL}/")
    for label, key in (
        ("Name", "name"),
        ("Email", "email"),
        ("Phone", "phone"),
        ("Subject", "subject"),
        ("Message", "message"),
    ):
        page.get_by_label(label, exact=True).fill(contact[key])


def send_contact(page: Page, contact: dict[str, str]) -> None:
    fill_contact(page, contact)
    page.get_by_role("button", name="Submit", exact=True).click()
    expect(confirmation(page, contact)).to_be_visible(
        timeout=UI_TIMEOUT_MS
    )


def open_messages(page: Page) -> None:
    messages_link(page).click()
    expect(page.get_by_role("table")).to_be_visible(
        timeout=UI_TIMEOUT_MS
    )


def matching_rows(page: Page, contact: dict[str, str]):
    return (
        page.get_by_role("table")
        .get_by_role("row")
        .filter(
            has=page.get_by_role(
                "cell", name=contact["name"], exact=True
            )
        )
        .filter(
            has=page.get_by_role(
                "cell", name=contact["subject"], exact=True
            )
        )
    )


def expect_messages(
    page: Page, contact: dict[str, str], quantity: int
) -> None:
    rows = matching_rows(page, contact)
    expect(rows).to_have_count(quantity, timeout=UI_TIMEOUT_MS)
    for index in range(quantity):
        row = rows.nth(index)
        expect(
            row.get_by_role("cell", name=contact["name"], exact=True)
        ).to_be_visible(timeout=UI_TIMEOUT_MS)
        expect(
            row.get_by_role("cell", name=contact["subject"], exact=True)
        ).to_be_visible(timeout=UI_TIMEOUT_MS)


def test_ct01_consultar_contador_inicial(page: Page) -> None:
    configure(page)
    login(page)
    initial = read_counter(page)

    page.reload(wait_until="domcontentloaded")

    expect_counter(page, initial)


def test_ct02_enviar_contato_valido(page: Page) -> None:
    configure(page)
    contact = new_contact()

    send_contact(page, contact)

    expect(confirmation(page, contact)).to_have_text(
        f"Thanks for getting in touch {contact['name']}!",
        timeout=UI_TIMEOUT_MS,
    )


def test_ct03_incrementar_contador_apos_envio(page: Page) -> None:
    configure(page)
    contact = new_contact()
    login(page)
    initial = read_counter(page)
    logout(page)

    send_contact(page, contact)
    login(page)

    expect_counter(page, initial + 1)


def test_ct04_localizar_mensagem_enviada(page: Page) -> None:
    configure(page)
    contact = new_contact()

    send_contact(page, contact)
    login(page)
    open_messages(page)

    expect_messages(page, contact, quantity=1)


def test_ct05_bloquear_acesso_direto_apos_logout(page: Page) -> None:
    configure(page)
    login(page)
    open_messages(page)
    logout(page)

    navigate(page, MESSAGES_URL)

    expect_login(page)
    expect(page.get_by_role("table")).to_have_count(
        0, timeout=UI_TIMEOUT_MS
    )
    expect(messages_link(page)).to_have_count(
        0, timeout=UI_TIMEOUT_MS
    )


def test_ct06_rejeitar_email_invalido(page: Page) -> None:
    configure(page)
    contact = new_contact()
    contact["email"] = INVALID_EMAIL
    login(page)
    initial = read_counter(page)
    logout(page)

    fill_contact(page, contact)
    page.get_by_role("button", name="Submit", exact=True).click()

    email = page.get_by_label("Email", exact=True)
    expect(email).to_be_visible(timeout=UI_TIMEOUT_MS)
    expect(email).to_have_value(INVALID_EMAIL, timeout=UI_TIMEOUT_MS)
    expect(email.and_(page.locator(":invalid"))).to_have_count(
        1, timeout=UI_TIMEOUT_MS
    )
    expect(confirmation(page, contact)).to_have_count(
        0, timeout=UI_TIMEOUT_MS
    )

    login(page)
    expect_counter(page, initial)


def test_ct07_processar_dois_envios_iguais(page: Page) -> None:
    configure(page)
    contact = new_contact()
    login(page)
    initial = read_counter(page)
    logout(page)

    send_contact(page, contact)
    login(page)
    expect_counter(page, initial + 1)
    logout(page)

    send_contact(page, contact)
    login(page)
    expect_counter(page, initial + 2)
    open_messages(page)

    expect_messages(page, contact, quantity=2)
