from decimal import Decimal

import pytest
from playwright.sync_api import Page, Playwright, Response, expect

# ---------------------------------------------------------------------------
# Configuração central (valores inferidos que podem exigir ajuste)
# ---------------------------------------------------------------------------
BASE_URL = "https://practicesoftwaretesting.com/"

TERMO_EXISTENTE = "hammer"
TERMO_INEXISTENTE = "zzzzxx"
MSG_SEM_RESULTADOS = "There are no products found."
LEGENDA_BUSCA = "Searched for: {termo}"

TEST_ID_ATTR = "data-test"
TID_CAMPO_BUSCA = "search-query"
TID_BOTAO_BUSCA = "search-submit"
TID_LEGENDA_BUSCA = "search-caption"
TID_ORDENACAO = "sort"
TID_NOME_PRODUTO = "product-name"
TID_PRECO_PRODUTO = "product-price"

OPCAO_PRECO_CRESCENTE = "Price (Low - High)"
OPCAO_NOME_DECRESCENTE = "Name (Z - A)"

URL_API_BUSCA = "/products/search"
URL_API_PRODUTOS = "/products"
PARAM_ORDENACAO = "sort="

TIMEOUT_MS = 15000


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def _configurar_test_id(playwright: Playwright) -> None:
    playwright.selectors.set_test_id_attribute(TEST_ID_ATTR)


@pytest.fixture
def url_loja(pytestconfig: pytest.Config) -> str:
    return pytestconfig.getoption("base_url", default=None) or BASE_URL


@pytest.fixture
def pagina_inicial(page: Page, url_loja: str) -> Page:
    page.set_default_timeout(TIMEOUT_MS)
    expect.set_options(timeout=TIMEOUT_MS)
    page.goto(url_loja)
    expect(page.get_by_test_id(TID_NOME_PRODUTO).first).to_be_visible()
    return page


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _nomes_da_resposta(resposta: Response) -> list[str]:
    assert resposta.ok, f"Requisição {resposta.url} retornou HTTP {resposta.status}"
    corpo = resposta.json()
    assert "data" in corpo, f"Resposta sem campo 'data': {corpo}"
    return [produto["name"].strip() for produto in corpo["data"]]


def _buscar(page: Page, termo: str) -> list[str]:
    page.get_by_test_id(TID_CAMPO_BUSCA).fill(termo)
    with page.expect_response(
        lambda r: URL_API_BUSCA in r.url
        and f"q={termo}" in r.url
        and r.request.method == "GET"
    ) as info:
        page.get_by_test_id(TID_BOTAO_BUSCA).click()
    return _nomes_da_resposta(info.value)


def _ordenar(page: Page, rotulo_opcao: str) -> list[str]:
    with page.expect_response(
        lambda r: URL_API_PRODUTOS in r.url
        and PARAM_ORDENACAO in r.url
        and r.request.method == "GET"
    ) as info:
        page.get_by_test_id(TID_ORDENACAO).select_option(label=rotulo_opcao)
    return _nomes_da_resposta(info.value)


def _aguardar_listagem(page: Page, nomes_esperados: list[str]) -> list[str]:
    nomes = page.get_by_test_id(TID_NOME_PRODUTO)
    expect(nomes).to_have_text(nomes_esperados)
    return [texto.strip() for texto in nomes.all_inner_texts()]


def _converter_preco(texto: str) -> Decimal:
    return Decimal(texto.replace("$", "").replace(",", "").strip())


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------
def test_CT001_busca_hammer_lista_apenas_produtos_com_hammer(pagina_inicial: Page) -> None:
    nomes_api = _buscar(pagina_inicial, TERMO_EXISTENTE)
    assert nomes_api, f"A busca por '{TERMO_EXISTENTE}' não retornou produtos"

    nomes_exibidos = _aguardar_listagem(pagina_inicial, nomes_api)

    expect(pagina_inicial.get_by_test_id(TID_LEGENDA_BUSCA)).to_have_text(
        LEGENDA_BUSCA.format(termo=TERMO_EXISTENTE)
    )
    assert len(nomes_exibidos) > 0
    nomes_invalidos = [
        nome for nome in nomes_exibidos if TERMO_EXISTENTE.casefold() not in nome.casefold()
    ]
    assert not nomes_invalidos, (
        f"Produtos sem '{TERMO_EXISTENTE}' no nome: {nomes_invalidos}"
    )


def test_CT002_busca_termo_inexistente_exibe_mensagem_sem_produtos(pagina_inicial: Page) -> None:
    nomes_api = _buscar(pagina_inicial, TERMO_INEXISTENTE)
    assert nomes_api == [], f"A busca por '{TERMO_INEXISTENTE}' retornou produtos: {nomes_api}"

    expect(pagina_inicial.get_by_text(MSG_SEM_RESULTADOS)).to_be_visible()
    expect(pagina_inicial.get_by_test_id(TID_NOME_PRODUTO)).to_have_count(0)


def test_CT003_ordenacao_preco_crescente(pagina_inicial: Page) -> None:
    nomes_api = _ordenar(pagina_inicial, OPCAO_PRECO_CRESCENTE)
    _aguardar_listagem(pagina_inicial, nomes_api)

    textos_precos = pagina_inicial.get_by_test_id(TID_PRECO_PRODUTO).all_inner_texts()
    precos = [_converter_preco(texto) for texto in textos_precos]

    assert len(precos) >= 2, f"Produtos insuficientes para verificar ordenação: {precos}"
    assert len(precos) == len(nomes_api)
    assert precos == sorted(precos), f"Preços fora de ordem crescente: {precos}"


def test_CT004_ordenacao_nome_z_a(pagina_inicial: Page) -> None:
    nomes_api = _ordenar(pagina_inicial, OPCAO_NOME_DECRESCENTE)
    nomes_exibidos = _aguardar_listagem(pagina_inicial, nomes_api)

    assert len(nomes_exibidos) >= 2, (
        f"Produtos insuficientes para verificar ordenação: {nomes_exibidos}"
    )
    esperado = sorted(nomes_exibidos, key=str.casefold, reverse=True)
    assert nomes_exibidos == esperado, (
        f"Nomes fora de ordem alfabética decrescente: {nomes_exibidos}"
    )
