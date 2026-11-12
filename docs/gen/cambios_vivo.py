"""Diferencias de pistas/vías entre la placa viva y una copia guardada. uso: cambios_vivo.py copia.kicad_pcb"""
import sys

import pcbnew
from kipy import KiCad
from kipy.proto.board.board_types_pb2 import BoardLayer

r = lambda v: round(v / 1000)   # µm


def clave_t(red, capa, a, b, w):
    p, q = sorted([a, b])
    return (red, capa, p, q, w)


c = pcbnew.LoadBoard(sys.argv[1])
copia = set()
for it in c.GetTracks():
    if it.GetClass() == "PCB_VIA":
        copia.add(("via", it.GetNetname(), (r(it.GetPosition().x), r(it.GetPosition().y))))
    else:
        copia.add(clave_t(it.GetNetname(), c.GetLayerName(it.GetLayer()), (r(it.GetStart().x), r(it.GetStart().y)),
                          (r(it.GetEnd().x), r(it.GetEnd().y)), r(it.GetWidth())))
b = KiCad().get_board()
vivo = set()
capa = {BoardLayer.BL_F_Cu: "F.Cu", BoardLayer.BL_B_Cu: "B.Cu"}
for t in b.get_tracks():
    vivo.add(clave_t(t.net.name, capa.get(t.layer, str(t.layer)), (r(t.start.x), r(t.start.y)), (r(t.end.x), r(t.end.y)),
                     r(t.width)))
for v in b.get_vias():
    vivo.add(("via", v.net.name, (r(v.position.x), r(v.position.y))))
print("sólo en VIVO:")
for k in sorted(vivo - copia, key=str):
    print("  ", k)
print("sólo en la COPIA:")
for k in sorted(copia - vivo, key=str):
    print("  ", k)
