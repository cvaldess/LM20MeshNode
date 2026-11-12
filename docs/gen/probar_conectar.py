"""Emula la conectividad de Freerouting antes/después de normalizar y la compara con la de KiCad (DRC JSON).
uso: probar_conectar.py x.dsn copia.kicad_pcb drc.json salida.dsn"""
import collections
import json
import re
import sys

import pcbnew

sys.path.insert(0, __file__.rsplit("\\", 1)[0])
import dsn_conectar as D  # noqa: E402

t = open(sys.argv[1], encoding="utf-8").read()
b = pcbnew.LoadBoard(sys.argv[2])
drc = json.load(open(sys.argv[3], encoding="utf-8"))
kicad = collections.Counter()
for v in drc["unconnected_items"]:
    for i in v["items"][:1]:
        m = re.search(r"\[([^\]]+)\]", i["description"])
        if m:
            kicad[m.group(1)] += 1
antes = D.emular(t, b)
t2, inf = D.normalizar(t, b)
despues = D.emular(t2, b)
print("informe:", inf)
PLANOS = {"GND", "3V3"}
malas_a = malas_d = 0
for red in sorted(antes):
    k = kicad.get(red, 0) + 1
    a, d = antes[red], despues[red]
    if red in PLANOS:
        continue
    malas_a += a != k
    malas_d += d != k
    if a != k or d != k:
        print(f"{red:28s} KiCad {k}  Freerouting(emulado) antes {a}  después {d}" + ("" if d == k else "   <-- distinto"))
print(f"redes (sin planos) que no casan con KiCad: antes {malas_a}, después {malas_d}")
open(sys.argv[4], "w", encoding="utf-8", newline="\n").write(t2)
print("escrito", sys.argv[4])
