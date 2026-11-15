# Resultados descritivos e estatística

Os dados por resposta (180 linhas) estão nas planilhas `experimento/analise/resultados_por_us.csv` e `experimento/analise/scores.csv`, geradas por `experimento/harness/score.py`; a estatística é gerada por `experimento/analise/estatistica.py` (`estatistica.csv`). A versão anterior das notas (`scores_v3.csv`) é mantida para comparação: as duas diferem apenas nos dois scripts do Flash-Lite que o pytest não coletou (grok/US09 e claude/US05), cuja cobertura de critérios verificada na execução passou a ser 0.

Unidade de inferência: como os 36 pares de cada comparação (9 US × 4 autores de prompt) repetem as mesmas User Stories, as comparações entre modelos usam a média dos quatro autores em cada US e as 9 diferenças pareadas resultantes; os 36 pares aparecem só como descrição.

Resultados por modelo e autor do prompt (9 respostas cada):

Quadro MC8 – Resultados por modelo e autor do prompt

| Grupo | Nota final (média ± DP) | Mediana | IQR | % passam (média das proporções) | % passam agregado (aprov./coletados) | Recall | Precisão | Nota casos (0–100) | Qualidade (0–5) | Tempo (s) média ± DP |
|---|---|---|---|---|---|---|---|---|---|---|
| haiku / grok | 77,1 ± 13,5 | 72,5 | 25,0 | 46,5 ± 46,7 | 44,7% (38/85) | 0,64 | 0,99 | 85,1 | 3,62 | 40,2 ± 14,0 |
| haiku / claude | 76,2 ± 12,7 | 70,6 | 21,9 | 42,5 ± 47,0 | 44,3% (35/79) | 0,60 | 0,96 | 82,4 | 3,78 | 50,7 ± 16,5 |
| haiku / chatgpt | 77,1 ± 12,9 | 77,4 | 23,7 | 48,1 ± 48,2 | 39,5% (32/81) | 0,60 | 0,98 | 83,1 | 3,89 | 76,5 ± 25,8 |
| haiku / gemini | 77,3 ± 13,8 | 76,0 | 26,4 | 47,6 ± 45,4 | 43,6% (41/94) | 0,66 | 0,96 | 84,2 | 3,73 | 48,0 ± 22,2 |
| opus / grok | 89,0 ± 6,4 | 86,7 | 12,0 | 79,8 ± 20,5 | 81,4% (70/86) | 0,64 | 0,98 | 84,7 | 4,40 | 48,8 ± 10,1 |
| opus / claude | 87,8 ± 7,8 | 90,8 | 8,8 | 73,0 ± 37,4 | 75,3% (64/85) | 0,62 | 0,99 | 84,5 | 4,33 | 52,4 ± 11,4 |
| opus / chatgpt | 87,2 ± 8,7 | 91,1 | 11,4 | 75,2 ± 34,9 | 78,0% (46/59) | 0,52 | 1,00 | 80,9 | 4,47 | 67,3 ± 21,5 |
| opus / gemini | 88,7 ± 8,0 | 91,8 | 13,5 | 81,2 ± 28,4 | 81,5% (66/81) | 0,59 | 1,00 | 83,7 | 4,44 | 52,6 ± 12,0 |
| luna / grok | 72,6 ± 14,6 | 67,1 | 28,1 | 42,5 ± 47,0 | 35,1% (20/57) | 0,53 | 1,00 | 81,1 | 2,89 | 15,9 ± 4,5 |
| luna / claude | 73,2 ± 13,2 | 70,8 | 27,6 | 40,0 ± 46,9 | 39,6% (19/48) | 0,50 | 1,00 | 80,2 | 3,11 | 18,1 ± 6,3 |
| luna / chatgpt | 69,6 ± 13,4 | 61,2 | 20,4 | 30,4 ± 42,4 | 31,8% (14/44) | 0,49 | 1,00 | 79,6 | 3,22 | 16,5 ± 4,6 |
| luna / gemini | 74,8 ± 12,1 | 70,9 | 22,3 | 44,3 ± 43,8 | 42,3% (22/52) | 0,53 | 1,00 | 81,2 | 3,11 | 20,6 ± 6,1 |
| astra / grok | 73,6 ± 16,7 | 64,3 | 32,1 | 39,7 ± 48,9 | 35,2% (25/71) | 0,58 | 1,00 | 83,0 | 4,02 | 86,2 ± 118,0 |
| astra / claude | 78,6 ± 13,4 | 71,1 | 23,0 | 46,0 ± 47,3 | 40,6% (26/64) | 0,59 | 1,00 | 83,4 | 4,31 | 81,3 ± 102,3 |
| astra / chatgpt | 75,6 ± 13,0 | 74,8 | 25,5 | 44,3 ± 41,9 | 43,1% (22/51) | 0,56 | 1,00 | 82,2 | 4,09 | 78,0 ± 104,3 |
| astra / gemini | 76,3 ± 13,4 | 71,3 | 24,7 | 39,4 ± 47,2 | 39,5% (32/81) | 0,56 | 0,98 | 81,6 | 4,13 | 48,6 ± 16,8 |
| flashlite / grok | 67,1 ± 12,9 | 64,8 | 9,7 | 38,0 ± 40,5 | 43,6% (17/39) | 0,47 | 1,00 | 78,9 | 2,33 | 8,8 ± 1,4 |
| flashlite / claude | 69,5 ± 14,6 | 65,1 | 22,0 | 40,2 ± 45,8 | 47,5% (19/40) | 0,47 | 1,00 | 78,9 | 2,49 | 8,8 ± 1,2 |
| flashlite / chatgpt | 70,9 ± 13,0 | 69,2 | 26,0 | 42,5 ± 45,8 | 41,7% (20/48) | 0,47 | 0,99 | 78,4 | 2,38 | 10,3 ± 1,9 |
| flashlite / gemini | 69,3 ± 12,9 | 66,8 | 28,3 | 33,3 ± 50,0 | 35,6% (16/45) | 0,47 | 1,00 | 78,6 | 2,38 | 11,1 ± 5,1 |

Fonte: Elaborado pelo autor.

Resultados por autor do prompt (45 respostas cada):

Quadro MC9 – Resultados por autor do prompt

| Grupo | Nota final (média ± DP) | Mediana | IQR | % passam (média das proporções) | % passam agregado (aprov./coletados) | Recall | Precisão | Nota casos (0–100) | Qualidade (0–5) | Tempo (s) média ± DP |
|---|---|---|---|---|---|---|---|---|---|---|
| grok | 75,9 ± 14,7 | 79,1 | 25,4 | 49,3 ± 43,0 | 50,3% (170/338) | 0,57 | 0,99 | 82,6 | 3,45 | 40,0 ± 58,0 |
| claude | 77,1 ± 13,5 | 72,7 | 24,1 | 48,3 ± 44,8 | 51,6% (163/316) | 0,56 | 0,99 | 81,9 | 3,60 | 42,3 ± 51,8 |
| chatgpt | 76,1 ± 13,3 | 76,4 | 27,9 | 48,1 ± 43,6 | 47,3% (134/283) | 0,53 | 0,99 | 80,8 | 3,61 | 49,7 ± 55,7 |
| gemini | 77,3 ± 13,3 | 75,8 | 24,7 | 49,2 ± 44,9 | 50,1% (177/353) | 0,56 | 0,99 | 81,9 | 3,56 | 36,2 ± 21,7 |

Fonte: Elaborado pelo autor.

Efeito do autor do prompt (Friedman por modelo, 9 blocos = US, valor-p por permutação com 10.000 reamostras e Holm entre os cinco modelos):

Quadro MC10 – Friedman por modelo para o efeito do autor do prompt

| Modelo | χ² Friedman (gl=3) | p assintótico | p permutação (10.000) | Kendall W | p Holm (perm., 5 modelos) |
|---|---|---|---|---|---|
| haiku | 0,10 | 0,992 | 0,996 | 0,004 | 1,000 |
| opus | 2,83 | 0,419 | 0,437 | 0,105 | 1,000 |
| luna | 3,88 | 0,275 | 0,287 | 0,144 | 1,000 |
| astra | 5,09 | 0,165 | 0,164 | 0,189 | 0,821 |
| flashlite | 2,28 | 0,516 | 0,534 | 0,085 | 1,000 |

Fonte: Elaborado pelo autor.

Comparações pareadas entre autores (Wilcoxon exato; Holm dentro de cada modelo):

Quadro MC11 – Comparações entre autores do prompt por modelo

| Modelo | Par | Δ médio nota [IC95% bootstrap] | p exato | p permutação | p Holm (6) | r rank-biserial |
|---|---|---|---|---|---|---|
| haiku | grok − claude | +0,9 [-0,8; +3,1] | 0,734 | 0,733 | 1,000 | +0,16 |
| haiku | grok − chatgpt | +0,1 [-4,8; +4,0] | 0,652 | 0,657 | 1,000 | +0,20 |
| haiku | grok − gemini | -0,2 [-2,7; +2,4] | 0,945 | 0,949 | 1,000 | -0,06 |
| haiku | claude − chatgpt | -0,9 [-4,8; +1,8] | 0,820 | 0,827 | 1,000 | +0,11 |
| haiku | claude − gemini | -1,1 [-3,2; +1,2] | 0,359 | 0,348 | 1,000 | -0,38 |
| haiku | chatgpt − gemini | -0,2 [-2,8; +2,8] | 0,652 | 0,650 | 1,000 | -0,20 |
| opus | grok − claude | +1,3 [-1,5; +4,4] | 0,496 | 0,478 | 1,000 | +0,29 |
| opus | grok − chatgpt | +1,8 [-1,1; +5,6] | 0,312 | 0,314 | 1,000 | +0,44 |
| opus | grok − gemini | +0,3 [-3,7; +3,7] | 0,641 | 0,638 | 1,000 | +0,22 |
| opus | claude − chatgpt | +0,6 [-0,4; +1,6] | 0,426 | 0,382 | 1,000 | +0,36 |
| opus | claude − gemini | -1,0 [-5,7; +3,4] | 0,820 | 0,770 | 1,000 | -0,13 |
| opus | chatgpt − gemini | -1,5 [-6,2; +2,7] | 0,844 | 0,843 | 1,000 | -0,11 |
| luna | grok − claude | -0,6 [-3,0; +2,1] | 0,426 | 0,412 | 1,000 | -0,33 |
| luna | grok − chatgpt | +3,0 [-0,6; +6,7] | 0,312 | 0,316 | 1,000 | +0,44 |
| luna | grok − gemini | -2,2 [-6,0; +1,3] | 0,426 | 0,431 | 1,000 | -0,33 |
| luna | claude − chatgpt | +3,6 [-0,2; +7,8] | 0,496 | 0,477 | 1,000 | +0,29 |
| luna | claude − gemini | -1,6 [-5,4; +2,3] | 0,496 | 0,444 | 1,000 | -0,31 |
| luna | chatgpt − gemini | -5,2 [-8,4; -2,1] | 0,020 | 0,020 | 0,117 | -0,87 |
| astra | grok − claude | -5,0 [-8,0; -2,0] | 0,020 | 0,020 | 0,117 | -0,87 |
| astra | grok − chatgpt | -2,0 [-6,9; +2,1] | 0,734 | 0,741 | 1,000 | -0,16 |
| astra | grok − gemini | -2,7 [-6,6; +0,7] | 0,312 | 0,314 | 0,938 | -0,44 |
| astra | claude − chatgpt | +3,0 [-0,5; +6,4] | 0,098 | 0,095 | 0,488 | +0,64 |
| astra | claude − gemini | +2,3 [-1,2; +5,8] | 0,098 | 0,099 | 0,488 | +0,64 |
| astra | chatgpt − gemini | -0,7 [-4,8; +4,3] | 0,910 | 0,885 | 1,000 | -0,07 |
| flashlite | grok − claude | -2,5 [-13,7; +6,6] | 0,426 | 0,416 | 1,000 | -0,33 |
| flashlite | grok − chatgpt | -3,8 [-12,9; +1,6] | 1,000 | 1,000 | 1,000 | 0,00 |
| flashlite | grok − gemini | -2,2 [-12,3; +5,3] | 0,820 | 0,823 | 1,000 | +0,11 |
| flashlite | claude − chatgpt | -1,3 [-7,1; +3,2] | 0,910 | 0,915 | 1,000 | +0,07 |
| flashlite | claude − gemini | +0,2 [-5,7; +4,7] | 0,426 | 0,432 | 1,000 | +0,33 |
| flashlite | chatgpt − gemini | +1,6 [-2,6; +6,6] | 0,641 | 0,643 | 1,000 | +0,22 |

Fonte: Elaborado pelo autor.

Básico × avançado por autor (Holm entre as 8 comparações):

Quadro MC12 – Básico × avançado por autor do prompt

| Autor | Família | Par | Δ médio [IC95%] | W | p SciPy exato | p permutação exata | p Holm (8) | r rank-biserial | US melhor/pior |
|---|---|---|---|---|---|---|---|---|---|
| grok | Claude | haiku → opus | +11,9 [+4,8; +19,7] | 3,0 | 0,020 | 0,020 | 0,078 | +0,87 | 8/1 |
| grok | GPT (Codex) | luna → astra | +1,0 [-2,3; +4,2] | 18,0 | 0,652 | 0,652 | 0,652 | +0,20 | 5/4 |
| claude | Claude | haiku → opus | +11,6 [+4,4; +20,1] | 0,0 | 0,004 | 0,004 | 0,031 | +1,00 | 9/0 |
| claude | GPT (Codex) | luna → astra | +5,4 [+2,6; +8,5] | 1,0 | 0,008 | 0,008 | 0,047 | +0,96 | 8/1 |
| chatgpt | Claude | haiku → opus | +10,1 [+0,7; +19,4] | 5,0 | 0,039 | 0,039 | 0,117 | +0,78 | 8/1 |
| chatgpt | GPT (Codex) | luna → astra | +6,0 [+2,6; +9,9] | 0,0 | 0,004 | 0,004 | 0,031 | +1,00 | 9/0 |
| gemini | Claude | haiku → opus | +11,4 [+4,1; +19,9] | 1,0 | 0,008 | 0,008 | 0,047 | +0,96 | 8/1 |
| gemini | GPT (Codex) | luna → astra | +1,5 [-1,0; +3,8] | 12,0 | 0,250 | 0,250 | 0,500 | +0,47 | 6/3 |

Fonte: Elaborado pelo autor.

Básico × avançado (inferência com as 9 diferenças médias por US e Holm entre as 6 comparações; os 36 pares só como descrição):

Quadro MC13 – Básico × avançado com a User Story como unidade

| Família | Par | Métrica | Δ médio [IC95% bootstrap] | p exato (n = 9) | p permutação | p Holm (6) | r rank-biserial | Descrição dos 36 pares |
|---|---|---|---|---|---|---|---|---|
| Claude | haiku → opus | nota final | +11,3 [+4,4; +19,6] | 0,004 | 0,003 | 0,023 | +1,00 | avançado melhor em 33 de 36 pares; empates 0 |
| GPT (Codex) | luna → astra | nota final | +3,5 [+2,6; +4,3] | 0,004 | 0,003 | 0,023 | +1,00 | avançado melhor em 28 de 36 pares; empates 0 |
| Claude | haiku → opus | % passam | +31,2 [+8,5; +58,7] | 0,156 | 0,154 | 0,625 | +0,71 | avançado melhor em 19 de 36 pares; empates 14 |
| GPT (Codex) | luna → astra | % passam | +3,0 [-1,7; +8,4] | 0,578 | 0,584 | 0,625 | +0,29 | avançado melhor em 6 de 36 pares; empates 25 |
| Claude | haiku → opus | recall | -0,029 [-0,063; +0,007] | 0,195 | 0,195 | 0,625 | -0,56 | avançado melhor em 9 de 36 pares; empates 11 |
| GPT (Codex) | luna → astra | recall | +0,056 [+0,003; +0,121] | 0,219 | 0,219 | 0,625 | +0,57 | avançado melhor em 13 de 36 pares; empates 20 |

Fonte: Elaborado pelo autor.

Três versões básicas (Friedman com 9 blocos = US e valor = média dos 4 autores; pós-teste de Wilcoxon exato com Holm):

Quadro MC14 – Comparação entre as versões básicas

| Teste | Δ médio ou χ² | p exato ou assintótico | p permutação | p Holm (3) | r ou W |
|---|---|---|---|---|---|
| Friedman (haiku, luna, flashlite) | 11,56 | 0,003 | 0,001 | – | 0,64 |
| haiku − luna | 4,33 | 0,039 | 0,041 | 0,078 | 0,78 |
| haiku − flashlite | 7,72 | 0,004 | 0,003 | 0,012 | 1,00 |
| luna − flashlite | 3,39 | 0,250 | 0,251 | 0,250 | 0,47 |

Fonte: Elaborado pelo autor.

Efeito do prompt da própria família (Holm entre os cinco modelos). Agregado com a US como unidade (média dos cinco modelos em cada US, n = 9): Δ = -1,17 (IC 95% de -2,78 a +0,10), p = 0,129, r = -0,60:

Quadro MC15 – Efeito do prompt da mesma família

| Modelo | Δ nota (próprio − outros) [IC95%] | p exato | p permutação | p Holm (5) | r rank-biserial |
|---|---|---|---|---|---|
| haiku | -1,0 [-2,8; +0,7] | 0,570 | 0,572 | 1,000 | -0,24 |
| opus | -0,6 [-2,9; +1,6] | 0,652 | 0,661 | 1,000 | -0,20 |
| luna | -3,9 [-7,1; -1,2] | 0,020 | 0,020 | 0,098 | -0,87 |
| astra | -0,5 [-3,8; +3,5] | 0,426 | 0,432 | 1,000 | -0,33 |
| flashlite | +0,1 [-4,8; +4,7] | 1,000 | 1,000 | 1,000 | +0,02 |

Fonte: Elaborado pelo autor.

Causas das falhas por autor do prompt:

Quadro MC16 – Causas das falhas por autor do prompt

| Causa | grok | claude | chatgpt | gemini | Total |
|---|---|---|---|---|---|
| seletor inventado | 97 | 65 | 74 | 75 | 311 |
| indeterminada | 21 | 42 | 31 | 35 | 129 |
| seletor ambíguo (strict mode) | 33 | 21 | 20 | 23 | 97 |
| divergência do alvo | 5 | 18 | 12 | 10 | 45 |
| uso incorreto da API do Playwright | 0 | 2 | 3 | 24 | 29 |
| espera/sincronização | 11 | 6 | 2 | 3 | 22 |
| dado inventado (URL/rota) | 1 | 0 | 7 | 6 | 14 |
| erro de sintaxe do código gerado | 1 | 0 | 0 | 0 | 1 |

Fonte: Elaborado pelo autor.

Manifestação imediata × causa identificada:

Quadro MC17 – Manifestação imediata e causa das falhas

| Manifestação imediata | seletor inventado | indeterminada | seletor ambíguo (strict mode) | divergência do alvo | uso incorreto da API do Playwright | espera/sincronização | dado inventado (URL/rota) | erro de sintaxe do código gerado |
|---|---|---|---|---|---|---|---|---|
| timeout ao localizar elemento (ação) | 201 | 70 | 0 | 0 | 0 | 0 | 0 | 0 |
| expect: elemento não encontrado/visível | 93 | 31 | 0 | 0 | 0 | 0 | 0 | 0 |
| strict mode violation | 0 | 0 | 97 | 0 | 0 | 0 | 0 | 0 |
| timeout de espera (navegação/resposta) | 0 | 6 | 0 | 22 | 0 | 17 | 0 | 0 |
| AttributeError/TypeError (chamada inválida) | 0 | 1 | 0 | 0 | 28 | 0 | 0 | 0 |
| expect: contagem divergente | 8 | 0 | 0 | 13 | 0 | 0 | 0 | 0 |
| expect: URL/título divergente | 0 | 0 | 0 | 2 | 0 | 0 | 14 | 0 |
| asserção Python (valor divergente) | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 0 |
| expect: elemento não encontrado/visível [setup] | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| falha/interrupção de navegação | 0 | 3 | 0 | 0 | 0 | 5 | 0 | 0 |
| outra manifestação | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| asserção HTTP (status/corpo) [teardown] | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| expect: texto/valor divergente | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| erro de sintaxe/import (não coletou) | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| asserção HTTP (status/corpo) | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |

Fonte: Elaborado pelo autor.
