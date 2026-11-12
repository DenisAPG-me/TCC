import pytest
from playwright.sync_api import expect

BASE_URL = "https://automationintesting.online/"


def _open_form(page):
    page.goto(BASE_URL)
    page.get_by_label("Name").fill("Ana Silva")
    page.get_by_label("Email").fill("ana@example.com")
    page.get_by_label("Phone").fill("11987654321")
    page.get_by_label("Subject").fill("Dúvida sobre reserva")
    page.get_by_label("Message").fill(
        "Olá, gostaria de saber mais sobre a disponibilidade."
    )


def _submit(page):
    page.get_by_role("button", name="Submit").click()


def _reset(page):
    page.goto(BASE_URL)


def test_TC01_empty_form_shows_required_field_messages(page):
    page.goto(BASE_URL)
    _submit(page)

    for field in ("Name", "Email", "Phone", "Subject", "Message"):
        expect(page.get_by_text(field, exact=False)).to_be_visible()


def test_TC02_phone_below_minimum_shows_validation(page):
    _open_form(page)
    page.get_by_label("Phone").fill("1234567890")
    _submit(page)

    expect(
        page.get_by_text("Phone must be between 11 and 21 characters.", exact=True)
    ).to_be_visible()


def test_TC03_subject_and_message_below_minimum_show_validation(page):
    _open_form(page)
    page.get_by_label("Subject").fill("abcd")
    page.get_by_label("Message").fill("1234567890123456789")
    _submit(page)

    expect(
        page.get_by_text("Subject must be between 5 and 100 characters.", exact=True)
    ).to_be_visible()
    expect(
        page.get_by_text("Message must be between 20 and 2000 characters.", exact=True)
    ).to_be_visible()


def test_TC04_malformed_email_shows_validation(page):
    _open_form(page)
    page.get_by_label("Email").fill("bad")
    _submit(page)

    expect(
        page.get_by_text("must be a well-formed email address", exact=False)
    ).to_be_visible()


def test_TC05_valid_submission_shows_confirmation_and_subject(page):
    subject = "Dúvida sobre reserva"
    _open_form(page)
    page.get_by_label("Subject").fill(subject)
    _submit(page)

    expect(page.get_by_text("Thanks for getting in touch Ana Silva!", exact=True)).to_be_visible()
    expect(page.get_by_text(subject, exact=True)).to_be_visible()


@pytest.mark.parametrize(
    "phone",
    ["12345678901", "123456789012345678901"],
    ids=["minimum-11", "maximum-21"],
)
def test_TC06_phone_length_boundaries_are_accepted(page, phone):
    # Cada valor parametrizado representa uma execução de caso de teste nas bordas.
    _open_form(page)
    page.get_by_label("Phone").fill(phone)
    _submit(page)

    expect(
        page.get_by_text("Phone must be between 11 and 21 characters.", exact=True)
    ).to_have_count(0)
    expect(page.get_by_text("Thanks for getting in touch Ana Silva!", exact=True)).to_be_visible()


@pytest.mark.parametrize(
    ("subject", "message"),
    [
        ("12345", "x" * 20),
        ("s" * 100, "m" * 2000),
    ],
    ids=["minimum-lengths", "maximum-lengths"],
)
def test_TC07_subject_and_message_length_boundaries_are_accepted(
    page, subject, message
):
    # Cada valor parametrizado representa uma execução de caso de teste nas bordas.
    _open_form(page)
    page.get_by_label("Subject").fill(subject)
    page.get_by_label("Message").fill(message)
    _submit(page)

    expect(
        page.get_by_text("Subject must be between 5 and 100 characters.", exact=True)
    ).to_have_count(0)
    expect(
        page.get_by_text("Message must be between 20 and 2000 characters.", exact=True)
    ).to_have_count(0)
    expect(page.get_by_text("Thanks for getting in touch Ana Silva!", exact=True)).to_be_visible()
