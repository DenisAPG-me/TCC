# Métricas, contagens e exemplo de cálculo

Contagem de testes por modelo (A1 = compila e foi coletado pelo pytest; A3 = aprovados/coletados):

Quadro 12 – Respostas e testes por modelo

| Escopo | Respostas | Compilam | Coletaram (A1=1) | Testes coletados | Aprovados | Falhos | Erros | Outros |
|---|---|---|---|---|---|---|---|---|
| haiku | 36 | 36 | 36 | 339 | 146 | 193 | 0 | 0 |
| opus | 36 | 36 | 36 | 311 | 246 | 65 | 0 | 0 |
| luna | 36 | 36 | 36 | 201 | 75 | 122 | 4 | 0 |
| astra | 36 | 36 | 36 | 267 | 105 | 153 | 9 | 0 |
| flashlite | 36 | 35 | 34 | 172 | 72 | 100 | 0 | 0 |
| Total | 180 | 179 | 178 | 1290 | 644 | 633 | 13 | 0 |

Fonte: Elaborado pelo autor.

Casos de teste listados, válidos, duplicados, alucinados e novos válidos:

Quadro 13 – Classificação dos casos de teste por modelo

| Modelo | Casos listados | Válidos | Duplicados | Alucinados | Novos válidos (soma) | Inválidos por outro motivo (soma) |
|---|---|---|---|---|---|---|
| haiku | 339 | 331 | 4 | 3 | 56 | 1 |
| opus | 311 | 308 | 3 | 0 | 50 | 0 |
| luna | 199 | 199 | 0 | 0 | 4 | 0 |
| astra | 267 | 266 | 1 | 0 | 36 | 0 |
| flashlite | 183 | 182 | 0 | 0 | 2 | 1 |

Fonte: Elaborado pelo autor.

Médias das cinco dimensões de qualidade do código (qualidade = média aritmética de C1 a C5):

Quadro 14 – Dimensões de qualidade do código por modelo

| Modelo | C1 | C2 | C3 | C4 | C5 | Média (C) |
|---|---|---|---|---|---|---|
| haiku | 4,00 | 4,00 | 3,81 | 3,42 | 3,56 | 3,76 |
| opus | 4,33 | 4,64 | 4,53 | 4,03 | 4,53 | 4,41 |
| luna | 3,47 | 3,17 | 3,25 | 2,89 | 2,64 | 3,08 |
| astra | 3,92 | 4,47 | 4,50 | 4,11 | 3,69 | 4,14 |
| flashlite | 2,97 | 1,83 | 2,78 | 2,39 | 2,00 | 2,39 |

Fonte: Elaborado pelo autor.

Exemplo completo de cálculo (autor Grok, modelo Opus, US01: 7 testes coletados, 4 aprovados, 4 de 4 critérios cobertos, recall 0,538, qualidade 4,20, tempo 52,61 s). Nota final = 100 × Σ(peso × componente) = 83,52:

Quadro 15 – Exemplo de cálculo da nota final de uma resposta

| Comp. | Fórmula | Valor | Peso | Contribuição (pontos) |
|---|---|---|---|---|
| e | A1 executa | 1,0000 | 0,05 | 5,00 |
| p | A3 aprovados/coletados | 0,5710 | 0,2 | 11,42 |
| s | 1 − A4/n | 1,0000 | 0,1 | 10,00 |
| c | critérios cobertos/total | 1,0000 | 0,15 | 15,00 |
| m | max(0, 1 − A6/50) | 1,0000 | 0,05 | 5,00 |
| r | recall B3 | 0,5380 | 0,1 | 5,38 |
| q | precisão B4 | 1,0000 | 0,1 | 10,00 |
| h | 1 − alucinados/casos | 1,0000 | 0,05 | 5,00 |
| k | qualidade/5 | 0,8400 | 0,15 | 12,60 |
| t | max(0, 1 − A7/300) | 0,8246 | 0,05 | 4,12 |

Fonte: Elaborado pelo autor.
