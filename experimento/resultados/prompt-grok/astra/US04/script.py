from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

VALID_DATA = {
    "name": "Ana Silva",
    "email": "ana.silva@example.com",
    "phone": "119876543210",
    "subject": "Duvida sobre reserva",
    "message": (
        "Gostaria de saber se ha quartos disponiveis em dezembro."
    ),
}

FIELD_LABELS = {
    "name": "Name",
    "email": "Email",
    "phone": "Phone",
    "subject": "Subject",
    "message": "Message",
}

BLANK_ERRORS = (
    "Name may not be blank",
    "Email may not be blank",
    "Phone may not be blank",
    "Subject may not be blank",
    "Message may not be blank",
)

PHONE_ERROR = "Phone must be between 11 and 21 characters."
SUBJECT_ERROR = "Subject must be between 5 and 100 characters."
MESSAGE_ERROR = "Message must be between 20 and 2000 characters."
EMAIL_ERROR = "must be a well-formed email address"


def _submit(page: Page, data: dict[str, str]) -> None:
    """Seletores presumidos: rótulos exatos e botão Submit único."""
    page.goto(BASE_URL)

    for field, label in FIELD_LABELS.items():
        page.get_by_label(label, exact=True).fill(data[field])

    page.get_by_role("button", name="Submit", exact=True).click()


def _submit_valid_variant(page: Page, **changes: str) -> dict[str, str]:
    """Cria dados independentes, sem modificar os valores padrão."""
    data = {**VALID_DATA, **changes}
    _submit(page, data)
    return data


def _expect_error(page: Page, message: str) -> None:
    expect(page.get_by_text(message, exact=False)).to_be_visible()


def _expect_success(page: Page, data: dict[str, str]) -> None:
    expect(
        page.get_by_text(
            f"Thanks for getting in touch {data['name']}!",
            exact=True,
        )
    ).to_be_visible()

    expect(
        page.get_by_text(data["subject"], exact=True)
    ).to_be_visible()


def test_TC01_formulario_vazio(page: Page) -> None:
    _submit(page, {field: "" for field in FIELD_LABELS})

    for message in BLANK_ERRORS:
        _expect_error(page, message)


def test_TC02_telefone_com_10_caracteres(page: Page) -> None:
    _submit_valid_variant(page, phone="1" * 10)

    _expect_error(page, PHONE_ERROR)


def test_TC03_assunto_com_4_e_mensagem_com_19_caracteres(
    page: Page,
) -> None:
    _submit_valid_variant(
        page,
        subject="A" * 4,
        message="M" * 19,
    )

    _expect_error(page, SUBJECT_ERROR)
    _expect_error(page, MESSAGE_ERROR)


def test_TC04_email_malformado(page: Page) -> None:
    _submit_valid_variant(page, email="bad")

    _expect_error(page, EMAIL_ERROR)


def test_TC05_dados_validos_intermediarios(page: Page) -> None:
    data = _submit_valid_variant(page)

    _expect_success(page, data)


def test_TC06_limites_minimos_validos(page: Page) -> None:
    data = _submit_valid_variant(
        page,
        phone="1" * 11,
        subject="A" * 5,
        message="M" * 20,
    )

    _expect_success(page, data)


def test_TC07_limites_maximos_validos(page: Page) -> None:
    data = _submit_valid_variant(
        page,
        phone="1" * 21,
        subject="A" * 100,
        message="M" * 2000,
    )

    _expect_success(page, data)


def test_TC08_telefone_com_22_caracteres(page: Page) -> None:
    _submit_valid_variant(page, phone="1" * 22)

    _expect_error(page, PHONE_ERROR)


def test_TC09_assunto_com_101_caracteres(page: Page) -> None:
    _submit_valid_variant(page, subject="A" * 101)

    _expect_error(page, SUBJECT_ERROR)


def test_TC10_mensagem_com_2001_caracteres(page: Page) -> None:
    _submit_valid_variant(page, message="M" * 2001)

    _expect_error(page, MESSAGE_ERROR)
