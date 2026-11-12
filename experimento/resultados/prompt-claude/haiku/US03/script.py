import re

from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com"
EMAIL_DEMO = "customer@practicesoftwaretesting.com"
SENHA_DEMO = "welcome01"
SENHA_INCORRETA = "senha-incorreta-123"
NOME_USUARIO_DEMO = "Jack Howe"
ENDERECO = {
    "rua": "Rua Exemplo, 100",
    "cidade": "São Paulo",
    "estado": "SP",
    "pais": "Brazil",
    "cep": "01001-000",
    "numero": "11999999999",
}
ENDERECO_VAZIO = {"rua": "", "cidade": "", "estado": "", "pais": None, "cep": "", "numero": ""}
CARTAO = {
    "numero": "4111 1111 1111 1111",
    "validade": "12/2030",
    "cvv": "123",
    "titular": NOME_USUARIO_DEMO,
}


def fazer_login(page: Page, email: str, senha: str) -> None:
    page.goto(f"{BASE_URL}/#/auth/login")
    page.get_by_label("Email address").fill(email)
    page.get_by_label("Password").fill(senha)
    page.get_by_role("button", name="Login").click()


def adicionar_produto_ao_carrinho(page: Page) -> None:
    page.goto(BASE_URL)
    page.locator("a.card").first.click()
    page.get_by_role("button", name="Add to cart").click()
    expect(page.get_by_text("Product added to shopping cart.")).to_be_visible()


def clicar_proceed(page: Page) -> None:
    page.get_by_role("button", name=re.compile("Proceed to checkout", re.IGNORECASE)).click()


def ir_para_checkout(page: Page) -> None:
    adicionar_produto_ao_carrinho(page)
    page.get_by_role("link", name=re.compile("Cart")).click()
    clicar_proceed(page)


def preencher_endereco(page: Page, dados: dict = ENDERECO) -> None:
    page.get_by_label("Address").fill(dados["rua"])
    page.get_by_label("City").fill(dados["cidade"])
    page.get_by_label("State").fill(dados["estado"])
    if dados["pais"]:
        page.get_by_label("Country").select_option(dados["pais"])
    page.get_by_label("Postcode").fill(dados["cep"])
    page.get_by_label("Phone").fill(dados["numero"])


def login_e_ir_para_endereco(page: Page) -> None:
    fazer_login(page, EMAIL_DEMO, SENHA_DEMO)
    expect(page.get_by_role("heading", name="My account")).to_be_visible()
    ir_para_checkout(page)


def login_e_ir_para_pagamento(page: Page) -> None:
    login_e_ir_para_endereco(page)
    preencher_endereco(page)
    clicar_proceed(page)


def preencher_cartao(page: Page) -> None:
    page.get_by_label("Payment method").select_option(label="Credit Card")
    page.get_by_label("Card number").fill(CARTAO["numero"])
    page.get_by_label("Expiration date").fill(CARTAO["validade"])
    page.get_by_label("CVV").fill(CARTAO["cvv"])
    page.get_by_label("Card holder name").fill(CARTAO["titular"])


def test_ct01_login_com_formulario_vazio_exibe_erros(page: Page):
    fazer_login(page, "", "")
    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_be_visible()


def test_ct02_login_com_senha_incorreta_nao_cria_sessao(page: Page):
    fazer_login(page, EMAIL_DEMO, SENHA_INCORRETA)
    expect(page.get_by_text("Invalid email or password")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/auth/login"))
    expect(page.get_by_role("button", name="Login")).to_be_visible()
    expect(page.get_by_role("heading", name="My account")).to_have_count(0)


def test_ct03_login_com_email_e_senha_vazia_exibe_erro_de_senha(page: Page):
    fazer_login(page, EMAIL_DEMO, "")
    expect(page.get_by_text("Password is required")).to_be_visible()
    expect(page.get_by_text("Email is required")).to_have_count(0)


def test_ct04_login_com_email_vazio_exibe_erro_de_email(page: Page):
    fazer_login(page, "", SENHA_DEMO)
    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_have_count(0)


def test_ct05_checkout_sem_autenticacao_redireciona_para_login(page: Page):
    ir_para_checkout(page)
    expect(page).to_have_url(re.compile(r"/auth/login"))
    expect(page.get_by_label("Email address")).to_be_visible()


def test_ct06_login_com_conta_demo_exibe_my_account(page: Page):
    fazer_login(page, EMAIL_DEMO, SENHA_DEMO)
    expect(page.get_by_role("heading", name="My account")).to_be_visible()
    expect(page.get_by_role("navigation").get_by_text(NOME_USUARIO_DEMO)).to_be_visible()


def test_ct07_endereco_com_campos_obrigatorios_vazios_nao_avanca(page: Page):
    login_e_ir_para_endereco(page)
    preencher_endereco(page, ENDERECO_VAZIO)
    clicar_proceed(page)
    expect(page.get_by_label("Payment method")).to_have_count(0)


def test_ct08_endereco_com_campos_obrigatorios_preenchidos_avanca(page: Page):
    login_e_ir_para_endereco(page)
    preencher_endereco(page)
    clicar_proceed(page)
    expect(page.get_by_label("Payment method")).to_be_visible()


def test_ct09_cep_vazio_impede_avanco_para_pagamento(page: Page):
    login_e_ir_para_endereco(page)
    preencher_endereco(page, {**ENDERECO, "cep": ""})
    clicar_proceed(page)
    expect(page.get_by_label("Payment method")).to_have_count(0)


def test_ct10_pagamento_com_cartao_valido_exibe_sucesso(page: Page):
    login_e_ir_para_pagamento(page)
    preencher_cartao(page)
    page.get_by_role("button", name="Confirm").click()
    expect(page.get_by_text("Payment was successful")).to_be_visible()


def test_ct11_confirmacao_do_pedido_exibe_numero_da_fatura(page: Page):
    login_e_ir_para_pagamento(page)
    preencher_cartao(page)
    page.get_by_role("button", name="Confirm").click()
    expect(
        page.get_by_text(re.compile(r"Thanks for your order! Your invoice number is INV-"))
    ).to_be_visible()


def test_ct12_pagamento_com_dados_de_cartao_vazios_nao_confirma(page: Page):
    login_e_ir_para_pagamento(page)
    page.get_by_label("Payment method").select_option(label="Credit Card")
    page.get_by_role("button", name="Confirm").click()
    expect(page.get_by_text("Payment was successful")).to_have_count(0)
