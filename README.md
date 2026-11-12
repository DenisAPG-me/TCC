# TCC — Agentes de IA básicos × avançados na geração de casos de teste e scripts E2E

Material complementar do Trabalho de Conclusão de Curso (Sistemas de Informação, UNISINOS). O artigo traz um exemplo de cada artefato nos apêndices; os artefatos completos estão aqui.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `material-complementar/` | Versões completas do que foi resumido nos apêndices: os quatro prompts, as nove User Stories, a rubrica, o oráculo (114 casos), métricas e exemplo de cálculo, resultados e estatística, preços e custo |
| `experimento/entradas/` | User Stories (`.md` e `.json`), prompts enviados, bloco de requisitos técnicos, oráculo (`oraculo-casos.json`) e rubrica |
| `experimento/harness/` | Scripts de geração (`run_model.py`), execução (`run_tests.py`, `run_tests_all.py`) e cálculo da nota (`score.py`) |
| `experimento/resultados/prompt-<autor>/<modelo>/<US>/` | Para cada uma das 180 respostas: resposta bruta, casos de teste, script, resultado da execução, julgamento dos casos e notas de qualidade |
| `experimento/projetos-automacao/` | Os scripts gerados organizados como projetos pytest prontos para executar |
| `experimento/analise/` | Notas por resposta (`scores_v3.csv`), resultados por US, estatística, classificação de falhas, custo por resposta e gráficos |
| `avaliacao-independente/` | Questionário do avaliador externo (planilha), guia de preenchimento e scripts de sorteio da amostra e de análise de concordância |

## Desenho do experimento
- 4 autores de prompt × 5 configurações (Claude Haiku 5.5, Claude Opus 5.5, GPT-6-Luna, GPT-6-Astra, Gemini 3.5 Flash-Lite) × 9 User Stories = 180 respostas.
- Sistemas-alvo públicos: Toolshop (https://practicesoftwaretesting.com/), B&B (https://automationintesting.online/) e Restful Booker (https://restful-booker.herokuapp.com).
- Nota final (0 a 100): `100 × (0,05e + 0,20p + 0,10s + 0,15c + 0,05m + 0,10r + 0,10q + 0,05h + 0,15k + 0,05t)`; ver `material-complementar/03-rubrica.md`.

## Executar os scripts gerados
```
pip install pytest pytest-playwright requests
playwright install
cd experimento/projetos-automacao/prompt-<autor>/<configuração>
pytest --browser chromium --browser-channel msedge
```

Caminhos locais nos registros de execução foram substituídos por `<HOME>`. As respostas individuais da avaliação independente não são publicadas, para preservar o anonimato dos avaliadores.
