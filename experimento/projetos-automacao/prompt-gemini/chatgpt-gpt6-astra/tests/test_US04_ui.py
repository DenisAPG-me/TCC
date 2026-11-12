import sys

import pytest
from playwright.sync_api import Page, expect


BASE_URL = "https://automationintesting.online/"

PHONE_ERROR = "Phone must be between 11 and 21 characters."
SUBJECT_ERROR = "Subject must be between 5 and 100 characters."
MESSAGE_ERROR = "Message must be between 20 and 2000 characters."
EMAIL_ERROR = "must be a well-formed email address"

REQUIRED_ERRORS = (
    "Name may not be blank",
    "Email may not be blank",
    "Phone may not be blank",
    "Subject may not be blank",
    "Message may not be blank",
)

LABELS = {
    "name": "Name",
    "email": "Email",
    "phone": "Phone",
    "subject": "Subject",
    "message": "Message",
}

VALID_DATA = {
    "name": "Ana Silva",
    "email": "ana.silva@example.com",
    "phone": "119876543210123",
    "subject": "Consulta sobre reserva",
    "message": "Gostaria de saber se ha quartos disponiveis para reserva.",
}

expect.set_options(timeout=10_000)


def open_contact(page: Page) -> None:
    page.goto(BASE_URL, wait_until="domcontentloaded")
    expect(page.get_by_label("Name", exact=True)).to_be_visible()
    expect(
        page.get_by_role("button", name="Submit", exact=True)
    ).to_be_visible()


def submit_contact(page: Page, **overrides: str) -> dict:
    data = {**VALID_DATA, **overrides}
    open_contact(page)

    for field, label in LABELS.items():
        control = page.get_by_label(label, exact=True)
        control.fill(data[field])
        # Detecta truncamento dos dados, inclusive nos limites superiores.
        expect(control).to_have_value(data[field])

    page.get_by_role("button", name="Submit", exact=True).click()
    return data


def expect_error(page: Page, message: str, exact: bool = True) -> None:
    expect(page.get_by_text(message, exact=exact)).to_be_visible()


def expect_success(page: Page, data: dict) -> None:
    expect(
        page.get_by_text(
            f"Thanks for getting in touch {data['name']}!",
            exact=True,
        )
    ).to_be_visible()
    expect(
        page.get_by_text(data["subject"], exact=True)
    ).to_be_visible()


def test_CT01_formulario_vazio(page: Page) -> None:
    open_contact(page)
    for label in LABELS.values():
        expect(page.get_by_label(label, exact=True)).to_have_value("")

    page.get_by_role("button", name="Submit", exact=True).click()

    for message in REQUIRED_ERRORS:
        expect_error(page, message)


def test_CT02_telefone_10_caracteres(page: Page) -> None:
    submit_contact(page, phone="1" * 10)
    expect_error(page, PHONE_ERROR)


def test_CT03_assunto_e_mensagem_abaixo_dos_minimos(page: Page) -> None:
    submit_contact(page, subject="S" * 4, message="M" * 19)
    expect_error(page, SUBJECT_ERROR)
    expect_error(page, MESSAGE_ERROR)


def test_CT04_email_malformado(page: Page) -> None:
    submit_contact(page, email="bad")
    expect_error(page, EMAIL_ERROR, exact=False)


def test_CT05_dados_validos(page: Page) -> None:
    data = submit_contact(page)
    expect_success(page, data)


def test_CT06_telefone_11_caracteres(page: Page) -> None:
    data = submit_contact(page, phone="1" * 11)
    expect_success(page, data)


def test_CT07_telefone_21_caracteres(page: Page) -> None:
    data = submit_contact(page, phone="1" * 21)
    expect_success(page, data)


def test_CT08_telefone_22_caracteres(page: Page) -> None:
    submit_contact(page, phone="1" * 22)
    expect_error(page, PHONE_ERROR)


def test_CT09_assunto_4_caracteres(page: Page) -> None:
    submit_contact(page, subject="S" * 4)
    expect_error(page, SUBJECT_ERROR)


def test_CT10_assunto_5_caracteres(page: Page) -> None:
    data = submit_contact(page, subject="S" * 5)
    expect_success(page, data)


def test_CT11_assunto_100_caracteres(page: Page) -> None:
    data = submit_contact(page, subject="S" * 100)
    expect_success(page, data)


def test_CT12_assunto_101_caracteres(page: Page) -> None:
    submit_contact(page, subject="S" * 101)
    expect_error(page, SUBJECT_ERROR)


def test_CT13_mensagem_19_caracteres(page: Page) -> None:
    submit_contact(page, message="M" * 19)
    expect_error(page, MESSAGE_ERROR)


def test_CT14_mensagem_20_caracteres(page: Page) -> None:
    data = submit_contact(page, message="M" * 20)
    expect_success(page, data)


def test_CT15_mensagem_2000_caracteres(page: Page) -> None:
    data = submit_contact(page, message="M" * 2000)
    expect_success(page, data)


def test_CT16_mensagem_2001_caracteres(page: Page) -> None:
    submit_contact(page, message="M" * 2001)
    expect_error(page, MESSAGE_ERROR)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))
