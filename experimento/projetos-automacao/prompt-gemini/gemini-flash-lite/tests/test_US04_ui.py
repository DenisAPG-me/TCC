import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

@pytest.fixture(autouse=True)
def setup_page(page: Page):
    page.goto(BASE_URL)

def test_ct01_envio_formulario_vazio(page: Page):
    # Clica diretamente no botão de envio sem preencher os campos
    submit_button = page.get_by_role("button", name="Submit")
    submit_button.click()

    # Valida as mensagens de erro de campos obrigatórios/em branco
    expect(page.get_by_text("Name may not be blank")).toBeVisible()
    expect(page.get_by_text("Email may not be blank")).toBeVisible()
    expect(page.get_by_text("Phone may not be blank")).toBeVisible()
    expect(page.get_by_text("Subject may not be blank")).toBeVisible()
    expect(page.get_by_text("Message may not be blank")).toBeVisible()

def test_ct02_telefone_menos_11_caracteres(page: Page):
    page.get_by_test_id("ContactName").fill("João Silva")
    page.get_by_test_id("ContactEmail").fill("joao@example.com")
    page.get_by_test_id("ContactPhone").fill("12345")
    page.get_by_test_id("ContactSubject").fill("Dúvida sobre reserva")
    page.get_by_test_id("ContactDescription").fill("Esta é uma mensagem de teste válida com mais de vinte caracteres.")
    
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Phone must be between 11 and 21 characters.")).toBeVisible()

def test_ct03_assunto_mensagem_abaixo_limite(page: Page):
    page.get_by_test_id("ContactName").fill("Maria Souza")
    page.get_by_test_id("ContactEmail").fill("maria@example.com")
    page.get_by_test_id("ContactPhone").fill("11988887777")
    page.get_by_test_id("ContactSubject").fill("Ajuda")
    page.get_by_test_id("ContactDescription").fill("Curto")
    
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Subject must be between 5 and 100 characters.")).toBeVisible()
    expect(page.get_by_text("Message must be between 20 and 2000 characters.")).toBeVisible()

def test_ct04_email_malformado(page: Page):
    page.get_by_test_id("ContactName").fill("Carlos Lima")
    page.get_by_test_id("ContactEmail").fill("bad")
    page.get_by_test_id("ContactPhone").fill("11977776666")
    page.get_by_test_id("ContactSubject").fill("Reserva de quarto")
    page.get_by_test_id("ContactDescription").fill("Gostaria de saber a disponibilidade para o próximo final de semana.")
    
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("must be a well-formed email address")).toBeVisible()

def test_ct05_dados_validos(page: Page):
    nome = "Ana Beatriz"
    assunto = "Consulta de valores"
    
    page.get_by_test_id("ContactName").fill(nome)
    page.get_by_test_id("ContactEmail").fill("ana.beatriz@example.com")
    page.get_by_test_id("ContactPhone").fill("11966665555")
    page.get_by_test_id("ContactSubject").fill(assunto)
    page.get_by_test_id("ContactDescription").fill("Gostaria de verificar os valores das diárias para casal em alta temporada.")
    
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text(f"Thanks for getting in touch {nome}!")).toBeVisible()
    expect(page.get_by_text(assunto)).toBeVisible()
