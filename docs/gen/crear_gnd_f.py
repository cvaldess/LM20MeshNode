"""Relleno GND en F.Cu («GND_F»), en vivo por kipy y en un commit: copia los ajustes de GND_In1 (contorno = rectángulo
de la placa; KiCad lo recorta al canto, la ranura y el rebaje con su holgura de 0,5) con holgura 0,25 y térmicas
0,3/0,3 (pads 0402). Se niega si ya existe. Rellena las zonas al final.
Uso (KiCad abierto): python crear_gnd_f.py [--apply]"""
import sys

from kipy import KiCad
from kipy.board_types import Zone
from kipy.proto.board.board_types_pb2 import BoardLayer

b = KiCad().get_board()
zs = {z.name: z for z in b.get_zones()}
assert "GND_F" not in zs, "GND_F ya existe"
base = zs["GND_In1"]
z = Zone(proto=base._proto)
z._proto.ClearField("id")
z.name = "GND_F"
z.layers = [BoardLayer.BL_F_Cu]
cs = z._proto.copper_settings
cs.clearance.value_nm = 250000
cs.connection.thermal_spokes.gap.value_nm = 300000
cs.connection.thermal_spokes.width.value_nm = 300000
z._proto.ClearField("filled_polygons") if z._proto.DESCRIPTOR.fields_by_name.get("filled_polygons") else None
print("nueva:", z.name, [BoardLayer.Name(l) for l in z.layers], cs.net.name, "holgura", cs.clearance.value_nm / 1e6,
      "térmica", cs.connection.thermal_spokes.gap.value_nm / 1e6, "/", cs.connection.thermal_spokes.width.value_nm / 1e6)
if "--apply" not in sys.argv:
    print("(simulacro)")
    sys.exit()
c = b.begin_commit()
try:
    b.create_items([z])
except Exception:
    b.drop_commit(c)
    raise
b.push_commit(c, "Relleno GND en F.Cu (GND_F)")
b.refill_zones()
print("zonas:", [(x.name, [BoardLayer.Name(l) for l in x.layers]) for x in b.get_zones()])
