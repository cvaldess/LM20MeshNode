"""Añade a una COPIA del PCB lo NUEVO de un SES de Freerouting, sin borrar nada (como nuevas_ses_ms2.py de ai_instruments):
  - GND: lo de Freerouting se tira (va por vía al plano In1, las pone él);
  - lo que repite cobre ya existente (fijo) se salta;
  - redes_fuera (opcional): redes que no se añaden.
Así no hace falta «Import Specctra Session» (borra todas las pistas del PCB y deja sólo las del SES).
Uso: python ses_mesh.py x.ses copia.kicad_pcb [salida.json] [redes_fuera,separadas,por,comas]
     salida.json = lista de tramos/vías añadidos (para aplicarlos luego en vivo con kipy)."""
import collections
import json
import math
import re
import sys

import pcbnew

FUERA = {"GND", *(sys.argv[4].split(",") if len(sys.argv) > 4 and sys.argv[4] else ())}
TOL = 2000   # nm
t = open(sys.argv[1], encoding="utf-8").read()
assert "(resolution um 10)" in t, "resolución inesperada"
b = pcbnew.LoadBoard(sys.argv[2])


def bloque(texto, inicio):
    n = 0
    for i in range(inicio, len(texto)):
        n += {"(": 1, ")": -1}.get(texto[i], 0)
        if n == 0:
            return i + 1
    raise ValueError("paréntesis sin cerrar")


def sobre(px, py, s):
    x0, y0, x1, y1 = s
    dx, dy = x1 - x0, y1 - y0
    l2 = dx * dx + dy * dy
    k = 0 if l2 == 0 else max(0, min(1, ((px - x0) * dx + (py - y0) * dy) / l2))
    return math.hypot(px - x0 - k * dx, py - y0 - k * dy) <= TOL


tramos, vias = collections.defaultdict(list), collections.defaultdict(list)
for it in b.GetTracks():
    if it.GetClass() == "PCB_VIA":
        vias[it.GetNetname()].append((it.GetPosition().x, it.GetPosition().y))
    else:
        tramos[it.GetNetname(), b.GetLayerName(it.GetLayer())].append(
            (it.GetStart().x, it.GetStart().y, it.GetEnd().x, it.GetEnd().y))

nuevas, repetidas, nv = collections.Counter(), 0, 0
mm = collections.Counter()
salida = []
i0 = t.index("(network_out")
for m in re.finditer(r'\(net "?([^"\s]+)"?\s', t[i0:]):
    red = m.group(1)
    if red in FUERA or red.split("/")[-1] in FUERA:
        continue
    ini = i0 + m.start()
    blq = t[ini:bloque(t, ini)]
    net = b.FindNet(red)
    assert net is not None, red
    for w in re.finditer(r"\(path (\S+) (\d+)\s+([-\d\s]+)\)", blq):
        v = [int(x) * 100 for x in w.group(3).split()]
        capa, ancho = w.group(1), int(w.group(2)) * 100
        for k in range(0, len(v) - 2, 2):
            x0, y0, x1, y1 = v[k], -v[k + 1], v[k + 2], -v[k + 3]
            if (x0, y0) == (x1, y1) or any(sobre(x0, y0, s) and sobre(x1, y1, s) for s in tramos[red, capa]):
                repetidas += 1
                continue
            s = pcbnew.PCB_TRACK(b)
            s.SetStart(pcbnew.VECTOR2I(x0, y0)); s.SetEnd(pcbnew.VECTOR2I(x1, y1)); s.SetWidth(ancho)
            s.SetLayer(b.GetLayerID(capa)); s.SetNet(net); b.Add(s)
            salida.append({"t": "tramo", "red": red, "capa": capa, "w": ancho, "a": [x0, y0], "b": [x1, y1]})
            nuevas[red] += 1
            mm[capa] += math.hypot(x1 - x0, y1 - y0) / 1e6
    for w in re.finditer(r'\(via "Via\[0-3\]_(\d+):(\d+)_um" (-?\d+) (-?\d+)', blq):
        x, y = int(w.group(3)) * 100, -int(w.group(4)) * 100
        if any(math.hypot(x - a, y - c) <= TOL for a, c in vias[red]):
            repetidas += 1
            continue
        d = pcbnew.PCB_VIA(b)
        d.SetPosition(pcbnew.VECTOR2I(x, y))
        try:
            d.SetWidth(int(w.group(1)) * 1000)
        except TypeError:
            d.SetWidth(pcbnew.F_Cu, int(w.group(1)) * 1000)
        d.SetDrill(int(w.group(2)) * 1000)
        d.SetNet(net)
        b.Add(d)
        salida.append({"t": "via", "red": red, "c": [x, y], "d": int(w.group(1)) * 1000, "taladro": int(w.group(2)) * 1000})
        vias[red].append((x, y))
        nv += 1
b.Save(sys.argv[2])
if len(sys.argv) > 3 and sys.argv[3]:
    json.dump(salida, open(sys.argv[3], "w", encoding="utf-8"), indent=0)
print(f"añadidos: {sum(nuevas.values())} tramos ({ {k: round(x) for k, x in mm.items()} } mm) y {nv} vías · "
      f"repetidos saltados: {repetidas} · fuera: {sorted(FUERA)}")
print("por red:", dict(nuevas.most_common(80)))
