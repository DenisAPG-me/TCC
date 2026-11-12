#!/usr/bin/env python3
"""Uso: python3 score.py [--root resultados] [--out scores.csv]. Aplica a rubrica.md ao que for automatizável;
julgamento.json / qualidade.json por resposta completam os itens [M]."""
import argparse, csv, difflib, json, re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
W = dict(e=.05, p=.20, s=.10, c=.15, m=.05, r=.10, q=.10, h=.05, k=.15, t=.05)

def toks(s): return set(re.findall(r"\w{3,}", str(s).lower()))
def jac(a, b):
    a, b = toks(a), toks(b); return len(a & b) / len(a | b) if a | b else 0

def load(p, default=None):
    p = Path(p); return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

def score_dir(d, us, oracle):
    meta = load(d / "meta.json", {}); tr = load(d / "tests_result.json", {"tests": [], "compila": 0})
    casos = load(d / "casos_teste.json", []); jul = load(d / "julgamento.json"); qual = load(d / "qualidade.json")
    code = (d / "script.py").read_text(encoding="utf-8") if (d / "script.py").exists() else ""
    fixed = d / "script_corrigido.py"
    linhas = 0
    if fixed.exists():
        linhas = sum(1 for l in difflib.unified_diff(code.splitlines(), fixed.read_text(encoding="utf-8").splitlines(), lineterm="", n=0)
                     if l[:1] in "+-" and l[:3] not in ("+++", "---"))
    tests = tr.get("tests", []); n = len(tests); ok = sum(t["outcome"] == "passed" for t in tests)
    executa = int(tr.get("compila") == 1 and tr.get("coletou") == 1)
    sel = sum(t["falha_seletor"] for t in tests if t["outcome"] != "passed") + (jul or {}).get("dado_inventado", 0)
    # critérios cobertos: manual se houver, senão heurística (strings entre aspas dos critérios presentes no script)
    if jul and "criterios_cobertos" in jul: cc, cc_src = len(jul["criterios_cobertos"]), "manual"
    else:
        cc = 0
        for crit in us["criterios"]:
            keys = re.findall(r'"([^"]{3,})"', crit)
            if keys and any(k.lower() in code.lower() for k in keys): cc += 1
        cc_src = "auto"
    # casos
    n_c = len(casos)
    if jul and "casos_oraculo_cobertos" in jul:
        cob = set(jul["casos_oraculo_cobertos"]); valid = len(jul.get("validos", [])); alu = len(jul.get("alucinados", [])); src = "manual"
        novos = max(0, valid - len(cob))
    else:
        cob, matched = set(), 0
        for c in casos:
            best = max(((jac(c if isinstance(c, str) else json.dumps(c, ensure_ascii=False), o["descricao"]), o["id"]) for o in oracle), default=(0, None))
            if best[0] >= .25: cob.add(best[1]); matched += 1
        valid, alu, novos, src = matched, 0, 0, "auto"
    recall = len(cob) / len(oracle) if oracle else 0
    prec = valid / n_c if n_c else 0
    k = None
    if qual:
        dims = [qual.get(x) for x in ("legibilidade", "estrutura", "assercoes", "espera", "manutenibilidade")]
        k = sum(dims) / 5 if None not in dims else None
    comp = dict(e=executa, p=ok / n if n else 0, s=max(0, 1 - sel / max(n, 1)), c=cc / len(us["criterios"]),
                m=max(0, 1 - linhas / 50) if (executa or fixed.exists()) else 0, r=recall, q=prec,
                h=1 - alu / max(n_c, 1), k=(k / 5 if k is not None else None), t=max(0, 1 - (meta.get("tempo_s") or 0) / 300))
    parcial = k is None or src == "auto" or cc_src == "auto"
    nota = 100 * sum(W[x] * (comp[x] or 0) for x in W)
    tk = meta.get("tokens") or {}
    conf = int(not re.search(r"sync_playwright", code)) if us["tipo"] == "ui" else int(not re.search(r"playwright", code))
    return dict(modelo=d.parent.name, conformidade_padrao=conf, us=d.name, tipo=us["tipo"], complexidade=us["complexidade"], executa=executa,
                n_testes=n, pct_passam=round(comp["p"] * 100, 1), falhas_seletor_dado=sel, criterios_cobertos=cc,
                criterios_total=len(us["criterios"]), criterios_fonte=cc_src, linhas_corrigidas=linhas,
                tempo_s=meta.get("tempo_s"), tokens=tk.get("total") or ((tk.get("input") or 0) + (tk.get("output") or 0)) or "",
                casos_total=n_c, casos_validos=valid, recall=round(recall, 3), precisao=round(prec, 3), casos_novos=novos,
                casos_alucinados=alu, casos_fonte=src, qualidade_codigo=round(k, 2) if k is not None else "",
                nota_final=round(nota, 1), nota_parcial=int(parcial))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(BASE / "resultados")); ap.add_argument("--out", default=str(BASE / "scores.csv"))
    a = ap.parse_args()
    stories = {u["id"]: u for u in json.load(open(BASE / "user-stories.json", encoding="utf-8"))}
    oracle = json.load(open(BASE / "oraculo-casos.json", encoding="utf-8"))
    rows = [score_dir(d, stories[d.name], oracle[d.name]["casos"]) for d in sorted(Path(a.root).glob("[a-z]*/US*")) if d.name in stories]
    if rows:
        with open(a.out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} linhas -> {a.out}")
