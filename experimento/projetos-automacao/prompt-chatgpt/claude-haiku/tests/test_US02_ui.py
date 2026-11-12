import re
from decimal import Decimal
from urllib.parse import urljoin

import pytest
from playwright.sync_api import expect, sync_playwright

BASE_URL = "https://practicesoftwaretesting.com/"
HEADLESS = True
TIMEOUT_MS = 10000

PRODUTO_PRINCIPAL = "Claw Hammer"
PRODUTO_LIMITE_UM = "Thor Hammer"
QUANTIDADE_TESTE = 3

ROTULO_QUANTIDADE = "Quantity"
TEXTO_BOTAO_ADICIONAR = "Add to cart"
TEXTO_BOTAO_ATUALIZAR = "Update"
MSG_ADICIONADO = "Product added to shopping cart."
MSG_LIMITE_THOR = "You can only have one Thor Hammer in the cart."
ROTA_CARRINHO = "checkout"

SELETOR_PRECO_UNITARIO = '[data-test="unit-price"]'
SELETOR_CONTADOR_CARRINHO = '[data-test="cart-quantity"]'
SELETOR_QUANTIDADE_LINHA = '[data-test="product-quantity"]'
SELETOR_TOTAL_LINHA = '[data-test="line-price"]'
SELETOR_TOTAL_CARRINHO = '[data-test="cart-total"]'


@pytest.fixture
def pagina():
    with sync_playwright() as playwright:
        navegador = playwright.chromium.launch(headless=HEADLESS)
        contexto = navegador.new_context()
        aba = contexto.new_page()
        aba.set_default_timeout(TIMEOUT_MS)
        yield aba
        contexto.close()
        navegador.close()


def valor_monetario(texto):
    encontrado = re.search(r"\d+(?:\.\d+)?", texto)
    assert encontrado, f"Valor monetário não encontrado em: {texto!r}"
    return Decimal(encontrado.group()).quantize(Decimal("0.01"))


def abrir_produto(pagina, nome):
    pagina.goto(BASE_URL)
    pagina.get_by_text(nome, exact=True).first.click()
    expect(pagina.get_by_role("button", name=TEXTO_BOTAO_ADICIONAR)).to_be_visible()
    expect(pagina.locator(SELETOR_PRECO_UNITARIO)).to_be_visible()


def adicionar_ao_carrinho(pagina, quantidade):
    pagina.get_by_label(ROTULO_QUANTIDADE).fill(str(quantidade))
    pagina.get_by_role("button", name=TEXTO_BOTAO_ADICIONAR).click()


def abrir_carrinho(pagina):
    pagina.goto(urljoin(BASE_URL, ROTA_CARRINHO))


def test_CT001_adicionar_3_unidades_exibe_confirmacao_e_contador(pagina):
    abrir_produto(pagina, PRODUTO_PRINCIPAL)
    adicionar_ao_carrinho(pagina, QUANTIDADE_TESTE)

    expect(pagina.get_by_text(MSG_ADICIONADO, exact=True)).to_be_visible()
    expect(pagina.locator(SELETOR_CONTADOR_CARRINHO)).to_have_text(str(QUANTIDADE_TESTE))


def test_CT002_total_da_linha_e_do_carrinho_com_3_unidades(pagina):
    abrir_produto(pagina, PRODUTO_PRINCIPAL)
    preco_unitario = valor_monetario(pagina.locator(SELETOR_PRECO_UNITARIO).inner_text())
    adicionar_ao_carrinho(pagina, QUANTIDADE_TESTE)
    expect(pagina.get_by_text(MSG_ADICIONADO, exact=True)).to_be_visible()

    abrir_carrinho(pagina)
    expect(pagina.locator(SELETOR_TOTAL_LINHA)).to_be_visible()
    total_linha = valor_monetario(pagina.locator(SELETOR_TOTAL_LINHA).inner_text())
    total_carrinho = valor_monetario(pagina.locator(SELETOR_TOTAL_CARRINHO).inner_text())

    assert total_linha == preco_unitario * QUANTIDADE_TESTE
    assert total_carrinho == total_linha


def test_CT003_alterar_quantidade_para_1_faz_total_igual_ao_preco_unitario(pagina):
    abrir_produto(pagina, PRODUTO_PRINCIPAL)
    preco_unitario = valor_monetario(pagina.locator(SELETOR_PRECO_UNITARIO).inner_text())
    adicionar_ao_carrinho(pagina, QUANTIDADE_TESTE)
    expect(pagina.get_by_text(MSG_ADICIONADO, exact=True)).to_be_visible()

    abrir_carrinho(pagina)
    expect(pagina.locator(SELETOR_QUANTIDADE_LINHA)).to_have_value(str(QUANTIDADE_TESTE))
    pagina.locator(SELETOR_QUANTIDADE_LINHA).fill("1")
    pagina.get_by_role("button", name=TEXTO_BOTAO_ATUALIZAR).click()
    expect(pagina.locator(SELETOR_QUANTIDADE_LINHA)).to_have_value("1")

    expect.poll(
        lambda: valor_monetario(pagina.locator(SELETOR_TOTAL_CARRINHO).inner_text())
    ).to_equal(preco_unitario)


def test_CT004_thor_hammer_com_3_unidades_exibe_mensagem_de_limite(pagina):
    abrir_produto(pagina, PRODUTO_LIMITE_UM)
    adicionar_ao_carrinho(pagina, QUANTIDADE_TESTE)

    expect(pagina.get_by_text(MSG_LIMITE_THOR, exact=True)).to_be_visible()


def test_CT005_thor_hammer_com_1_unidade_e_aceito(pagina):
    abrir_produto(pagina, PRODUTO_LIMITE_UM)
    adicionar_ao_carrinho(pagina, 1)

    expect(pagina.get_by_text(MSG_ADICIONADO, exact=True)).to_be_visible()
    expect(pagina.locator(SELETOR_CONTADOR_CARRINHO)).to_have_text("1")
