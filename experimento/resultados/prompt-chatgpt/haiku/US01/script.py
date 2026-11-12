import re

import pytest
from playwright.sync_api import expect, sync_playwright

BASE_URL = "https://practicesoftwaretesting.com/"
TEST_ID_ATTRIBUTE = "data-test"
NAVIGATION_TIMEOUT_MS = 30_000
ASSERTION_TIMEOUT_MS = 10_000

SEARCH_INPUT_TEST_ID = "search-query"
PRODUCT_NAME_TEST_ID = "product-name"
PRODUCT_PRICE_TEST_ID = "product-price"
SORT_SELECT_TEST_ID = "sort"

SEARCH_TERM = "hammer"
SEARCH_TERM_UPPERCASE = "HAMMER"
NON_EXISTENT_TERM = "zzzzxx"
NO_RESULTS_MESSAGE = "There are no products found."
SORT_BY_PRICE_ASC_LABEL = "Price (Low - High)"
SORT_BY_NAME_DESC_LABEL = "Name (Z - A)"

PRICE_PATTERN = re.compile(r"\d+(?:[.,]\d+)?")


@pytest.fixture(scope="module")
def playwright_instance():
    with sync_playwright() as playwright:
        playwright.selectors.set_test_id_attribute(TEST_ID_ATTRIBUTE)
        yield playwright


@pytest.fixture(scope="module")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(NAVIGATION_TIMEOUT_MS)
    yield page
    context.close()


def searched_for_pattern(term):
    return re.compile(rf"searched for:\s*{re.escape(term)}", re.IGNORECASE)


def open_home_page(page):
    page.goto(BASE_URL)
    expect(page.get_by_test_id(PRODUCT_NAME_TEST_ID).first).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)


def search_products(page, term):
    search_input = page.get_by_test_id(SEARCH_INPUT_TEST_ID)
    search_input.fill(term)
    search_input.press("Enter")
    page.wait_for_load_state("networkidle")


def sort_products(page, label):
    page.get_by_test_id(SORT_SELECT_TEST_ID).select_option(label=label)
    page.wait_for_load_state("networkidle")
    expect(page.get_by_test_id(PRODUCT_NAME_TEST_ID).first).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)


def read_product_names(page):
    return [name.strip() for name in page.get_by_test_id(PRODUCT_NAME_TEST_ID).all_inner_texts()]


def read_product_prices(page):
    prices = []
    for text in page.get_by_test_id(PRODUCT_PRICE_TEST_ID).all_inner_texts():
        match = PRICE_PATTERN.search(text)
        assert match, f"Preço não identificado no texto: {text!r}"
        prices.append(float(match.group().replace(",", ".")))
    return prices


def test_CT001_busca_por_hammer_lista_somente_produtos_com_hammer(page):
    open_home_page(page)
    search_products(page, SEARCH_TERM)

    expect(page.get_by_text(searched_for_pattern(SEARCH_TERM))).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)
    names = read_product_names(page)

    assert names, "A busca por 'hammer' não listou nenhum produto."
    not_matching = [name for name in names if SEARCH_TERM not in name.lower()]
    assert not not_matching, f"Produtos sem 'hammer' no nome: {not_matching}"


def test_CT002_busca_com_termo_em_maiusculas_retorna_mesmos_produtos(page):
    open_home_page(page)

    search_products(page, SEARCH_TERM)
    expect(page.get_by_text(searched_for_pattern(SEARCH_TERM))).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)
    lowercase_names = read_product_names(page)

    search_products(page, SEARCH_TERM_UPPERCASE)
    expect(page.get_by_text(searched_for_pattern(SEARCH_TERM_UPPERCASE))).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)
    uppercase_names = read_product_names(page)

    assert lowercase_names, "A busca por 'hammer' não listou nenhum produto."
    assert uppercase_names == lowercase_names


def test_CT003_busca_por_termo_inexistente_exibe_mensagem_sem_produtos(page):
    open_home_page(page)
    search_products(page, NON_EXISTENT_TERM)

    expect(page.get_by_text(NO_RESULTS_MESSAGE, exact=True)).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)
    expect(page.get_by_test_id(PRODUCT_NAME_TEST_ID)).to_have_count(0)


def test_CT004_ordenar_por_preco_crescente_ordena_precos_da_pagina(page):
    open_home_page(page)
    sort_products(page, SORT_BY_PRICE_ASC_LABEL)

    prices = read_product_prices(page)

    assert len(prices) >= 2, f"Quantidade insuficiente de produtos para validar a ordenação: {len(prices)}"
    assert prices == sorted(prices), f"Preços fora de ordem crescente: {prices}"


def test_CT005_ordenacao_por_preco_crescente_aplicada_aos_resultados_de_busca(page):
    open_home_page(page)
    search_products(page, SEARCH_TERM)
    expect(page.get_by_text(searched_for_pattern(SEARCH_TERM))).to_be_visible(timeout=ASSERTION_TIMEOUT_MS)

    sort_products(page, SORT_BY_PRICE_ASC_LABEL)
    names = read_product_names(page)
    prices = read_product_prices(page)

    assert len(prices) >= 2, f"Quantidade insuficiente de produtos para validar a ordenação: {len(prices)}"
    not_matching = [name for name in names if SEARCH_TERM not in name.lower()]
    assert not not_matching, f"Produtos sem 'hammer' no nome: {not_matching}"
    assert prices == sorted(prices), f"Preços fora de ordem crescente: {prices}"


def test_CT006_ordenar_por_nome_z_a_ordena_nomes_em_ordem_decrescente(page):
    open_home_page(page)
    sort_products(page, SORT_BY_NAME_DESC_LABEL)

    keys = [name.casefold() for name in read_product_names(page)]

    assert len(keys) >= 2, f"Quantidade insuficiente de produtos para validar a ordenação: {len(keys)}"
    assert keys == sorted(keys, reverse=True), f"Nomes fora de ordem decrescente: {keys}"
