"""DSN para Freerouting del nrf54lm20-meshnode, desde una COPIA del PCB (volcada de KiCad con volcar_copia.py, con su
.kicad_pro y .kicad_dru al lado). Receta de ai_instruments (dsn_ms2.py / dsn_prueba_ina.py):
  - In1 (plano GND) e In2 (plano 3V3) = capas de alimentación: las señales sólo por F.Cu y B.Cu;
  - TODAS las pistas y vías BLOQUEADAS (salen como protegidas: Freerouting no las mueve; incluye las vías GND/3V3 que
    ponga él a mano aunque no las bloquee);
  - franja de 0,5 mm junto al canto como keepout en F y B (Freerouting no respeta la distancia al borde): se saca del
    propio contorno (Edge.Cuts) ⇒ sigue las esquinas R3, el rebaje del JST y la ranura del SHT41;
  - no hay rellenos en F/B que quitar (sólo GND_In1 y 3V3_In2, que pasan a planos).
Uso: "C:/Program Files/KiCad/10.0/bin/python.exe" -X utf8 dsn_mesh.py copia.kicad_pcb salida.dsn
"""
import re
import sys

import pcbnew

BORDE = 0.5
b = pcbnew.LoadBoard(sys.argv[1])
# rellenos exteriores fuera (Freerouting los toma por cobre y no rutea por ahí); se rellenan al final en el PCB
quitadas = []   # pcbnew: soltar la referencia de lo quitado rompe SWIG
for z in list(b.Zones()):
    if z.GetZoneName() in ("GND_F", "GND_B"):
        quitadas.append(z)
        b.Remove(z)
zonas = sorted(z.GetZoneName() for z in b.Zones() if not z.GetIsRuleArea())
assert zonas == ["3V3_In2", "GND_In1"], zonas
print("rellenos exteriores quitados de la copia:", [z.GetZoneName() for z in quitadas])
b.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)
n_bloq = 0
for t in b.GetTracks():
    if not t.IsLocked():
        t.SetLocked(True)
        n_bloq += 1

# franja de canto = (contorno inflado 2 mm) − (contorno encogido 0,5 mm)
placa = pcbnew.SHAPE_POLY_SET()
assert b.GetBoardPolygonOutlines(placa, False), "contorno no cerrado"
assert placa.OutlineCount() == 1 and placa.HoleCount(0) == 1, (placa.OutlineCount(), placa.HoleCount(0))  # placa + ranura
err = pcbnew.FromMM(0.005)
fuera = pcbnew.SHAPE_POLY_SET(placa)
fuera.Inflate(pcbnew.FromMM(2.0), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, err)
dentro = pcbnew.SHAPE_POLY_SET(placa)
dentro.Deflate(pcbnew.FromMM(BORDE), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, err)
franja = pcbnew.SHAPE_POLY_SET(fuera)
franja.BooleanSubtract(dentro)
franja.Fracture()
capas = pcbnew.LSET()
capas.AddLayer(pcbnew.F_Cu)
capas.AddLayer(pcbnew.B_Cu)
vivos = []
for i in range(franja.OutlineCount()):
    z = pcbnew.ZONE(b)
    z.SetIsRuleArea(True)
    z.SetLayerSet(capas)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowZoneFills(False)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    z.SetZoneName(f"CANTO_{i}")
    # OJO: ZONE.SetOutline() se queda con el puntero ⇒ doble free al salir; se rellena el contorno propio de la zona
    cad = franja.Outline(i)
    z.Outline().NewOutline()
    for k in range(cad.PointCount()):
        q = cad.CPoint(k)
        z.Outline().Append(q.x, q.y)
    b.Add(z)
    vivos.append(z)
print("franja de canto:", franja.OutlineCount(), "polígonos,",
      [franja.Outline(i).PointCount() for i in range(franja.OutlineCount())], "vértices")

assert pcbnew.ExportSpecctraDSN(b, sys.argv[2]), "falló la exportación"
t = open(sys.argv[2], encoding="utf-8").read()
# conectividad del cableado fijo como la ve KiCad (Freerouting sólo une extremos exactos): ver dsn_conectar.py
sys.path.insert(0, __file__.rsplit("\\", 1)[0])
import dsn_conectar  # noqa: E402
antes = dsn_conectar.emular(t, b)
t, inf = dsn_conectar.normalizar(t, b)
despues = dsn_conectar.emular(t, b)
print("normalización del cableado fijo:", inf)
print("redes con más trozos para Freerouting que antes de normalizar → después:",
      {r: (antes[r], despues[r]) for r in antes if antes[r] != despues[r] and r not in ("GND", "3V3")})
# clases: KiCad 10 las exporta como «POT,Default» ⇒ sin coma
t, nc = re.subn(r"\(class (\w+),Default\b", r"(class \1", t)
print("clases renombradas (sin «,Default»):", nc)
# GND y 3V3 a una clase propia PLANOS: Freerouting la ignora (--router.autorouter.ignore_net_classes=PLANOS) y las
# vías a los planos las pone él después (11-11: «las vías entorpecen el ruteado de Freerouting»)
i = t.index("(network")
red = t[i:]
for n in ("GND", "3V3"):
    red, k = re.subn(r"(\(class \S+(?:\s+(?:\"[^\"]*\"|[^\s()]+))*?)\s+" + re.escape(n) + r"(?=[\s)])", r"\1", red, count=1)
    assert k == 1, f"{n} no está en ninguna clase"
planos = ("    (class PLANOS GND 3V3\n      (circuit\n        (use_via \"Via[0-3]_600:300_um\")\n      )\n"
          "      (rule\n        (width 200)\n        (clearance 200)\n      )\n    )\n")
red, k = re.subn(r"(\n\s*\(class kicad_default)", "\n" + planos.rstrip() + r"\1", red, count=1)
assert k == 1
t = t[:i] + red
print("clase PLANOS (GND, 3V3) añadida: Freerouting la ignora")
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(t)
capas_dsn = re.findall(r"\(layer (\S+)\s+\(type (\w+)\)", t)
redes = re.findall(r"\(net (\"[^\"]+\"|\S+)\s+\(pins", t)
clases = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(
    r"\(class (\S+)\s.*?\(width (\d+(?:\.\d+)?)\).*?\(clearance (\d+(?:\.\d+)?)\)", t, flags=re.S)}
print("capas:", capas_dsn)
print("planos:", re.findall(r"\(plane (\S+)", t))
print("redes en el DSN:", len(redes))
print("clases (ancho, holgura) en µm:", clases)
print("cableado fijo:", len(re.findall(r"\(wire", t)), "tramos,", len(re.findall(r"\(via ", t)), "vías;",
      "tipos", sorted(set(re.findall(r"\(type (protect|fix|route|normal)\)", t))))
print("keepouts:", len(re.findall(r"\(keepout", t)), "· bloqueados ahora:", n_bloq)
