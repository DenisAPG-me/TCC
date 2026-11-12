import re

from playwright.sync_api import Page, expect

BASE_URL = "https://practicesoftwaretesting.com/"
TERMO_BUSCA = "hammer"
TERMO_INEXISTENTE = "zzzzxx"
MENSAGEM_SEM_PRODUTOS = "There are no products found."
OPCAO_PRECO_CRESCENTE = "Price (Low - High)"
OPCAO_NOME_Z_A = "Name (Z - A)"

CAMPO_BUSCA = '[data-test="search-query"]'
SELECT_ORDENACAO = '[data-test="sort"]'
NOME_PRODUTO = '[data-test="product-name"]'
PRECO_PRODUTO = '[data-test="product-price"]'


def _buscar(page: Page, termo: str) -> None:
    campo = page.locator(CAMPO_BUSCA)
    campo.fill(termo)
    with page.expect_response(lambda r: "products" in r.url):
        campo.press("Enter")
    page.wait_for_load_state("networkidle")


def _ordenar(page: Page, opcao: str) -> None:
    with page.expect_response(lambda r: "products" in r.url):
        page.locator(SELECT_ORDENACAO).select_option(label=opcao)
    page.wait_for_load_state("networkidle")


def _nomes(page: Page) -> list[str]:
    return page.locator(NOME_PRODUTO).all_inner_texts()


def _precos(page: Page) -> list[float]:
    return [float(re.sub(r"[^\d.]", "", t)) for t in page.locator(PRECO_PRODUTO).all_inner_texts()]


def test_ct01_busca_hammer_lista_somente_produtos_com_hammer(page: Page):
    page.goto(BASE_URL)
    _buscar(page, TERMO_BUSCA)

    expect(page.get_by_text(re.compile(r"Searched for:\s*hammer", re.IGNORECASE)).first).to_be_visible()
    nomes = _nomes(page)
    assert nomes, "A busca por 'hammer' deveria retornar produtos"
    assert all(TERMO_BUSCA in nome.lower() for nome in nomes), nomes


def test_ct02_busca_termo_inexistente_exibe_mensagem_sem_produtos(page: Page):
    page.goto(BASE_URL)
    _buscar(page, TERMO_INEXISTENTE)

    expect(page.get_by_text(MENSAGEM_SEM_PRODUTOS)).to_be_visible()
    expect(page.locator(NOME_PRODUTO)).to_have_count(0)


def test_ct03_ordenar_por_preco_do_menor_para_o_maior(page: Page):
    page.goto(BASE_URL)
    expect(page.locator(NOME_PRODUTO).first).to_be_visible()
    _ordenar(page, OPCAO_PRECO_CRESCENTE)

    precos = _precos(page)
    assert len(precos) > 1, "A listagem deveria conter mais de um produto para ordenar"
    assert precos == sorted(precos), precos


def test_ct04_ordenar_por_nome_de_z_a(page: Page):
    page.goto(BASE_URL)
    expect(page.locator(NOME_PRODUTO).first).to_be_visible()
    _ordenar(page, OPCAO_NOME_Z_A)

    nomes = _nomes(page)
    assert len(nomes) > 1, "A listagem deveria conter mais de um produto para ordenar"
    assert nomes == sorted(nomes, key=str.lower, reverse=True), nomes


def test_ct05_busca_ignora_diferenca_de_maiusculas_e_minusculas(page: Page):
    page.goto(BASE_URL)
    _buscar(page, TERMO_BUSCA.upper())

    nomes = _nomes(page)
    assert nomes, "A busca por 'HAMMER' deveria retornar produtos"
    assert all(TERMO_BUSCA in nome.lower() for nome in nomes), nomes


def test_ct06_ordenar_por_preco_sobre_resultados_da_busca(page: Page):
    page.goto(BASE_URL)
    _buscar(page, TERMO_BUSCA)
    expect(page.locator(NOME_PRODUTO).first).to_be_visible()
    _ordenar(page, OPCAO_PRECO_CRESCENTE)

    precos = _precos(page)
    assert precos, "A busca por 'hammer' deveria retornar produtos"
    assert precos == sorted(precos), precos
