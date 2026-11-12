import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"
PRODUCT_NAME = '[data-test="product-name"]'
PRODUCT_PRICE = '[data-test="product-price"]'
SEARCH_BOX = "Search"
SORT_BOX = "Sort"
NO_RESULTS = "There are no products found."
PRICE_LOW_HIGH = "Price (Low - High)"
NAME_Z_A = "Name (Z - A)"


def open_home(page: Page) -> None:
    page.goto(BASE_URL)


def search(page: Page, term: str) -> None:
    search_box = page.get_by_role("textbox", name=SEARCH_BOX)
    search_box.fill(term)
    with page.expect_response(lambda r: "products" in r.url):
        search_box.press("Enter")


def sort_by(page: Page, option: str) -> None:
    with page.expect_response(lambda r: "products" in r.url):
        page.get_by_label(SORT_BOX).select_option(label=option)


def visible_texts(page: Page, selector: str) -> list[str]:
    expect(page.locator(selector).first).to_be_visible()
    return page.locator(selector).all_inner_texts()


def parse_prices(texts: list[str]) -> list[float]:
    return [float(t.replace("$", "").strip()) for t in texts]


def test_ct01_busca_hammer_lista_somente_produtos_com_hammer(page: Page):
    open_home(page)
    search(page, "hammer")
    names = visible_texts(page, PRODUCT_NAME)
    assert names
    assert all("hammer" in name.lower() for name in names)


def test_ct02_pagina_indica_que_busca_foi_por_hammer(page: Page):
    open_home(page)
    search(page, "hammer")
    expect(page.get_by_role("textbox", name=SEARCH_BOX)).to_have_value("hammer")


def test_ct03_termo_inexistente_exibe_mensagem_nenhum_produto(page: Page):
    open_home(page)
    search(page, "zzzzxx")
    expect(page.get_by_text(NO_RESULTS)).to_be_visible()


def test_ct04_termo_inexistente_nao_lista_produtos(page: Page):
    open_home(page)
    search(page, "zzzzxx")
    expect(page.get_by_text(NO_RESULTS)).to_be_visible()
    expect(page.locator(PRODUCT_NAME)).to_have_count(0)


def test_ct05_ordena_por_preco_do_menor_para_o_maior(page: Page):
    open_home(page)
    sort_by(page, PRICE_LOW_HIGH)
    prices = parse_prices(visible_texts(page, PRODUCT_PRICE))
    assert prices == sorted(prices)


def test_ct06_ordena_por_nome_de_z_a_a(page: Page):
    open_home(page)
    sort_by(page, NAME_Z_A)
    names = visible_texts(page, PRODUCT_NAME)
    assert names == sorted(names, key=str.lower, reverse=True)


def test_ct07_busca_sem_diferenciar_maiusculas_e_minusculas(page: Page):
    open_home(page)
    search(page, "hammer")
    lower_names = sorted(visible_texts(page, PRODUCT_NAME))
    search(page, "HAMMER")
    upper_names = sorted(visible_texts(page, PRODUCT_NAME))
    assert lower_names
    assert lower_names == upper_names


def test_ct08_termo_com_espacos_nas_bordas_retorna_mesmos_resultados(page: Page):
    open_home(page)
    search(page, "hammer")
    expected = sorted(visible_texts(page, PRODUCT_NAME))
    search(page, "  hammer  ")
    actual = sorted(visible_texts(page, PRODUCT_NAME))
    assert expected
    assert actual == expected


def test_ct09_ordenacao_por_preco_preserva_filtro_da_busca(page: Page):
    open_home(page)
    search(page, "hammer")
    sort_by(page, PRICE_LOW_HIGH)
    names = visible_texts(page, PRODUCT_NAME)
    assert all("hammer" in name.lower() for name in names)
    prices = parse_prices(visible_texts(page, PRODUCT_PRICE))
    assert prices == sorted(prices)


def test_ct10_ordenacao_em_busca_sem_resultados_nao_exibe_produtos(page: Page):
    open_home(page)
    search(page, "zzzzxx")
    expect(page.get_by_text(NO_RESULTS)).to_be_visible()
    sort_by(page, PRICE_LOW_HIGH)
    expect(page.get_by_text(NO_RESULTS)).to_be_visible()
    expect(page.locator(PRODUCT_NAME)).to_have_count(0)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
