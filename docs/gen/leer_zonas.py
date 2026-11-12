"""Solo lectura: zonas de la placa abierta con sus ajustes."""
from kipy import KiCad
from kipy.proto.board.board_types_pb2 import BoardLayer

b = KiCad().get_board()
for z in b.get_zones():
    p = z._proto
    print("==", repr(z.name), "regla" if z.is_rule_area() else "cobre", [BoardLayer.Name(l) for l in z.layers],
          "red", p.copper_settings.net.name if p.HasField("copper_settings") else "-", "prio", p.priority)
    if z.is_rule_area():
        print(p.rule_area_settings)
    else:
        print(p.copper_settings)
    ol = z.outline
    pts = [(n.point.x / 1e6, n.point.y / 1e6) for n in ol.outline.nodes]
    print("  contorno:", pts[:8], "...", len(pts), "puntos")
