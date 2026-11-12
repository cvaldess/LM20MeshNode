"""Compara dos informes DRC JSON de kicad-cli: violaciones nuevas/desaparecidas y resumen por tipo.
uso: drc_diff.py antes.json despues.json [filtro_texto]"""
import json
import sys
from collections import Counter


def clave(v):
    return (v["type"], tuple(sorted(i["description"] for i in v.get("items", []))))


def carga(p):
    d = json.load(open(p, encoding="utf-8"))
    return d.get("violations", []), d.get("unconnected_items", []), d.get("schematic_parity", [])


a, ua, _ = carga(sys.argv[1])
b, ub, _ = carga(sys.argv[2])
filtro = sys.argv[3] if len(sys.argv) > 3 else None
ka, kb = Counter(map(clave, a)), Counter(map(clave, b))
print("violaciones antes/después:", len(a), len(b), "| sin conectar:", len(ua), len(ub))
print("por tipo (después):", dict(Counter(v["type"] for v in b)))
nuevas = kb - ka
idas = ka - kb
print("NUEVAS:", sum(nuevas.values()))
for (t, items), n in nuevas.items():
    print("  +", t, n, items)
print("DESAPARECIDAS:", sum(idas.values()))
for (t, items), n in idas.items():
    print("  -", t, n, items)
if filtro:
    print(f"violaciones (después) que mencionan '{filtro}':")
    for v in b:
        if any(filtro in i["description"] for i in v.get("items", [])):
            print("  ", v["type"], [i["description"] for i in v["items"]])
    print(f"sin conectar (después) que mencionan '{filtro}':")
    for v in ub:
        if any(filtro in i["description"] for i in v.get("items", [])):
            print("  ", [i["description"] for i in v["items"]])
