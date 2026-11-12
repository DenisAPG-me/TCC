import uuid

import pytest
from playwright.sync_api import expect


BASE_URL = "https://automationintesting.online/"
ADMIN_URL = BASE_URL.rstrip("/") + "/admin"
MESSAGES_URL = BASE_URL.rstrip("/") + "/admin/messages"


def unique_suffix():
    return uuid.uuid4().hex[:8]


def fill_contact_form(page, name, subject, *, include_name=True, include_subject=True):
    page.goto(BASE_URL)
    page.get_by_label("Name").fill(name if include_name else "")
    page.get_by_label("Email").fill(f"qa-{unique_suffix()}@example.com")
    page.get_by_label("Phone").fill("11987654321")
    page.get_by_label("Subject").fill(subject if include_subject else "")
    page.get_by_label("Message").fill("Mensagem de teste automatizado.")
    page.get_by_role("button", name="Submit").click()


def login_as_admin(page):
    page.goto(ADMIN_URL)
    page.get_by_label("Username").fill("admin")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()


def read_message_count(page):
    messages_link = page.get_by_role("link", name="Messages")
    expect(messages_link).to_be_visible()
    import re
    match = re.search(r"\d+", messages_link.inner_text())
    assert match, "Não foi encontrado um número ao lado de Messages"
    return int(match.group())


def test_TC01_enviar_mensagem_valida(page):
    name = f"Visitante {unique_suffix()}"
    fill_contact_form(page, name, f"Assunto {unique_suffix()}")
    expect(page.get_by_text(f"Thanks for getting in touch {name}!", exact=True)).to_be_visible()


def test_TC02_contador_aumenta_apos_envio(page):
    login_as_admin(page)
    before = read_message_count(page)

    name = f"Visitante {unique_suffix()}"
    fill_contact_form(page, name, f"Assunto {unique_suffix()}")

    login_as_admin(page)
    after = read_message_count(page)
    assert after == before + 1


def test_TC03_mensagem_enviada_aparece_na_lista(page):
    name = f"Visitante {unique_suffix()}"
    subject = f"Assunto {unique_suffix()}"
    fill_contact_form(page, name, subject)
    expect(page.get_by_text(f"Thanks for getting in touch {name}!", exact=True)).to_be_visible()

    login_as_admin(page)
    page.get_by_role("link", name="Messages").click()
    expect(page.get_by_text(name, exact=True)).to_be_visible()
    expect(page.get_by_text(subject, exact=True)).to_be_visible()


def test_TC04_caixa_de_mensagens_exige_login_apos_logout(page):
    login_as_admin(page)
    page.get_by_role("link", name="Logout").click()
    page.goto(MESSAGES_URL)

    login_prompt = page.get_by_label("Username")
    admin_route = page.get_by_role("heading", name="Admin")
    expect(login_prompt.or_(admin_route)).to_be_visible()


def test_TC05_envio_sem_nome_nao_e_confirmado(page):
    name = f"Visitante {unique_suffix()}"
    fill_contact_form(
        page,
        name,
        f"Assunto {unique_suffix()}",
        include_name=False,
    )
    expect(page.get_by_text("Thanks for getting in touch", exact=False)).to_have_count(0)


def test_TC06_envio_sem_assunto_nao_e_confirmado(page):
    name = f"Visitante {unique_suffix()}"
    fill_contact_form(
        page,
        name,
        f"Assunto {unique_suffix()}",
        include_subject=False,
    )
    expect(page.get_by_text("Thanks for getting in touch", exact=False)).to_have_count(0)


def test_TC07_envio_invalido_nao_incrementa_contador(page):
    login_as_admin(page)
    before = read_message_count(page)

    fill_contact_form(
        page,
        f"Visitante {unique_suffix()}",
        f"Assunto {unique_suffix()}",
        include_name=False,
    )

    login_as_admin(page)
    after = read_message_count(page)
    assert after == before


def test_TC08_mensagem_com_dados_distintivos_e_preservada(page):
    name = f"  Ana QA {unique_suffix()}  "
    subject = f"Consulta especial {unique_suffix()}"
    fill_contact_form(page, name, subject)

    normalized_name = name.strip()
    expect(
        page.get_by_text(
            f"Thanks for getting in touch {normalized_name}!",
            exact=True,
        )
    ).to_be_visible()

    login_as_admin(page)
    page.get_by_role("link", name="Messages").click()
    expect(page.get_by_text(normalized_name, exact=True)).to_be_visible()
    expect(page.get_by_text(subject, exact=True)).to_be_visible()
