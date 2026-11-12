import re
from decimal import Decimal
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import Page, Response, expect


BASE_URL = "https://practicesoftwaretesting.com/"
USERNAME = None
PASSWORD = None

SEARCH_TERM = "hammer"
MISSING_TERM = "zzzzxx"
NO_RESULTS_MESSAGE = "There are no products found."
TIMEOUT_MS = 15_000

SEARCH_LABEL = "Search"
SEARCH_BUTTON_NAME = "Search"
SORT_LABEL = "Sort"
PRICE_ASC_VALUE = "price,asc"
NAME_DESC_VALUE = "name,desc"

CARD_TEST_ID = "product-card"
NAME_TEST_ID = "product-name"
PRICE_TEST_ID = "product-price"
SEARCH_CAPTION_TEST_ID = "search-caption"

PRODUCTS_PATH = "/products"
SEARCH_PARAMETER = "search"
SORT_PARAMETER = "sort"
RESPONSE_DATA_KEY = "data"
RESPONSE_NAME_KEY = "name"

PRICE_PATTERN = re.compile(
    r"^\s*\$\s*(?P<amount>(?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2})\s*$"
)
HAMMER_PATTERN = re.compile(re.escape(SEARCH_TERM), re.IGNORECASE)


def is_products_response(
    response: Response,
    parameter: str = None,
    value: str = None,
) -> bool:
    parsed = urlsplit(response.url)
    if response.request.method != "GET":
        return False
    if parsed.path.rstrip("/") != PRODUCTS_PATH:
        return False
    if parameter is None:
        return True
    return parse_qs(parsed.query).get(parameter) == [value]


def cards(page: Page):
    return page.get_by_test_id(CARD_TEST_ID)


def product_names(page: Page):
    return cards(page).get_by_test_id(NAME_TEST_ID)


def product_prices(page: Page):
    return cards(page).get_by_test_id(PRICE_TEST_ID)


def synchronize_products(page: Page, response: Response) -> None:
    """Espera que a UI reflita os nomes retornados pela ação executada."""
    assert response.status == 200, (
        f"Resposta de produtos inesperada: HTTP {response.status}"
    )
    payload = response.json()
    assert isinstance(payload, dict), "A resposta deve ser um objeto JSON."
    products = payload.get(RESPONSE_DATA_KEY)
    assert isinstance(products, list), "O campo data deve ser uma lista."

    expected_names = []
    for product in products:
        assert isinstance(product, dict), "Produto inválido na resposta."
        name = product.get(RESPONSE_NAME_KEY)
        assert isinstance(name, str) and name.strip(), (
            "Cada produto deve possuir um nome não vazio."
        )
        expected_names.append(name)

    expect(cards(page)).to_have_count(len(expected_names))
    if expected_names:
        expect(product_names(page)).to_have_text(expected_names)
        expect(cards(page).first).to_be_visible()


def open_store(page: Page) -> None:
    page.set_default_timeout(TIMEOUT_MS)
    expect.set_options(timeout=TIMEOUT_MS)

    with page.expect_response(
        lambda response: is_products_response(response),
        timeout=TIMEOUT_MS,
    ) as pending:
        page.goto(BASE_URL, wait_until="domcontentloaded")

    synchronize_products(page, pending.value)
    expect(page.get_by_label(SEARCH_LABEL, exact=True)).to_be_visible()
    expect(page.get_by_label(SORT_LABEL, exact=True)).to_be_visible()


def search(page: Page, term: str) -> None:
    page.get_by_label(SEARCH_LABEL, exact=True).fill(term)

    with page.expect_response(
        lambda response: is_products_response(
            response, SEARCH_PARAMETER, term
        ),
        timeout=TIMEOUT_MS,
    ) as pending:
        page.get_by_role(
            "button", name=SEARCH_BUTTON_NAME, exact=True
        ).click()

    synchronize_products(page, pending.value)


def sort_products(page: Page, value: str) -> None:
    with page.expect_response(
        lambda response: is_products_response(
            response, SORT_PARAMETER, value
        ),
        timeout=TIMEOUT_MS,
    ) as pending:
        page.get_by_label(SORT_LABEL, exact=True).select_option(
            value=value
        )

    synchronize_products(page, pending.value)


def verify_hammer_results(page: Page) -> None:
    caption = page.get_by_test_id(SEARCH_CAPTION_TEST_ID)
    expect(caption).to_be_visible()
    expect(caption).to_contain_text(SEARCH_TERM)
    expect(cards(page).first).to_be_visible()

    names = product_names(page)
    expect(names).to_have_count(cards(page).count())
    for index in range(names.count()):
        expect(names.nth(index)).to_be_visible()
        expect(names.nth(index)).to_contain_text(HAMMER_PATTERN)

    expect(
        page.get_by_text(NO_RESULTS_MESSAGE, exact=True)
    ).to_be_hidden()


def verify_no_results(page: Page) -> None:
    expect(
        page.get_by_text(NO_RESULTS_MESSAGE, exact=True)
    ).to_be_visible()
    expect(cards(page)).to_have_count(0)
    expect(product_names(page)).to_have_count(0)


def parse_price(text: str) -> Decimal:
    match = PRICE_PATTERN.fullmatch(text)
    if match is None:
        pytest.fail(f"Formato de preço não previsto: {text!r}")
    return Decimal(match.group("amount").replace(",", ""))


def verify_price_ascending(page: Page) -> None:
    # Dois itens evitam uma aprovação trivial com lista vazia ou unitária.
    expect(cards(page).nth(1)).to_be_visible()

    prices = product_prices(page)
    expect(prices).to_have_count(cards(page).count())
    for index in range(prices.count()):
        expect(prices.nth(index)).to_be_visible()
        expect(prices.nth(index)).to_have_text(PRICE_PATTERN)

    displayed = prices.all_text_contents()
    expected = sorted(displayed, key=parse_price)
    expect(prices).to_have_text(expected)


def verify_name_descending(page: Page) -> None:
    expect(cards(page).nth(1)).to_be_visible()

    names = product_names(page)
    expect(names).to_have_count(cards(page).count())
    for index in range(names.count()):
        expect(names.nth(index)).to_be_visible()
        expect(names.nth(index)).to_have_text(re.compile(r"\S"))

    displayed = names.all_text_contents()
    expected = sorted(
        displayed,
        key=lambda name: name.strip().casefold(),
        reverse=True,
    )
    expect(names).to_have_text(expected)


def test_ct01_buscar_hammer(page: Page) -> None:
    open_store(page)
    search(page, SEARCH_TERM)
    verify_hammer_results(page)


def test_ct02_buscar_termo_inexistente(page: Page) -> None:
    open_store(page)
    search(page, MISSING_TERM)
    verify_no_results(page)


def test_ct03_ordenar_preco_crescente(page: Page) -> None:
    open_store(page)
    expect(cards(page).nth(1)).to_be_visible()
    sort_products(page, PRICE_ASC_VALUE)
    expect(page.get_by_label(SORT_LABEL, exact=True)).to_have_value(
        PRICE_ASC_VALUE
    )
    verify_price_ascending(page)


def test_ct04_ordenar_nome_decrescente(page: Page) -> None:
    open_store(page)
    expect(cards(page).nth(1)).to_be_visible()
    sort_products(page, NAME_DESC_VALUE)
    expect(page.get_by_label(SORT_LABEL, exact=True)).to_have_value(
        NAME_DESC_VALUE
    )
    verify_name_descending(page)


def test_ct05_buscar_hammer_apos_resultado_vazio(page: Page) -> None:
    open_store(page)
    search(page, MISSING_TERM)
    verify_no_results(page)
    search(page, SEARCH_TERM)
    verify_hammer_results(page)


def test_ct06_buscar_inexistente_apos_resultado_valido(page: Page) -> None:
    open_store(page)
    search(page, SEARCH_TERM)
    verify_hammer_results(page)
    search(page, MISSING_TERM)
    verify_no_results(page)
