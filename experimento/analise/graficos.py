#!/usr/bin/env python3
"""Uso: python experimento/analise/graficos.py [--scores experimento/analise/scores.csv] [--dir experimento/analise/graficos]
Gera os gráficos de tempo médio de geração x nota final e x % de testes aprovados por modelo e autor do prompt."""
import argparse, csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

BASE = Path(__file__).resolve().parent
MODELOS = {"haiku": ("Haiku", "#2a7bdc"), "opus": ("Opus", "#6552d9"), "luna": ("Luna", "#1aae7f"),
           "astra": ("Astra", "#ec6935"), "flashlite": ("Flash-Lite", "#e87ea7")}
AUTORES = {"grok": ("Grok", "o"), "claude": ("Claude", "s"), "chatgpt": ("ChatGPT", "^"), "gemini": ("Gemini", "D")}
CINZA = "#c4c4b8"


def medias(rows):
    out = {}
    for m in MODELOS:
        for a in AUTORES:
            r = [x for x in rows if x["modelo"] == m and x["autor_prompt"] == a]
            out[(m, a)] = tuple(sum(float(x[c]) for x in r) / len(r) for c in ("tempo_s", "nota_final", "pct_passam"))
    return out


def eixo(ax, ylabel, titulo):
    ax.set_xlabel("Tempo médio de geração (s)", fontsize=13); ax.set_ylabel(ylabel, fontsize=13)
    ax.set_title(titulo, loc="left", fontsize=14); ax.grid(color="#e6e6e6", linewidth=1); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=12, colors="#444444")


def legendas(ax, tamanho=False):
    h1 = [Line2D([], [], marker="o", ls="", color=c, markersize=10, label=n) for n, c in MODELOS.values()]
    l1 = ax.legend(handles=h1, title="Modelo (cor + rótulo)", loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False,
                   fontsize=13, title_fontsize=13, alignment="left"); ax.add_artist(l1)
    h2 = [Line2D([], [], marker=mk, ls="", markerfacecolor=CINZA, markeredgecolor="black", markersize=11, label=n) for n, mk in AUTORES.values()]
    l2 = ax.legend(handles=h2, title="Autor do prompt (forma)", loc="upper left", bbox_to_anchor=(1.02, 0.62), frameon=False,
                   fontsize=13, title_fontsize=13, alignment="left")
    if tamanho:
        ax.add_artist(l2)
        h3 = [plt.scatter([], [], s=tam(p), marker="o", color=CINZA, edgecolors="black", label=f"{p}%") for p in (25, 50, 75, 100)]
        ax.legend(handles=h3, title="Tamanho = % de testes\nque passam", loc="upper left", bbox_to_anchor=(1.03, 0.30), frameon=False,
                  fontsize=13, title_fontsize=13, labelspacing=1.3, borderpad=0.8, alignment="left")


def tam(p): return 40 + 9 * p


def rotulos(ax, med, y):
    for m, (nome, _) in MODELOS.items():
        pts = [(med[(m, a)][0], med[(m, a)][y]) for a in AUTORES]
        if m == "flashlite":  # abaixo do grupo, para não sobrepor os pontos do Luna
            yy = min(t[1] for t in pts); dy = -34
        else:
            yy = max(t[1] for t in pts); dy = 22
        x, ha = sum(t[0] for t in pts) / len(pts), "center"
        if m == "flashlite": x, ha = 1, "left"  # junto ao eixo, para não encostar nos pontos do Luna
        ax.annotate(nome, (x, yy), xytext=(0, dy), textcoords="offset points", ha=ha, fontsize=14, fontweight="bold")


def grafico(med, y, ylabel, titulo, arquivo, tamanho=False):
    fig, ax = plt.subplots(figsize=(12.3, 7.5), dpi=225)
    for (m, a), v in med.items():
        ax.scatter(v[0], v[y], s=tam(v[2]) if tamanho else 140, marker=AUTORES[a][1], color=MODELOS[m][1],
                   edgecolors="black", linewidths=1.6 if not tamanho else 1.0, alpha=0.88 if tamanho else 1, zorder=3)
    ys = [v[y] for v in med.values()]; amp = max(ys) - min(ys)
    ax.set_ylim(min(ys) - 0.16 * amp, max(ys) + 0.12 * amp); ax.set_xlim(0, max(v[0] for v in med.values()) + 6)
    rotulos(ax, med, y); eixo(ax, ylabel, titulo); legendas(ax, tamanho)
    fig.subplots_adjust(left=0.09, right=0.76, top=0.93, bottom=0.11); fig.savefig(arquivo); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", default=str(BASE / "scores.csv")); ap.add_argument("--dir", default=str(BASE / "graficos"))
    a = ap.parse_args(); d = Path(a.dir); d.mkdir(exist_ok=True)
    med = medias(list(csv.DictReader(open(a.scores, encoding="utf-8"))))
    grafico(med, 1, "Nota final média (0–100)", "Tempo × nota final (média das 9 US; cada ponto = modelo × autor do prompt)", d / "a_tempo_x_nota.png")
    grafico(med, 2, "% de testes que passam (média)", "Tempo × % de testes que passam (média das 9 US; cada ponto = modelo × autor do prompt)",
            d / "b_tempo_x_pct_passam.png")
    grafico(med, 1, "Nota final média (0–100)", "Tempo × nota final, tamanho = % de testes que passam", d / "c_tempo_nota_pct_passam.png", tamanho=True)
    print("3 gráficos ->", d)


if __name__ == "__main__":
    main()
