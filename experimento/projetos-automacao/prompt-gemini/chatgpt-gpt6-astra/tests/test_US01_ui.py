import re
import sys
from decimal import Decimal
from urllib.parse import parse_qs, urlparse

import pytest
from playwright.sync_api import Page, Response, expect


BASE_URL = "https://practicesoftwaretesting.com/"
TIMEOUT_MS = 15_000

CARD_SELECTOR = 'a[data-test^="product-"]'
NAME_SELECTOR = '[data-test="product-name"]'
PRICE_SELECTOR = '[data-test="product-price"]'
CAPTION_SELECTOR = '[data-test="search-caption"]'

EMPTY_MESSAGE = "There are no products found."


def is_products_response(response: Response, **parameters: str) -> bool:
    url = urlparse(response.url)
    query = parse_qs(url.query)

    return (
        response.request.method == "GET"
        and url.path.rstrip("/").endswith("/products")
        and all(query.get(key) == [value] for key, value in parameters.items())
    )


def read_products(response: Response) -> list[dict]:
    response.finished()

    if not response.ok:
        pytest.fail(
            f"A requisição de produtos retornou HTTP {response.status}."
        )

    payload = response.json()
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        pytest.fail("Premissa incompatível: esperado JSON com lista em 'data'.")

    products = payload["data"]
    for product in products:
        if (
            not isinstance(product, dict)
            or not isinstance(product.get("name"), str)
            or "price" not in product
        ):
            pytest.fail("Premissa incompatível: produto sem 'name' ou 'price'.")

    return products


def cards(page: Page):
    return page.locator(CARD_SELECTOR)


def names(page: Page):
    return cards(page).locator(NAME_SELECTOR)


def prices(page: Page):
    return cards(page).locator(PRICE_SELECTOR)


def expect_rendered_products(page: Page, products: list[dict]) -> None:
    expect(cards(page)).to_have_count(len(products), timeout=TIMEOUT_MS)
    expect(names(page)).to_have_text(
        [product["name"] for product in products],
        timeout=TIMEOUT_MS,
    )


def open_home(page: Page) -> list[dict]:
    with page.expect_response(is_products_response, timeout=TIMEOUT_MS) as pending:
        page.goto(BASE_URL)

    products = read_products(pending.value)
    if not products:
        pytest.fail("Premissa violada: o catálogo inicial está vazio.")

    expect_rendered_products(page, products)
    return products


def search(page: Page, term: str) -> list[dict]:
    page.get_by_role(
        "textbox", name=re.compile("search", re.IGNORECASE)
    ).fill(term)

    with page.expect_response(
        lambda response: is_products_response(response, q=term),
        timeout=TIMEOUT_MS,
    ) as pending:
        page.get_by_role("button", name="Search", exact=True).click()

    return read_products(pending.value)


def sort_products(page: Page, value: str) -> list[dict]:
    with page.expect_response(
        lambda response: is_products_response(response, sort=value),
        timeout=TIMEOUT_MS,
    ) as pending:
        page.get_by_role("combobox").select_option(value)

    return read_products(pending.value)


def require_sortable(products: list[dict], field: str) -> None:
    if len(products) < 2:
        pytest.fail("Premissa violada: ordenação exige pelo menos dois produtos.")

    if field == "price":
        distinct = {Decimal(str(product[field])) for product in products}
    else:
        distinct = {product[field].casefold() for product in products}

    if len(distinct) < 2:
        pytest.fail(
            f"Premissa violada: necessários pelo menos dois valores "
            f"distintos para '{field}'."
        )


def price_pattern(value: Decimal) -> re.Pattern:
    amount = re.escape(format(value, ".2f"))
    return re.compile(r"^\s*\$\s*" + amount + r"\s*$")


def test_CT01_busca_exibe_somente_nomes_com_hammer(page: Page) -> None:
    open_home(page)
    products = search(page, "hammer")

    if not products:
        pytest.fail("Premissa violada: não há correspondências para 'hammer'.")

    expect_rendered_products(page, products)
    expect(names(page)).to_have_text(
        [re.compile(r".*hammer.*", re.IGNORECASE | re.DOTALL)]
        * len(products),
        timeout=TIMEOUT_MS,
    )

    for index in range(len(products)):
        expect(cards(page).nth(index)).to_be_visible()
        expect(names(page).nth(index)).to_be_visible()


def test_CT02_pagina_indica_busca_por_hammer(page: Page) -> None:
    open_home(page)
    products = search(page, "hammer")
    expect_rendered_products(page, products)

    caption = page.locator(CAPTION_SELECTOR)
    expect(caption).to_be_visible(timeout=TIMEOUT_MS)
    expect(caption).to_contain_text("hammer", timeout=TIMEOUT_MS)


def test_CT03_termo_inexistente_exibe_mensagem(page: Page) -> None:
    open_home(page)
    products = search(page, "zzzzxx")

    if products:
        pytest.fail("Premissa violada: 'zzzzxx' retornou produtos.")

    expect(
        page.get_by_text(EMPTY_MESSAGE, exact=True)
    ).to_be_visible(timeout=TIMEOUT_MS)


def test_CT04_busca_sem_correspondencias_tem_zero_produtos(page: Page) -> None:
    open_home(page)
    products = search(page, "zzzzxx")

    if products:
        pytest.fail("Premissa violada: 'zzzzxx' retornou produtos.")

    # A mensagem confirma o estado final da busca antes de verificar o limite zero.
    expect(
        page.get_by_text(EMPTY_MESSAGE, exact=True)
    ).to_be_visible(timeout=TIMEOUT_MS)
    expect(cards(page)).to_have_count(0, timeout=TIMEOUT_MS)
    expect(names(page)).to_have_count(0, timeout=TIMEOUT_MS)
    expect(prices(page)).to_have_count(0, timeout=TIMEOUT_MS)


def test_CT05_ordenacao_por_preco_crescente(page: Page) -> None:
    initial_products = open_home(page)
    require_sortable(initial_products, "price")

    products = sort_products(page, "price,asc")
    require_sortable(products, "price")

    expected_prices = sorted(
        Decimal(str(product["price"])) for product in products
    )

    expect(cards(page)).to_have_count(len(products), timeout=TIMEOUT_MS)
    expect(prices(page)).to_have_text(
        [price_pattern(value) for value in expected_prices],
        timeout=TIMEOUT_MS,
    )

    for index in range(len(products)):
        expect(prices(page).nth(index)).to_be_visible()


def test_CT06_ordenacao_por_nome_de_z_a_a(page: Page) -> None:
    initial_products = open_home(page)
    require_sortable(initial_products, "name")

    products = sort_products(page, "name,desc")
    require_sortable(products, "name")

    expected_names = sorted(
        (product["name"] for product in products),
        key=str.casefold,
        reverse=True,
    )

    expect(cards(page)).to_have_count(len(products), timeout=TIMEOUT_MS)
    expect(names(page)).to_have_text(expected_names, timeout=TIMEOUT_MS)

    for index in range(len(products)):
        expect(names(page).nth(index)).to_be_visible()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))
