"""Bloquea (locked) todas las pistas, arcos y vías de la placa abierta, en un solo commit (un Ctrl+Z).
Sin --apply: simulacro. Con --apply: aplica y verifica releyendo."""
import sys
from kipy import KiCad

APPLY = "--apply" in sys.argv
b = KiCad().get_board()
items = list(b.get_tracks()) + list(b.get_vias())
sueltos = [i for i in items if not i.locked]
print(f"pistas+vías: {len(items)}; sin bloquear: {len(sueltos)}")
if not APPLY or not sueltos:
    print("(simulacro)" if not APPLY else "nada que hacer")
    sys.exit(0)
for i in sueltos:
    i.locked = True
c = b.begin_commit()
try:
    b.update_items(sueltos)
except Exception:
    b.drop_commit(c)
    raise
b.push_commit(c, "Bloquear rutado a mano")
items = list(b.get_tracks()) + list(b.get_vias())
n_lock = sum(1 for i in items if i.locked)
print(f"verificación: {n_lock}/{len(items)} bloqueados ->", "OK" if n_lock == len(items) else "REVISAR")
