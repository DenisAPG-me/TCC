# Preços e custo

Preços oficiais por milhão de tokens, consultados em 31/10/2026; os agentes foram usados por assinatura ou cota gratuita, e os valores representam o custo equivalente de API.

Quadro 25 – Preços de tabela por modelo (US$ por 1 milhão de tokens)

| Modelo | Entrada | Saída | Cache escrita | Cache leitura | Nível | Fonte |
|---|---|---|---|---|---|---|
| Claude Haiku 5.5 | 0,10 | 0,50 | 0,125 (5 min); 1 h: não informado | 0,01 | prompt ≤ 100k (>100k: 0,50 / 2,50 / 0,625 / 0,05) | https://claude.com/pricing#api |
| Claude Opus 5.5 | 4,00 | 20,00 | 5,00 (5 min); 1 h: não informado | 0,20 | sem faixas de contexto | https://claude.com/pricing#api |
| GPT-6-Luna | 0,10 | 0,50 | não informado | 0,01 | Standard, contexto curto ≤272k (longo: 0,20 / 0,75; cache 0,02) | https://developers.openai.com/api/docs/pricing |
| GPT-6-Astra | 10,00 | 50,00 | não informado | 1,00 | Standard, contexto curto ≤272k (longo: 20 / 75; cache 2,00) | https://developers.openai.com/api/docs/pricing |
| Gemini 3.5 Flash-Lite | 0,30 | 2,50 (inclui thinking) | armazenamento 1,00 por 1M/hora | 0,03 | Paid Standard, sem faixas de contexto (Free: gratuito, sem cache) | https://ai.google.dev/gemini-api/docs/pricing |

Fonte: Elaborado pelo autor.

Quadro 26 – Custo médio por resposta e por ponto de nota

| Modelo | Nota média (v3) | Custo por resposta (média ± DP) | Origem | Custo por ponto de nota |
|---|---|---|---|---|
| Haiku 5.5 | 76,91 | US$ 0,00781 ± 0,00309 | real (CLI) | 0,000101 |
| Opus 5.5 | 88,18 | US$ 0,17431 ± 0,03751 | real (CLI) | 0,001977 |
| GPT-6-Luna | 72,58 | US$ 0,00150 ± 0,00042 | tabela + divisão real | 0,0000206 |
| GPT-6-Astra | 76,05 | US$ 0,19068 ± 0,05227 | tabela + divisão real | 0,002507 |
| Gemini 3.5 Flash-Lite | 70,02 | US$ 0,01093 ± 0,00126 | tabela Paid Standard (execução gratuita) | 0,000156 |

Fonte: Elaborado pelo autor.
