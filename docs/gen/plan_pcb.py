"""Primera colocación del PCB de nrf54lm20-meshnode, según el croquis del usuario (09-11-2026):

    antena BLE (por fuera del PCB)
    ME54BS13 -- SWD
    E22 -- U.FL
    U.FL -- E108 -- ↑        (botones ↑ OK ↓ en el canto derecho)
    Buzzer -- BATT
    SHT -- IMU
    cabeza del OLED          (OLED en la cara INFERIOR, a lo largo del PCB, pines junto al USB, extremo hacia la antena)
    nPM1300 -- ON/OFF
    USB

Todo en la cara superior (salvo el OLED). Placa rectangular con esquinas redondeadas y 4 agujeros M2 NPTH en las
esquinas. Coordenadas relativas a la esquina superior izquierda del contorno (X0, Y0). Comprueba solapes de courtyard
(rectángulos girados 0/90/180/270) y que todo quede dentro del contorno. Escribe plan_pcb.json.
Uso: python plan_pcb.py <dir_salida>"""
import itertools
import json
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
X0, Y0 = 100.0, 60.0          # esquina superior izquierda del contorno en el PCB
W, L, RADIO = 40.0, 97.0, 3.0  # ancho, largo, radio de las esquinas
HOLES = [(3.5, 3.5), (W - 3.5, 3.5), (3.5, L - 3.5), (W - 3.5, L - 3.5)]
HOLE_R = 2.6                   # radio libre alrededor del M2 (cabeza de tornillo ~3,8 mm + holgura)

LIBS = {"meshnode": os.path.join(HERE, "..", "..", "libs", "meshnode.pretty"),
        "easyeda2kicad": "C:/Users/cvald/Documents/KiCad/easyeda2kicad/easyeda2kicad.pretty"}
KFP = "C:/Program Files/KiCad/10.0/share/kicad/footprints/"

# ref → (x, y, giro)   (relativo al contorno; giro KiCad en grados, antihorario)
P = {
    # --- fila 1: ME54BS13 con la antena fuera del canto superior (línea de antena del módulo en y = 0) · SWD
    "U201": (14.0, 3.79, 0), "J201": (28.5, 6.6, 0),
    "C204": (4.2, 13.0, 90),                                    # VBUS del módulo (pata 9, lado izquierdo)
    "C201": (23.4, 12.8, 0), "FB201": (26.5, 12.8, 0), "C202": (29.6, 12.8, 0), "C203": (33.3, 12.8, 0),
    "TP201": (36.5, 9.2, 0), "TP202": (36.5, 11.6, 0), "TP203": (36.5, 14.0, 0),
    # --- fila 2: E22 girado 90 (SPI hacia el ME54BS13, ANT hacia el U.FL) · π · U.FL
    "U301": (16.0, 19.6, 90),
    "R301": (25.0, 16.0, 0), "R302": (25.0, 18.0, 0), "R303": (28.0, 17.0, 90),
    "C303": (24.2, 24.2, 90), "R304": (26.3, 22.1, 0), "C304": (28.4, 24.2, 90), "J301": (31.0, 22.1, 0),
    "C301": (6.0, 20.0, 90), "C302": (6.0, 24.0, 90),
    # --- fila 3: U.FL GNSS · E108 · botón ↑ (y OK, ↓ debajo, en el canto derecho)
    "U401": (19.0, 36.0, 0),
    "J401": (6.4, 41.9, 180), "C404": (9.6, 41.9, 0), "L401": (9.6, 44.3, 0), "TP401": (6.0, 31.0, 0),
    "R402": (29.6, 29.8, 0), "R403": (29.6, 31.8, 0), "R401": (29.6, 33.8, 0), "C403": (29.6, 35.8, 0),
    "C401": (32.8, 30.2, 90), "C402": (32.8, 33.6, 90), "R404": (32.8, 37.0, 90),
    "SW501": (38.06, 31.0, 270), "SW502": (38.06, 39.0, 270), "SW503": (38.06, 47.0, 270),
    # --- fila 4: zumbador (con su excitador) · batería
    "BZ501": (8.0, 52.0, 0), "D502": (8.6, 57.6, 0), "Q501": (14.6, 52.0, 0),
    "R504": (19.6, 50.6, 0), "R505": (19.6, 53.0, 0), "R506": (14.6, 56.4, 0), "R507": (14.6, 58.8, 0),
    "J102": (34.88, 55.0, 90), "RT101": (27.0, 58.6, 90),
    # --- fila 5: SHT41 en el canto izquierdo · IMU · (Qwiic y LED de estado: no estaban en el croquis)
    "U501": (2.6, 64.0, 0), "C501": (5.6, 64.0, 90), "R501": (9.0, 62.8, 0), "R502": (9.0, 65.2, 0),
    "C502": (12.4, 64.0, 90),
    "U502": (21.0, 64.0, 0), "C503": (25.6, 62.8, 0), "C504": (25.6, 65.2, 0),
    "J501": (37.65, 64.0, 90), "R503": (30.0, 62.8, 0), "D501": (30.0, 65.2, 0),
    # --- fila 6: cabeza del OLED (cara inferior, pines a lo largo del ancho)
    "DS501": (20.0, 72.0, None),          # se coloca a mano tras voltearla (ver aplicar)
    # --- fila 7: nPM1300 y su corte · ON/OFF en el canto derecho
    "U101": (13.0, 81.0, 0),
    "L101": (21.4, 79.2, 0), "C107": (24.6, 79.2, 90), "L102": (21.4, 83.0, 0), "C108": (24.6, 83.0, 90),
    "C103": (5.2, 77.6, 90), "C104": (5.2, 81.0, 90), "C105": (5.2, 84.4, 90), "C106": (8.2, 87.4, 0),
    "C110": (8.6, 76.6, 0), "R101": (12.0, 76.6, 0), "R102": (15.0, 76.6, 0),
    "C101": (12.0, 86.2, 0), "C102": (15.0, 86.2, 0),
    "R103": (28.4, 76.6, 0), "R104": (28.4, 78.8, 0), "C111": (28.4, 81.0, 0),
    "D102": (28.4, 83.6, 0), "D103": (28.4, 86.0, 0),
    "SW101": (38.06, 80.0, 270),
    "TP101": (32.6, 74.6, 0), "TP102": (32.6, 77.0, 0), "TP103": (32.6, 79.4, 0),
    "TP104": (32.6, 81.8, 0), "TP105": (32.6, 84.2, 0), "TP106": (32.6, 86.6, 0),
    # --- fila 8: USB-C al canto inferior (boca hacia abajo; borde de placa en y_local = +5,0) · ESD
    "J101": (20.0, L - 5.0, 0), "U102": (26.0, 89.6, 0), "D101": (12.0, 89.6, 0),
}
# OLED en B: tira de 4 pines (TH) en (20 ± 3,81, 72) ⇒ zona prohibida para piezas de arriba
OLED_PINS_TOP = (20.0 - 3.81 - 1.2, 72.0 - 1.2, 20.0 + 3.81 + 1.2, 72.0 + 1.2)


def footprint_ids():
    net = open(sys.argv[2], encoding="utf-8").read() if len(sys.argv) > 2 else None
    import re
    return dict(re.findall(r'\(comp\s+\(ref "([^"]+)"\).*?\(footprint "([^"]*)"\)', net, re.S))


def courtyard(fpid):
    lib, name = fpid.split(":")
    f = pcbnew.FootprintLoad(LIBS.get(lib, KFP + lib + ".pretty"), name)
    xs, ys = [], []
    for g in f.GraphicalItems():
        if g.GetLayer() == pcbnew.F_CrtYd:
            b = g.GetBoundingBox()
            xs += [b.GetLeft(), b.GetRight()]
            ys += [b.GetTop(), b.GetBottom()]
    if not xs:   # sin courtyard: pads
        for p in f.Pads():
            b = p.GetBoundingBox()
            xs += [b.GetLeft(), b.GetRight()]
            ys += [b.GetTop(), b.GetBottom()]
    m = pcbnew.ToMM
    return m(min(xs)), m(min(ys)), m(max(xs)), m(max(ys))


def rot_box(box, r):
    x1, y1, x2, y2 = box
    pts = [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
    out = []
    for x, y in pts:
        for _ in range(int(r // 90) % 4):   # 90 antihorario en pantalla: (x, y) → (y, −x)
            x, y = y, -x
        out.append((x, y))
    return min(p[0] for p in out), min(p[1] for p in out), max(p[0] for p in out), max(p[1] for p in out)


def main():
    out = sys.argv[1]
    fps = footprint_ids()
    assert set(fps) == set(P), (sorted(set(fps) - set(P)), sorted(set(P) - set(fps)))
    boxes = {}
    for ref, (x, y, r) in P.items():
        if r is None:
            continue
        bx = rot_box(courtyard(fps[ref]), r)
        boxes[ref] = (x + bx[0], y + bx[1], x + bx[2], y + bx[3])
    boxes["OLED_PINS"] = OLED_PINS_TOP
    fallos = 0
    for (a, A), (b, B) in itertools.combinations(boxes.items(), 2):
        if A[0] < B[2] - 1e-6 and B[0] < A[2] - 1e-6 and A[1] < B[3] - 1e-6 and B[1] < A[3] - 1e-6:
            fallos += 1
            print(f"✗ solape {a} {tuple(round(v, 2) for v in A)} con {b} {tuple(round(v, 2) for v in B)}")
    for ref, (x1, y1, x2, y2) in boxes.items():
        if ref == "U201":
            y1 = 0.0   # la antena sale del contorno a propósito
        if x1 < -0.01 or y1 < -0.01 or x2 > W + 0.2 or y2 > L + 0.2:
            fallos += 1
            print(f"✗ fuera del contorno: {ref} {tuple(round(v, 2) for v in (x1, y1, x2, y2))}")
        for hx, hy in HOLES:
            cx, cy = min(max(hx, x1), x2), min(max(hy, y1), y2)
            if (cx - hx) ** 2 + (cy - hy) ** 2 < HOLE_R ** 2:
                fallos += 1
                print(f"✗ {ref} invade el agujero ({hx}, {hy})")
    place = [{"reference": r, "x": round(X0 + x, 3), "y": round(Y0 + y, 3), "rotation": rr}
             for r, (x, y, rr) in sorted(P.items()) if rr is not None]
    json.dump({"placements": place, "outline": [X0, Y0, X0 + W, Y0 + L, RADIO],
               "holes": [[X0 + hx, Y0 + hy] for hx, hy in HOLES], "oled": [X0 + 20.0, Y0 + 72.0]},
              open(os.path.join(out, "plan_pcb.json"), "w"), indent=1)
    print(f"{len(place)} piezas · contorno {W}×{L} mm · {'sin solapes' if not fallos else str(fallos) + ' FALLOS'}")
    return fallos


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
