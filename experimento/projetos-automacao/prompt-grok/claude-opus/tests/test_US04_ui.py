import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

VALID_NAME = "Maria Souza"
VALID_EMAIL = "maria.souza@example.com"
VALID_PHONE = "01234567890"
VALID_SUBJECT = "Duvida sobre reserva"
VALID_MESSAGE = "Gostaria de saber se aceitam animais de estimacao."

PHONE_ERROR = "Phone must be between 11 and 21 characters."
SUBJECT_ERROR = "Subject must be between 5 and 100 characters."
MESSAGE_ERROR = "Message must be between 20 and 2000 characters."
EMAIL_ERROR = "must be a well-formed email address"


@pytest.fixture
def home_url(pytestconfig) -> str:
    return pytestconfig.getoption("base_url", default=None) or BASE_URL


def open_home(page: Page, url: str) -> None:
    page.goto(url)
    expect(page.get_by_test_id("ContactName")).to_be_visible()


def submit_contact(
    page: Page,
    name: str = VALID_NAME,
    email: str = VALID_EMAIL,
    phone: str = VALID_PHONE,
    subject: str = VALID_SUBJECT,
    message: str = VALID_MESSAGE,
) -> None:
    page.get_by_test_id("ContactName").fill(name)
    page.get_by_test_id("ContactEmail").fill(email)
    page.get_by_test_id("ContactPhone").fill(phone)
    page.get_by_test_id("ContactSubject").fill(subject)
    page.get_by_test_id("ContactDescription").fill(message)
    page.get_by_role("button", name="Submit").click()


def test_TC01_empty_form_shows_blank_errors(page: Page, home_url: str):
    open_home(page, home_url)
    submit_contact(page, name="", email="", phone="", subject="", message="")
    for field in ["Name", "Email", "Phone", "Subject", "Message"]:
        expect(
            page.get_by_text(re.compile(rf"{field} may not be blank", re.IGNORECASE))
        ).to_be_visible()


def test_TC02_phone_with_10_chars_shows_error(page: Page, home_url: str):
    open_home(page, home_url)
    submit_contact(page, phone="0123456789")
    expect(page.get_by_text(PHONE_ERROR)).to_be_visible()


def test_TC03_phone_with_11_chars_is_accepted(page: Page, home_url: str):
    open_home(page, home_url)
    submit_contact(page, phone="0" * 11, subject="abcd")
    expect(page.get_by_text(SUBJECT_ERROR)).to_be_visible()
    expect(page.get_by_text(PHONE_ERROR)).to_have_count(0)


def test_TC04_phone_with_21_chars_is_accepted(page: Page, home_url: str):
    open_home(page, home_url)
    submit_contact(page, phone="0" * 21, subject="abcd")
    expect(page.get_by_text(SUBJECT_ERROR)).to_be_visible()
    expect(page.get_by_text(PHONE_ERROR)).to_have_count(0)


def test_TC05_phone_with_22_chars_shows_error(page: Page, home_url: str):
    open_home(page, home_url)
    submit_contact(page, phone="0" * 22)
    expect(page.get_by_text(PHONE_ERROR)).to_be_visible()


def test_TC06_short_subject_and_message_show_errors(page: Page, home_url: str):
    open_home(page, home_url)
    submit_contact(page, subject="a" * 4, message="m" * 19)
    expect(page.get_by_text(SUBJECT_ERROR)).to_be_visible()
    expect(page.get_by_text(MESSAGE_ERROR)).to_be_visible()


def test_TC07_min_subject_and_message_are_accepted(page: Page, home_url: str):
    open_home(page, home_url)
    submit_contact(page, phone="0123456789", subject="a" * 5, message="m" * 20)
    expect(page.get_by_text(PHONE_ERROR)).to_be_visible()
    expect(page.get_by_text(SUBJECT_ERROR)).to_have_count(0)
    expect(page.get_by_text(MESSAGE_ERROR)).to_have_count(0)


def test_TC08_long_subject_and_message_show_errors(page: Page, home_url: str):
    open_home(page, home_url)
    submit_contact(page, subject="a" * 101, message="m" * 2001)
    expect(page.get_by_text(SUBJECT_ERROR)).to_be_visible()
    expect(page.get_by_text(MESSAGE_ERROR)).to_be_visible()


def test_TC09_malformed_email_shows_error(page: Page, home_url: str):
    open_home(page, home_url)
    submit_contact(page, email="bad")
    expect(page.get_by_text(EMAIL_ERROR)).to_be_visible()


def test_TC10_valid_submission_shows_confirmation(page: Page, home_url: str):
    open_home(page, home_url)
    subject = "Duvida sobre reserva TC10"
    submit_contact(page, subject=subject)
    expect(page.get_by_text(f"Thanks for getting in touch {VALID_NAME}!")).to_be_visible()
    expect(page.get_by_text(subject)).to_be_visible()


def test_TC11_max_subject_and_message_are_accepted(page: Page, home_url: str):
    open_home(page, home_url)
    subject = "S" * 100
    submit_contact(page, subject=subject, message="m" * 2000)
    expect(page.get_by_text(f"Thanks for getting in touch {VALID_NAME}!")).to_be_visible()
    expect(page.get_by_text(subject)).to_be_visible()
