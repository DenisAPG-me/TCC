#!/usr/bin/env python3
"""Uso (WSL): python3 run_tests.py [--root resultados] [--model haiku] [--us US01] [--file script_corrigido.py]
Executa cada script com pytest do Python do Windows (Playwright Edge headless) e grava tests_result.json."""
import argparse, json, os, re, subprocess, time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PY = "/mnt/c/Python314/python.exe"
SEL = re.compile(r"waiting for|Timeout .*exceed|strict mode|locator|selector|Target page|not an <input>|element is not", re.I)

def win(p): return subprocess.check_output(["wslpath", "-w", str(p)], text=True).strip()

def run_dir(d, fname="script.py", timeout=600):
    d = Path(d); f = d / fname
    res = {"arquivo": fname, "compila": 0, "coletou": 0, "tests": []}
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", WSLENV="PYTHONIOENCODING:PYTHONUTF8")
    if not f.exists() or not f.read_text(encoding="utf-8").strip():
        res["erro"] = "sem script"; return res
    c = subprocess.run([PY, "-m", "py_compile", win(f)], capture_output=True, text=True, cwd="/mnt/c", env=env)
    res["compila"] = int(c.returncode == 0)
    if c.returncode:
        res["erro"] = c.stderr[-800:]; return res
    jr = d / ("report_" + fname + ".json")
    if jr.exists(): jr.unlink()
    t0 = time.time()
    try:
        p = subprocess.run([PY, "-m", "pytest", win(f), "-p", "no:cacheprovider", "--browser", "chromium", "--browser-channel", "msedge",
                            "--json-report", f"--json-report-file={win(jr)}", "--json-report-indent=1", "-q", "--tb=short",
                            "--rootdir", win(d)],
                           capture_output=True, text=True, cwd="/mnt/c", env=env, timeout=timeout)
        res["stdout_tail"] = p.stdout[-1500:]; res["returncode"] = p.returncode
    except subprocess.TimeoutExpired:
        res["erro"] = "timeout"; return res
    res["duracao_s"] = round(time.time() - t0, 2)
    if not jr.exists():
        res["erro"] = "sem relatorio (erro de coleta/import)"; return res
    j = json.loads(jr.read_text(encoding="utf-8"))
    cols = [c for c in j.get("collectors", []) if c.get("outcome") == "failed"]
    if cols and not j.get("tests"):
        res["erro"] = "erro de coleta/import"; res["coleta"] = str(cols[0].get("longrepr", ""))[-800:]; return res
    res["coletou"] = 1
    for t in j.get("tests", []):
        msg = ""
        for ph in ("setup", "call", "teardown"):
            if t.get(ph, {}).get("outcome") == "failed":
                msg = t[ph].get("longrepr") or t[ph].get("crash", {}).get("message", ""); break
        res["tests"].append({"nodeid": t["nodeid"], "outcome": t["outcome"], "falha_seletor": bool(msg and SEL.search(msg)), "msg": str(msg)[-600:]})
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(BASE / "resultados"))
    ap.add_argument("--model"); ap.add_argument("--us"); ap.add_argument("--file", default="script.py")
    ap.add_argument("--dir", help="rodar uma pasta específica")
    a = ap.parse_args()
    dirs = [Path(a.dir)] if a.dir else sorted(p for p in Path(a.root).glob("*/*") if p.is_dir()
            and (not a.model or p.parent.name == a.model) and (not a.us or p.name == a.us))
    for d in dirs:
        r = run_dir(d, a.file)
        out = d / ("tests_result.json" if a.file == "script.py" else f"tests_result_{Path(a.file).stem}.json")
        out.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        n = len(r["tests"]); ok = sum(t["outcome"] == "passed" for t in r["tests"])
        print(f"{d}: compila={r['compila']} testes={n} passou={ok} {r.get('erro','')}")
