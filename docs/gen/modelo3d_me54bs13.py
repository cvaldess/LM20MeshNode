"""Modelo 3D (STEP) del Minew ME54BS13 a partir de su datasheet (plano mecánico, pág. 10).

Medidas del plano: 12,0 x 16,5 x 2,4 mm; PCB 1,0 mm; zona de antena 4,46 mm arriba;
20 medias vías Ø0,5 en los cantos izquierdo/derecho, paso 1,1, centros como los pads 1-20 de
`meshnode:ME54BS13`; rejilla inferior 6x10 Ø0,6 (paso 1,5 x 1,2) como los pads A0-F9.
Blindaje medido sobre el plano a escala (~32,3 px/mm): 10,2 de ancho, de 4,63 a 15,28 mm del canto
superior; agujero Ø1 (marca de pin 1) a 2,48 / 6,1 mm del canto superior izquierdo.

Origen = centro del cuerpo (igual que la huella), z = 0 en la cara inferior del módulo.
Ejes del modelo: x a la derecha, y hacia la antena (= -y de la huella), z hacia arriba.

Uso (necesita build123d; no está en el Python de KiCad):
    python modelo3d_me54bs13.py [salida.step]
Por defecto escribe ../../libs/meshnode.3dshapes/ME54BS13.step
"""
import sys
from pathlib import Path

from build123d import (Align, Box, Color, Compound, Cylinder, Pos, export_step, offset,
                       Axis)

MIN = (Align.CENTER, Align.CENTER, Align.MIN)

W, L, H = 12.0, 16.5, 2.4          # cuerpo
T_CU = 0.035                        # cobre de pads
Z_PCB0, Z_PCB1 = T_CU, 1.0          # PCB del módulo (1,0 mm con el cobre inferior)
R_CAST = 0.25                       # media vía Ø0,5
PLATING = 0.04
CAST_PAD_W, CAST_PAD_IN = 0.7, 0.75  # pad de media vía: ancho a lo largo del canto x hacia dentro


def fy(v_from_top):
    """Distancia desde el canto superior (antena) -> y del modelo."""
    return L / 2 - v_from_top


def caja(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN)


# --- posiciones (coordenadas de la HUELLA: y hacia abajo) -----------------------------------
cast_fp = [(-6.0, -2.75 + k * 1.1) for k in range(10)] + [(6.0, -2.75 + k * 1.1) for k in range(10)]
grid_fp = [(-3.75 + i * 1.5, -3.45 + j * 1.2) for i in range(6) for j in range(10)]

# --- PCB con las medias vías ----------------------------------------------------------------
pcb = caja(-W / 2, W / 2, -L / 2, L / 2, Z_PCB0, Z_PCB1)
for x, yf in cast_fp:
    pcb -= Pos(x, -yf, -1) * Cylinder(R_CAST + PLATING, 3, align=MIN)

# --- cobre: medias vías metalizadas + pads arriba/abajo + rejilla inferior --------------------
cuerpo = caja(-W / 2, W / 2, -L / 2, L / 2, 0, Z_PCB1 + T_CU)
oro = None
for x, yf in cast_fp:
    y = -yf
    xin = x - CAST_PAD_IN if x > 0 else x + CAST_PAD_IN
    x0, x1 = sorted((x, xin))
    p = (caja(x0, x1, y - CAST_PAD_W / 2, y + CAST_PAD_W / 2, 0, T_CU)
         + caja(x0, x1, y - CAST_PAD_W / 2, y + CAST_PAD_W / 2, Z_PCB1, Z_PCB1 + T_CU)
         + Pos(x, y, 0) * Cylinder(R_CAST + PLATING, Z_PCB1 + T_CU, align=MIN))
    p -= Pos(x, y, -1) * Cylinder(R_CAST, 3, align=MIN)
    p &= cuerpo
    oro = p if oro is None else oro + p
for x, yf in grid_fp:
    oro += Pos(x, -yf, 0) * Cylinder(0.3, T_CU, align=MIN)

# --- antena (cobre bajo máscara, en la franja de 4,46 mm) ------------------------------------
def tira(u0, u1, v0, v1):
    return caja(u0 - W / 2, u1 - W / 2, fy(v1), fy(v0), Z_PCB1, Z_PCB1 + 0.02)

antena = (tira(0.37, 11.60, 0.43, 0.95)     # brazo superior
          + tira(11.05, 11.60, 0.43, 2.80)  # bajada derecha
          + tira(0.37, 11.60, 2.25, 2.80)   # brazo medio
          + tira(0.37, 0.90, 0.43, 4.46)    # corto a masa
          + tira(2.97, 3.30, 2.80, 4.46))   # alimentación

# --- blindaje: caja hueca abierta por abajo, agujero de pin 1 y patas ------------------------
SH_X = 10.2 / 2
SH_V0, SH_V1 = 4.63, 15.28
WALL = 0.12
caja_sh = caja(-SH_X, SH_X, fy(SH_V1), fy(SH_V0), Z_PCB1, H)
blindaje = offset(caja_sh, amount=-WALL, openings=caja_sh.faces().sort_by(Axis.Z)[0])
blindaje -= Pos(2.48 - W / 2, fy(6.1), H - 1) * Cylinder(0.5, 2, align=MIN)
for u0, u1 in ((1.73, 2.75), (9.07, 10.09)):          # patas inferiores
    blindaje += caja(u0 - W / 2, u1 - W / 2, fy(16.05), fy(SH_V1), Z_PCB1, Z_PCB1 + WALL)
blindaje += caja(7.15 - W / 2, 8.08 - W / 2, fy(SH_V0), fy(4.33), Z_PCB1, Z_PCB1 + WALL)  # pata sup.

# --- ensamblaje con colores ----------------------------------------------------------------
partes = []
for nombre, forma, color in (("PCB", pcb, (0.08, 0.38, 0.18)),
                             ("Antena", antena, (0.20, 0.55, 0.25)),
                             ("Pads", oro, (0.83, 0.69, 0.22)),
                             ("Blindaje", blindaje, (0.78, 0.78, 0.80))):
    forma.label = nombre
    forma.color = Color(*color)
    partes.append(forma)
modulo = Compound(label="ME54BS13", children=partes)

salida = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path(__file__).resolve().parents[2] / "libs" / "meshnode.3dshapes" / "ME54BS13.step")
export_step(modulo, str(salida))
bb = modulo.bounding_box()
print(f"{salida}\n  x {bb.min.X:.3f}..{bb.max.X:.3f}  y {bb.min.Y:.3f}..{bb.max.Y:.3f}"
      f"  z {bb.min.Z:.3f}..{bb.max.Z:.3f}")
