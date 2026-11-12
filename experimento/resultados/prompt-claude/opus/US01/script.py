import re
from urllib.parse import unquote

import pytest
from playwright.sync_api import Page, Playwright, expect

BASE_URL = "https://practicesoftwaretesting.com/"

TERMO_EXISTENTE = "hammer"
TERMO_EXISTENTE_MAIUSCULO = "HAMMER"
TERMO_INEXISTENTE = "zzzzxx"
TERMO_CARACTERES_ESPECIAIS = "#$%&*"
MENSAGEM_SEM_RESULTADOS = "There are no products found."
LEGENDA_BUSCA = "Searched for:"

ORDEM_PRECO_CRESCENTE = "price,asc"
ORDEM_NOME_DECRESCENTE = "name,desc"

TIMEOUT_MS = 15000


@pytest.fixture(scope="session", autouse=True)
def configurar_test_id(playwright: Playwright):
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture(autouse=True)
def configurar_timeout():
    expect.set_options(timeout=TIMEOUT_MS)


def abrir_pagina_inicial(page: Page):
    page.goto(BASE_URL)
    expect(page.get_by_test_id("product-name").first).to_be_visible()


def buscar(page: Page, termo: str) -> list[str]:
    page.get_by_test_id("search-query").fill(termo)
    with page.expect_response(
        lambda r: "/products/search" in r.url and r.request.method == "GET",
        timeout=TIMEOUT_MS,
    ) as resposta:
        page.get_by_test_id("search-submit").click()
    return [produto["name"] for produto in resposta.value.json().get("data", [])]


def ordenar(page: Page, valor: str) -> list[str]:
    with page.expect_response(
        lambda r: "/products" in r.url
        and f"sort={valor}" in unquote(r.url)
        and r.request.method == "GET",
        timeout=TIMEOUT_MS,
    ) as resposta:
        page.get_by_test_id("sort").select_option(valor)
    return [produto["name"] for produto in resposta.value.json().get("data", [])]


def converter_preco(texto: str) -> float:
    return float(re.sub(r"[^\d.]", "", texto))


def validar_busca_com_resultados(page: Page, termo: str):
    nomes_api = buscar(page, termo)
    assert len(nomes_api) > 0, f"A busca por '{termo}' não retornou produtos"

    expect(page.get_by_test_id("search-caption")).to_contain_text(LEGENDA_BUSCA)
    expect(page.get_by_test_id("search-caption")).to_contain_text(termo)

    nomes = page.get_by_test_id("product-name")
    expect(nomes).to_have_text(nomes_api)
    expect(nomes).to_have_text(
        [re.compile(re.escape(TERMO_EXISTENTE), re.IGNORECASE)] * len(nomes_api)
    )


def validar_busca_sem_resultados(page: Page, termo: str):
    buscar(page, termo)
    expect(page.get_by_test_id("no-results")).to_have_text(MENSAGEM_SEM_RESULTADOS)
    expect(page.get_by_test_id("product-name")).to_have_count(0)


def test_ct01_buscar_produtos_por_hammer(page: Page):
    abrir_pagina_inicial(page)
    validar_busca_com_resultados(page, TERMO_EXISTENTE)


def test_ct02_buscar_produtos_por_hammer_em_maiusculas(page: Page):
    abrir_pagina_inicial(page)
    validar_busca_com_resultados(page, TERMO_EXISTENTE_MAIUSCULO)


def test_ct03_buscar_termo_inexistente(page: Page):
    abrir_pagina_inicial(page)
    validar_busca_sem_resultados(page, TERMO_INEXISTENTE)


def test_ct04_buscar_termo_com_caracteres_especiais(page: Page):
    abrir_pagina_inicial(page)
    validar_busca_sem_resultados(page, TERMO_CARACTERES_ESPECIAIS)


def test_ct05_ordenar_por_preco_crescente(page: Page):
    abrir_pagina_inicial(page)
    nomes_api = ordenar(page, ORDEM_PRECO_CRESCENTE)
    assert len(nomes_api) > 1, "Produtos insuficientes para validar a ordenação"

    expect(page.get_by_test_id("product-name")).to_have_text(nomes_api)
    precos_locator = page.get_by_test_id("product-price")
    expect(precos_locator).to_have_count(len(nomes_api))

    precos = [converter_preco(t) for t in precos_locator.all_inner_texts()]
    assert precos == sorted(precos), f"Preços fora de ordem crescente: {precos}"


def test_ct06_ordenar_por_nome_z_a(page: Page):
    abrir_pagina_inicial(page)
    nomes_api = ordenar(page, ORDEM_NOME_DECRESCENTE)
    assert len(nomes_api) > 1, "Produtos insuficientes para validar a ordenação"

    nomes_locator = page.get_by_test_id("product-name")
    expect(nomes_locator).to_have_text(nomes_api)

    nomes = [n.strip() for n in nomes_locator.all_inner_texts()]
    assert nomes == sorted(nomes, key=str.lower, reverse=True), (
        f"Nomes fora de ordem alfabética decrescente: {nomes}"
    )
