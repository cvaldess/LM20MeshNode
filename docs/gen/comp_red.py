"""Componentes (regla Freerouting emulada) de unas redes en un DSN, con sus pines y tramos.
uso: comp_red.py x.dsn copia.kicad_pcb RED [RED...]"""
import collections
import re
import sys

import pcbnew

sys.path.insert(0, __file__.rsplit("\\", 1)[0])
import dsn_conectar as D  # noqa: E402

t = open(sys.argv[1], encoding="utf-8").read()
b = pcbnew.LoadBoard(sys.argv[2])
segs, vias = D.leer(t)
i = t.index("(network")
redes = {m.group(1).strip('"'): m.group(2).split() for m in re.finditer(r'\(net ("[^"]+"|\S+)\s+\(pins ([^)]*)\)', t[i:])}
padpos = collections.defaultdict(list)
for f in b.Footprints():
    for p in f.Pads():
        c = p.GetPosition()
        padpos[f"{f.GetReference()}-{p.GetNumber()}"].append((round(c.x / 1000, 1), round(-c.y / 1000, 1)))
k = lambda p: (round(p[0], 1), round(p[1], 1))
for red in sys.argv[3:]:
    padre = {}

    def raiz(x):
        while padre.setdefault(x, x) != x:
            x = padre[x]
        return x

    def unir(a, c):
        padre[raiz(a)] = raiz(c)

    ss = [s for s in segs if s["red"].strip('"') == red]
    for s in ss:
        unir(k(s["a"]), k(s["b"]))
    for v in vias:
        if v["red"].strip('"') == red:
            unir(("via", k(v["c"])), k(v["c"]))
    for pn in redes[red]:
        for c in padpos[pn]:
            unir(("pin", pn), c)
    grupos = collections.defaultdict(list)
    for pn in redes[red]:
        grupos[raiz(("pin", pn))].append(pn)
    for v in vias:
        if v["red"].strip('"') == red:
            grupos[raiz(("via", k(v["c"])))].append(f"vía{k(v['c'])}")
    print(red, "componentes:", len(grupos))
    for g in grupos.values():
        print("   ", g)
    print("   pines:", {pn: padpos[pn] for pn in redes[red]})
    for s in ss:
        print("   ", s["capa"], s["w"], k(s["a"]), "->", k(s["b"]))
