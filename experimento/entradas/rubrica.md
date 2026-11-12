# Rubrica de avaliação

Unidade de análise: uma resposta (configuração x US, com um dos prompts). 4 autores de prompt x 5 configurações x 9 US = 180 respostas (dois fatores: modelo/configuração e autor do prompt; a rodada Grok, com 45 respostas, foi o piloto refeito e integra as 180). Cada resposta contém (a) casos de teste identificados e (b) um script Python. Coleta: `harness/run_model.py` (resposta, tempo, tokens), `harness/run_tests.py` (execução), `harness/score.py` (cálculo). Itens marcados [M] exigem julgamento humano, registrado em arquivos por resposta (ver final).

## A. Métricas quantitativas do script
| Id | Métrica | Como medir |
|---|---|---|
| A1 | Executa sem erro de import/sintaxe (0/1) | `py_compile` + `pytest --collect-only` sem erro. Automático |
| A2 | Nº de testes | Testes coletados pelo pytest. Automático |
| A3 | % de testes que passam no alvo real | passed / coletados, execução real (Edge headless para UI; requests para API), script ORIGINAL, sem correção. Automático |
| A4 | Falhas por seletor ou dado inventado | Contagem de testes que falham por (i) timeout/locator não encontrado/strict mode violation (automático, heurística na mensagem) ou (ii) valor/mensagem/endpoint/credencial que não existe no alvo [M] (campo `dado_inventado` em `julgamento.json`) |
| A5 | Nº de critérios de aceitação cobertos | Critério coberto = existe ao menos um teste que o exercita E o verifica com asserção. Estimativa automática por palavras-chave dos critérios no script; valor final [M] (`criterios_cobertos` em `julgamento.json`) |
| A6 | Correções manuais mínimas | Nº de linhas alteradas (adicionadas+removidas, difflib) entre `script.py` e `script_corrigido.py`, onde o corrigido é a menor edição que faz o script executar sem erro de import/sintaxe/infra (não conserta asserções nem lógica de negócio). Sem arquivo corrigido = 0. Medido por `score.py` |
| A7 | Tempo de geração (s) | Relógio de parede da chamada da CLI |
| A8 | Tokens (se disponíveis) | Claude: `usage` do JSON (input+cache+output); Codex: "tokens used" no stderr; Gemini: normalmente indisponível (NA) |

Regras: o alvo real é a verdade (se o teste falha por comportamento real divergente do esperado pela IA, conta como falha, e o motivo é classificado). Uma execução por script, repetida 1 vez se falhar por rede/infra (servidor 5xx/timeout de rede). Dados compartilhados: o oráculo foi verificado em 30/10/2026; mudanças no alvo devem ser registradas.

## B. Métricas dos casos de teste identificados
Oráculo: `oraculo-casos.json` (por US, casos positivos/negativos/borda de um testador experiente, com campo `criterios` ligando a critérios da US).
| Id | Métrica | Definição |
|---|---|---|
| B1 | Total | Nº de casos listados pela IA (`casos_teste.json`) |
| B2 | Válidos | Casos coerentes com a US e executáveis/verificáveis no alvo real (não contradizem o comportamento real, não dependem de funcionalidade inexistente) [M]; padrão automático = caso casa com oráculo |
| B3 | Cobertura do oráculo (recall) | casos do oráculo cobertos por >=1 caso da IA / total do oráculo. Um caso da IA cobre um caso do oráculo se testa a mesma condição de entrada e o mesmo resultado esperado [M]; estimativa automática por similaridade de tokens (Jaccard >= 0,25) |
| B4 | Precisão | válidos / total (B2/B1) |
| B5 | Casos novos válidos | válidos que não casam com nenhum caso do oráculo (mas são verificados como corretos no alvo) [M]. Servem para ampliar o oráculo, e não penalizam |
| B6 | Casos alucinados | casos que descrevem mensagens, campos, endpoints, status ou fluxos inexistentes no alvo, ou contradizem a US [M]. Se `valid` + `alucinados` não cobrem todos, o restante é "inválido por outro motivo" (ex.: duplicado, vago) |

## C. Qualidade de código (0 a 5, humano, dois critérios de ancoragem)
Cada dimensão de 0 a 5 (0 ausente/péssimo; 3 aceitável; 5 exemplar):
- C1 Legibilidade: nomes, tamanho de testes, clareza, idioma consistente.
- C2 Estrutura: uso de fixtures, page objects/helpers, parametrização, ausência de duplicação.
- C3 Asserções significativas: verificam resultado de negócio (texto, status, corpo), não apenas "não quebrou"; sem `assert True`.
- C4 Espera/flakiness: auto-wait/expect do Playwright, sem `sleep` fixo, dados únicos, isolamento entre testes, timeouts razoáveis.
- C5 Manutenibilidade: seletores robustos (role/label/data-test), constantes de configuração, independência de ordem, limpeza de dados.
Qualidade de código = média de C1..C5. Avaliador cego ao modelo (arquivos anonimizados). Registrar em `qualidade.json` da resposta. Se A1 = 0 e não houver script corrigido, avaliar o script como está.

## D. Nota final (0 a 100) por resposta
Componentes normalizados em [0,1]:
- e = A1
- p = A3 (fração que passa)
- s = 1 - (A4 / max(A2,1)), mínimo 0
- c = A5 / nº de critérios da US
- m = max(0, 1 - A6/50)
- r = B3 (recall)
- q = B4 (precisão)
- h = 1 - B6/max(B1,1)
- k = C / 5 (qualidade de código)
- t = max(0, 1 - A7/300)

NotaFinal = 100 * ( 0,05 e + 0,20 p + 0,10 s + 0,15 c + 0,05 m + 0,10 r + 0,10 q + 0,05 h + 0,15 k + 0,05 t )

Pesos: 70% script (e,p,s,c,m,k), 25% casos de teste (r,q,h), 5% tempo. Se A1 = 0 sem correção, p=s=c=0 e m = 0. Tokens não pontuam (reportados à parte para análise de custo). Agregação: média por configuração, por tipo (ui/api) e por complexidade; reportar também desvio padrão e a nota apenas de casos de teste (25%) e apenas de script (70%) para análise separada. Análise de sensibilidade: repetir com pesos iguais.

## E. Arquivos por resposta (`resultados/<modelo>/<US>/`)
`resposta_bruta.txt`, `casos_teste.json`, `script.py`, `meta.json` (tempo, tokens, comando), `tests_result.json` (run_tests), opcionais: `script_corrigido.py`, `julgamento.json` ({"validos":[idx...], "alucinados":[idx...], "casos_oraculo_cobertos":["US01-C01",...], "criterios_cobertos":[n...], "dado_inventado":n}), `qualidade.json` ({"legibilidade":0-5,"estrutura":..,"assercoes":..,"espera":..,"manutenibilidade":..}).
