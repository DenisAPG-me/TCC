import re
from decimal import Decimal

from playwright.sync_api import Page, expect


BASE_URL = "https://practicesoftwaretesting.com/"
TIMEOUT_MS = 15_000

SEARCH_LABEL = "Search"
SEARCH_BUTTON = "Search"
SORT_LABEL = "Sort"

LIST_ID = "product-list"
CARD_ID = "product-card"
NAME_ID = "product-name"
PRICE_ID = "product-price"
SEARCH_TERM_ID = "search-term"
EMPTY_STATE_ID = "empty-state"

PRICE_ASC = "price,asc"
NAME_DESC = "name,desc"

expect.set_options(timeout=TIMEOUT_MS)


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def normalized_literal_pattern(value: str) -> re.Pattern:
    """Permite diferenças de espaços, preservando o texto e sua caixa."""
    words = normalize_text(value).split(" ")
    body = r"\s+".join(re.escape(word) for word in words)
    return re.compile(r"^\s*" + body + r"\s*$")


def results(page: Page):
    return page.get_by_test_id(LIST_ID)


def cards(page: Page):
    return results(page).get_by_test_id(CARD_ID)


def names(page: Page):
    return cards(page).get_by_test_id(NAME_ID)


def prices(page: Page):
    return cards(page).get_by_test_id(PRICE_ID)


def wait_for_results(
    page: Page,
    search_term: str,
    sort_value: str,
) -> None:
    # Contrato hipotético: atributos aplicados só mudam após renderização.
    listing = results(page)
    expect(listing).to_be_visible()
    expect(listing).to_have_attribute("data-applied-search", search_term)
    expect(listing).to_have_attribute("data-applied-sort", sort_value)
    expect(listing).to_have_attribute("aria-busy", "false")


def open_home(page: Page) -> None:
    page.goto(f"{BASE_URL.rstrip('/')}/")
    expect(page.get_by_label(SEARCH_LABEL, exact=True)).to_be_visible()
    wait_for_results(page, search_term="", sort_value="default")
    expect(cards(page).first).to_be_visible()


def search(page: Page, term: str) -> None:
    page.get_by_label(SEARCH_LABEL, exact=True).fill(term)
    page.get_by_role("button", name=SEARCH_BUTTON, exact=True).click()
    wait_for_results(page, search_term=term, sort_value="default")


def check_search_indicator(page: Page, term: str) -> None:
    indicator = page.get_by_test_id(SEARCH_TERM_ID)
    expect(indicator).to_be_visible()
    expect(indicator).to_have_text(term)


def check_matching_products(page: Page, term: str) -> None:
    check_search_indicator(page, term)
    expect(cards(page).first).to_be_visible()

    product_count = cards(page).count()
    expect(names(page)).to_have_count(product_count)

    pattern = re.compile(re.escape(term), re.IGNORECASE)
    for index in range(product_count):
        card = cards(page).nth(index)
        name = card.get_by_test_id(NAME_ID)
        expect(card).to_be_visible()
        expect(name).to_be_visible()
        expect(name).to_contain_text(pattern)


def select_sort(page: Page, value: str) -> None:
    # Evita que a verificação de ordem passe com apenas zero ou um produto.
    expect(cards(page).nth(1)).to_be_visible()

    select = page.get_by_label(SORT_LABEL, exact=True)
    expect(select).to_be_visible()
    select.select_option(value)
    expect(select).to_have_value(value)

    wait_for_results(page, search_term="", sort_value=value)
    expect(cards(page).nth(1)).to_be_visible()


def price_to_decimal(text: str) -> Decimal:
    # O formato já é validado com expect antes desta conversão.
    normalized = normalize_text(text)
    numeric = normalized.replace("$", "").replace(",", "").strip()
    return Decimal(numeric)


def test_TC01_buscar_hammer(page: Page) -> None:
    open_home(page)
    search(page, "hammer")
    check_matching_products(page, "hammer")


def test_TC02_buscar_termo_inexistente(page: Page) -> None:
    open_home(page)
    search(page, "zzzzxx")

    message = page.get_by_test_id(EMPTY_STATE_ID)
    expect(message).to_be_visible()
    expect(message).to_have_text("There are no products found.")
    expect(cards(page)).to_have_count(0)


def test_TC03_ordenar_precos_crescentes(page: Page) -> None:
    open_home(page)
    select_sort(page, PRICE_ASC)

    price_locator = prices(page)
    product_count = cards(page).count()
    expect(price_locator).to_have_count(product_count)

    price_pattern = re.compile(
        r"^\s*\$\s*(?:\d+|\d{1,3}(?:,\d{3})+)\.\d{2}\s*$"
    )
    for index in range(product_count):
        expect(cards(page).nth(index)).to_be_visible()
        expect(price_locator.nth(index)).to_be_visible()
        expect(price_locator.nth(index)).to_have_text(price_pattern)

    displayed_prices = [
        normalize_text(text) for text in price_locator.all_text_contents()
    ]
    expected_prices = sorted(displayed_prices, key=price_to_decimal)

    # Compara a sequência inteira, usando valores numéricos como chave.
    expect(price_locator).to_have_text(
        [normalized_literal_pattern(text) for text in expected_prices]
    )


def test_TC04_ordenar_nomes_de_z_a_a(page: Page) -> None:
    open_home(page)
    select_sort(page, NAME_DESC)

    name_locator = names(page)
    product_count = cards(page).count()
    expect(name_locator).to_have_count(product_count)

    for index in range(product_count):
        expect(cards(page).nth(index)).to_be_visible()
        expect(name_locator.nth(index)).to_be_visible()
        expect(name_locator.nth(index)).to_have_text(re.compile(r"\S"))

    displayed_names = [
        normalize_text(text) for text in name_locator.all_text_contents()
    ]
    expected_names = sorted(
        displayed_names,
        key=str.casefold,
        reverse=True,
    )

    expect(name_locator).to_have_text(
        [normalized_literal_pattern(text) for text in expected_names]
    )


def test_TC05_buscar_parte_da_palavra(page: Page) -> None:
    open_home(page)
    search(page, "ham")
    check_matching_products(page, "ham")


def test_TC06_buscar_nome_completo(page: Page) -> None:
    open_home(page)
    search(page, "hammer")
    check_matching_products(page, "hammer")

    full_name = normalize_text(names(page).first.inner_text())

    open_home(page)
    search(page, full_name)
    check_matching_products(page, full_name)

    exact_name = names(page).filter(
        has_text=normalized_literal_pattern(full_name)
    )
    expect(exact_name.first).to_be_visible()
