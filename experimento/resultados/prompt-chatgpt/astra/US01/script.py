import re
from decimal import Decimal

import pytest
from playwright.sync_api import expect, sync_playwright


BASE_URL = "https://practicesoftwaretesting.com/"
TIMEOUT_MS = 15_000

UI = {
    "test_id_attribute": "data-test",
    "search_label": "Search",
    "search_button": "Search",
    "search_summary": "Search results for: hammer",
    "empty_message": "There are no products found.",
    "sort_label": "Sort",
    "price_option": "Price (Low - High)",
    "name_option": "Name (Z - A)",
    "card_selector": '[data-test^="product-"]',
    "name_test_id": "product-name",
    "price_test_id": "product-price",
}

SEARCH_TERM = "hammer"
ABSENT_TERM = "zzzzxx"
MIN_SORT_PRODUCTS = 2

NAME_SELECTOR = (
    f'{UI["card_selector"]} '
    f'[{UI["test_id_attribute"]}="{UI["name_test_id"]}"]'
)
PRICE_SELECTOR = (
    f'{UI["card_selector"]} '
    f'[{UI["test_id_attribute"]}="{UI["price_test_id"]}"]'
)

PRICE_PATTERN = (
    r"^\$\s*(?P<amount>"
    r"(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)"
    r"\.[0-9]{2})$"
)

# Espera baseada no estado observável do DOM, sem pausas fixas.
# Os mesmos valores são novamente verificados em Python após a espera.
SORTED_DOM_PREDICATE = r"""
({selector, kind, minimum, pricePattern}) => {
    const visible = Array.from(document.querySelectorAll(selector))
        .filter(element => {
            const style = getComputedStyle(element);
            return style.visibility !== "hidden"
                && style.display !== "none"
                && element.getClientRects().length > 0;
        });

    if (visible.length < minimum) {
        return false;
    }

    const texts = visible.map(element =>
        element.innerText.trim().replace(/\s+/g, " ")
    );

    if (texts.some(text => text.length === 0)) {
        return false;
    }

    let values;
    if (kind === "price") {
        const pattern = new RegExp(pricePattern);
        if (texts.some(text => !pattern.test(text))) {
            return false;
        }
        values = texts.map(text =>
            Number(text.replace(/^\$\s*/, "").replace(/,/g, ""))
        );
    } else {
        values = texts.map(text => text.toLowerCase());
    }

    return values.every((value, index) =>
        index === 0
        || (kind === "price"
            ? values[index - 1] <= value
            : values[index - 1] >= value)
    );
}
"""


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        playwright.selectors.set_test_id_attribute(UI["test_id_attribute"])
        instance = playwright.chromium.launch(headless=True)
        try:
            yield instance
        finally:
            instance.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(
        locale="en-US",
        viewport={"width": 1440, "height": 1000},
    )
    try:
        current_page = context.new_page()
        current_page.set_default_timeout(TIMEOUT_MS)
        current_page.set_default_navigation_timeout(TIMEOUT_MS)
        yield current_page
    finally:
        context.close()


def normalized(text):
    return " ".join(text.split())


def product_cards(page):
    return page.locator(UI["card_selector"]).filter(
        has=page.get_by_test_id(UI["name_test_id"])
    )


def product_names(page):
    return product_cards(page).get_by_test_id(UI["name_test_id"])


def product_prices(page):
    return product_cards(page).get_by_test_id(UI["price_test_id"])


def open_home(page):
    response = page.goto(BASE_URL, wait_until="domcontentloaded")
    assert response is not None, "A navegação não retornou uma resposta."
    assert response.ok, (
        f"Falha ao abrir a página inicial: HTTP {response.status}."
    )
    expect(product_cards(page).first).to_be_visible(timeout=TIMEOUT_MS)


def search(page, term):
    field = page.get_by_label(UI["search_label"], exact=True)
    expect(field).to_be_visible(timeout=TIMEOUT_MS)
    field.fill(term)
    page.get_by_role(
        "button", name=UI["search_button"], exact=True
    ).click()


def select_sort(page, option_label):
    expect(
        product_cards(page).nth(MIN_SORT_PRODUCTS - 1)
    ).to_be_visible(timeout=TIMEOUT_MS)

    control = page.get_by_label(UI["sort_label"], exact=True)
    expect(control).to_be_visible(timeout=TIMEOUT_MS)
    control.select_option(label=option_label)

    selected = control.locator("option:checked")
    expect(selected).to_have_text(option_label, timeout=TIMEOUT_MS)


def wait_for_order(page, kind):
    # Remove apenas a sintaxe de grupo nomeado específica do Python.
    js_price_pattern = PRICE_PATTERN.replace("(?P<amount>", "(")
    page.wait_for_function(
        SORTED_DOM_PREDICATE,
        arg={
            "selector": PRICE_SELECTOR if kind == "price" else NAME_SELECTOR,
            "kind": kind,
            "minimum": MIN_SORT_PRODUCTS,
            "pricePattern": js_price_pattern,
        },
        timeout=TIMEOUT_MS,
    )


def read_visible_texts(locator):
    count = locator.count()
    texts = []
    for index in range(count):
        item = locator.nth(index)
        expect(item).to_be_visible(timeout=TIMEOUT_MS)
        value = normalized(item.inner_text())
        assert value, f"Elemento {index + 1} contém texto vazio."
        texts.append(value)
    return texts


def parse_price(text):
    match = re.fullmatch(PRICE_PATTERN, normalized(text))
    assert match is not None, f"Formato de preço inesperado: {text!r}."
    return Decimal(match.group("amount").replace(",", ""))


def test_CT001_buscar_hammer(page):
    open_home(page)
    search(page, SEARCH_TERM)

    expect(
        page.get_by_text(UI["search_summary"], exact=True)
    ).to_be_visible(timeout=TIMEOUT_MS)

    names = product_names(page)
    expect(names.first).to_be_visible(timeout=TIMEOUT_MS)
    count = names.count()
    assert count >= 1, "A busca por hammer não retornou produtos."

    pattern = re.compile(
        rf"[\s\S]*{re.escape(SEARCH_TERM)}[\s\S]*",
        flags=re.IGNORECASE,
    )
    expect(names).to_have_text(
        [pattern] * count,
        timeout=TIMEOUT_MS,
    )

    actual_names = read_visible_texts(names)
    assert all(
        SEARCH_TERM.lower() in name.lower() for name in actual_names
    ), f"Há nomes sem hammer nos resultados: {actual_names!r}."


def test_CT002_buscar_termo_inexistente(page):
    open_home(page)
    search(page, ABSENT_TERM)

    expect(
        page.get_by_text(UI["empty_message"], exact=True)
    ).to_be_visible(timeout=TIMEOUT_MS)
    expect(product_cards(page)).to_have_count(0, timeout=TIMEOUT_MS)
    expect(product_names(page)).to_have_count(0, timeout=TIMEOUT_MS)


def test_CT003_ordenar_preco_crescente(page):
    open_home(page)
    select_sort(page, UI["price_option"])
    wait_for_order(page, "price")

    cards = product_cards(page)
    prices_locator = product_prices(page)
    count = cards.count()
    assert count >= MIN_SORT_PRODUCTS, (
        "São necessários pelo menos dois produtos para comparar preços."
    )
    expect(prices_locator).to_have_count(count, timeout=TIMEOUT_MS)

    price_texts = read_visible_texts(prices_locator)
    prices = [parse_price(text) for text in price_texts]

    assert prices == sorted(prices), (
        f"Preços fora da ordem crescente: {price_texts!r}."
    )


def test_CT004_ordenar_nome_decrescente(page):
    open_home(page)
    select_sort(page, UI["name_option"])
    wait_for_order(page, "name")

    cards = product_cards(page)
    names_locator = product_names(page)
    count = cards.count()
    assert count >= MIN_SORT_PRODUCTS, (
        "São necessários pelo menos dois produtos para comparar nomes."
    )
    expect(names_locator).to_have_count(count, timeout=TIMEOUT_MS)

    names = read_visible_texts(names_locator)
    comparison_names = [name.lower() for name in names]

    assert comparison_names == sorted(comparison_names, reverse=True), (
        f"Nomes fora da ordem alfabética decrescente: {names!r}."
    )
