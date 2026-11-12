import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"

SEARCH_TERM = "hammer"
NONEXISTENT_TERM = "zzzzxx"
SPECIAL_CHARS_TERM = "@#$%"
NO_PRODUCTS_MESSAGE = "There are no products found."
SORT_PRICE_ASC = "Price (Low - High)"
SORT_NAME_DESC = "Name (Z - A)"

PRICE_SELECTOR = '[data-test="product-price"]'
NAME_SELECTOR = '[data-test="product-name"]'


@pytest.fixture(scope="session", autouse=True)
def configure_test_id_attribute(playwright):
    playwright.selectors.set_test_id_attribute("data-test")


def open_home(page: Page, base_url):
    page.goto(base_url or BASE_URL)
    expect(page.get_by_test_id("product-name").first).to_be_visible()


def search(page: Page, term: str):
    page.get_by_test_id("search-query").fill(term)
    with page.expect_response(lambda r: "/products/search" in r.url):
        page.get_by_test_id("search-submit").click()
    expect(page.get_by_test_id("search-caption")).to_contain_text(term)


def sort_by(page: Page, label: str):
    with page.expect_response(lambda r: "sort=" in r.url):
        page.get_by_test_id("sort").select_option(label=label)


def parse_price(text: str) -> float:
    return float(re.sub(r"[^0-9.]", "", text))


def wait_prices_ascending(page: Page):
    page.wait_for_function(
        """selector => {
            const v = [...document.querySelectorAll(selector)]
                .map(e => parseFloat(e.textContent.replace(/[^0-9.]/g, '')));
            return v.length > 0 && v.every((x, i) => i === 0 || v[i - 1] <= x);
        }""",
        arg=PRICE_SELECTOR,
    )


def wait_names_descending(page: Page):
    page.wait_for_function(
        """selector => {
            const v = [...document.querySelectorAll(selector)]
                .map(e => e.textContent.trim().toLowerCase());
            return v.length > 0 && v.every((x, i) => i === 0 || v[i - 1] >= x);
        }""",
        arg=NAME_SELECTOR,
    )


def assert_all_names_contain(page: Page, term: str):
    names = page.get_by_test_id("product-name")
    expect(names.first).to_be_visible()
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    for i in range(names.count()):
        expect(names.nth(i)).to_have_text(pattern)


def assert_prices_ascending(page: Page):
    prices = page.get_by_test_id("product-price")
    texts = prices.all_text_contents()
    expected = sorted(texts, key=parse_price)
    expect(prices).to_have_text(expected)


def assert_no_products(page: Page):
    expect(page.get_by_text(NO_PRODUCTS_MESSAGE)).to_be_visible()
    expect(page.get_by_test_id("product-name")).to_have_count(0)


def test_TC01_busca_hammer_exibe_somente_produtos_com_hammer(page: Page, base_url):
    open_home(page, base_url)
    search(page, SEARCH_TERM)
    expect(page.get_by_test_id("search-caption")).to_contain_text(SEARCH_TERM)
    assert_all_names_contain(page, SEARCH_TERM)


def test_TC02_busca_hammer_maiusculo_ignora_caixa(page: Page, base_url):
    open_home(page, base_url)
    search(page, SEARCH_TERM.upper())
    assert_all_names_contain(page, SEARCH_TERM)


def test_TC03_busca_termo_inexistente_exibe_mensagem(page: Page, base_url):
    open_home(page, base_url)
    search(page, NONEXISTENT_TERM)
    assert_no_products(page)


def test_TC04_busca_caracteres_especiais_nao_lista_produtos(page: Page, base_url):
    open_home(page, base_url)
    search(page, SPECIAL_CHARS_TERM)
    assert_no_products(page)


def test_TC05_ordenar_preco_crescente(page: Page, base_url):
    open_home(page, base_url)
    sort_by(page, SORT_PRICE_ASC)
    wait_prices_ascending(page)
    assert_prices_ascending(page)


def test_TC06_ordenar_nome_z_a(page: Page, base_url):
    open_home(page, base_url)
    sort_by(page, SORT_NAME_DESC)
    wait_names_descending(page)
    names = page.get_by_test_id("product-name")
    texts = [t.strip() for t in names.all_text_contents()]
    expected = sorted(texts, key=str.lower, reverse=True)
    expect(names).to_have_text(expected)


def test_TC07_busca_hammer_e_ordena_preco_crescente_mantem_filtro(page: Page, base_url):
    open_home(page, base_url)
    search(page, SEARCH_TERM)
    sort_by(page, SORT_PRICE_ASC)
    wait_prices_ascending(page)
    assert_all_names_contain(page, SEARCH_TERM)
    assert_prices_ascending(page)
