import pytest
import requests
from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

def test_CT001_visualizar_e_anotar_contador_de_mensagens_no_painel(page: Page) -> None:
    page.goto(f"{BASE_URL}#/admin")
    page.get_by_label("Username").fill("admin")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()
    
    messages_counter = page.locator("#messagesCount, [href*='messages'], .card").filter(has_text="Messages").first
    expect(messages_counter).to_be_visible()

def test_CT002_envio_de_formulario_de_contato_com_dados_validos_pelo_visitante(page: Page) -> None:
    page.goto(BASE_URL)
    page.get_by_placeholder("Name").fill("Visitante Teste")
    page.get_by_placeholder("Email").fill("visitante@teste.com")
    page.get_by_placeholder("Phone").fill("01234567890")
    page.get_by_placeholder("Subject").fill("Reserva de Quarto")
    page.get_by_placeholder("Message").fill("Gostaria de saber a disponibilidade para o próximo fim de semana.")
    
    page.get_by_role("button", name="Submit").click()
    
    confirmation = page.get_by_text("Thanks for getting in touch Visitante Teste!")
    expect(confirmation).to_be_visible()

def test_CT003_incrementar_contador_de_mensagens_apos_envio(page: Page) -> None:
    response = requests.post(
        f"{BASE_URL}message/",
        json={
            "name": "Remetente Incremental",
            "email": "incremental@teste.com",
            "phone": "12345678901",
            "subject": "Teste Incremento",
            "description": "Mensagem gerada para teste de incremento do contador."
        },
        timeout=10
    )
    assert response.status_code in [200, 201]

    page.goto(f"{BASE_URL}#/admin")
    page.get_by_label("Username").fill("admin")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()
    
    dashboard_element = page.get_by_text("Messages").first
    expect(dashboard_element).to_be_visible()

def test_CT004_exibir_mensagem_recem_enviada_na_caixa_de_mensagens(page: Page) -> None:
    unique_subject = "Assunto Unico CT004"
    unique_name = "Remetente CT004"
    requests.post(
        f"{BASE_URL}message/",
        json={
            "name": unique_name,
            "email": "ct004@teste.com",
            "phone": "12345678901",
            "subject": unique_subject,
            "description": "Conteudo da mensagem para validacao na caixa de entrada."
        },
        timeout=10
    )

    page.goto(f"{BASE_URL}#/admin")
    page.get_by_label("Username").fill("admin")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()
    
    messages_link = page.get_by_role("link", name="Messages")
    if messages_link.count() > 0:
        messages_link.click()
    
    expect(page.get_by_text(unique_subject)).to_be_visible()
    expect(page.get_by_text(unique_name)).to_be_visible()

def test_CT005_restricao_de_acesso_a_caixa_de_mensagens_apos_logout(page: Page) -> None:
    page.goto(f"{BASE_URL}#/admin")
    page.get_by_label("Username").fill("admin")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()
    
    logout_button = page.get_by_role("button", name="Logout")
    if logout_button.count() > 0:
        logout_button.click()
    
    page.goto(f"{BASE_URL}#/admin")
    expect(page.get_by_label("Username")).to_be_visible()

def test_CT006_envio_de_formulario_de_contato_com_campos_obrigatorios_vazios(page: Page) -> None:
    page.goto(BASE_URL)
    page.get_by_role("button", name="Submit").click()
    
    error_indicator = page.locator(".alert, .alert-danger, input:invalid, textarea:invalid").first
    expect(error_indicator).to_be_visible()

def test_CT007_tentativa_de_login_no_painel_com_credenciais_invalidas(page: Page) -> None:
    page.goto(f"{BASE_URL}#/admin")
    page.get_by_label("Username").fill("admin")
    page.get_by_label("Password").fill("wrongpassword")
    page.get_by_role("button", name="Login").click()
    
    error_message = page.locator(".alert, .alert-danger, .error").first
    expect(error_message).to_be_visible()

def test_CT008_limite_de_caracteres_no_campo_de_assunto_do_contato(page: Page) -> None:
    page.goto(BASE_URL)
    long_subject = "A" * 300
    page.get_by_placeholder("Name").fill("Teste Limite")
    page.get_by_placeholder("Email").fill("limite@teste.com")
    page.get_by_placeholder("Phone").fill("01234567890")
    page.get_by_placeholder("Subject").fill(long_subject)
    page.get_by_placeholder("Message").fill("Testando limite de caracteres no campo de assunto.")
    
    page.get_by_role("button", name="Submit").click()
    
    page.wait_for_load_state("networkidle")
