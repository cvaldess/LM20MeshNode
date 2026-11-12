# Lee símbolos de KiCad (.kicad_sym o los lib_symbols embebidos en un .kicad_sch) y calcula dónde cae cada pata de un
# símbolo colocado y hacia dónde debe salir su etiqueta. Copiado de ai_instruments/docs/gen (09-11-2026).
import math
import re


def parse(s):
    """s-expresión → listas anidadas (las cadenas entre comillas quedan como str con prefijo '"')."""
    tok = re.findall(r'"(?:[^"\\]|\\.)*"|[()]|[^\s()"]+', s)
    st = [[]]
    for t in tok:
        if t == "(":
            st.append([])
        elif t == ")":
            x = st.pop()
            st[-1].append(x)
        else:
            st[-1].append(t)
    return st[0][0]


def uq(t):
    return t[1:-1] if isinstance(t, str) and t.startswith('"') else t


def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def lib_pins(symbols, name):
    """{nombre: [(número, nombre_pata, tipo, x, y, ángulo, unidad)]} de un símbolo, siguiendo 'extends'."""
    sym = symbols[name]
    ext = find(sym, "extends")
    base = symbols[uq(ext[0][1])] if ext else sym
    out = []
    for sub in find(base, "symbol"):
        m = re.search(r"_(\d+)_(\d+)$", uq(sub[1]))
        unit = int(m.group(1)) if m else 0
        for p in find(sub, "pin"):
            at = find(p, "at")[0]
            num = uq(find(p, "number")[0][1])
            nm = uq(find(p, "name")[0][1])
            out.append((num, nm, p[1], float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0, unit))
    return out


def load_lib(path):
    root = parse(open(path, encoding="utf-8").read())
    return {uq(s[1]): s for s in find(root, "symbol")}


def rot(dx, dy, r):
    for _ in range(int(round(r / 90)) % 4):
        dx, dy = dy, -dx
    return dx, dy


def place_pins(pins, X, Y, r, unit=1):
    """[(número, x, y, dirección de la etiqueta en grados KiCad: 0 E, 90 N, 180 O, 270 S)] de un símbolo colocado."""
    res = []
    for num, nm, typ, px, py, a, u in pins:
        if u not in (0, unit):
            continue
        dx, dy = rot(px, -py, r)
        ox, oy = -math.cos(math.radians(a)), math.sin(math.radians(a))   # hacia fuera, en pantalla
        ox, oy = rot(ox, oy, r)
        d = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}[(round(ox), round(oy))]
        res.append((num, round(X + dx, 3), round(Y + dy, 3), d, typ))
    return res
