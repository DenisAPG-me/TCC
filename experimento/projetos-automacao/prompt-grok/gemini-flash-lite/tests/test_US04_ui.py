import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

@pytest.fixture(autouse=True)
def setup_page(page: Page):
    page.goto(BASE_URL)

def test_TC01_enviar_formulario_vazio(page: Page):
    # Clica no botão de envio sem preencher os campos
    submit_button = page.get_by_role("button", name="Submit")
    submit_button.click()

    # Valida as mensagens de erro de campos obrigatórios/em branco
    expect(page.get_by_text("Name may not be blank")).to_be_visible()
    expect(page.get_by_text("Email may not be blank")).to_be_visible()
    expect(page.get_by_text("Phone may not be blank")).to_be_visible()
    expect(page.get_by_text("Subject may not be blank")).to_be_visible()
    expect(page.get_by_text("Message may not be blank")).to_be_visible()

def test_TC02_telefone_curto(page: Page):
    page.get_by_label("Name").fill("João Silva")
    page.get_by_label("Email").fill("joao@example.com")
    page.get_by_label("Phone").fill("12345")  # Menos de 11 caracteres
    page.get_by_label("Subject").fill("Dúvida sobre reserva")
    page.get_by_label("Message").fill("Gostaria de saber mais informações sobre as acomodações disponíveis.")
    
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Phone must be between 11 and 21 characters.")).to_be_visible()

def test_TC03_assunto_e_mensagem_curtos(page: Page):
    page.get_by_label("Name").fill("João Silva")
    page.get_by_label("Email").fill("joao@example.com")
    page.get_by_label("Phone").fill("11987654321")
    page.get_by_label("Subject").fill("Oi")  # Menos de 5 caracteres
    page.get_by_label("Message").fill("Curta")  # Menos de 20 caracteres
    
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Subject must be between 5 and 100 characters.")).to_be_visible()
    expect(page.get_by_text("Message must be between 20 and 2000 characters.")).to_be_visible()

def test_TC04_email_malformado(page: Page):
    page.get_by_label("Name").fill("João Silva")
    page.get_by_label("Email").fill("bad")  # E-mail malformado
    page.get_by_label("Phone").fill("11987654321")
    page.get_by_label("Subject").fill("Dúvida sobre reserva")
    page.get_by_label("Message").fill("Gostaria de saber mais informações sobre as acomodações disponíveis.")
    
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("must be a well-formed email address")).to_be_visible()

def test_TC05_formulario_valido(page: Page):
    nome = "João Silva"
    assunto = "Dúvida sobre reserva"
    
    page.get_by_label("Name").fill(nome)
    page.get_by_label("Email").fill("joao@example.com")
    page.get_by_label("Phone").fill("11987654321")
    page.get_by_label("Subject").fill(assunto)
    page.get_by_label("Message").fill("Gostaria de saber mais informações sobre as acomodações disponíveis.")
    
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text(f"Thanks for getting in touch {nome}!")).to_be_visible()
    expect(page.get_by_text(assunto)).to_be_visible()
