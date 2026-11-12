import re

import pytest
from playwright.sync_api import expect


BASE_URL = "https://practicesoftwaretesting.com/"
DEMO_EMAIL = "customer@practicesoftwaretesting.com"
DEMO_PASSWORD = "welcome01"


def abrir_login(page):
    page.goto(f"{BASE_URL}auth/login")


def fazer_login(page, email=DEMO_EMAIL, senha=DEMO_PASSWORD):
    abrir_login(page)
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(senha)
    page.get_by_role("button", name="Login").click()


def adicionar_produto_ao_carrinho(page):
    page.goto(BASE_URL)
    page.get_by_role("button", name="Add to cart").first.click()
    page.get_by_role("link", name="Cart").click()


def abrir_checkout(page):
    page.get_by_role("button", name="Proceed to checkout").click()


def preencher_endereco(page):
    page.get_by_label("Country").fill("United States")
    page.get_by_label("Postcode").fill("12345")
    page.get_by_label("Number").fill("123")
    page.get_by_label("Address").fill("Main Street")
    page.get_by_label("City").fill("Austin")
    page.get_by_label("State").fill("Texas")


def avancar_para_pagamento(page):
    page.get_by_role("button", name="Proceed to payment").click()


def test_CT_01_login_com_formulario_vazio(page):
    abrir_login(page)
    page.get_by_role("button", name="Login").click()

    expect(page.get_by_text("Email is required", exact=True)).to_be_visible()
    expect(page.get_by_text("Password is required", exact=True)).to_be_visible()


def test_CT_02_login_com_senha_incorreta_permanece_sem_sessao(page):
    fazer_login(page, senha="senha-incorreta")

    expect(page.get_by_text("Invalid email or password", exact=True)).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()


def test_CT_03_checkout_sem_autenticacao_solicita_login(page):
    adicionar_produto_ao_carrinho(page)
    abrir_checkout(page)

    expect(page.get_by_label("Email")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()


def test_CT_04_login_com_conta_demo_exibe_minha_conta_e_usuario(page):
    fazer_login(page)

    expect(page.get_by_text("My account", exact=True)).to_be_visible()
    expect(page.get_by_text(re.compile(re.escape(DEMO_EMAIL)), exact=False)).to_be_visible()


def test_CT_05_endereco_vazio_impede_avanco_para_pagamento(page):
    fazer_login(page)
    adicionar_produto_ao_carrinho(page)
    abrir_checkout(page)

    page.get_by_role("button", name="Proceed to payment").click()

    expect(page.get_by_label("Country")).to_be_visible()
    expect(page.get_by_label("Postcode")).to_be_visible()
    expect(page.get_by_label("Number")).to_be_visible()
    expect(page.get_by_label("Address")).to_be_visible()
    expect(page.get_by_label("City")).to_be_visible()
    expect(page.get_by_label("State")).to_be_visible()
    expect(page.get_by_text("Payment", exact=True)).not_to_be_visible()


def test_CT_06_endereco_e_pagamento_com_cartao_finalizam_pedido(page):
    fazer_login(page)
    adicionar_produto_ao_carrinho(page)
    abrir_checkout(page)

    preencher_endereco(page)
    avancar_para_pagamento(page)

    page.get_by_label("Credit Card").check()
    page.get_by_label("Cardholder Name").fill("Test Customer")
    page.get_by_label("Card Number").fill("4111111111111111")
    page.get_by_label("Expiration Date").fill("12/30")
    page.get_by_label("CVV").fill("123")
    page.get_by_role("button", name="Confirm").click()

    expect(page.get_by_text("Payment was successful", exact=True)).to_be_visible()
    page.get_by_role("button", name="Confirm order").click()

    expect(page.get_by_text("Thanks for your order!", exact=True)).to_be_visible()
    expect(page.get_by_text(re.compile(r"INV-[A-Z0-9-]+"))).to_be_visible()
