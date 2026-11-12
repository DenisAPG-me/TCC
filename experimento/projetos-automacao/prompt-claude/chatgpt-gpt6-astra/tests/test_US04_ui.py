from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"
CREDENTIALS = None

ASSERT_TIMEOUT_MS = 10_000
NAVIGATION_TIMEOUT_MS = 30_000

VALID_DATA = {
    "name": "Ana Teste",
    "email": "ana.teste@example.com",
    "phone": "11987654321",
    "subject": "Consulta sobre reserva",
    "message": "Gostaria de saber se ha quartos disponiveis em dezembro.",
}

EMPTY_DATA = {field: "" for field in VALID_DATA}

PHONE_BELOW_MIN = "1" * 10
PHONE_AT_MIN = "1" * 11
PHONE_AT_MAX = "1" * 21
PHONE_ABOVE_MAX = "1" * 22

SUBJECT_BELOW_MIN = "S" * 4
SUBJECT_AT_MIN = "S" * 5
SUBJECT_AT_MAX = "S" * 100
SUBJECT_ABOVE_MAX = "S" * 101

MESSAGE_BELOW_MIN = "M" * 19
MESSAGE_AT_MIN = "M" * 20
MESSAGE_AT_MAX = "M" * 2000
MESSAGE_ABOVE_MAX = "M" * 2001

MALFORMED_EMAIL = "bad"

FIELD_LABELS = {
    "name": "Name",
    "email": "Email",
    "phone": "Phone",
    "subject": "Subject",
    "message": "Message",
}
SUBMIT_BUTTON_NAME = "Submit"

REQUIRED_ERRORS = {
    "name": "Name may not be blank",
    "email": "Email may not be blank",
    "phone": "Phone may not be blank",
    "subject": "Subject may not be blank",
    "message": "Message may not be blank",
}
PHONE_LENGTH_ERROR = "Phone must be between 11 and 21 characters."
SUBJECT_LENGTH_ERROR = "Subject must be between 5 and 100 characters."
MESSAGE_LENGTH_ERROR = "Message must be between 20 and 2000 characters."
EMAIL_FORMAT_ERROR = "must be a well-formed email address"
SUCCESS_TEMPLATE = "Thanks for getting in touch {name}!"


def submit_contact(page: Page, data: dict[str, str]) -> None:
    """Abre uma página nova e envia todos os campos pela interface."""
    page.set_default_timeout(ASSERT_TIMEOUT_MS)
    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=NAVIGATION_TIMEOUT_MS,
    )

    for field, label in FIELD_LABELS.items():
        control = page.get_by_label(label, exact=True)
        expect(control).to_be_visible(timeout=ASSERT_TIMEOUT_MS)
        control.fill(data[field])

    page.get_by_role(
        "button", name=SUBMIT_BUTTON_NAME, exact=True
    ).click()


def test_ct01_enviar_formulario_vazio(page: Page) -> None:
    submit_contact(page, EMPTY_DATA)

    for error in REQUIRED_ERRORS.values():
        expect(page.get_by_text(error, exact=True)).to_be_visible(
            timeout=ASSERT_TIMEOUT_MS
        )


def test_ct02_telefone_abaixo_do_minimo(page: Page) -> None:
    data = {**VALID_DATA, "phone": PHONE_BELOW_MIN}
    submit_contact(page, data)

    expect(page.get_by_text(PHONE_LENGTH_ERROR, exact=True)).to_be_visible(
        timeout=ASSERT_TIMEOUT_MS
    )


def test_ct03_telefone_no_minimo(page: Page) -> None:
    data = {**VALID_DATA, "phone": PHONE_AT_MIN}
    submit_contact(page, data)

    expect(
        page.get_by_role(
            "heading",
            name=SUCCESS_TEMPLATE.format(name=data["name"]),
            exact=True,
        )
    ).to_be_visible(timeout=ASSERT_TIMEOUT_MS)
    expect(page.get_by_text(data["subject"], exact=True)).to_be_visible(
        timeout=ASSERT_TIMEOUT_MS
    )


def test_ct04_telefone_no_maximo(page: Page) -> None:
    data = {**VALID_DATA, "phone": PHONE_AT_MAX}
    submit_contact(page, data)

    expect(
        page.get_by_role(
            "heading",
            name=SUCCESS_TEMPLATE.format(name=data["name"]),
            exact=True,
        )
    ).to_be_visible(timeout=ASSERT_TIMEOUT_MS)
    expect(page.get_by_text(data["subject"], exact=True)).to_be_visible(
        timeout=ASSERT_TIMEOUT_MS
    )


def test_ct05_telefone_acima_do_maximo(page: Page) -> None:
    data = {**VALID_DATA, "phone": PHONE_ABOVE_MAX}
    submit_contact(page, data)

    expect(page.get_by_text(PHONE_LENGTH_ERROR, exact=True)).to_be_visible(
        timeout=ASSERT_TIMEOUT_MS
    )


def test_ct06_assunto_e_mensagem_abaixo_do_minimo(page: Page) -> None:
    data = {
        **VALID_DATA,
        "subject": SUBJECT_BELOW_MIN,
        "message": MESSAGE_BELOW_MIN,
    }
    submit_contact(page, data)

    expect(page.get_by_text(SUBJECT_LENGTH_ERROR, exact=True)).to_be_visible(
        timeout=ASSERT_TIMEOUT_MS
    )
    expect(page.get_by_text(MESSAGE_LENGTH_ERROR, exact=True)).to_be_visible(
        timeout=ASSERT_TIMEOUT_MS
    )


def test_ct07_assunto_e_mensagem_nos_minimos(page: Page) -> None:
    data = {
        **VALID_DATA,
        "subject": SUBJECT_AT_MIN,
        "message": MESSAGE_AT_MIN,
    }
    submit_contact(page, data)

    expect(
        page.get_by_role(
            "heading",
            name=SUCCESS_TEMPLATE.format(name=data["name"]),
            exact=True,
        )
    ).to_be_visible(timeout=ASSERT_TIMEOUT_MS)
    expect(page.get_by_text(data["subject"], exact=True)).to_be_visible(
        timeout=ASSERT_TIMEOUT_MS
    )


def test_ct08_assunto_e_mensagem_nos_maximos(page: Page) -> None:
    data = {
        **VALID_DATA,
        "subject": SUBJECT_AT_MAX,
        "message": MESSAGE_AT_MAX,
    }
    submit_contact(page, data)

    expect(
        page.get_by_role(
            "heading",
            name=SUCCESS_TEMPLATE.format(name=data["name"]),
            exact=True,
        )
    ).to_be_visible(timeout=ASSERT_TIMEOUT_MS)
    expect(page.get_by_text(data["subject"], exact=True)).to_be_visible(
        timeout=ASSERT_TIMEOUT_MS
    )


def test_ct09_assunto_acima_do_maximo(page: Page) -> None:
    data = {**VALID_DATA, "subject": SUBJECT_ABOVE_MAX}
    submit_contact(page, data)

    expect(page.get_by_text(SUBJECT_LENGTH_ERROR, exact=True)).to_be_visible(
        timeout=ASSERT_TIMEOUT_MS
    )


def test_ct10_mensagem_acima_do_maximo(page: Page) -> None:
    data = {**VALID_DATA, "message": MESSAGE_ABOVE_MAX}
    submit_contact(page, data)

    expect(page.get_by_text(MESSAGE_LENGTH_ERROR, exact=True)).to_be_visible(
        timeout=ASSERT_TIMEOUT_MS
    )


def test_ct11_email_malformado(page: Page) -> None:
    data = {**VALID_DATA, "email": MALFORMED_EMAIL}
    submit_contact(page, data)

    expect(page.get_by_text(EMAIL_FORMAT_ERROR, exact=False)).to_be_visible(
        timeout=ASSERT_TIMEOUT_MS
    )


def test_ct12_enviar_dados_validos(page: Page) -> None:
    data = VALID_DATA.copy()
    submit_contact(page, data)

    expect(
        page.get_by_role(
            "heading",
            name=SUCCESS_TEMPLATE.format(name=data["name"]),
            exact=True,
        )
    ).to_be_visible(timeout=ASSERT_TIMEOUT_MS)
    expect(page.get_by_text(data["subject"], exact=True)).to_be_visible(
        timeout=ASSERT_TIMEOUT_MS
    )
