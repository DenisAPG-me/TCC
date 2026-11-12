# Resultados descritivos e estatística

Os dados por resposta (180 linhas) estão nas planilhas resultados_por_us.csv e scores_v3.csv do experimento.

Resultados por modelo e autor do prompt (9 respostas cada):

Quadro 16 – Resultados por modelo e autor do prompt

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
| flashlite / grok | 68,7 ± 10,9 | 64,8 | 7,6 | 38,0 ± 40,5 | 43,6% (17/39) | 0,47 | 1,00 | 78,9 | 2,33 | 8,8 ± 1,4 |
| flashlite / claude | 71,2 ± 12,5 | 65,1 | 22,0 | 40,2 ± 45,8 | 47,5% (19/40) | 0,47 | 1,00 | 78,9 | 2,49 | 8,8 ± 1,2 |
| flashlite / chatgpt | 70,9 ± 13,0 | 69,2 | 26,0 | 42,5 ± 45,8 | 41,7% (20/48) | 0,47 | 0,99 | 78,4 | 2,38 | 10,3 ± 1,9 |
| flashlite / gemini | 69,3 ± 12,9 | 66,8 | 28,3 | 33,3 ± 50,0 | 35,6% (16/45) | 0,47 | 1,00 | 78,6 | 2,38 | 11,1 ± 5,1 |

Fonte: Elaborado pelo autor.

Resultados por autor do prompt (45 respostas cada):

Quadro 17 – Resultados por autor do prompt

| Grupo | Nota final (média ± DP) | Mediana | IQR | % passam (média das proporções) | % passam agregado (aprov./coletados) | Recall | Precisão | Nota casos (0–100) | Qualidade (0–5) | Tempo (s) média ± DP |
|---|---|---|---|---|---|---|---|---|---|---|
| grok | 76,2 ± 14,2 | 79,1 | 25,4 | 49,3 ± 43,0 | 50,3% (170/338) | 0,57 | 0,99 | 82,6 | 3,45 | 40,0 ± 58,0 |
| claude | 77,4 ± 12,9 | 72,7 | 24,1 | 48,3 ± 44,8 | 51,6% (163/316) | 0,56 | 0,99 | 81,9 | 3,60 | 42,3 ± 51,8 |
| chatgpt | 76,1 ± 13,3 | 76,4 | 27,9 | 48,1 ± 43,6 | 47,3% (134/283) | 0,53 | 0,99 | 80,8 | 3,61 | 49,7 ± 55,7 |
| gemini | 77,3 ± 13,3 | 75,8 | 24,7 | 49,2 ± 44,9 | 50,1% (177/353) | 0,56 | 0,99 | 81,9 | 3,56 | 36,2 ± 21,7 |

Fonte: Elaborado pelo autor.

Efeito do autor do prompt (Friedman por modelo, valor-p por permutação e Holm entre os cinco modelos):

Quadro 18 – Friedman por modelo para o efeito do autor do prompt

| Modelo | χ² Friedman (gl=3) | p assintótico | p permutação (10.000) | Kendall W | p Holm (perm., 5 modelos) |
|---|---|---|---|---|---|
| haiku | 0,10 | 0,992 | 0,996 | 0,004 | 1,000 |
| opus | 2,83 | 0,419 | 0,433 | 0,105 | 1,000 |
| luna | 3,88 | 0,275 | 0,291 | 0,144 | 1,000 |
| astra | 5,09 | 0,165 | 0,167 | 0,189 | 0,835 |
| flashlite | 2,28 | 0,516 | 0,538 | 0,085 | 1,000 |

Fonte: Elaborado pelo autor.

Comparações pareadas entre autores (Wilcoxon; Holm dentro de cada modelo):

Quadro 19 – Comparações entre autores do prompt por modelo

| Modelo | Par | Δ médio nota [IC95% bootstrap] | W (SciPy) | p SciPy exato | p permutação exata | p Holm (6) | r rank-biserial |
|---|---|---|---|---|---|---|---|
| haiku | grok − claude | +0,9 [-0,7; +3,1] | 19,0 | 0,734 | 0,734 | 1,000 | +0,16 |
| haiku | grok − chatgpt | +0,1 [-4,9; +4,0] | 18,0 | 0,652 | 0,652 | 1,000 | +0,20 |
| haiku | grok − gemini | -0,2 [-2,7; +2,4] | 17,0 | 0,945 | 0,945 | 1,000 | -0,06 |
| haiku | claude − chatgpt | -0,9 [-4,8; +1,8] | 20,0 | 0,820 | 0,820 | 1,000 | +0,11 |
| haiku | claude − gemini | -1,1 [-3,2; +1,2] | 14,0 | 0,359 | 0,344 | 1,000 | -0,38 |
| haiku | chatgpt − gemini | -0,2 [-2,8; +2,7] | 18,0 | 0,652 | 0,652 | 1,000 | -0,20 |
| opus | grok − claude | +1,3 [-1,5; +4,3] | 16,0 | 0,496 | 0,477 | 1,000 | +0,29 |
| opus | grok − chatgpt | +1,8 [-1,0; +5,6] | 10,0 | 0,312 | 0,312 | 1,000 | +0,44 |
| opus | grok − gemini | +0,3 [-3,6; +3,7] | 14,0 | 0,641 | 0,641 | 1,000 | +0,22 |
| opus | claude − chatgpt | +0,6 [-0,4; +1,6] | 14,5 | 0,426 | 0,375 | 1,000 | +0,36 |
| opus | claude − gemini | -1,0 [-5,8; +3,4] | 19,5 | 0,820 | 0,762 | 1,000 | -0,13 |
| opus | chatgpt − gemini | -1,5 [-6,1; +2,6] | 16,0 | 0,844 | 0,844 | 1,000 | -0,11 |
| luna | grok − claude | -0,6 [-3,1; +2,1] | 15,0 | 0,426 | 0,406 | 1,000 | -0,33 |
| luna | grok − chatgpt | +3,0 [-0,4; +6,8] | 10,0 | 0,312 | 0,312 | 1,000 | +0,44 |
| luna | grok − gemini | -2,2 [-6,0; +1,3] | 15,0 | 0,426 | 0,430 | 1,000 | -0,33 |
| luna | claude − chatgpt | +3,6 [-0,2; +7,8] | 16,0 | 0,496 | 0,477 | 1,000 | +0,29 |
| luna | claude − gemini | -1,6 [-5,4; +2,3] | 15,5 | 0,496 | 0,441 | 1,000 | -0,31 |
| luna | chatgpt − gemini | -5,2 [-8,4; -2,2] | 3,0 | 0,020 | 0,020 | 0,117 | -0,87 |
| astra | grok − claude | -5,0 [-8,1; -2,0] | 3,0 | 0,020 | 0,020 | 0,117 | -0,87 |
| astra | grok − chatgpt | -2,0 [-6,8; +2,0] | 19,0 | 0,734 | 0,734 | 1,000 | -0,16 |
| astra | grok − gemini | -2,7 [-6,7; +0,7] | 10,0 | 0,312 | 0,312 | 0,938 | -0,44 |
| astra | claude − chatgpt | +3,0 [-0,5; +6,4] | 8,0 | 0,098 | 0,090 | 0,449 | +0,64 |
| astra | claude − gemini | +2,3 [-1,3; +5,8] | 8,0 | 0,098 | 0,098 | 0,449 | +0,64 |
| astra | chatgpt − gemini | -0,7 [-4,8; +4,3] | 21,0 | 0,910 | 0,883 | 1,000 | -0,07 |
| flashlite | grok − claude | -2,5 [-9,1; +2,2] | 15,0 | 0,426 | 0,410 | 1,000 | -0,33 |
| flashlite | grok − chatgpt | -2,1 [-8,0; +1,6] | 18,0 | 1,000 | 1,000 | 1,000 | +0,00 |
| flashlite | grok − gemini | -0,6 [-7,4; +5,3] | 20,0 | 0,820 | 0,820 | 1,000 | +0,11 |
| flashlite | claude − chatgpt | +0,3 [-2,9; +3,3] | 20,0 | 0,820 | 0,820 | 1,000 | +0,11 |
| flashlite | claude − gemini | +1,9 [-0,9; +4,9] | 13,0 | 0,301 | 0,301 | 1,000 | +0,42 |
| flashlite | chatgpt − gemini | +1,6 [-2,5; +6,6] | 14,0 | 0,641 | 0,641 | 1,000 | +0,22 |

Fonte: Elaborado pelo autor.

Básico × avançado por autor (Holm entre as 8 comparações):

Quadro 20 – Básico × avançado por autor do prompt

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

Básico × avançado agregado (n = 36 pares não independentes):

Quadro 21 – Básico × avançado agregado

| Família | Par | Δ médio [IC95%] | p SciPy (auto) | p permutação (MC 100k) | p Holm (2) | r rank-biserial | melhor/pior |
|---|---|---|---|---|---|---|---|
| Claude | haiku → opus | +11,3 [+7,2; +15,5] | 0,0000 | 0,0000 | 0,0000 | +0,88 | 33/3 |
| GPT (Codex) | luna → astra | +3,5 [+1,7; +5,2] | 0,0003 | 0,0002 | 0,0002 | +0,67 | 28/8 |

Fonte: Elaborado pelo autor.

Efeito da mesma família (Holm entre os cinco modelos); agregado: Δ = −1,39 (IC 95% de −2,79 a +0,04), p = 0,0552, r = −0,33:

Quadro 22 – Efeito do prompt da mesma família

| Modelo | Família do prompt | Δ nota (próprio − outros) [IC95%] | p SciPy exato | p permutação exata | p Holm (5) | r rank-biserial |
|---|---|---|---|---|---|---|
| haiku | claude | -1,0 [-2,8; +0,7] | 0,570 | 0,570 | 1,000 | -0,24 |
| opus | claude | -0,6 [-2,8; +1,6] | 0,652 | 0,652 | 1,000 | -0,20 |
| luna | chatgpt | -3,9 [-7,1; -1,1] | 0,020 | 0,020 | 0,098 | -0,87 |
| astra | chatgpt | -0,5 [-3,8; +3,5] | 0,426 | 0,426 | 1,000 | -0,33 |
| flashlite | gemini | -1,0 [-5,2; +2,7] | 0,910 | 0,910 | 1,000 | -0,07 |

Fonte: Elaborado pelo autor.

Causas das falhas por autor do prompt:

Quadro 23 – Causas das falhas por autor do prompt

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

Quadro 24 – Manifestação imediata e causa das falhas

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
