from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

FIELD_LABELS = {
    "name": "Name",
    "email": "Email",
    "phone": "Phone",
    "subject": "Subject",
    "message": "Message",
}
SUBMIT_BUTTON_NAME = "Submit"

VALID_DATA = {
    "name": "Ana Silva",
    "email": "ana.silva@example.com",
    "phone": "12345678901",
    "subject": "Consulta sobre reserva",
    "message": "Gostaria de saber mais sobre disponibilidade.",
}


def open_contact_form(page: Page) -> None:
    page.goto(BASE_URL)
    for label in FIELD_LABELS.values():
        expect(page.get_by_label(label)).to_be_visible()


def fill_form(page: Page, values: dict[str, str]) -> None:
    for field, value in values.items():
        page.get_by_label(FIELD_LABELS[field]).fill(value)


def submit_form(page: Page) -> None:
    page.get_by_role("button", name=SUBMIT_BUTTON_NAME).click()


def required_error_for(page: Page, field_label: str) -> None:
    # A mensagem exata não consta da especificação; procura texto visível
    # relacionado ao campo e à obrigatoriedade.
    message = page.get_by_text(
        __import__("re").compile(
            rf"(?=.*{__import__('re').escape(field_label)})(?=.*(required|cannot be empty|must not be empty))",
            __import__("re").IGNORECASE,
        )
    )
    expect(message).to_be_visible()


def test_CT001_envio_vazio_exibe_validacoes_dos_campos_obrigatorios(page: Page) -> None:
    open_contact_form(page)
    submit_form(page)

    for label in FIELD_LABELS.values():
        required_error_for(page, label)


def test_CT002_telefone_abaixo_do_minimo_exibe_validacao(page: Page) -> None:
    open_contact_form(page)
    values = dict(VALID_DATA)
    values["phone"] = "1234567890"
    fill_form(page, values)
    submit_form(page)

    expect(page.get_by_text("Phone must be between 11 and 21 characters.", exact=True)).to_be_visible()


def test_CT003_assunto_e_mensagem_abaixo_dos_minimos_exibem_validacoes(page: Page) -> None:
    open_contact_form(page)
    values = dict(VALID_DATA)
    values["subject"] = "abcd"
    values["message"] = "1234567890123456789"
    fill_form(page, values)
    submit_form(page)

    expect(page.get_by_text("Subject must be between 5 and 100 characters.", exact=True)).to_be_visible()
    expect(page.get_by_text("Message must be between 20 and 2000 characters.", exact=True)).to_be_visible()


def test_CT004_email_malformado_exibe_validacao(page: Page) -> None:
    open_contact_form(page)
    values = dict(VALID_DATA)
    values["email"] = "bad"
    fill_form(page, values)
    submit_form(page)

    expect(page.get_by_text("must be a well-formed email address", exact=False)).to_be_visible()


def test_CT005_formulario_valido_confirma_o_contato(page: Page) -> None:
    open_contact_form(page)
    fill_form(page, VALID_DATA)
    submit_form(page)

    expect(page.get_by_text("Thanks for getting in touch Ana Silva!", exact=True)).to_be_visible()
    expect(page.get_by_text(VALID_DATA["subject"], exact=True)).to_be_visible()
