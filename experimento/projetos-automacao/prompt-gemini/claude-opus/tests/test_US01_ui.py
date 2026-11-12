import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"


@pytest.fixture(scope="session", autouse=True)
def configure_test_id(playwright):
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture
def home(page: Page, pytestconfig) -> Page:
    url = pytestconfig.getoption("base_url", default=None) or BASE_URL
    page.goto(url)
    expect(page.get_by_test_id("product-name").first).to_be_visible()
    return page


def search(page: Page, term: str) -> list:
    with page.expect_response(lambda r: "/products/search" in r.url) as response_info:
        page.get_by_test_id("search-query").fill(term)
        page.get_by_test_id("search-submit").click()
    return response_info.value.json().get("data", [])


def sort_by(page: Page, label: str) -> None:
    with page.expect_response(lambda r: "/products" in r.url and "sort=" in r.url) as response_info:
        page.get_by_test_id("sort").select_option(label=label)
    expected_names = [p["name"] for p in response_info.value.json()["data"]]
    expect(page.get_by_test_id("product-name")).to_have_text(expected_names)


def assert_search_results(page: Page, term: str, results: list) -> None:
    expect(page.get_by_test_id("search-caption")).to_contain_text(term)
    names = page.get_by_test_id("product-name")
    assert len(results) > 0
    expect(names).to_have_count(len(results))
    for i in range(len(results)):
        expect(names.nth(i)).to_contain_text(re.compile("hammer", re.IGNORECASE))


def parse_price(text: str) -> float:
    return float(text.replace("$", "").replace(",", "").strip())


def test_ct01_busca_por_hammer_lista_somente_produtos_com_hammer(home: Page):
    results = search(home, "hammer")
    assert_search_results(home, "hammer", results)


def test_ct02_busca_por_hammer_maiusculo_ignora_caixa(home: Page):
    results = search(home, "HAMMER")
    assert_search_results(home, "HAMMER", results)


def test_ct03_busca_por_termo_inexistente_exibe_mensagem_sem_produtos(home: Page):
    search(home, "zzzzxx")
    expect(home.get_by_text("There are no products found.")).to_be_visible()
    expect(home.get_by_test_id("product-name")).to_have_count(0)


def test_ct04_ordenacao_por_preco_crescente(home: Page):
    sort_by(home, "Price (Low - High)")
    prices = [parse_price(t) for t in home.get_by_test_id("product-price").all_inner_texts()]
    assert len(prices) > 0
    assert prices == sorted(prices)


def test_ct05_ordenacao_por_nome_z_a(home: Page):
    sort_by(home, "Name (Z - A)")
    names = [n.strip() for n in home.get_by_test_id("product-name").all_inner_texts()]
    assert len(names) > 0
    assert names == sorted(names, key=str.casefold, reverse=True)


def test_ct06_ordenacao_mantem_quantidade_de_produtos_na_pagina(home: Page):
    count_before = home.get_by_test_id("product-name").count()
    assert count_before > 0
    sort_by(home, "Price (Low - High)")
    expect(home.get_by_test_id("product-name")).to_have_count(count_before)
