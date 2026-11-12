import re

from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"
DEMO_EMAIL = "customer@practicesoftwaretesting.com"
DEMO_PASSWORD = "welcome01"
WRONG_PASSWORD = "SenhaErrada123"
DEMO_USER_NAME = "Jane"
COUNTRY = "Brazil"
ADDRESS = {
    "Street": "Rua das Flores",
    "House number": "100",
    "Postcode": "01001000",
    "City": "Sao Paulo",
    "State": "SP",
}
CARD = {
    "Card holder name": "Joao Teste",
    "Card number": "4111111111111111",
    "Expiration date": "12/30",
    "CVV": "123",
}


def open_login(page: Page) -> None:
    page.goto(f"{BASE_URL}auth/login")


def login(page: Page, email: str, password: str) -> None:
    open_login(page)
    page.get_by_label("Email address").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Login", exact=True).click()


def add_product_to_cart(page: Page) -> None:
    page.goto(BASE_URL)
    page.locator(".card").first.click()
    page.get_by_role("button", name="Add to cart", exact=True).click()
    expect(page.get_by_text("Product added to shopping cart.")).to_be_visible()


def proceed_to_checkout(page: Page) -> None:
    page.get_by_role("link", name=re.compile("Cart")).click()
    page.get_by_role("button", name="Proceed to Checkout", exact=True).click()


def fill_address(page: Page, skip: str = "") -> None:
    fields = {"Country": COUNTRY, **ADDRESS}
    for label, value in fields.items():
        if label == skip:
            continue
        if label == "Country":
            page.get_by_label(label).select_option(value)
        else:
            page.get_by_label(label).fill(value)


def go_to_address_step(page: Page) -> None:
    login(page, DEMO_EMAIL, DEMO_PASSWORD)
    add_product_to_cart(page)
    proceed_to_checkout(page)


def go_to_payment_step(page: Page) -> None:
    go_to_address_step(page)
    fill_address(page)
    page.get_by_role("button", name="Proceed to Payment", exact=True).click()
    expect(page.get_by_label("Card number")).to_be_visible()


def pay_with_credit_card(page: Page) -> None:
    page.get_by_label("Payment method").select_option("Credit Card")
    for label, value in CARD.items():
        page.get_by_label(label).fill(value)
    page.get_by_role("button", name="Confirm", exact=True).click()


def test_TC01_login_vazio_exibe_mensagens_obrigatorias(page: Page) -> None:
    open_login(page)
    page.get_by_role("button", name="Login", exact=True).click()
    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_be_visible()


def test_TC02_senha_incorreta_exibe_erro_e_sem_sessao(page: Page) -> None:
    login(page, DEMO_EMAIL, WRONG_PASSWORD)
    expect(page.get_by_text("Invalid email or password")).to_be_visible()
    expect(page.get_by_label("Email address")).to_be_visible()
    expect(page.get_by_role("navigation").get_by_text(DEMO_USER_NAME)).to_have_count(0)


def test_TC03_email_vazio_exibe_apenas_mensagem_do_email(page: Page) -> None:
    open_login(page)
    page.get_by_label("Password").fill(DEMO_PASSWORD)
    page.get_by_role("button", name="Login", exact=True).click()
    expect(page.get_by_text("Email is required")).to_be_visible()
    expect(page.get_by_text("Password is required")).to_have_count(0)


def test_TC04_senha_vazia_exibe_apenas_mensagem_da_senha(page: Page) -> None:
    open_login(page)
    page.get_by_label("Email address").fill(DEMO_EMAIL)
    page.get_by_role("button", name="Login", exact=True).click()
    expect(page.get_by_text("Password is required")).to_be_visible()
    expect(page.get_by_text("Email is required")).to_have_count(0)


def test_TC05_login_valido_exibe_my_account_com_nome(page: Page) -> None:
    login(page, DEMO_EMAIL, DEMO_PASSWORD)
    expect(page.get_by_role("heading", name="My account")).to_be_visible()
    expect(page.get_by_role("navigation").get_by_text(DEMO_USER_NAME)).to_be_visible()


def test_TC06_checkout_sem_autenticacao_leva_ao_login(page: Page) -> None:
    add_product_to_cart(page)
    proceed_to_checkout(page)
    expect(page.get_by_label("Email address")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()


def test_TC07_endereco_vazio_nao_avanca_para_pagamento(page: Page) -> None:
    go_to_address_step(page)
    page.get_by_role("button", name="Proceed to Payment", exact=True).click()
    expect(page.get_by_label("Street")).to_be_visible()
    expect(page.get_by_label("Card number")).to_have_count(0)


def test_TC08_endereco_preenchido_avanca_para_pagamento(page: Page) -> None:
    go_to_address_step(page)
    fill_address(page)
    page.get_by_role("button", name="Proceed to Payment", exact=True).click()
    expect(page.get_by_label("Card number")).to_be_visible()


def test_TC09_endereco_sem_cep_nao_avanca_para_pagamento(page: Page) -> None:
    go_to_address_step(page)
    fill_address(page, skip="Postcode")
    page.get_by_role("button", name="Proceed to Payment", exact=True).click()
    expect(page.get_by_label("Street")).to_be_visible()
    expect(page.get_by_label("Card number")).to_have_count(0)


def test_TC10_pagamento_cartao_credito_exibe_sucesso(page: Page) -> None:
    go_to_payment_step(page)
    pay_with_credit_card(page)
    expect(page.get_by_text("Payment was successful")).to_be_visible()


def test_TC11_confirmar_pedido_exibe_numero_da_fatura(page: Page) -> None:
    go_to_payment_step(page)
    pay_with_credit_card(page)
    expect(page.get_by_text("Payment was successful")).to_be_visible()
    page.get_by_role("button", name="Confirm order", exact=True).click()
    expect(
        page.get_by_text(re.compile(r"Thanks for your order! Your invoice number is INV-"))
    ).to_be_visible()
