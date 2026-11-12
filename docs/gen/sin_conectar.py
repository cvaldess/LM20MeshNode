"""Cuenta los «unconnected items» del DRC JSON por red. uso: sin_conectar.py drc.json"""
import json
import re
import sys
from collections import Counter

d = json.load(open(sys.argv[1], encoding="utf-8"))
c = Counter()
for v in d["unconnected_items"]:
    redes = {m.group(1) for i in v["items"] for m in [re.search(r"\[([^\]]+)\]", i["description"])] if m}
    c[" / ".join(sorted(redes))] += 1
for r, n in c.most_common():
    print(f"{n:3d}  {r}")
print("total", sum(c.values()))
