BASE_URL = "https://practicesoftwaretesting.com/"

import re
from decimal import Decimal

import pytest
from playwright.sync_api import Page, Playwright, expect


PRODUTO_COMUM = "Claw Hammer"
PRODUTO_RESTRITO = "Thor Hammer"

MENSAGEM_SUCESSO = "Product added to shopping cart."
MENSAGEM_THOR = "You can only have one Thor Hammer in the cart."

TIMEOUT_MS = 15_000
PADRAO_PRECO = re.compile(r"^\s*\$\s*(\d+\.\d{2})\s*$")


@pytest.fixture(autouse=True)
def configurar_identificadores(playwright: Playwright):
    """Configura o atributo dos locators sem criar browser, context ou page."""
    playwright.selectors.set_test_id_attribute("data-test")


def abrir_produto(page: Page, nome: str) -> None:
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.get_by_role("link", name=nome, exact=True).click()
    expect(
        page.get_by_role("heading", name=nome, exact=True)
    ).to_be_visible(timeout=TIMEOUT_MS)
    expect(page.get_by_test_id("quantity")).to_be_editable()


def adicionar_quantidade(page: Page, quantidade: int) -> None:
    campo = page.get_by_test_id("quantity")
    campo.fill(str(quantidade))
    expect(campo).to_have_value(str(quantidade))
    page.get_by_test_id("add-to-cart").click()


def preparar_carrinho_com_tres_unidades(page: Page) -> None:
    abrir_produto(page, PRODUTO_COMUM)
    adicionar_quantidade(page, 3)
    expect(
        page.get_by_text(MENSAGEM_SUCESSO, exact=True)
    ).to_be_visible(timeout=TIMEOUT_MS)
    expect(page.get_by_test_id("cart-quantity")).to_have_text(
        "3", timeout=TIMEOUT_MS
    )


def abrir_linha_do_produto(page: Page):
    page.get_by_test_id("nav-cart").click()
    linha = page.get_by_role("row").filter(
        has=page.get_by_text(PRODUTO_COMUM, exact=True)
    )
    expect(linha).to_have_count(1, timeout=TIMEOUT_MS)
    expect(linha).to_be_visible()
    expect(linha.get_by_test_id("product-quantity")).to_have_value(
        "3", timeout=TIMEOUT_MS
    )
    return linha


def ler_preco_unitario(linha) -> Decimal:
    campo_preco = linha.get_by_test_id("product-price")
    expect(campo_preco).to_have_text(PADRAO_PRECO, timeout=TIMEOUT_MS)
    texto = campo_preco.inner_text()
    correspondencia = PADRAO_PRECO.fullmatch(texto)
    if correspondencia is None:
        raise ValueError(f"Formato monetário inesperado: {texto!r}")
    return Decimal(correspondencia.group(1))


def padrao_monetario(valor: Decimal):
    valor_formatado = format(valor.quantize(Decimal("0.01")), ".2f")
    return re.compile(r"^\s*\$\s*" + re.escape(valor_formatado) + r"\s*$")


def test_CT01_adicionar_tres_unidades(page: Page) -> None:
    abrir_produto(page, PRODUTO_COMUM)

    adicionar_quantidade(page, 3)

    expect(
        page.get_by_text(MENSAGEM_SUCESSO, exact=True)
    ).to_be_visible(timeout=TIMEOUT_MS)
    expect(page.get_by_test_id("cart-quantity")).to_have_text(
        "3", timeout=TIMEOUT_MS
    )


def test_CT02_calcular_totais_para_tres_unidades(page: Page) -> None:
    preparar_carrinho_com_tres_unidades(page)
    linha = abrir_linha_do_produto(page)
    preco_unitario = ler_preco_unitario(linha)
    total_esperado = preco_unitario * Decimal("3")

    expect(linha.get_by_test_id("product-total")).to_have_text(
        padrao_monetario(total_esperado), timeout=TIMEOUT_MS
    )
    expect(page.get_by_test_id("cart-total")).to_have_text(
        padrao_monetario(total_esperado), timeout=TIMEOUT_MS
    )


def test_CT03_recalcular_total_para_uma_unidade(page: Page) -> None:
    preparar_carrinho_com_tres_unidades(page)
    linha = abrir_linha_do_produto(page)
    preco_unitario = ler_preco_unitario(linha)

    expect(page.get_by_test_id("cart-total")).to_have_text(
        padrao_monetario(preco_unitario * Decimal("3")),
        timeout=TIMEOUT_MS,
    )

    quantidade = linha.get_by_test_id("product-quantity")
    quantidade.fill("1")
    quantidade.press("Tab")

    expect(quantidade).to_have_value("1", timeout=TIMEOUT_MS)
    expect(page.get_by_test_id("cart-total")).to_have_text(
        padrao_monetario(preco_unitario), timeout=TIMEOUT_MS
    )


def test_CT04_rejeitar_tres_unidades_de_thor_hammer(page: Page) -> None:
    abrir_produto(page, PRODUTO_RESTRITO)

    adicionar_quantidade(page, 3)

    expect(
        page.get_by_text(MENSAGEM_THOR, exact=True)
    ).to_be_visible(timeout=TIMEOUT_MS)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
