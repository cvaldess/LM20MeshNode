"""Solo lectura (placa abierta en KiCad): pistas y vías por red, anchos, capas, bloqueo."""
from collections import defaultdict
import math
from kipy import KiCad
from kipy.proto.board.board_types_pb2 import BoardLayer

b = KiCad().get_board()
por_red = defaultdict(lambda: {"n": 0, "mm": 0.0, "anchos": set(), "capas": set(), "vias": 0, "fijas": 0})
tracks = b.get_tracks()
vias = b.get_vias()
for t in tracks:
    d = por_red[t.net.name]
    d["n"] += 1
    try:
        d["mm"] += t.length() / 1e6
    except Exception:
        d["mm"] += math.hypot(t.end.x - t.start.x, t.end.y - t.start.y) / 1e6
    d["anchos"].add(round(t.width / 1e6, 3))
    d["capas"].add(BoardLayer.Name(t.layer))
    if t.locked:
        d["fijas"] += 1
for v in vias:
    d = por_red[v.net.name]
    d["vias"] += 1
    if v.locked:
        d["fijas"] += 1
for n, d in sorted(por_red.items()):
    print(f"{n:28s} tramos {d['n']:3d}  {d['mm']:6.1f} mm  anchos {sorted(d['anchos'])}  capas {sorted(d['capas'])}  vías {d['vias']}  fijas {d['fijas']}")
print("total tramos:", len(tracks), "vías:", len(vias))
