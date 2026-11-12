from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"


def test_ct01_buscar_produto_por_palavra_chave_existente(page: Page) -> None:
    page.goto(BASE_URL)
    search_input = page.get_by_placeholder("Search")
    search_input.fill("hammer")
    search_button = page.get_by_role("button", name="Search")
    search_button.click()

    expect(page.get_by_text("hammer")).to_be_visible()
    product_cards = page.get_by_test_id("product-card")
    count = product_cards.count()
    assert count > 0
    for i in range(count):
        title = product_cards.nth(i).locator(".card-title").inner_text().lower()
        assert "hammer" in title


def test_ct02_buscar_por_termo_inexistente(page: Page) -> None:
    page.goto(BASE_URL)
    search_input = page.get_by_placeholder("Search")
    search_input.fill("zzzzxx")
    search_button = page.get_by_role("button", name="Search")
    search_button.click()

    expect(page.get_by_text("There are no products found.")).to_be_visible()
    product_cards = page.get_by_test_id("product-card")
    assert product_cards.count() == 0


def test_ct03_ordenar_produtos_por_preco_crescente(page: Page) -> None:
    page.goto(BASE_URL)
    sort_select = page.get_by_test_id("sort")
    sort_select.select_option(label="Price (Low - High)")

    product_cards = page.get_by_test_id("product-card")
    expect(product_cards.first).to_be_visible()
    count = product_cards.count()
    assert count > 1

    prices = []
    for i in range(count):
        price_text = product_cards.nth(i).locator(".card-footer span").inner_text()
        clean_price = float(price_text.replace("$", "").strip())
        prices.append(clean_price)

    assert prices == sorted(prices)


def test_ct04_ordenar_produtos_por_nome_z_a(page: Page) -> None:
    page.goto(BASE_URL)
    sort_select = page.get_by_test_id("sort")
    sort_select.select_option(label="Name (Z - A)")

    product_cards = page.get_by_test_id("product-card")
    expect(product_cards.first).to_be_visible()
    count = product_cards.count()
    assert count > 1

    names = []
    for i in range(count):
        name_text = product_cards.nth(i).locator(".card-title").inner_text()
        names.append(name_text)

    assert names == sorted(names, reverse=True)
