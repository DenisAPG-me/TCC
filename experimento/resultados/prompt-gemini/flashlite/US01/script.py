from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"

def test_ct01_busca_por_termo_existente(page: Page):
    page.goto(BASE_URL)
    
    search_input = page.get_by_test_id("search-query")
    search_input.fill("hammer")
    
    search_button = page.get_by_test_id("search-submit")
    search_button.click()
    
    product_cards = page.locator('[data-test="product-card"]')
    expect(product_cards.first).toBe_visible()
    
    for i in range(product_cards.count()):
        product_name = product_cards.nth(i).locator('[data-test="product-name"]').inner_text().lower()
        assert "hammer" in product_name

def test_ct02_busca_por_termo_inexistente(page: Page):
    page.goto(BASE_URL)
    
    search_input = page.get_by_test_id("search-query")
    search_input.fill("zzzzxx")
    
    search_button = page.get_by_test_id("search-submit")
    search_button.click()
    
    no_results = page.get_by_text("There are no products found.")
    expect(no_results).toBe_visible()
    
    product_cards = page.locator('[data-test="product-card"]')
    expect(product_cards).toHave_count(0)

def test_ct03_ordenacao_por_preco_crescente(page: Page):
    page.goto(BASE_URL)
    
    sort_select = page.get_by_test_id("sort")
    sort_select.select_option(label="Price: Low to High")
    
    product_prices = page.locator('[data-test="product-price"]')
    expect(product_prices.first).toBe_visible()
    
    prices = []
    for i in range(product_prices.count()):
        price_text = product_prices.nth(i).inner_text().replace("$", "").strip()
        prices.append(float(price_text))
        
    assert prices == sorted(prices), "Prices are not in ascending order"

def test_ct04_ordenacao_por_nome_z_a(page: Page):
    page.goto(BASE_URL)
    
    sort_select = page.get_by_test_id("sort")
    sort_select.select_option(label="Name: Z to A")
    
    product_names = page.locator('[data-test="product-name"]')
    expect(product_names.first).toBe_visible()
    
    names = []
    for i in range(product_names.count()):
        names.append(product_names.nth(i).inner_text().strip())
        
    expected_names = sorted(names, reverse=True)
    assert names == expected_names, "Product names are not in descending order (Z to A)"
