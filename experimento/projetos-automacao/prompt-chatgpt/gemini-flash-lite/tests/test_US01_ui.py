from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"

def test_CT001_buscar_produto_existente(page: Page) -> None:
    page.goto(BASE_URL)
    search_input = page.get_by_placeholder("Search")
    search_input.fill("hammer")
    page.get_by_role("button", name="Search").click()
    
    product_cards = page.locator(".card")
    expect(product_cards.first).to_be_visible()
    
    for i in range(product_cards.count()):
        title = product_cards.nth(i).locator(".card-title").inner_text().lower()
        assert "hammer" in title

def test_CT002_buscar_termo_inexistente(page: Page) -> None:
    page.goto(BASE_URL)
    search_input = page.get_by_placeholder("Search")
    search_input.fill("zzzzxx")
    page.get_by_role("button", name="Search").click()
    
    no_results = page.get_by_text("There are no products found.")
    expect(no_results).to_be_visible()
    
    product_cards = page.locator(".card")
    expect(product_cards).to_have_count(0)

def test_CT003_ordenar_por_preco_crescente(page: Page) -> None:
    page.goto(BASE_URL)
    sort_select = page.locator("select[data-test='sort']")
    expect(sort_select).to_be_visible()
    sort_select.select_option(value="price,asc")
    
    prices = page.locator(".card-body .float-end")
    expect(prices.first).to_be_visible()
    
    price_values = []
    for i in range(prices.count()):
        price_text = prices.nth(i).inner_text().replace("$", "").strip()
        price_values.append(float(price_text))
        
    assert price_values == sorted(price_values), "Os preços não estão em ordem crescente"

def test_CT004_ordenar_por_nome_z_a(page: Page) -> None:
    page.goto(BASE_URL)
    sort_select = page.locator("select[data-test='sort']")
    expect(sort_select).to_be_visible()
    sort_select.select_option(value="name,desc")
    
    product_titles = page.locator(".card-title")
    expect(product_titles.first).to_be_visible()
    
    titles = []
    for i in range(product_titles.count()):
        titles.append(product_titles.nth(i).inner_text().strip())
        
    sorted_titles = sorted(titles, reverse=True)
    assert titles == sorted_titles, "Os nomes não estão em ordem alfabética decrescente"
