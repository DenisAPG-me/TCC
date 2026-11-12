import re
from decimal import Decimal

from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"
PRODUTO_CLAW_HAMMER = "Claw Hammer"
PRODUTO_THOR_HAMMER = "Thor Hammer"
MSG_ADICIONADO = "Product added to shopping cart."
MSG_LIMITE_THOR = "You can only have one Thor Hammer in the cart."


def abrir_produto(page: Page, nome: str) -> None:
    page.goto(BASE_URL)
    campo_busca = page.get_by_placeholder("Search")
    campo_busca.fill(nome)
    campo_busca.press("Enter")
    page.get_by_role("heading", name=nome, exact=True).click()
    expect(page.get_by_role("heading", name=nome, exact=True)).to_be_visible()


def adicionar_ao_carrinho(page: Page, quantidade: int) -> None:
    page.get_by_label("Quantity").fill(str(quantidade))
    page.get_by_role("button", name="Add to cart").click()


def abrir_carrinho(page: Page) -> None:
    page.get_by_role("link", name=re.compile("Cart")).click()


def verificar_indicador_carrinho(page: Page, valor: str) -> None:
    expect(page.get_by_role("link", name=re.compile("Cart"))).to_contain_text(valor)


def ler_preco(localizador) -> Decimal:
    texto = localizador.inner_text()
    numero = re.search(r"\d+(?:[.,]\d+)?", texto).group()
    return Decimal(numero.replace(",", "."))


def test_ct01_adicionar_3_unidades_claw_hammer_ao_carrinho(page: Page):
    abrir_produto(page, PRODUTO_CLAW_HAMMER)
    adicionar_ao_carrinho(page, 3)
    expect(page.get_by_text(MSG_ADICIONADO)).to_be_visible()
    verificar_indicador_carrinho(page, "3")


def test_ct02_total_da_linha_e_do_carrinho_com_3_unidades(page: Page):
    abrir_produto(page, PRODUTO_CLAW_HAMMER)
    preco_unitario = ler_preco(page.locator("[data-test='unit-price']"))
    adicionar_ao_carrinho(page, 3)
    expect(page.get_by_text(MSG_ADICIONADO)).to_be_visible()
    abrir_carrinho(page)
    total_linha = ler_preco(page.locator("[data-test='line-price']"))
    total_carrinho = ler_preco(page.locator("[data-test='cart-total']"))
    assert total_linha == preco_unitario * 3
    assert total_carrinho == total_linha


def test_ct03_alterar_quantidade_no_carrinho_de_3_para_1(page: Page):
    abrir_produto(page, PRODUTO_CLAW_HAMMER)
    preco_unitario = ler_preco(page.locator("[data-test='unit-price']"))
    adicionar_ao_carrinho(page, 3)
    expect(page.get_by_text(MSG_ADICIONADO)).to_be_visible()
    abrir_carrinho(page)
    total = page.locator("[data-test='cart-total']")
    texto_antes = total.inner_text()
    page.locator("[data-test='product-quantity']").fill("1")
    page.get_by_role("button", name="Update").click()
    expect(total).not_to_have_text(texto_antes)
    assert ler_preco(total) == preco_unitario


def test_ct04_adicionar_com_quantidade_padrao(page: Page):
    abrir_produto(page, PRODUTO_CLAW_HAMMER)
    page.get_by_role("button", name="Add to cart").click()
    expect(page.get_by_text(MSG_ADICIONADO)).to_be_visible()
    verificar_indicador_carrinho(page, "1")


def test_ct05_adicionar_3_unidades_thor_hammer_exibe_limite(page: Page):
    abrir_produto(page, PRODUTO_THOR_HAMMER)
    adicionar_ao_carrinho(page, 3)
    expect(page.get_by_text(MSG_LIMITE_THOR)).to_be_visible()


def test_ct06_adicionar_1_unidade_thor_hammer_no_limite_permitido(page: Page):
    abrir_produto(page, PRODUTO_THOR_HAMMER)
    adicionar_ao_carrinho(page, 1)
    expect(page.get_by_text(MSG_ADICIONADO)).to_be_visible()
    expect(page.get_by_text(MSG_LIMITE_THOR)).to_have_count(0)
    verificar_indicador_carrinho(page, "1")
