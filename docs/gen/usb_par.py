"""Par USB (USB_DP/USB_DM) desde el ESD U102 (pines 1/2) hasta el ME54BS13 U201 (pads 8/7).

Geometría (decidida a mano tras medir obstáculos con obstaculos.py):
  - U201: salidas en F.Cu 0,28 hacia el oeste; vías 0,6/0,3 en (111,5; 68,51) D- y (112,3; 69,61) D+.
  - B.Cu: par 0,28/0,2 (90 ohm supuesto) bajando por x ~112 (oeste del OLED), giro a y ~130,2 por debajo de la vía
    de VSYS (119,24; 129,16), y bajada final a dos vías encima de U102 en y 134,52 (entre la pista 3V3 de C108 y el ESD).
  - U102: bajadas cortas en F.Cu 0,2 a los pines 2 (D-) y 1 (D+).
  - D- sale más largo por el giro de salida de U201 ⇒ meandro en D+ (hacia el este) justo tras sus vías.
Modos:
  python usb_par.py                 -> imprime plan y longitudes
  python usb_par.py --copia X.pcb   -> lo añade a una copia con pcbnew y la guarda (para DRC)
  python usb_par.py --apply         -> lo crea en vivo con kipy (un commit) y lo deja bloqueado
"""
import math
import sys

W, G = 0.28, 0.2
S = (W + G) / 2                 # semiseparación de ejes: 0,24
WS = 0.2                        # ancho en los pines del ESD (paso 0,5)
VIA = (0.6, 0.3)


def desplazar(pts, d):
    """Paralela a la polilínea pts a distancia d (positivo = a la izquierda de (-uy, ux), en pantalla y hacia abajo)."""
    seg = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
        seg.append(((x0 - d * uy, y0 + d * ux), (ux, uy)))
    out = [seg[0][0]]
    for (p, u), (q, v) in zip(seg, seg[1:]):
        den = u[0] * v[1] - u[1] * v[0]
        if abs(den) < 1e-9:
            continue
        t = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / den
        out.append((p[0] + t * u[0], p[1] + t * u[1]))
    (x1, y1), (ux, uy) = pts[-1], seg[-1][1]
    out.append((x1 - d * uy, y1 + d * ux))
    return out


def largo(pts):
    return sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:]))


def meandro(x0, ya, h, L=0.6, c=0.2):
    """Bulto hacia +x en una pista que baja por x0 (45° en las 4 esquinas). Devuelve puntos tras (x0, ya)."""
    return [(x0 + c, ya + c), (x0 + h - c, ya + c), (x0 + h, ya + 2 * c), (x0 + h, ya + 2 * c + L),
            (x0 + h - c, ya + 3 * c + L), (x0 + c, ya + 3 * c + L), (x0, ya + 4 * c + L)]


# --- puntos fijos -----------------------------------------------------------------------------------------------
PAD_DM_N, PAD_DP_N = (113.86, 68.51), (113.86, 69.61)       # U201.7 / U201.8
VN_M, VN_P = (111.50, 68.51), (112.30, 69.61)               # vías norte
PAD_DM_S, PAD_DP_S = (120.12, 135.53), (120.62, 135.53)     # U102.2 / U102.1
VS_M, VS_P = (120.12, 134.52), (120.92, 134.52)             # vías sur

# eje del par en B.Cu: baja por xc=112,06, gira al este en yc=130,24, baja por xc=120,36
XC1, YC, XC2, R = 112.06, 130.24, 120.36, 1.0
Y_INI, Y_FIN = 70.42, 133.60
eje = [(XC1, Y_INI), (XC1, YC - R), (XC1 + R, YC), (XC2 - R, YC), (XC2, YC + R), (XC2, Y_FIN)]
# rumbo sur: d>0 = oeste ⇒ D- = +S, D+ = -S
dm_par, dp_par = desplazar(eje, +S), desplazar(eje, -S)
assert abs(dm_par[0][0] - 111.82) < 1e-9 and abs(dp_par[0][0] - 112.30) < 1e-9, (dm_par[0], dp_par[0])
assert abs(dm_par[-1][0] - 120.12) < 1e-9 and abs(dp_par[-1][0] - 120.60) < 1e-9, (dm_par[-1], dp_par[-1])


def construir(h):
    plan = []   # (red, capa, puntos, ancho) | ("via", red, (x, y))
    # D-
    dm_b = [VN_M, (111.50, 70.10), dm_par[0]] + dm_par[1:] + [VS_M]
    plan += [("/USB_DM", "F", [PAD_DM_N, VN_M], W), ("via", "/USB_DM", VN_M),
             ("/USB_DM", "B", dm_b, W), ("via", "/USB_DM", VS_M),
             ("/USB_DM", "F", [VS_M, PAD_DM_S], WS)]
    # D+ (con meandro tras empezar el par)
    YM = 71.00
    dp_b = [VN_P, (112.30, YM)] + (meandro(112.30, YM, h) if h > 0 else []) + dp_par[1:] + \
           [(120.92, Y_FIN + 0.32), VS_P]
    plan += [("/USB_DP", "F", [PAD_DP_N, VN_P], W), ("via", "/USB_DP", VN_P),
             ("/USB_DP", "B", dp_b, W), ("via", "/USB_DP", VS_P),
             ("/USB_DP", "F", [VS_P, (120.92, 134.90), (120.62, 135.20), PAD_DP_S], WS)]
    return plan


def longitudes(plan):
    tot = {"/USB_DM": 0.0, "/USB_DP": 0.0}
    for e in plan:
        if e[0] != "via":
            tot[e[0]] += largo(e[2])
    return tot


# h del meandro que iguala longitudes (bisección; el añadido crece con h)
l0 = longitudes(construir(0))
dif0 = l0["/USB_DM"] - l0["/USB_DP"]
lo, hi = 0.0, 3.0
for _ in range(60):
    mid = (lo + hi) / 2
    l = longitudes(construir(mid))
    if l["/USB_DP"] < l["/USB_DM"]:
        lo = mid
    else:
        hi = mid
H = round((lo + hi) / 2, 3)
PLAN = construir(H)
LON = longitudes(PLAN)

if __name__ == "__main__":
    print(f"sin meandro: D- {l0['/USB_DM']:.3f}  D+ {l0['/USB_DP']:.3f}  (D- más largo {dif0:+.3f} mm)")
    print(f"meandro h = {H} mm ⇒ D- {LON['/USB_DM']:.3f}  D+ {LON['/USB_DP']:.3f}  dif {LON['/USB_DM']-LON['/USB_DP']:+.4f} mm")
    for e in PLAN:
        if e[0] == "via":
            print("  vía", e[1], e[2])
        else:
            print(" ", e[0], e[1], f"w{e[3]}", [(round(x, 3), round(y, 3)) for x, y in e[2]])

    if "--copia" in sys.argv:
        import pcbnew
        ruta = sys.argv[sys.argv.index("--copia") + 1]
        b = pcbnew.LoadBoard(ruta)
        capa = {"F": pcbnew.F_Cu, "B": pcbnew.B_Cu}
        iu = lambda v: int(round(v * 1e6))
        n = 0
        for e in PLAN:
            if e[0] == "via":
                v = pcbnew.PCB_VIA(b)
                v.SetPosition(pcbnew.VECTOR2I(iu(e[2][0]), iu(e[2][1])))
                v.SetViaType(pcbnew.VIATYPE_THROUGH)
                v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                try:
                    v.SetWidth(iu(VIA[0]))
                except TypeError:
                    v.SetWidth(pcbnew.F_Cu, iu(VIA[0]))
                v.SetDrill(iu(VIA[1]))
                v.SetNet(b.FindNet(e[1]))
                v.SetLocked(True)
                b.Add(v); n += 1
                continue
            red, c, pts, w = e
            for p, q in zip(pts, pts[1:]):
                if math.hypot(q[0] - p[0], q[1] - p[1]) < 1e-4:
                    continue
                t = pcbnew.PCB_TRACK(b)
                t.SetStart(pcbnew.VECTOR2I(iu(p[0]), iu(p[1]))); t.SetEnd(pcbnew.VECTOR2I(iu(q[0]), iu(q[1])))
                t.SetWidth(iu(w)); t.SetLayer(capa[c]); t.SetNet(b.FindNet(red)); t.SetLocked(True)
                b.Add(t); n += 1
        b.Save(ruta)
        print("copia:", n, "objetos añadidos ->", ruta)

    if "--apply" in sys.argv:
        from kipy import KiCad
        from kipy.board_types import Track, Via
        from kipy.geometry import Vector2
        from kipy.proto.board.board_types_pb2 import BoardLayer
        from kipy.util.units import from_mm
        k = KiCad().get_board()
        nets = {n.name: n for n in k.get_nets()}
        capa = {"F": BoardLayer.BL_F_Cu, "B": BoardLayer.BL_B_Cu}
        ya = [t for t in list(k.get_tracks()) + list(k.get_vias())
              if t.net.name in ("/USB_DP", "/USB_DM") and t.layer == BoardLayer.BL_B_Cu] if False else []
        nuevas = []
        for e in PLAN:
            if e[0] == "via":
                v = Via(); v.position = Vector2.from_xy_mm(*e[2]); v.diameter = from_mm(VIA[0])
                v.drill_diameter = from_mm(VIA[1]); v.net = nets[e[1]]; v.locked = True; nuevas.append(v)
                continue
            red, c, pts, w = e
            for p, q in zip(pts, pts[1:]):
                if math.hypot(q[0] - p[0], q[1] - p[1]) < 1e-4:
                    continue
                t = Track(); t.start = Vector2.from_xy_mm(*p); t.end = Vector2.from_xy_mm(*q)
                t.width = from_mm(w); t.layer = capa[c]; t.net = nets[red]; t.locked = True; nuevas.append(t)
        c = k.begin_commit()
        try:
            creados = k.create_items(nuevas)
        except Exception:
            k.drop_commit(c)
            raise
        k.push_commit(c, "Par USB U102 -> U201 (usb_par.py)")
        print("en vivo:", len(nuevas), "objetos creados")
