#!/usr/bin/env python3
"""Atualiza resultados_por_us.csv e tabelas_descritivas.csv com a nota de scores.csv e a cobertura verificada na execução (A5)."""
import csv, statistics as st
from pathlib import Path
B = Path(__file__).resolve().parent
sc = {(r["autor_prompt"], r["modelo"], r["us"]): r for r in csv.DictReader(open(B / "scores.csv", encoding="utf-8"))}
rows = list(csv.DictReader(open(B / "resultados_por_us.csv", encoding="utf-8"))); campos = list(rows[0])
if "crit_verificados_pct" not in campos: campos.insert(campos.index("crit_pct") + 1, "crit_verificados_pct")
for r in rows:
    s = sc[(r["autor_prompt"], r["modelo"], r["us"])]
    ver = int(s["criterios_verificados"]) / int(s["criterios_total"])
    r["nota_script"] = float(r["nota_script"]) - 100 * 0.15 * (float(r["crit_pct"]) - ver) / 0.70 if r.get("crit_verificados_pct", "") == "" else r["nota_script"]
    r["crit_verificados_pct"] = ver; r["nota_final"] = s["nota_final"]
with open(B / "resultados_por_us.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=campos); w.writeheader(); w.writerows(rows)

def q(v, p):
    v = sorted(v); k = (len(v) - 1) * p; i = int(k); return v[i] + (v[min(i + 1, len(v) - 1)] - v[i]) * (k - i)
tab = list(csv.DictReader(open(B / "tabelas_descritivas.csv", encoding="utf-8"))); ct = list(tab[0])
if "crit_verificados_pct" not in ct: ct.insert(ct.index("crit_pct") + 1, "crit_verificados_pct")
for t in tab:
    g = [r for r in rows if t["autor_prompt"] in ("todos", r["autor_prompt"]) and t["modelo"] in ("todos", r["modelo"])]
    n = [float(r["nota_final"]) for r in g]
    t["nota_media"] = round(st.mean(n), 2); t["nota_dp"] = round(st.stdev(n), 2); t["nota_mediana"] = round(st.median(n), 2)
    t["nota_iqr"] = round(q(n, .75) - q(n, .25), 2)
    t["nota_script"] = round(st.mean(float(r["nota_script"]) for r in g), 2)
    t["crit_verificados_pct"] = round(st.mean(float(r["crit_verificados_pct"]) for r in g), 3)
with open(B / "tabelas_descritivas.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=ct); w.writeheader(); w.writerows(tab)
print("ok")
