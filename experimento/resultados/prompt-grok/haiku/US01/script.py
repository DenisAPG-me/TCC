import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"
TEST_ID_ATTR = "data-test"

SEARCH_INPUT = "search-query"
SEARCH_BUTTON = "search-submit"
PRODUCT_NAME = "product-name"
PRODUCT_PRICE = "product-price"
SORT_SELECT = "sort"


@pytest.fixture(autouse=True)
def _configurar_test_id(playwright):
    playwright.selectors.set_test_id_attribute(TEST_ID_ATTR)


def abrir_home_e_buscar(page: Page, termo: str) -> None:
    page.goto(BASE_URL)
    page.get_by_test_id(SEARCH_INPUT).fill(termo)
    page.get_by_test_id(SEARCH_BUTTON).click()
    page.wait_for_load_state("networkidle")


def nomes_da_pagina(page: Page) -> list[str]:
    return page.get_by_test_id(PRODUCT_NAME).all_inner_texts()


def precos_da_pagina(page: Page) -> list[float]:
    textos = page.get_by_test_id(PRODUCT_PRICE).all_inner_texts()
    return [float(re.sub(r"[^\d.]", "", texto)) for texto in textos]


def test_TC01_busca_hammer_exibe_somente_produtos_com_hammer(page: Page):
    abrir_home_e_buscar(page, "hammer")

    expect(page.get_by_test_id(PRODUCT_NAME).first).to_be_visible()
    expect(page.get_by_test_id(SEARCH_INPUT)).to_have_value("hammer")

    nomes = nomes_da_pagina(page)
    assert len(nomes) > 0
    assert all("hammer" in nome.lower() for nome in nomes)


def test_TC02_busca_nao_diferencia_maiusculas_de_minusculas(page: Page):
    abrir_home_e_buscar(page, "HAMMER")

    expect(page.get_by_test_id(PRODUCT_NAME).first).to_be_visible()

    nomes = nomes_da_pagina(page)
    assert len(nomes) > 0
    assert all("hammer" in nome.lower() for nome in nomes)


def test_TC03_busca_termo_inexistente_exibe_mensagem_sem_produtos(page: Page):
    abrir_home_e_buscar(page, "zzzzxx")

    expect(page.get_by_text("There are no products found.")).to_be_visible()
    expect(page.get_by_test_id(PRODUCT_NAME)).to_have_count(0)


def test_TC04_busca_com_espacos_nas_extremidades_retorna_mesmo_resultado(page: Page):
    abrir_home_e_buscar(page, "  hammer  ")

    expect(page.get_by_test_id(PRODUCT_NAME).first).to_be_visible()

    nomes = nomes_da_pagina(page)
    assert len(nomes) > 0
    assert all("hammer" in nome.lower() for nome in nomes)


def test_TC05_ordenar_por_preco_menor_para_maior_retorna_precos_crescentes(page: Page):
    page.goto(BASE_URL)
    expect(page.get_by_test_id(PRODUCT_PRICE).first).to_be_visible()

    page.get_by_test_id(SORT_SELECT).select_option(label="Price (Low - High)")
    page.wait_for_load_state("networkidle")
    expect(page.get_by_test_id(PRODUCT_PRICE).first).to_be_visible()

    precos = precos_da_pagina(page)
    assert len(precos) > 0
    assert precos == sorted(precos)


def test_TC06_ordenar_por_nome_z_a_retorna_nomes_decrescentes(page: Page):
    page.goto(BASE_URL)
    expect(page.get_by_test_id(PRODUCT_NAME).first).to_be_visible()

    page.get_by_test_id(SORT_SELECT).select_option(label="Name (Z - A)")
    page.wait_for_load_state("networkidle")
    expect(page.get_by_test_id(PRODUCT_NAME).first).to_be_visible()

    nomes = nomes_da_pagina(page)
    assert len(nomes) > 0
    assert nomes == sorted(nomes, key=str.lower, reverse=True)
