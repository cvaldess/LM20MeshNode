"""Modelo 3D (STEP) del Ebyte E108-GN04S a partir del manual (E108-GN04 Series User Manual v1.3, pág. 8).

Medidas acotadas: 12,2 x 16,0 x 2,4 mm; 24 medias vías (12 por lado), paso 1,10, la 1.ª a 1,00 del canto
superior, salto de 3,00 entre las patas 7 y 8 (y 18 y 17); pad superior 0,40 (hacia dentro) x 0,80,
pad inferior 0,80 x 0,80, media vía Ø0,50. Posiciones = pads de `meshnode:E108-GN04S` (pad 1 arriba izq.).
Medido sobre el dibujo (la imagen no tiene la misma escala en x que en y; cada eje con la suya):
blindaje 9,88 de ancho centrado, de 1,25 a 15,17 mm del canto superior. La vista lateral no está a escala:
PCB 0,8 + blindaje 1,6 (total 2,4 acotado).

Origen = centro del cuerpo (igual que la huella), z = 0 en la cara inferior del módulo.
Ejes del modelo: x a la derecha, y hacia el pad 1 (= -y de la huella), z hacia arriba.

Uso (necesita build123d; no está en el Python de KiCad):
    python modelo3d_e108gn04s.py [salida.step]
Por defecto escribe ../../libs/meshnode.3dshapes/E108-GN04S.step
"""
import sys
from pathlib import Path

from build123d import Align, Axis, Box, Color, Compound, Cylinder, Pos, export_step, offset

MIN = (Align.CENTER, Align.CENTER, Align.MIN)

W, L, H = 12.2, 16.0, 2.4
T_CU = 0.035
Z_PCB0, Z_PCB1 = T_CU, 0.8
R_CAST = 0.25
PLATING = 0.04
PAD_W = 0.80                      # a lo largo del canto
PAD_IN_TOP, PAD_IN_BOT = 0.40, 0.80


def caja(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN)


def fy(v_from_top):
    return L / 2 - v_from_top


# --- posiciones en coordenadas de la HUELLA (y hacia abajo) ---------------------------------
ys = [-7.0 + k * 1.1 for k in range(7)] + [2.6 + k * 1.1 for k in range(5)]
cast_fp = [(-W / 2, y) for y in ys] + [(W / 2, y) for y in ys]

# --- PCB ----------------------------------------------------------------------------------
pcb = caja(-W / 2, W / 2, -L / 2, L / 2, Z_PCB0, Z_PCB1)
for x, yf in cast_fp:
    pcb -= Pos(x, -yf, -1) * Cylinder(R_CAST + PLATING, 3, align=MIN)

# --- medias vías metalizadas con sus pads ---------------------------------------------------
cuerpo = caja(-W / 2, W / 2, -L / 2, L / 2, 0, Z_PCB1 + T_CU)
oro = None
for x, yf in cast_fp:
    y = -yf
    s = -1 if x > 0 else 1                     # hacia dentro
    xt0, xt1 = sorted((x, x + s * PAD_IN_TOP))
    xb0, xb1 = sorted((x, x + s * PAD_IN_BOT))
    p = (caja(xb0, xb1, y - PAD_W / 2, y + PAD_W / 2, 0, T_CU)
         + caja(xt0, xt1, y - PAD_W / 2, y + PAD_W / 2, Z_PCB1, Z_PCB1 + T_CU)
         + Pos(x, y, 0) * Cylinder(R_CAST + PLATING, Z_PCB1 + T_CU, align=MIN))
    p -= Pos(x, y, -1) * Cylinder(R_CAST, 3, align=MIN)
    p &= cuerpo
    oro = p if oro is None else oro + p

# --- blindaje (caja hueca abierta por abajo) ------------------------------------------------
SH_X = 9.88 / 2
SH_V0, SH_V1 = 1.25, 15.17
WALL = 0.12
caja_sh = caja(-SH_X, SH_X, fy(SH_V1), fy(SH_V0), Z_PCB1, H)
blindaje = offset(caja_sh, amount=-WALL, openings=caja_sh.faces().sort_by(Axis.Z)[0])

# --- ensamblaje con colores ----------------------------------------------------------------
partes = []
for nombre, forma, color in (("PCB", pcb, (0.08, 0.38, 0.18)),
                             ("Pads", oro, (0.83, 0.69, 0.22)),
                             ("Blindaje", blindaje, (0.78, 0.78, 0.80))):
    forma.label = nombre
    forma.color = Color(*color)
    partes.append(forma)
modulo = Compound(label="E108-GN04S", children=partes)

salida = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path(__file__).resolve().parents[2] / "libs" / "meshnode.3dshapes" / "E108-GN04S.step")
export_step(modulo, str(salida))
bb = modulo.bounding_box()
print(f"{salida}\n  x {bb.min.X:.3f}..{bb.max.X:.3f}  y {bb.min.Y:.3f}..{bb.max.Y:.3f}"
      f"  z {bb.min.Z:.3f}..{bb.max.Z:.3f}")
