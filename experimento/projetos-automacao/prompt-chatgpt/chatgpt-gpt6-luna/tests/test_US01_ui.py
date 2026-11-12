import re

import pytest
from playwright.sync_api import expect


BASE_URL = "https://practicesoftwaretesting.com/"
SEARCH_LABEL = "Search"
SEARCH_PLACEHOLDER = "Search"
SEARCH_BUTTON_NAME = "Search"
SORT_LABEL = "Sort"
SORT_PRICE_ASCENDING = "Price (Low - High)"
SORT_NAME_DESCENDING = "Name (Z - A)"
NO_PRODUCTS_MESSAGE = "There are no products found."


def open_home(page):
    page.goto(BASE_URL)
    expect(page).to_have_url(re.compile(r"practicesoftware\.testing\.com/?$"))


def search_input(page):
    by_label = page.get_by_label(SEARCH_LABEL, exact=True)
    if by_label.count():
        return by_label
    return page.get_by_placeholder(SEARCH_PLACEHOLDER, exact=True)


def visible_product_links(page):
    return page.get_by_role("link").filter(has=page.locator("img"))


def product_names(page):
    links = visible_product_links(page)
    return [link.inner_text().strip() for link in links.all() if link.is_visible()]


def extract_prices(text):
    matches = re.findall(r"(?:[$€£]\s*)?\d[\d,]*(?:\.\d{1,2})?", text)
    return [float(match.replace(",", "")) for match in matches]


def product_prices(page):
    links = visible_product_links(page)
    prices = []
    for link in links.all():
        if link.is_visible():
            prices.extend(extract_prices(link.inner_text()))
    return prices


def submit_search(page, term):
    field = search_input(page)
    expect(field).to_be_visible()
    field.fill(term)
    page.get_by_role("button", name=SEARCH_BUTTON_NAME, exact=True).click()


def choose_sort(page, option_name):
    sort = page.get_by_label(SORT_LABEL, exact=True)
    expect(sort).to_be_visible()
    sort.select_option(label=option_name)


def test_CT001_buscar_produtos_por_hammer(page):
    open_home(page)
    submit_search(page, "hammer")

    expect(page.get_by_text(re.compile("hammer", re.IGNORECASE))).to_be_visible()
    names = product_names(page)
    assert names, "A busca por hammer deveria exibir produtos."
    assert all("hammer" in name.casefold() for name in names)


def test_CT002_buscar_termo_sem_resultados(page):
    open_home(page)
    submit_search(page, "zzzzxx")

    expect(page.get_by_text(NO_PRODUCTS_MESSAGE, exact=True)).to_be_visible()
    assert product_names(page) == []


def test_CT003_ordenar_precos_crescente(page):
    open_home(page)
    choose_sort(page, SORT_PRICE_ASCENDING)

    prices = product_prices(page)
    assert prices, "A página deveria exibir produtos com preços identificáveis."
    assert prices == sorted(prices), f"Preços fora de ordem crescente: {prices}"


def test_CT004_ordenar_nomes_decrescente(page):
    open_home(page)
    choose_sort(page, SORT_NAME_DESCENDING)

    names = product_names(page)
    assert names, "A página deveria exibir produtos."
    normalized_names = [name.casefold() for name in names]
    assert normalized_names == sorted(normalized_names, reverse=True), (
        f"Nomes fora de ordem alfabética decrescente: {names}"
    )
