#!/usr/bin/env python3
"""Uso: python experimento/analise/estatistica.py [--scores experimento/analise/scores.csv] [--out experimento/analise/estatistica.csv]

Análise estatística exploratória (alfa = 0,05). As comparações entre modelos usam, como unidade de inferência,
a User Story: para cada uma das nove US calcula-se a média dos quatro autores de prompt, e a inferência usa as
nove diferenças pareadas. Os 36 pares (US x autor do prompt) só entram na descrição (vitórias por par).
"""
import argparse, csv, itertools
from pathlib import Path
import numpy as np
from scipy import stats

BASE = Path(__file__).resolve().parent
AUTORES = ["grok", "claude", "chatgpt", "gemini"]
MODELOS = ["haiku", "opus", "luna", "astra", "flashlite"]
FAMILIA_DO_AUTOR = {"claude": ["haiku", "opus"], "chatgpt": ["luna", "astra"], "gemini": ["flashlite"]}
N_PERM, N_BOOT, SEED = 10_000, 10_000, 42


def holm(ps):
    ordem = np.argsort(ps); m = len(ps); adj = np.empty(m); acum = 0
    for i, j in enumerate(ordem):
        acum = max(acum, min(1, (m - i) * ps[j])); adj[j] = acum
    return adj


def rank_biserial(d):
    d = np.asarray(d, float); d = d[d != 0]
    if not len(d): return 0.0
    r = stats.rankdata(abs(d)); return (r[d > 0].sum() - r[d < 0].sum()) / r.sum()


def wilcoxon(d):
    d = np.asarray(d, float)
    if not np.any(d != 0): return 1.0, 1.0
    p = stats.wilcoxon(d, zero_method="wilcox", method="exact").pvalue
    # conferência: permutação com inversão de sinais sobre a soma dos postos com sinal (estatística de Wilcoxon)
    dz = d[d != 0]; postos = stats.rankdata(abs(dz)); obs = abs(np.sum(np.sign(dz) * postos))
    rng = np.random.default_rng(SEED); sinais = rng.choice([-1, 1], size=(N_PERM, len(dz)))
    p_perm = (np.sum(abs((sinais * postos).sum(1)) >= obs - 1e-9) + 1) / (N_PERM + 1)
    return p, p_perm


def ic_bootstrap(d):
    d = np.asarray(d, float); rng = np.random.default_rng(SEED)
    medias = d[rng.integers(0, len(d), (N_BOOT, len(d)))].mean(1)
    return np.percentile(medias, [2.5, 97.5])


def friedman(blocos):
    """blocos: matriz n x k (uma linha por US). Retorna chi2, p assintótico, p por permutação e W de Kendall."""
    x = np.asarray(blocos, float); n, k = x.shape
    chi2, p = stats.friedmanchisquare(*x.T)
    rng = np.random.default_rng(SEED); cont = 0
    for _ in range(N_PERM):
        xp = np.array([rng.permutation(l) for l in x])
        if stats.friedmanchisquare(*xp.T).statistic >= chi2 - 1e-12: cont += 1
    return chi2, p, (cont + 1) / (N_PERM + 1), chi2 / (n * (k - 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", default=str(BASE / "scores.csv")); ap.add_argument("--out", default=str(BASE / "estatistica.csv"))
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.scores, encoding="utf-8")))
    uss = sorted({r["us"] for r in rows})
    val = lambda col: {(r["autor_prompt"], r["modelo"], r["us"]): float(r[col]) for r in rows}
    nota = val("nota_final")
    media_us = lambda tab, m, u: np.mean([tab[(au, m, u)] for au in AUTORES])
    out = []

    # F2: básico x avançado em cada família (inferência com as 9 médias por US)
    for col in ("nota_final", "pct_passam", "recall"):
        tab = val(col)
        for b, av in (("haiku", "opus"), ("luna", "astra")):
            d9 = [media_us(tab, av, u) - media_us(tab, b, u) for u in uss]
            d36 = [tab[(au, av, u)] - tab[(au, b, u)] for au in AUTORES for u in uss]
            p, pp = wilcoxon(d9); lo, hi = ic_bootstrap(d9)
            out.append(dict(familia="F2-por-US", alvo=f"{b}-{av}", metrica=col, n=9, delta=np.mean(d9), ic95_inf=lo, ic95_sup=hi,
                            p_exato=p, p_permutacao=pp, efeito_r_ou_W=rank_biserial(d9),
                            descricao=f"avançado melhor em {sum(x > 0 for x in d36)} de 36 pares; empates {sum(x == 0 for x in d36)}"))

    # F4: três versões básicas (Friedman com 9 blocos = US, valor = média dos 4 prompts) e pós-teste de Wilcoxon com Holm
    basicos = ["haiku", "luna", "flashlite"]
    x = [[media_us(nota, m, u) for m in basicos] for u in uss]
    chi2, p, pp, w = friedman(x)
    out.append(dict(familia="F4-Friedman", alvo="basicos", metrica="nota_final", n=9, delta=chi2, p_exato=p, p_permutacao=pp, efeito_r_ou_W=w))
    pares = list(itertools.combinations(basicos, 2)); res = []
    for m1, m2 in pares:
        d = [media_us(nota, m1, u) - media_us(nota, m2, u) for u in uss]; res.append((m1, m2, d, *wilcoxon(d)))
    adj = holm(np.array([r[3] for r in res]))
    for (m1, m2, d, p, pp), ph in zip(res, adj):
        out.append(dict(familia="F4-posthoc", alvo=f"{m1}-{m2}", metrica="nota_final", n=9, delta=np.mean(d), p_exato=p, p_permutacao=pp,
                        p_holm=ph, efeito_r_ou_W=rank_biserial(d)))

    # F1: efeito do autor do prompt em cada modelo (Friedman com 9 blocos = US, 4 grupos = autores)
    fr = []
    for m in MODELOS:
        x = [[nota[(au, m, u)] for au in AUTORES] for u in uss]; fr.append((m, *friedman(x)))
    adj = holm(np.array([f[3] for f in fr]))
    for (m, chi2, p, pp, w), ph in zip(fr, adj):
        out.append(dict(familia="F1-Friedman", alvo=m, metrica="nota_final", n=9, delta=chi2, p_exato=p, p_permutacao=pp, p_holm=ph, efeito_r_ou_W=w))
    for m in MODELOS:
        res = []
        for a1, a2 in itertools.combinations(AUTORES, 2):
            d = [nota[(a1, m, u)] - nota[(a2, m, u)] for u in uss]; res.append((a1, a2, d, *wilcoxon(d)))
        adj = holm(np.array([r[3] for r in res]))
        for (a1, a2, d, p, pp), ph in zip(res, adj):
            lo, hi = ic_bootstrap(d)
            out.append(dict(familia="F1-posthoc", alvo=m, metrica=f"{a1}-{a2}", n=9, delta=np.mean(d), ic95_inf=lo, ic95_sup=hi, p_exato=p, p_permutacao=pp, p_holm=ph,
                            efeito_r_ou_W=rank_biserial(d)))

    # F3: prompt da própria família x média dos outros autores; inferência com a média por US dos modelos da família
    d_par = {}
    for au, ms in FAMILIA_DO_AUTOR.items():
        for m in ms:
            for u in uss:
                d_par[(m, u)] = nota[(au, m, u)] - np.mean([nota[(o, m, u)] for o in AUTORES if o != au])
    res = []
    for m in MODELOS:
        d = [d_par[(m, u)] for u in uss]; res.append((m, d, *wilcoxon(d)))
    adj = holm(np.array([r[2] for r in res]))
    for (m, d, p, pp), ph in zip(res, adj):
        lo, hi = ic_bootstrap(d)
        out.append(dict(familia="F3-por-modelo", alvo=m, metrica="nota_final", n=9, delta=np.mean(d), ic95_inf=lo, ic95_sup=hi,
                        p_exato=p, p_permutacao=pp, p_holm=ph, efeito_r_ou_W=rank_biserial(d)))
    d9 = [np.mean([d_par[(m, u)] for m in MODELOS]) for u in uss]
    p, pp = wilcoxon(d9); lo, hi = ic_bootstrap(d9)
    out.append(dict(familia="F3-por-US", alvo="propria-familia", metrica="nota_final", n=9, delta=np.mean(d9), ic95_inf=lo, ic95_sup=hi,
                    p_exato=p, p_permutacao=pp, efeito_r_ou_W=rank_biserial(d9),
                    descricao=f"{len(d_par)} pares modelo x US; média dos pares {np.mean(list(d_par.values())):.3f}"))

    campos = ["familia", "alvo", "metrica", "n", "delta", "ic95_inf", "ic95_sup", "p_exato", "p_permutacao", "p_holm", "efeito_r_ou_W", "descricao"]
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos); w.writeheader()
        for r in out: w.writerow({k: (f"{v:.6g}" if isinstance(v, (float, np.floating)) else v) for k, v in r.items()})
    print(f"{len(out)} linhas -> {a.out}")


if __name__ == "__main__":
    main()
