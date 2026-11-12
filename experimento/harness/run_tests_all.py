import json, sys, subprocess, urllib.request, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import run_tests as rt
BASE = rt.BASE
def unlock():
    body = json.dumps({"email": "customer@practicesoftwaretesting.com", "password": "welcome01"}).encode()
    for _ in range(12):
        try:
            r = urllib.request.urlopen(urllib.request.Request("https://api.practicesoftwaretesting.com/users/login", body, {"Content-Type": "application/json"}), timeout=20)
            if r.status == 200: return True
        except Exception: pass
        time.sleep(30)
    return False
root = BASE / sys.argv[1]
for d in sorted(p for p in root.glob("*/US*") if p.is_dir()):
    if (d / "tests_result.json").exists(): continue
    if d.name == "US03": unlock()
    r = rt.run_dir(d)
    (d / "tests_result.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(d.relative_to(BASE), r["compila"], len(r["tests"]), sum(t["outcome"] == "passed" for t in r["tests"]), r.get("erro", "")[:80], flush=True)
