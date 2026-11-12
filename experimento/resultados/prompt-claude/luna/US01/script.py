import re
import unicodedata

import pytest
from playwright.sync_api import Page, expect


BASE_URL = "https://practicesoftwaretesting.com/"
SEARCH_TERM = "hammer"
NO_RESULTS_TERM = "zzzzxx"
SEARCH_TERM_WITH_SPACES = " hammer "

SEARCH_FIELD_NAME = "Search"
SORT_CONTROL_NAME = "Sort"
SORT_PRICE_ASCENDING = "Price (low to high)"
SORT_NAME_DESCENDING = "Name (Z to A)"
NO_PRODUCTS_MESSAGE = "There are no products found."


def _open_home(page: Page) -> None:
    page.goto(BASE_URL)


def _search(page: Page, term: str) -> None:
    search_field = page.get_by_role("textbox", name=SEARCH_FIELD_NAME)
    search_field.fill(term)
    search_field.press("Enter")


def _product_name_links(page: Page):
    return page.locator('a[href*="/product/"]')


def _normalize_text(value: str) -> str:
    return " ".join(value.split()).casefold()


def _normalize_sort_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _price_value(text: str) -> float:
    # Remove símbolos e espaços; interpreta o último separador decimal como decimal.
    cleaned = re.sub(r"[^\d,.-]", "", text)
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    return float(cleaned)


def _select_sort(page: Page, option: str) -> None:
    page.get_by_label(SORT_CONTROL_NAME).select_option(label=option)


def test_ct01_buscar_produtos_por_palavra_chave(page: Page) -> None:
    _open_home(page)
    _search(page, SEARCH_TERM)

    expect(page.get_by_text(re.compile(r"hammer", re.IGNORECASE))).to_be_visible()
    names = _product_name_links(page).all_text_contents()
    assert names, "A busca por hammer deveria exibir produtos."
    assert all("hammer" in _normalize_text(name) for name in names), (
        f"Todos os nomes deveriam conter {SEARCH_TERM!r}; nomes encontrados: {names!r}"
    )


def test_ct02_buscar_termo_sem_resultados(page: Page) -> None:
    _open_home(page)
    _search(page, NO_RESULTS_TERM)

    expect(page.get_by_text(NO_PRODUCTS_MESSAGE, exact=True)).to_be_visible()
    expect(_product_name_links(page)).to_have_count(0)


def test_ct03_ordenar_precos_em_ordem_crescente(page: Page) -> None:
    _open_home(page)
    _select_sort(page, SORT_PRICE_ASCENDING)

    price_texts = page.locator("app-product-card .card-footer").all_text_contents()
    assert price_texts, "A página deveria exibir produtos com preços."
    prices = [_price_value(text) for text in price_texts]
    assert prices == sorted(prices), f"Preços fora de ordem crescente: {prices!r}"


def test_ct04_ordenar_nomes_em_ordem_decrescente(page: Page) -> None:
    _open_home(page)
    _select_sort(page, SORT_NAME_DESCENDING)

    names = _product_name_links(page).all_text_contents()
    assert names, "A página deveria exibir produtos."
    keys = [_normalize_sort_key(name.strip()) for name in names]
    assert keys == sorted(keys, reverse=True), f"Nomes fora de ordem decrescente: {names!r}"


def test_ct05_buscar_termo_com_espacos_nas_extremidades(page: Page) -> None:
    _open_home(page)
    _search(page, SEARCH_TERM_WITH_SPACES)

    expect(page.get_by_text(re.compile(r"hammer", re.IGNORECASE))).to_be_visible()
    names = _product_name_links(page).all_text_contents()
    assert names, "A busca com espaços deveria exibir produtos."
    assert all("hammer" in _normalize_text(name) for name in names), (
        f"Todos os nomes deveriam conter 'hammer'; nomes encontrados: {names!r}"
    )
