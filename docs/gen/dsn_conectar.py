"""Normaliza el cableado FIJO de un DSN para que Freerouting lo vea conectado como lo ve KiCad.

Freerouting sólo une un tramo a un pin/vía si su EXTREMO cae EXACTAMENTE en el centro del pin/vía, y dos tramos sólo
si comparten extremo. KiCad, en cambio, da por conectado todo lo que se solapa. Además el exportador de KiCad junta
tramos seguidos en polilíneas (un pad en un vértice intermedio queda «suelto») y redondea los tramos a 1 µm mientras
los pines quedan con 0,5 µm (J101). Esto (sólo en el DSN; el PCB no se toca):
  1. parte cada polilínea en tramos de 2 puntos;
  2. para cada tramo que toca un pad/vía de su red: si un extremo cae dentro, tramito fijo extremo→centro; si sólo lo
     cruza, se parte el tramo en la proyección del centro y tramito de ahí al centro;
  3. uniones en T (extremo que cae sobre el cuerpo de otro tramo de la misma red y capa): se parte el otro tramo.
Uso como módulo: normalizar(texto_dsn, board_pcbnew) -> (texto_nuevo, informe)
"""
import math
import re

import pcbnew

TOL = 0.05          # µm: dos puntos son el mismo


def _fmt(v):
    r = round(v, 1)
    return f"{r:.1f}".rstrip("0").rstrip(".") if r != int(r) else str(int(r))


def _igual(p, q):
    return abs(p[0] - q[0]) <= TOL and abs(p[1] - q[1]) <= TOL


def _proy(c, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return 0.0, a
    t = ((c[0] - a[0]) * dx + (c[1] - a[1]) * dy) / L2
    t = max(0.0, min(1.0, t))
    return t, (a[0] + t * dx, a[1] + t * dy)


def leer(texto):
    i = texto.index("(wiring")
    segs, vias = [], []
    for m in re.finditer(r'\(wire\s+\(path (\S+) ([\d.]+)\s+([-\d.\s]+)\)\s*\(net ("[^"]+"|\S+)\)\s*\(type (\w+)\)\)',
                         texto[i:]):
        v = [float(x) for x in m.group(3).split()]
        pts = [(v[k], v[k + 1]) for k in range(0, len(v), 2)]
        for a, b in zip(pts, pts[1:]):
            segs.append({"capa": m.group(1), "w": float(m.group(2)), "a": a, "b": b, "red": m.group(4), "tipo": m.group(5)})
    for m in re.finditer(r'\(via ("[^"]+"|\S+)\s+([-\d.]+) ([-\d.]+)\s*\(net ("[^"]+"|\S+)\)\s*\(type (\w+)\)\)', texto[i:]):
        vias.append({"ps": m.group(1), "c": (float(m.group(2)), float(m.group(3))), "red": m.group(4), "tipo": m.group(5)})
    return segs, vias


def normalizar(texto, b):
    segs, vias = leer(texto)
    n_poli = len(segs)
    capas_cu = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}
    nm = lambda p: pcbnew.VECTOR2I(int(round(p[0] * 1000)), int(round(-p[1] * 1000)))   # DSN µm (y arriba) -> nm
    # pads de KiCad con su centro en coordenadas DSN
    pads = []
    for f in b.Footprints():
        for p in f.Pads():
            if not p.GetNetname():
                continue
            c = p.GetPosition()
            pads.append({"pad": p, "c": (c.x / 1000, -c.y / 1000), "red": p.GetNetname(),
                         "nombre": f"{f.GetReference()}-{p.GetNumber()}"})
    clave = lambda r: r.strip('"')
    nuevos, partidos, conectores = [], 0, []

    def dentro_pad(pd, capa, q, w=0.0):
        """¿El cobre de un tramo de ancho w con eje en q pisa el pad? (KiCad lo da por conectado)."""
        lid = capas_cu[capa]
        if not pd["pad"].IsOnLayer(lid):
            return False
        acc = int(round(w / 2 * 1000))
        try:
            return pd["pad"].HitTest(nm(q), acc, lid)
        except TypeError:
            return pd["pad"].HitTest(nm(q), acc)

    def toca(s, centro, dentro):
        """Devuelve el punto del tramo s que se unirá al centro, partiendo s si hace falta (o None)."""
        nonlocal partidos
        for e in (s["a"], s["b"]):
            if dentro(e):
                return e
        for k in range(1, 40):
            q = (s["a"][0] + (s["b"][0] - s["a"][0]) * k / 40, s["a"][1] + (s["b"][1] - s["a"][1]) * k / 40)
            if dentro(q):
                _, pq = _proy(centro, s["a"], s["b"])
                if not dentro(pq):
                    pq = q
                pq = (round(pq[0], 1), round(pq[1], 1))
                s2 = dict(s, a=pq)
                s["b"] = pq
                nuevos.append(s2)
                partidos += 1
                return pq
        return None

    # 2. pads y vías
    for pd in pads:
        for s in segs + nuevos:
            if clave(s["red"]) != pd["red"] or s["capa"] not in capas_cu:
                continue
            e = toca(s, pd["c"], lambda q: dentro_pad(pd, s["capa"], q, s["w"]))
            if e is not None and not _igual(e, pd["c"]):
                conectores.append(dict(s, a=e, b=pd["c"], tipo="fix"))
    for v in vias:
        r = 300.0   # radio de la vía 0,6
        for s in segs + nuevos:
            if s["red"] != v["red"]:
                continue
            e = toca(s, v["c"], lambda q: math.hypot(q[0] - v["c"][0], q[1] - v["c"][1]) < r + s["w"] / 2)
            if e is not None and not _igual(e, v["c"]):
                conectores.append(dict(s, a=e, b=v["c"], tipo="fix"))
    # pads de la misma red que se tocan (J101: A4-B9, B4-A9): tramito de centro a centro si cabe dentro de los dos
    n_pp = 0
    for i, p1 in enumerate(pads):
        for p2 in pads[i + 1:]:
            if p1["red"] != p2["red"] or _igual(p1["c"], p2["c"]):
                continue
            for capa, lid in capas_cu.items():
                if not (p1["pad"].IsOnLayer(lid) and p2["pad"].IsOnLayer(lid)):
                    continue
                if math.hypot(p1["c"][0] - p2["c"][0], p1["c"][1] - p2["c"][1]) > 3000:
                    continue
                w = 100.0
                pasos = [(p1["c"][0] + (p2["c"][0] - p1["c"][0]) * k / 20, p1["c"][1] + (p2["c"][1] - p1["c"][1]) * k / 20)
                         for k in range(21)]
                if all(dentro_pad(p1, capa, q, w) or dentro_pad(p2, capa, q, w) for q in pasos) and \
                        all(dentro_pad(p1, capa, q) or dentro_pad(p2, capa, q) for q in pasos):
                    red = next((s["red"] for s in segs if clave(s["red"]) == p1["red"]), None) or \
                        (p1["red"] if re.fullmatch(r"[\w/.+-]+", p1["red"]) else f'"{p1["red"]}"')
                    conectores.append({"capa": capa, "w": w, "a": p1["c"], "b": p2["c"], "red": red, "tipo": "fix"})
                    n_pp += 1
                    break
    # 3. uniones en T (una sola pasada: se reúnen los cortes de cada tramo y luego se parte)
    base = segs + nuevos + conectores
    cortes = {}            # id(o) -> lista de (t, q)
    extra = []
    d = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    for s in base:
        for e in (s["a"], s["b"]):
            for o in base:
                if o is s or o["red"] != s["red"] or o["capa"] != s["capa"]:
                    continue
                if _igual(e, o["a"]) or _igual(e, o["b"]):
                    continue
                cerca = [x for x in (o["a"], o["b"]) if d(e, x) <= 1.0]
                if cerca:                                   # casi en el extremo de o: tramito hasta él
                    extra.append(dict(s, a=e, b=cerca[0], tipo="fix"))
                    continue
                t, q = _proy(e, o["a"], o["b"])
                if not (0 < t < 1) or d(e, q) > (o["w"] + s["w"]) / 2:
                    continue
                q = (round(q[0], 1), round(q[1], 1))
                if d(q, o["a"]) <= 1.0 or d(q, o["b"]) <= 1.0:
                    continue
                cortes.setdefault(id(o), []).append((t, q))
                if not _igual(e, q):
                    extra.append(dict(s, a=e, b=q, tipo="fix"))
    todos = []
    for o in base:
        cs = sorted(set(cortes.get(id(o), [])))
        if not cs:
            todos.append(o)
            continue
        pts = [o["a"]] + [q for _, q in cs] + [o["b"]]
        for a, c in zip(pts, pts[1:]):
            if not _igual(a, c):
                todos.append(dict(o, a=a, b=c))
        partidos += len(cs)
    todos += extra
    # reescribir el bloque wiring
    lineas, vistos = [], set()
    for s in todos:
        if _igual(s["a"], s["b"]):
            continue
        k = (s["capa"], s["red"], s["w"]) + tuple(sorted([(round(s["a"][0], 1), round(s["a"][1], 1)),
                                                          (round(s["b"][0], 1), round(s["b"][1], 1))]))
        if k in vistos:
            continue
        vistos.add(k)
        lineas.append(f'    (wire (path {s["capa"]} {_fmt(s["w"])}  {_fmt(s["a"][0])} {_fmt(s["a"][1])}  '
                      f'{_fmt(s["b"][0])} {_fmt(s["b"][1])})(net {s["red"]})(type {s["tipo"]}))')
    for v in vias:
        lineas.append(f'    (via {v["ps"]}  {_fmt(v["c"][0])} {_fmt(v["c"][1])} (net {v["red"]})(type {v["tipo"]}))')
    i = texto.index("(wiring")
    n = 0
    for k in range(i, len(texto)):
        n += {"(": 1, ")": -1}.get(texto[k], 0)
        if n == 0:
            fin = k + 1
            break
    nuevo = texto[:i] + "(wiring\n" + "\n".join(lineas) + "\n  )" + texto[fin:]
    informe = {"tramos_de_2_puntos": n_poli, "partidos": partidos, "pad_a_pad": n_pp,
               "tramitos_añadidos": len(lineas) - len(vias) - n_poli - partidos, "tramos_final": len(lineas) - len(vias)}
    return nuevo, informe


def emular(texto, b):
    """Componentes conexas por red según la regla de Freerouting (extremos exactos en centros / extremos comunes)."""
    segs, vias = leer(texto)
    i = texto.index("(network")
    redes = {}
    for m in re.finditer(r'\(net ("[^"]+"|\S+)\s+\(pins ([^)]*)\)', texto[i:]):
        redes[m.group(1).strip('"')] = m.group(2).split()
    padpos = {}
    for f in b.Footprints():
        for p in f.Pads():
            c = p.GetPosition()
            padpos.setdefault(f"{f.GetReference()}-{p.GetNumber()}", []).append((c.x / 1000, -c.y / 1000))
    padre = {}

    def raiz(x):
        while padre.setdefault(x, x) != x:
            padre[x] = padre[padre[x]]
            x = padre[x]
        return x

    def unir(a, c):
        padre[raiz(a)] = raiz(c)

    clave = lambda p: (round(p[0], 1), round(p[1], 1))
    res = {}
    for red, pins in redes.items():
        nodos = {}
        for pn in pins:
            for c in padpos.get(pn, []):
                nodos.setdefault(clave(c), []).append(("pin", pn))
        for v in vias:
            if v["red"].strip('"') == red:
                nodos.setdefault(clave(v["c"]), []).append(("via", v["c"]))
        for s in segs:
            if s["red"].strip('"') == red:
                unir(("pt", red, clave(s["a"])), ("pt", red, clave(s["b"])))
        for k, lst in nodos.items():
            for it in lst:
                unir(("pt", red, k), it)
        comps = {raiz(("pin", pn)) for pn in pins}
        res[red] = len(comps)
    return res
