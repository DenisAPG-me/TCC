from playwright.sync_api import Page, expect

BASE_URL = "https://automationintesting.online/"

VALID_NAME = "John Doe"
VALID_EMAIL = "john.doe@example.com"
VALID_PHONE = "11987654321"
VALID_SUBJECT = "Dúvida sobre reserva"
VALID_MESSAGE = "Gostaria de saber se há disponibilidade de vaga para o próximo final de semana."


def test_ct01_envio_do_formulario_vazio(page: Page):
    page.goto(BASE_URL)
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Name may not be blank")).to_be_visible()
    expect(page.get_by_text("Email may not be blank")).to_be_visible()
    expect(page.get_by_text("Phone may not be blank")).to_be_visible()
    expect(page.get_by_text("Subject may not be blank")).to_be_visible()
    expect(page.get_by_text("Message may not be blank")).to_be_visible()


def test_ct02_envio_de_telefone_com_menos_de_11_caracteres(page: Page):
    page.goto(BASE_URL)
    page.get_by_label("Name").fill(VALID_NAME)
    page.get_by_label("Email").fill(VALID_EMAIL)
    page.get_by_label("Phone").fill("12345")
    page.get_by_label("Subject").fill(VALID_SUBJECT)
    page.get_by_label("Message").fill(VALID_MESSAGE)
    page.get_by_role("button", name="Submit").click()

    expect(
        page.get_by_text("Phone must be between 11 and 21 characters.")
    ).to_be_visible()


def test_ct03_envio_de_assunto_curto_e_mensagem_curta(page: Page):
    page.goto(BASE_URL)
    page.get_by_label("Name").fill(VALID_NAME)
    page.get_by_label("Email").fill(VALID_EMAIL)
    page.get_by_label("Phone").fill(VALID_PHONE)
    page.get_by_label("Subject").fill("Oi")
    page.get_by_label("Message").fill("Curta")
    page.get_by_role("button", name="Submit").click()

    expect(
        page.get_by_text("Subject must be between 5 and 100 characters.")
    ).to_be_visible()
    expect(
        page.get_by_text("Message must be between 20 and 2000 characters.")
    ).to_be_visible()


def test_ct04_envio_de_email_malformado(page: Page):
    page.goto(BASE_URL)
    page.get_by_label("Name").fill(VALID_NAME)
    page.get_by_label("Email").fill("bad")
    page.get_by_label("Phone").fill(VALID_PHONE)
    page.get_by_label("Subject").fill(VALID_SUBJECT)
    page.get_by_label("Message").fill(VALID_MESSAGE)
    page.get_by_role("button", name="Submit").click()

    expect(
        page.get_by_text("must be a well-formed email address")
    ).to_be_visible()


def test_ct05_envio_de_todos_os_campos_com_dados_validos(page: Page):
    page.goto(BASE_URL)
    page.get_by_label("Name").fill(VALID_NAME)
    page.get_by_label("Email").fill(VALID_EMAIL)
    page.get_by_label("Phone").fill(VALID_PHONE)
    page.get_by_label("Subject").fill(VALID_SUBJECT)
    page.get_by_label("Message").fill(VALID_MESSAGE)
    page.get_by_role("button", name="Submit").click()

    expect(
        page.get_by_text(f"Thanks for getting in touch {VALID_NAME}!")
    ).to_be_visible()
    expect(page.get_by_text(VALID_SUBJECT)).to_be_visible()
