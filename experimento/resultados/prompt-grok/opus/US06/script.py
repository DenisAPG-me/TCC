import re
import uuid

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online"
ADMIN_URL = f"{BASE_URL}/admin"
MESSAGES_URL = f"{BASE_URL}/admin/message"
ADMIN_USER = "admin"
ADMIN_PASS = "password"

VALIDATION_ERROR = re.compile(r"blank|must|between|size|well-formed", re.IGNORECASE)


def unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def valid_contact(name: str | None = None) -> dict:
    suffix = unique_suffix()
    return {
        "name": name or f"Visitante {suffix}",
        "email": f"visitante.{suffix}@example.com",
        "phone": "01234567890",
        "subject": f"Assunto teste {suffix}",
        "message": f"Mensagem de teste automatizado {suffix} com tamanho suficiente.",
    }


def username_field(page: Page):
    return page.get_by_label("Username").or_(page.get_by_placeholder("Username"))


def password_field(page: Page):
    return page.get_by_label("Password").or_(page.get_by_placeholder("Password"))


def login_button(page: Page):
    return page.get_by_role("button", name="Login")


def messages_link(page: Page):
    return page.get_by_role("link", name=re.compile(r"Messages"))


def login(page: Page, user: str = ADMIN_USER, password: str = ADMIN_PASS) -> None:
    page.goto(ADMIN_URL)
    username_field(page).fill(user)
    password_field(page).fill(password)
    login_button(page).click()


def logout(page: Page) -> None:
    page.get_by_role("button", name="Logout").or_(page.get_by_role("link", name="Logout")).click()
    expect(messages_link(page)).to_have_count(0)


def read_messages_count(page: Page) -> int:
    link = messages_link(page)
    expect(link).to_be_visible()
    page.wait_for_load_state("networkidle")
    match = re.search(r"\d+", link.inner_text())
    return int(match.group()) if match else 0


def fill_contact_form(page: Page, data: dict) -> None:
    page.goto(BASE_URL)
    page.get_by_test_id("ContactName").fill(data["name"])
    page.get_by_test_id("ContactEmail").fill(data["email"])
    page.get_by_test_id("ContactPhone").fill(data["phone"])
    page.get_by_test_id("ContactSubject").fill(data["subject"])
    page.get_by_test_id("ContactDescription").fill(data["message"])
    page.get_by_role("button", name="Submit").click()


def assert_login_required(page: Page) -> None:
    expect(username_field(page)).to_be_visible()
    expect(password_field(page)).to_be_visible()
    expect(login_button(page)).to_be_visible()
    expect(messages_link(page)).to_have_count(0)


def test_TC01_admin_sees_numeric_messages_counter(page: Page):
    login(page)
    count = read_messages_count(page)
    assert count >= 0


def test_TC02_visitor_submits_valid_contact_and_sees_confirmation(page: Page):
    data = valid_contact()
    fill_contact_form(page, data)
    expect(page.get_by_text(f"Thanks for getting in touch {data['name']}!")).to_be_visible()


def test_TC03_messages_counter_increments_by_one_after_visitor_submission(page: Page):
    login(page)
    before = read_messages_count(page)
    logout(page)

    data = valid_contact()
    fill_contact_form(page, data)
    expect(page.get_by_text(f"Thanks for getting in touch {data['name']}!")).to_be_visible()

    login(page)
    expect(messages_link(page)).to_have_text(re.compile(rf"Messages\D*{before + 1}(\D|$)"))


def test_TC04_new_message_listed_with_sender_name_and_subject(page: Page):
    data = valid_contact()
    fill_contact_form(page, data)
    expect(page.get_by_text(f"Thanks for getting in touch {data['name']}!")).to_be_visible()

    login(page)
    expect(messages_link(page)).to_be_visible()
    messages_link(page).click()
    expect(page.get_by_text(data["name"], exact=True).first).to_be_visible()
    expect(page.get_by_text(data["subject"], exact=True).first).to_be_visible()


def test_TC05_direct_access_to_messages_after_logout_requires_login(page: Page):
    login(page)
    expect(messages_link(page)).to_be_visible()
    logout(page)
    page.goto(MESSAGES_URL)
    assert_login_required(page)


def test_TC06_direct_access_to_messages_without_session_requires_login(page: Page):
    page.context.clear_cookies()
    page.goto(MESSAGES_URL)
    assert_login_required(page)


def test_TC07_empty_contact_form_shows_errors_and_no_confirmation(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text(VALIDATION_ERROR).first).to_be_visible()
    expect(page.get_by_text("Thanks for getting in touch")).to_have_count(0)
    expect(page.get_by_test_id("ContactName")).to_be_visible()


def test_TC08_invalid_email_submission_does_not_increment_counter(page: Page):
    login(page)
    before = read_messages_count(page)
    logout(page)

    data = valid_contact()
    data["email"] = "email-invalido"
    fill_contact_form(page, data)
    expect(page.get_by_text(VALIDATION_ERROR).first).to_be_visible()
    expect(page.get_by_text("Thanks for getting in touch")).to_have_count(0)

    login(page)
    assert read_messages_count(page) == before


def test_TC09_invalid_password_does_not_grant_panel_access(page: Page):
    login(page, password="senha-incorreta")
    page.wait_for_load_state("networkidle")
    assert_login_required(page)


def test_TC10_confirmation_preserves_name_with_special_characters(page: Page):
    data = valid_contact(name=f"José D'Ávila-Ção {unique_suffix()}")
    fill_contact_form(page, data)
    expect(page.get_by_text(f"Thanks for getting in touch {data['name']}!")).to_be_visible()
