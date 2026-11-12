import re
import uuid

import pytest
from playwright.sync_api import Page, expect


BASE_URL = "https://automationintesting.online/"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"


def unique_contact():
    suffix = uuid.uuid4().hex[:8]
    return {
        "name": f"Visitante {suffix}",
        "email": f"visitante.{suffix}@example.com",
        "phone": f"1198765{suffix[:4]}",
        "subject": f"Assunto {suffix}",
        "message": f"Mensagem de teste {suffix}",
    }


def fill_and_submit_contact(page: Page, contact):
    page.goto(BASE_URL)
    page.get_by_label("Name").fill(contact["name"])
    page.get_by_label("Email").fill(contact["email"])
    page.get_by_label("Phone").fill(contact["phone"])
    page.get_by_label("Subject").fill(contact["subject"])
    page.get_by_label("Message").fill(contact["message"])
    page.get_by_role("button", name=re.compile(r"submit", re.I)).click()


def login_admin(page: Page):
    page.goto(f"{BASE_URL.rstrip('/')}/admin")
    page.get_by_label("Username").fill(ADMIN_USERNAME)
    page.get_by_label("Password").fill(ADMIN_PASSWORD)
    page.get_by_role("button", name=re.compile(r"login", re.I)).click()


def messages_link(page: Page):
    return page.get_by_role("link", name=re.compile(r"^Messages\b", re.I))


def message_count(page: Page) -> int:
    link = messages_link(page)
    expect(link).to_be_visible()
    match = re.search(r"\d+", link.inner_text())
    assert match, "O link Messages não exibe um contador numérico."
    return int(match.group())


def open_messages(page: Page):
    page.goto(f"{BASE_URL.rstrip('/')}/admin")
    if page.get_by_label("Username").count():
        page.get_by_label("Username").fill(ADMIN_USERNAME)
        page.get_by_label("Password").fill(ADMIN_PASSWORD)
        page.get_by_role("button", name=re.compile(r"login", re.I)).click()
    messages_link(page).click()


def test_CT01_admin_can_view_messages_counter(page: Page):
    login_admin(page)

    expect(messages_link(page)).to_be_visible()
    assert message_count(page) >= 0


def test_CT02_valid_contact_submission_shows_confirmation(page: Page):
    contact = unique_contact()
    fill_and_submit_contact(page, contact)

    expect(
        page.get_by_text(
            f"Thanks for getting in touch {contact['name']}!",
            exact=True,
        )
    ).to_be_visible()


def test_CT03_message_counter_increases_by_one_after_submission(page: Page):
    login_admin(page)
    before = message_count(page)

    contact = unique_contact()
    fill_and_submit_contact(page, contact)
    expect(
        page.get_by_text(
            f"Thanks for getting in touch {contact['name']}!",
            exact=True,
        )
    ).to_be_visible()

    login_admin(page)
    after = message_count(page)
    assert after == before + 1


def test_CT04_submitted_message_is_listed_with_name_and_subject(page: Page):
    contact = unique_contact()
    fill_and_submit_contact(page, contact)
    expect(
        page.get_by_text(
            f"Thanks for getting in touch {contact['name']}!",
            exact=True,
        )
    ).to_be_visible()

    login_admin(page)
    messages_link(page).click()

    expect(page.get_by_text(contact["name"], exact=True)).to_be_visible()
    expect(page.get_by_text(contact["subject"], exact=True)).to_be_visible()


def test_CT05_direct_messages_access_after_logout_requires_login(page: Page):
    login_admin(page)

    logout = page.get_by_role("link", name=re.compile(r"logout", re.I))
    if logout.count() == 0:
        logout = page.get_by_role("button", name=re.compile(r"logout", re.I))
    expect(logout).to_be_visible()
    logout.click()

    page.goto(f"{BASE_URL.rstrip('/')}/admin/messages")

    login_prompt = page.get_by_label("Username")
    expect(login_prompt).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()


def test_CT06_incomplete_contact_form_does_not_show_success(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("button", name=re.compile(r"submit", re.I)).click()

    expect(
        page.get_by_text(re.compile(r"Thanks for getting in touch", re.I))
    ).to_have_count(0)
