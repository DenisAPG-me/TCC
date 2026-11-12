from collections.abc import Iterator

import pytest
from playwright.sync_api import Browser, Page, expect, sync_playwright


BASE_URL = "https://automationintesting.online/"

# Valores inferidos e opções ajustáveis.
HEADLESS = True
ACTION_TIMEOUT_MS = 15_000
NAVIGATION_TIMEOUT_MS = 30_000
ASSERTION_TIMEOUT_MS = 15_000

FIELD_LABELS = {
    "name": "Name",
    "email": "Email",
    "phone": "Phone",
    "subject": "Subject",
    "message": "Message",
}

SUBMIT_BUTTON_NAME = "Submit"
SUCCESS_TEMPLATE = "Thanks for getting in touch {name}!"

REQUIRED_ERRORS = {
    "name": "Name may not be blank",
    "email": "Email may not be blank",
    "phone": "Phone may not be blank",
    "subject": "Subject may not be blank",
    "message": "Message may not be blank",
}

# Textos explícitos dos critérios de aceitação.
PHONE_ERROR = "Phone must be between 11 and 21 characters."
SUBJECT_ERROR = "Subject must be between 5 and 100 characters."
MESSAGE_ERROR = "Message must be between 20 and 2000 characters."
EMAIL_ERROR = "must be a well-formed email address"

# Limites inferidos das mensagens de validação.
PHONE_MIN = 11
PHONE_MAX = 21
SUBJECT_MIN = 5
SUBJECT_MAX = 100
MESSAGE_MIN = 20
MESSAGE_MAX = 2000

VALID_DATA = {
    "name": "Ana Silva",
    "email": "ana.silva@example.com",
    "phone": "5511998765432",
    "subject": "Consulta sobre disponibilidade",
    "message": "Gostaria de saber se ha quartos disponiveis para duas pessoas.",
}


@pytest.fixture(scope="session")
def chromium_browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=HEADLESS)
        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture
def contact_page(chromium_browser: Browser) -> Iterator[Page]:
    context = chromium_browser.new_context()
    try:
        page = context.new_page()
        page.set_default_timeout(ACTION_TIMEOUT_MS)
        page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)

        response = page.goto(BASE_URL, wait_until="domcontentloaded")
        assert response is not None, "A navegação não retornou resposta HTTP."
        assert response.ok, (
            f"Falha ao abrir a página inicial: HTTP {response.status}."
        )

        for label in FIELD_LABELS.values():
            expect(page.get_by_label(label, exact=True)).to_be_visible(
                timeout=ASSERTION_TIMEOUT_MS
            )

        expect(
            page.get_by_role("button", name=SUBMIT_BUTTON_NAME, exact=True)
        ).to_be_enabled(timeout=ASSERTION_TIMEOUT_MS)

        yield page
    finally:
        context.close()


def data_with(**overrides: str) -> dict[str, str]:
    unknown_fields = set(overrides) - set(VALID_DATA)
    assert not unknown_fields, f"Campos desconhecidos: {unknown_fields}"
    return {**VALID_DATA, **overrides}


def fill_contact(page: Page, data: dict[str, str]) -> None:
    for field, label in FIELD_LABELS.items():
        locator = page.get_by_label(label, exact=True)
        locator.fill(data[field])
        expect(locator).to_have_value(
            data[field], timeout=ASSERTION_TIMEOUT_MS
        )


def submit_contact(page: Page) -> None:
    page.get_by_role(
        "button", name=SUBMIT_BUTTON_NAME, exact=True
    ).click()


def assert_error(page: Page, text: str) -> None:
    expect(page.get_by_text(text, exact=True)).to_be_visible(
        timeout=ASSERTION_TIMEOUT_MS
    )


def assert_no_success(page: Page, name: str) -> None:
    expect(
        page.get_by_text(SUCCESS_TEMPLATE.format(name=name), exact=True)
    ).to_have_count(0, timeout=ASSERTION_TIMEOUT_MS)


def assert_success(page: Page, data: dict[str, str]) -> None:
    expect(
        page.get_by_text(
            SUCCESS_TEMPLATE.format(name=data["name"]), exact=True
        )
    ).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)

    expect(
        page.get_by_text(data["subject"], exact=True)
    ).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)


def test_CT001_enviar_formulario_vazio(contact_page: Page) -> None:
    data = {field: "" for field in FIELD_LABELS}
    fill_contact(contact_page, data)
    submit_contact(contact_page)

    for error in REQUIRED_ERRORS.values():
        assert_error(contact_page, error)

    assert_no_success(contact_page, data["name"])


def test_CT002_telefone_abaixo_do_minimo(contact_page: Page) -> None:
    data = data_with(phone="1" * (PHONE_MIN - 1))
    assert len(data["phone"]) == 10

    fill_contact(contact_page, data)
    submit_contact(contact_page)

    assert_error(contact_page, PHONE_ERROR)
    assert_no_success(contact_page, data["name"])


def test_CT003_assunto_mensagem_abaixo_dos_minimos(
    contact_page: Page,
) -> None:
    data = data_with(
        subject="A" * (SUBJECT_MIN - 1),
        message="M" * (MESSAGE_MIN - 1),
    )
    assert len(data["subject"]) == 4
    assert len(data["message"]) == 19

    fill_contact(contact_page, data)
    submit_contact(contact_page)

    assert_error(contact_page, SUBJECT_ERROR)
    assert_error(contact_page, MESSAGE_ERROR)
    assert_no_success(contact_page, data["name"])


def test_CT004_email_malformado(contact_page: Page) -> None:
    data = data_with(email="bad")
    fill_contact(contact_page, data)
    submit_contact(contact_page)

    assert_error(contact_page, EMAIL_ERROR)
    assert_no_success(contact_page, data["name"])


def test_CT005_dados_validos_intermediarios(contact_page: Page) -> None:
    data = data_with()
    assert PHONE_MIN < len(data["phone"]) < PHONE_MAX
    assert SUBJECT_MIN < len(data["subject"]) < SUBJECT_MAX
    assert MESSAGE_MIN < len(data["message"]) < MESSAGE_MAX

    fill_contact(contact_page, data)
    submit_contact(contact_page)

    assert_success(contact_page, data)


def test_CT006_dados_nos_limites_minimos(contact_page: Page) -> None:
    data = data_with(
        phone="1" * PHONE_MIN,
        subject="A" * SUBJECT_MIN,
        message="M" * MESSAGE_MIN,
    )
    assert len(data["phone"]) == 11
    assert len(data["subject"]) == 5
    assert len(data["message"]) == 20

    fill_contact(contact_page, data)
    submit_contact(contact_page)

    assert_success(contact_page, data)


def test_CT007_dados_nos_limites_maximos(contact_page: Page) -> None:
    data = data_with(
        phone="1" * PHONE_MAX,
        subject="A" * SUBJECT_MAX,
        message="M" * MESSAGE_MAX,
    )
    assert len(data["phone"]) == 21
    assert len(data["subject"]) == 100
    assert len(data["message"]) == 2000

    fill_contact(contact_page, data)
    submit_contact(contact_page)

    assert_success(contact_page, data)


def test_CT008_telefone_acima_do_maximo(contact_page: Page) -> None:
    data = data_with(phone="1" * (PHONE_MAX + 1))
    assert len(data["phone"]) == 22

    fill_contact(contact_page, data)
    submit_contact(contact_page)

    assert_error(contact_page, PHONE_ERROR)
    assert_no_success(contact_page, data["name"])


def test_CT009_assunto_mensagem_acima_dos_maximos(
    contact_page: Page,
) -> None:
    data = data_with(
        subject="A" * (SUBJECT_MAX + 1),
        message="M" * (MESSAGE_MAX + 1),
    )
    assert len(data["subject"]) == 101
    assert len(data["message"]) == 2001

    fill_contact(contact_page, data)
    submit_contact(contact_page)

    assert_error(contact_page, SUBJECT_ERROR)
    assert_error(contact_page, MESSAGE_ERROR)
    assert_no_success(contact_page, data["name"])
