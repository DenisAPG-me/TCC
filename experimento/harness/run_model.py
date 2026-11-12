#!/usr/bin/env python3
"""Uso (WSL): python3 run_model.py --model haiku --us US01 [--us US02 ...|--all]
Modelos: haiku, opus (claude, WSL), luna, astra (codex via cmd.exe), flashlite (gemini via cmd.exe)."""
import argparse, json, re, subprocess, sys, time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
EMPTY_CWD = "<HOME>/AppData/Local/Temp/tcc_empty"
CMDS = {
    "haiku": ["claude", "-p", "--model", "haiku", "--tools", "", "--output-format", "json"],
    "opus": ["claude", "-p", "--model", "opus", "--tools", "", "--output-format", "json"],
    "luna": ["cmd.exe", "/c", "codex exec --skip-git-repo-check -m gpt-6-luna -s read-only -"],
    "astra": ["cmd.exe", "/c", "codex exec --skip-git-repo-check -m gpt-6-astra -s read-only -"],
    "flashlite": ["cmd.exe", "/c", "gemini --skip-trust -m gemini-flash-lite-latest -p -"],
}

def render_us(us):
    crit = "\n".join(f"{i}. {c}" for i, c in enumerate(us["criterios"], 1))
    return f"{us['texto']}\nURL base: {us['url_base']}\n\nCritérios de aceitação:\n{crit}"

def parse_table(text):
    rest = re.sub(r"```.*?```", "", text, flags=re.S)
    keys = ["id", "titulo", "tipo", "criterio", "passos", "esperado"]
    rows = []
    for l in rest.splitlines():
        if l.count("|") < 5:
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cells) < 6 or re.fullmatch(r"[-: ]+", cells[0]) or cells[0].lower() == "id":
            continue
        rows.append(dict(zip(keys, cells[:5] + [" | ".join(cells[5:])])))
    return rows or None

def parse_assumptions(text):
    m = re.search(r"SUPOSI[ÇC][ÕO]ES\s*\n(.*?)(?=```|\Z)", text, re.S | re.I)
    if not m:
        return []
    return [re.sub(r"^\s*[-*]\s*", "", l).strip() for l in m.group(1).splitlines() if re.match(r"^\s*(?:[-*]|\d+[.)])\s*", l)]

def extract(text):
    blocks = re.findall(r"```(\w*)[ \t]*\n(.*?)```", text, re.S)
    py = [b for l, b in blocks if l.lower() in ("python", "py")]
    code = max(py, key=len) if py else ""
    casos = None
    for l, b in blocks:
        if l.lower() == "json":
            try:
                d = json.loads(b)
                casos = d.get("casos", d.get("test_cases")) if isinstance(d, dict) else d
                if casos is not None:
                    break
            except Exception:
                pass
    if casos is None:
        casos = parse_table(text)
    if casos is None:  # fallback: linhas numeradas/bullets/tabela fora dos blocos de código
        rest = re.sub(r"```.*?```", "", text, flags=re.S)
        casos = [re.sub(r"^\s*(?:[-*]|\d+[.)]|\|)\s*", "", l).strip(" |") for l in rest.splitlines()
                 if re.match(r"^\s*(?:[-*]|\d+[.)]|\|\s*(?:TC|CT|\d))", l)]
    return casos, code

def run(model, us, prompt_tpl, outroot):
    prompt = prompt_tpl.replace("{{USER_STORY}}", render_us(us))
    out = outroot / model / us["id"]
    out.mkdir(parents=True, exist_ok=True)
    cmd = CMDS[model]
    t0 = time.time()
    p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8",
                       cwd=EMPTY_CWD, timeout=900)
    dt = time.time() - t0
    raw, tokens = p.stdout, None
    if model in ("haiku", "opus"):
        try:
            j = json.loads(p.stdout); raw = j.get("result", "")
            u = j.get("usage", {})
            tokens = {"input": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0),
                      "output": u.get("output_tokens"), "cost_usd": j.get("total_cost_usd")}
        except Exception:
            pass
    elif model in ("luna", "astra"):
        m = re.search(r"tokens used\s*\n?\s*([\d,]+)", p.stderr + p.stdout)
        tokens = {"total": int(m.group(1).replace(",", ""))} if m else None
    casos, code = extract(raw)
    (out / "prompt_enviado.txt").write_text(prompt, encoding="utf-8")
    (out / "resposta_bruta.txt").write_text(raw, encoding="utf-8")
    (out / "casos_teste.json").write_text(json.dumps(casos, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "suposicoes.json").write_text(json.dumps(parse_assumptions(raw), ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "script.py").write_text(code, encoding="utf-8")
    meta = {"model": model, "us": us["id"], "cmd": cmd, "returncode": p.returncode, "tempo_s": round(dt, 2),
            "tokens": tokens, "n_casos_extraidos": len(casos), "tem_codigo": bool(code),
            "stderr_tail": p.stderr[-500:]}
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=CMDS)
    ap.add_argument("--us", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--prompt", default=str(BASE / "prompt-padrao.txt"))
    ap.add_argument("--out", default=str(BASE / "resultados"))
    a = ap.parse_args()
    stories = {u["id"]: u for u in json.load(open(BASE / "user-stories.json", encoding="utf-8"))}
    ids = list(stories) if a.all else a.us
    tpl = Path(a.prompt).read_text(encoding="utf-8")
    if "{{USER_STORY}}" not in tpl:
        sys.exit("prompt sem {{USER_STORY}}")
    for i in ids:
        print(json.dumps(run(a.model, stories[i], tpl, Path(a.out)), ensure_ascii=False))
