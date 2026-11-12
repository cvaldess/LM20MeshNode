# Kit de dibujo de las hojas SVG de nrf54lm20-meshnode. Mismo estilo que ai_instruments/docs/gen/simbolos.py
# (copiado y ampliado: inductores, diodos, MOSFET, zumbador, bloques del diagrama). Uso:
#   from svgkit import *;  nueva(W, H);  ...dibujar...;  guardar(ruta)
from xml.sax.saxutils import escape

o = []


def add(s):
    o.append(s)


def T(x, y, s, cls="t", anchor="start", extra=""):
    add(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def P(pts, cls="w"):
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    add(f'<path d="{d}" class="{cls}"/>')


def dot(x, y):
    add(f'<circle cx="{x}" cy="{y}" r="3.2" fill="#263238"/>')


def gnd(x, y):
    P([(x, y), (x, y + 7)])
    for dx, dy in ((9, 7), (6, 11), (3, 15)):
        P([(x - dx, y + dy), (x + dx, y + dy)])


def _side(x, m, ref, val, side, dx):
    if side == "r":
        T(x + dx, m - 2, ref, "ref"); T(x + dx, m + 11, val, "val")
    else:
        T(x - dx, m - 2, ref, "ref", "end"); T(x - dx, m + 11, val, "val", "end")


def res_v(x, y, ref, val, L=50, side="r", cls="w", sym="sym"):
    m = y + L / 2
    P([(x, y), (x, m - 13)], cls); P([(x, m + 13), (x, y + L)], cls)
    add(f'<rect x="{x-5}" y="{m-13}" width="10" height="26" class="{sym}"/>')
    _side(x, m, ref, val, side, 9)


def res_h(x, y, ref, val, L=60, cls="w", sym="sym"):
    m = x + L / 2
    P([(x, y), (m - 13, y)], cls); P([(m + 13, y), (x + L, y)], cls)
    add(f'<rect x="{m-13}" y="{y-5}" width="26" height="10" class="{sym}"/>')
    T(m, y - 9, f"{ref} {val}", "ref", "middle")


def cap_v(x, y, ref, val, L=44, side="r", cls="w", pc="plate"):
    m = y + L / 2
    P([(x, y), (x, m - 3)], cls); P([(x, m + 3), (x, y + L)], cls)
    P([(x - 9, m - 3), (x + 9, m - 3)], pc); P([(x - 9, m + 3), (x + 9, m + 3)], pc)
    _side(x, m, ref, val, side, 12)


def cap_h(x, y, ref, val, L=60, pc="plate"):
    m = x + L / 2
    P([(x, y), (m - 3, y)]); P([(m + 3, y), (x + L, y)])
    P([(m - 3, y - 9), (m - 3, y + 9)], pc); P([(m + 3, y - 9), (m + 3, y + 9)], pc)
    T(m, y - 13, f"{ref} {val}", "ref", "middle")


def ind_h(x, y, ref, val, L=70, cls="pw"):
    a, b, n = x + 11, x + L - 11, 4
    w = (b - a) / n
    P([(x, y), (a, y)], cls); P([(b, y), (x + L, y)], cls)
    d = f"M{a},{y}" + "".join(f" a{w/2},{w/2} 0 0 1 {w},0" for _ in range(n))
    add(f'<path d="{d}" class="w"/>')
    T(x + L / 2, y - 14, f"{ref} {val}", "ref", "middle")


def ind_v(x, y, ref, val, L=60, side="r", cls="w"):
    a, b, n = y + 9, y + L - 9, 4
    h = (b - a) / n
    P([(x, y), (x, a)], cls); P([(x, b), (x, y + L)], cls)
    d = f"M{x},{a}" + "".join(f" a{h/2},{h/2} 0 0 1 0,{h}" for _ in range(n))
    add(f'<path d="{d}" class="w"/>')
    _side(x, y + L / 2, ref, val, side, 12)


def diode_v(x, y, ref, val, L=50, side="r", kind="d"):
    """Cátodo ARRIBA. kind: d (rectificador/flyback) · tvs (unidireccional ESD)."""
    m = y + L / 2
    P([(x, y), (x, m - 7)]); P([(x, m + 7), (x, y + L)])
    add(f'<path d="M{x-8},{m+7} L{x+8},{m+7} L{x},{m-7} Z" class="sym"/>')
    if kind == "tvs":
        P([(x - 11, m - 10), (x - 8, m - 7), (x + 8, m - 7), (x + 11, m - 4)], "plate")
    else:
        P([(x - 8, m - 7), (x + 8, m - 7)], "plate")
    _side(x, m, ref, val, side, 14)


def led_v(x, y, ref, val, L=44, side="r"):
    """LED vertical: ánodo arriba, cátodo abajo."""
    m = y + L / 2
    P([(x, y), (x, m - 7)]); P([(x, m + 7), (x, y + L)])
    add(f'<path d="M{x-8},{m-7} L{x+8},{m-7} L{x},{m+7} Z" class="sym"/>')
    P([(x - 8, m + 7), (x + 8, m + 7)])
    for dy in (-3, 4):
        P([(x + 10, m + dy), (x + 17, m + dy - 7)]); P([(x + 13, m + dy - 7), (x + 17, m + dy - 7), (x + 17, m + dy - 3)])
    _side(x, m, ref, val, side, 22 if side == "r" else 12)


def sw_v(x, y, ref, val, L=56, side="r"):
    """Pulsador NA vertical entre y e y+L."""
    m = y + L / 2
    P([(x, y), (x, m - 9)]); P([(x, m + 9), (x, y + L)])
    for cy in (m - 9, m + 9):
        add(f'<circle cx="{x}" cy="{cy}" r="2.6" fill="#fff" stroke="#263238" stroke-width="1.5"/>')
    P([(x - 10, m - 13), (x - 10, m + 13)], "plate")
    P([(x - 10, m), (x - 19, m)]); P([(x - 19, m - 6), (x - 19, m + 6)])
    _side(x, m, ref, val, side, 12)


def nmos(x, y, ref, val):
    """N-MOS: drenador arriba (x, y), surtidor abajo (x, y+60), puerta a la izquierda (x-34, y+30)."""
    P([(x, y), (x, y + 18), (x - 12, y + 18)]); P([(x, y + 60), (x, y + 42), (x - 12, y + 42)])
    P([(x - 12, y + 14), (x - 12, y + 46)], "plate"); P([(x - 18, y + 18), (x - 18, y + 42)], "plate")
    P([(x - 34, y + 30), (x - 18, y + 30)])
    add(f'<path d="M{x-12},{y+42} l7,-4 v8 z" fill="#263238"/>')
    T(x + 8, y + 24, ref, "ref"); T(x + 8, y + 37, val, "val")
    T(x + 4, y + 10, "D", "pn"); T(x + 4, y + 56, "S", "pn"); T(x - 34, y + 25, "G", "pn")


def buzzer(x, y, ref, val):
    """Zumbador: + arriba (x, y), − abajo (x, y+54)."""
    P([(x, y), (x, y + 14)]); P([(x, y + 40), (x, y + 54)])
    add(f'<rect x="{x-14}" y="{y+14}" width="28" height="26" rx="13" class="sym"/>')
    add(f'<path d="M{x-7},{y+33} a7,7 0 0 1 14,0" class="w"/>')
    T(x - 6, y + 11, "+", "pn", "end")
    T(x + 20, y + 25, ref, "ref"); T(x + 20, y + 38, val, "val")


def label(x, y, name, kind="sig", anchor="start"):
    w = len(name) * 7.4 + 12
    cls = {"pwr": "lab_p", "sig": "lab_s", "loc": "lab_l"}[kind]
    tcls = {"pwr": "lp", "sig": "lsb", "loc": "ll"}[kind]
    x0 = {"start": x, "end": x - w, "middle": x - w / 2}[anchor]
    add(f'<rect x="{x0}" y="{y-9}" width="{w}" height="18" rx="3" class="{cls}"/>')
    T(x0 + w / 2, y + 4.5, name, tcls, "middle")
    return w


def tp(x, y, ref, side="r"):
    add(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff" stroke="#263238" stroke-width="1.6"/>')
    T(x + 9 if side == "r" else x - 9, y + 4, ref, "ref", "start" if side == "r" else "end")


def nc(x, y):
    P([(x - 5, y - 5), (x + 5, y + 5)], "nc"); P([(x - 5, y + 5), (x + 5, y - 5)], "nc")


def ic(x, y, w, h, ref, part, left, right, cls="sym", stub=20):
    """left/right: [(num, nombre, y)]; devuelve {num: (x_extremo, y)}."""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" class="{cls}"/>')
    T(x + w / 2, y - 22, ref, "icref", "middle")
    T(x + w / 2, y - 8, part, "val", "middle")
    ends = {}
    for num, name, py in left:
        P([(x - stub, py), (x, py)])
        T(x - 4, py - 4, str(num), "pn", "end"); T(x + 6, py + 4, name, "pname")
        ends[str(num)] = (x - stub, py)
    for num, name, py in right:
        P([(x + w, py), (x + w + stub, py)])
        T(x + w + 4, py - 4, str(num), "pn"); T(x + w - 6, py + 4, name, "pname", "end")
        ends[str(num)] = (x + w + stub, py)
    return ends


def frame(x, y, w, h, title, cls="frame"):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" class="{cls}"/>')
    T(x + 12, y + 20, title, "ft")


def notes(x, y, lines, cls="ts", dy=15):
    for i, s in enumerate(lines):
        if isinstance(s, tuple):
            T(x, y + i * dy, s[0], s[1])
        else:
            T(x, y + i * dy, s, cls)


def tabla(x, y, w, cols, hdr, rows, dy=18.5, mono=(0,)):
    for c, h in zip(cols, hdr):
        T(c, y, h, "th")
    P([(x + 10, y + 6), (x + w - 10, y + 6)], "thin")
    for i, r in enumerate(rows):
        yy = y + 24 + i * dy
        if i % 2 == 1:
            add(f'<rect x="{x+8}" y="{yy-13}" width="{w-16}" height="{dy}" fill="#f1f5f9"/>')
        for k, (c, s) in enumerate(zip(cols, r)):
            T(c, yy, s, "tdm" if k in mono else "td")
    return y + 24 + len(rows) * dy


def blk(x, y, w, h, title, lines=(), cls="blk"):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="{cls}"/>')
    T(x + w / 2, y + 20, title, "bt", "middle")
    for i, s in enumerate(lines):
        T(x + w / 2, y + 38 + i * 15, s, "bs", "middle")


def arrow(pts, cls="sg", label_=None, at=None):
    P(pts, cls)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    if x2 != x1:
        s = 1 if x2 > x1 else -1
        add(f'<path d="M{x2},{y2} l{-9*s},-5 v10 z" class="ah_{cls}"/>')
    else:
        s = 1 if y2 > y1 else -1
        add(f'<path d="M{x2},{y2} l-5,{-9*s} h10 z" class="ah_{cls}"/>')
    if label_:
        T(at[0], at[1], label_, "al", "middle")


def nueva(W, H, titulo, sub):
    o.clear()
    add(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">
<defs><style>
 .frame {{ fill:#fbfcfe; stroke:#90a4ae; stroke-width:1.3; }}
 .framep {{ fill:#fffaf0; stroke:#b7791f; stroke-width:1.5; stroke-dasharray:6 4; }}
 .ft {{ font-size:13.5px; font-weight:700; fill:#102a43; }}
 .sym {{ fill:#ffffff; stroke:#263238; stroke-width:1.6; }}
 .symp {{ fill:#fff4d6; stroke:#b7791f; stroke-width:1.6; stroke-dasharray:5 3; }}
 .dnp {{ fill:#ffffff; stroke:#90a4ae; stroke-width:1.4; stroke-dasharray:4 3; }}
 .w {{ stroke:#263238; stroke-width:1.5; fill:none; }}
 .thin {{ stroke:#90a4ae; stroke-width:1.2; fill:none; }}
 .pw {{ stroke:#c62828; stroke-width:2.4; fill:none; }}
 .sg {{ stroke:#1565c0; stroke-width:1.8; fill:none; }}
 .rf {{ stroke:#2e7d32; stroke-width:2.6; fill:none; }}
 .df {{ stroke:#6a1b9a; stroke-width:2.0; fill:none; }}
 .gn {{ stroke:#ef6c00; stroke-width:2.2; fill:none; }}
 .ah_sg {{ fill:#1565c0; }} .ah_pw {{ fill:#c62828; }} .ah_rf {{ fill:#2e7d32; }} .ah_df {{ fill:#6a1b9a; }} .ah_gn {{ fill:#ef6c00; }}
 .plate {{ stroke:#263238; stroke-width:2.4; fill:none; }}
 .plated {{ stroke:#90a4ae; stroke-width:2.4; fill:none; stroke-dasharray:3 2; }}
 .nc {{ stroke:#c62828; stroke-width:1.8; }}
 .blk {{ fill:#eef4fb; stroke:#5c7a99; stroke-width:1.6; }}
 .blkp {{ fill:#fdecea; stroke:#c62828; stroke-width:1.6; }}
 .blkr {{ fill:#e8f5e9; stroke:#2e7d32; stroke-width:1.6; }}
 .blkg {{ fill:#fff3e0; stroke:#ef6c00; stroke-width:1.6; }}
 .bt {{ font-size:14px; font-weight:700; fill:#102a43; }}
 .bs {{ font-size:11.5px; fill:#37474f; }}
 .al {{ font-size:11px; fill:#102a43; font-weight:600; }}
 .t {{ font-size:13px; fill:#212121; }}
 .ts {{ font-size:11.5px; fill:#455a64; }}
 .tp {{ font-size:11.5px; fill:#8a5a00; font-weight:600; }}
 .tw {{ font-size:11.5px; fill:#b71c1c; font-weight:600; }}
 .tb {{ font-size:13px; font-weight:700; fill:#102a43; }}
 .h1 {{ font-size:22px; font-weight:700; fill:#102a43; }}
 .h2 {{ font-size:13px; fill:#455a64; }}
 .ref {{ font-size:11.5px; font-weight:700; fill:#102a43; }}
 .val {{ font-size:11px; fill:#37474f; }}
 .icref {{ font-size:13px; font-weight:700; fill:#102a43; }}
 .pn {{ font-size:10px; fill:#8d6e63; font-weight:600; }}
 .pname {{ font-size:11px; fill:#102a43; }}
 .lp {{ font-size:11.5px; fill:#c62828; font-weight:700; }}
 .lsb {{ font-size:11.5px; fill:#1565c0; font-weight:700; }}
 .ll {{ font-size:11.5px; fill:#4e342e; font-weight:700; }}
 .lab_p {{ fill:#ffebee; stroke:#c62828; stroke-width:1.2; }}
 .lab_s {{ fill:#e3f2fd; stroke:#1565c0; stroke-width:1.2; }}
 .lab_l {{ fill:#efebe9; stroke:#8d6e63; stroke-width:1.2; }}
 .th {{ font-size:11.5px; font-weight:700; fill:#102a43; }}
 .td {{ font-size:11px; fill:#263238; }}
 .tdm {{ font-size:11px; fill:#263238; font-family:Consolas, monospace; }}
</style></defs>
<rect width="{W}" height="{H}" fill="#ffffff"/>''')
    T(24, 36, titulo, "h1")
    T(24, 56, sub, "h2")


def guardar(ruta):
    add("</svg>")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print("ok", ruta)


# ---- helpers de hoja (leyenda, IC por filas, etiquetas en cada pata, filas de condensadores)
def leyenda(x, y):
    label(x, y, "3V3", "pwr"); T(x + 46, y + 4, "alimentación global", "ts")
    label(x + 185, y, "I2C_SDA", "sig"); T(x + 260, y + 4, "jerárquica (otra hoja)", "ts")
    label(x + 405, y, "SW1", "loc"); T(x + 448, y + 4, "local de la hoja", "ts")
    add(f'<rect x="{x+560}" y="{y-9}" width="34" height="18" rx="3" class="dnp"/>'); T(x + 600, y + 4, "DNP / opcional", "ts")
    add(f'<rect x="{x+705}" y="{y-9}" width="34" height="18" rx="3" class="symp"/>'); T(x + 745, y + 4, "pendiente de confirmar", "ts")


def pin_labels(ends, spec):
    """spec: {num: (nombre, tipo)} tipo ∈ pwr/sig/loc/gnd/nc. Etiqueta al final del stub de cada pata."""
    for num, (name, kind) in spec.items():
        x, y = ends[str(num)]
        if kind == "nc":
            nc(x, y)
        elif kind == "gnd":
            gx = x + (-10 if ends_is_left(ends, num) else 10)
            P([(x, y), (gx, y)])
            gnd(gx, y)
        else:
            label(x, y, name, kind, "end" if ends_is_left(ends, num) else "start")


_LEFT = set()


def ends_is_left(ends, num):
    return (id(ends), str(num)) in _LEFT


def ic2(x, y, w, ref, part, left, right, pitch=24, top_pad=20, **kw):
    """IC con filas: listas de (num, nombre) o None (hueco). Devuelve los extremos."""
    rows = max(len(left), len(right))
    h = top_pad * 2 + (rows - 1) * pitch
    lp = [(n, nm, y + top_pad + i * pitch) for i, e in enumerate(left) if e for n, nm in [e]]
    rp = [(n, nm, y + top_pad + i * pitch) for i, e in enumerate(right) if e for n, nm in [e]]
    ends = ic(x, y, w, h, ref, part, lp, rp, **kw)
    for n, _, _ in lp:
        _LEFT.add((id(ends), str(n)))
    return ends, h


def conn_l(x, y, ref, part, pins, pitch=24, w=150, **kw):
    """Conector con patas a la DERECHA (cuerpo a la izquierda)."""
    return ic2(x, y, w, ref, part, [], pins, pitch, **kw)


def caps_to_gnd(x, y, net, kind, items, dx=62, L=44):
    """Fila de condensadores de 'net' a GND: etiqueta arriba a la izquierda, raíl horizontal."""
    label(x, y, net, kind, "end")
    x0 = x + 10
    xe = x0 + dx * (len(items) - 1) + 10
    P([(x, y), (xe, y)], "w")
    for i, (ref, val) in enumerate(items):
        cx = x0 + 10 + i * dx
        if i:
            dot(cx, y)
        cap_v(cx, y, ref, val, L)
        gnd(cx, y + L)


