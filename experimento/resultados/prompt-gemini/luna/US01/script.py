import re

import pytest
from playwright.sync_api import expect


BASE_URL = "https://practicesoftwaretesting.com/"


def product_cards(page):
    cards = page.get_by_role("article")
    if cards.count() == 0:
        cards = page.locator('[data-test="product"]')
    return cards


def product_names(page):
    cards = product_cards(page)
    names = []
    for index in range(cards.count()):
        card = cards.nth(index)
        heading = card.get_by_role("heading")
        if heading.count():
            names.append(heading.first.inner_text().strip())
        else:
            names.append(card.locator('[data-test="product-name"]').inner_text().strip())
    return names


def product_prices(page):
    cards = product_cards(page)
    prices = []
    for index in range(cards.count()):
        card = cards.nth(index)
        price_locator = card.locator('[data-test="product-price"]')
        raw_price = price_locator.inner_text().strip()
        match = re.search(r"-?\d+(?:[.,]\d+)?", raw_price.replace(",", ""))
        assert match, f"Não foi possível interpretar o preço: {raw_price!r}"
        prices.append(float(match.group(0).replace(",", ".")))
    return prices


def search_products(page, term):
    search = page.get_by_role("textbox", name=re.compile("search", re.I))
    if search.count() == 0:
        search = page.get_by_placeholder(re.compile("search", re.I))
    search.fill(term)

    button = page.get_by_role("button", name=re.compile("search", re.I))
    if button.count():
        button.first.click()
    else:
        search.press("Enter")


def choose_sort_option(page, pattern, fallback_text):
    sort_control = page.get_by_label(re.compile("sort", re.I))
    if sort_control.count() == 0:
        sort_control = page.get_by_role("combobox")
    if sort_control.count():
        sort_control.first.select_option(label=re.compile(pattern, re.I))
    else:
        page.get_by_text(re.compile(pattern, re.I)).click()


def test_CT01_busca_hammer_exibe_apenas_produtos_correspondentes(page):
    page.goto(BASE_URL)
    search_products(page, "hammer")

    expect(page.get_by_text(re.compile("hammer", re.I))).to_be_visible()

    cards = product_cards(page)
    expect(cards.first).to_be_visible()
    for name in product_names(page):
        assert "hammer" in name.casefold(), f"Produto inesperado na busca: {name!r}"


def test_CT02_busca_sem_resultados_exibe_mensagem_e_lista_vazia(page):
    page.goto(BASE_URL)
    search_products(page, "zzzzxx")

    expect(page.get_by_text("There are no products found.", exact=True)).to_be_visible()
    expect(product_cards(page)).to_have_count(0)


def test_CT03_ordenacao_por_preco_crescente(page):
    page.goto(BASE_URL)
    choose_sort_option(page, r"price.*(low|ascending|lowest)", "Price (Low to High)")

    prices = product_prices(page)
    assert prices, "Não há preços de produtos para verificar."
    assert prices == sorted(prices), f"Preços fora de ordem crescente: {prices}"


def test_CT04_ordenacao_por_nome_decrescente(page):
    page.goto(BASE_URL)
    choose_sort_option(page, r"name.*(z.*a|descending)", "Name (Z to A)")

    names = product_names(page)
    assert names, "Não há nomes de produtos para verificar."
    normalized = [name.casefold() for name in names]
    assert normalized == sorted(normalized, reverse=True), (
        f"Nomes fora de ordem alfabética decrescente: {names}"
    )
