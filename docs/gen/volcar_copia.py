"""Solo lectura: vuelca la placa abierta (con cambios sin guardar) a una copia para DRC."""
import sys
from kipy import KiCad

out = sys.argv[1]
txt = KiCad().get_board().get_as_string()
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write(txt)
print("escrito", out, len(txt), "bytes")
