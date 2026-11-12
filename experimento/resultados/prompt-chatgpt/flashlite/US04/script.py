import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

def test_CT001_envio_formulario_vazio(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("Name may not be blank")).toBeVisible()
    expect(page.get_by_text("Email may not be blank")).toBeVisible()
    expect(page.get_by_text("Phone may not be blank")).toBeVisible()
    expect(page.get_by_text("Subject may not be blank")).toBeVisible()
    expect(page.get_by_text("Message may not be blank")).toBeVisible()

def test_CT002_telefone_curto(page: Page):
    page.goto(BASE_URL)
    page.get_by_label("Name").fill("Joao Silva")
    page.get_by_label("Email").fill("joao.silva@example.com")
    page.get_by_label("Phone").fill("1234567890")
    page.get_by_label("Subject").fill("Reserva")
    page.get_by_label("Message").fill("Gostaria de saber a disponibilidade de quartos.")
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("Phone must be between 11 and 21 characters.")).toBeVisible()

def test_CT003_assunto_e_mensagem_curtos(page: Page):
    page.goto(BASE_URL)
    page.get_by_label("Name").fill("Joao Silva")
    page.get_by_label("Email").fill("joao.silva@example.com")
    page.get_by_label("Phone").fill("11987654321")
    page.get_by_label("Subject").fill("Res")
    page.get_by_label("Message").fill("Curta")
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("Subject must be between 5 and 100 characters.")).toBeVisible()
    expect(page.get_by_text("Message must be between 20 and 2000 characters.")).toBeVisible()

def test_CT004_email_malformado(page: Page):
    page.goto(BASE_URL)
    page.get_by_label("Name").fill("Joao Silva")
    page.get_by_label("Email").fill("bad")
    page.get_by_label("Phone").fill("11987654321")
    page.get_by_label("Subject").fill("Reserva")
    page.get_by_label("Message").fill("Gostaria de saber a disponibilidade de quartos.")
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("must be a well-formed email address")).toBeVisible()

def test_CT005_envio_dados_validos(page: Page):
    page.goto(BASE_URL)
    page.get_by_label("Name").fill("Joao Silva")
    page.get_by_label("Email").fill("joao.silva@example.com")
    page.get_by_label("Phone").fill("11987654321")
    page.get_by_label("Subject").fill("Reserva para o fim de semana")
    page.get_by_label("Message").fill("Gostaria de saber a disponibilidade de quartos para o proximo final de semana.")
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("Thanks for getting in touch Joao Silva!")).toBeVisible()
    expect(page.get_by_text("Reserva para o fim de semana")).toBeVisible()
