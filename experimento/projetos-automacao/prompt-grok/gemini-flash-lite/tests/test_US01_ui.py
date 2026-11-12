import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"

def test_TC01_buscar_palavra_chave_valida(page: Page):
    page.goto(BASE_URL)
    
    # Preenche o campo de busca e submete
    search_input = page.get_by_placeholder("Search")
    search_input.fill("hammer")
    search_input.press("Enter")
    
    # Valida que a página indica a busca e exibe produtos contendo "hammer"
    expect(page.get_by_text("hammer")).to_be_visible()
    
    products = page.locator(".card-title")
    expect(products.first).to_be_visible()
    count = products.count()
    assert count > 0
    for i in range(count):
        product_name = products.nth(i).text_content()
        assert product_name is not None
        assert "hammer" in product_name.lower()

def test_TC02_buscar_termo_inexistente(page: Page):
    page.goto(BASE_URL)
    
    search_input = page.get_by_placeholder("Search")
    search_input.fill("zzzzxx")
    search_input.press("Enter")
    
    # Valida mensagem de nenhum produto encontrado e ausência de itens
    expect(page.get_by_text("There are no products found.")).to_be_visible()
    products = page.locator(".card-title")
    expect(products).to_have_count(0)

def test_TC03_ordenar_preco_crescente(page: Page):
    page.goto(BASE_URL)
    
    # Seleciona a opção de ordenação por preço (menor para o maior)
    sort_select = page.locator("select.sort, select[data-test='sort']")
    sort_select.select_option(label="Price: Low to High")
    
    # Extrai os preços visíveis
    prices = page.locator(".card-body span.float-end, .card-body [data-test='product-price']")
    expect(prices.first).to_be_visible()
    
    price_values = []
    for i in range(prices.count()):
        text = prices.nth(i).text_content() or ""
        # Remove símbolos de moeda para conversão
        clean_text = text.replace("$", "").replace("€", "").strip()
        price_values.append(float(clean_text))
        
    assert price_values == sorted(price_values), "Os preços não estão em ordem crescente"

def test_TC04_ordenar_nome_z_a(page: Page):
    page.goto(BASE_URL)
    
    # Seleciona a opção de ordenação por nome de Z a A
    sort_select = page.locator("select.sort, select[data-test='sort']")
    sort_select.select_option(label="Name: Z to A")
    
    products = page.locator(".card-title")
    expect(products.first).to_be_visible()
    
    names = []
    for i in range(products.count()):
        names.append(products.nth(i).text_content() or "")
        
    sorted_names = sorted(names, reverse=True)
    assert names == sorted_names, "Os produtos não estão ordenados de Z a A"
