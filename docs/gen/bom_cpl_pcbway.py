"""BOM y centroid (CPL) para PCBWay, en el formato de Rpi3FanHatPlus.

BOM: "Designator","Qty","Manufacturer","Mfg Part #","Description/Value","Package/Footprint","LCSC Part #"
CPL: Ref,Val,Package,PosX,PosY,Rot,Side (mm, mismas coordenadas absolutas que los Gerber).
Fuera de los dos: piezas DNP, agujeros H* y puntos de test TP* (sólo cobre).
Las piezas sin MPN (genéricas del cajón) salen como «Generic» con su especificación; si aparece otra pieza
sin MPN, el script se para.

Uso (Python de KiCad, con kicad-cli):  python bom_cpl_pcbway.py
Escribe fab/pcbway/nrflm20-meshnode-BOM-PCBWay.csv y fab/pcbway/nrflm20-meshnode-CPL-PCBWay.csv
"""
import csv
import re
import subprocess
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PROY = "nrflm20-meshnode"
SALIDA = RAIZ / "fab" / "pcbway"
KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"

# (Value, Footprint) de piezas genéricas sin MPN -> especificación
GENERICAS = {
    ("10u 10V", "Capacitor_SMD:C_0603_1608Metric"): "10uF 20% 10V X7R 0603",
    ("10u", "Capacitor_SMD:C_0603_1608Metric"): "10uF 20% 10V X7R 0603",
    ("22u 10V", "Capacitor_SMD:C_0603_1608Metric"): "22uF 20% 10V X7R 0603",
    ("10R 0603", "Resistor_SMD:R_0603_1608Metric"): "10R 5% 0603",
    ("0R", "Resistor_SMD:R_0603_1608Metric"): "0R 0603 jumper",
}
TRADUCCION = {
    "LED azul": "Blue LED",
    "LED verde": "Green LED",
    "82nH (activa)": "82nH (active GNSS antenna bias)",
}
FUERA = re.compile(r"^(H|TP)\d+$")


def natural(ref):
    m = re.match(r"([A-Z]+)(\d+)", ref)
    return (m.group(1), int(m.group(2))) if m else (ref, 0)


def kicad(*args):
    subprocess.run([KICAD_CLI, *args], check=True, capture_output=True, cwd=RAIZ)


with tempfile.TemporaryDirectory() as tmp:
    bom_raw, pos_raw = Path(tmp) / "bom.csv", Path(tmp) / "pos.csv"
    kicad("sch", "export", "bom", "--output", str(bom_raw),
          "--fields", "Reference,Value,Footprint,${QUANTITY},${DNP},Manufacturer,MPN,LCSC Part",
          "--group-by", "Value,Footprint,Manufacturer,MPN,LCSC Part,${DNP}",
          "--ref-range-delimiter", "", f"{PROY}.kicad_sch")
    kicad("pcb", "export", "pos", "--output", str(pos_raw), "--format", "csv", "--units", "mm",
          "--side", "both", "--exclude-dnp", f"{PROY}.kicad_pcb")
    filas_bom = list(csv.DictReader(bom_raw.open(encoding="utf-8")))
    filas_pos = list(csv.DictReader(pos_raw.open(encoding="utf-8")))

# ---------------------------------------------------------------- BOM
lineas = {}
dnp = []
for f in filas_bom:
    refs = [r for r in f["Reference"].split(",") if r]
    if f["DNP"]:
        dnp += refs
        continue
    refs = [r for r in refs if not FUERA.match(r)]
    if not refs:
        continue
    valor, huella = f["Value"], f["Footprint"]
    fab, mpn, lcsc = f["Manufacturer"], f["MPN"], f["LCSC Part"]
    if not mpn:
        if (valor, huella) not in GENERICAS:
            raise SystemExit(f"pieza sin MPN y sin especificación genérica: {refs} {valor} {huella}")
        fab, desc = "Generic", GENERICAS[(valor, huella)]
    else:
        desc = TRADUCCION.get(valor, valor)
    clave = (fab, mpn, desc, huella, lcsc)
    lineas.setdefault(clave, []).extend(refs)

bom = sorted(((sorted(r, key=natural), c) for c, r in lineas.items()), key=lambda x: natural(x[0][0]))
ruta_bom = SALIDA / f"{PROY}-BOM-PCBWay.csv"
with ruta_bom.open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, quoting=csv.QUOTE_ALL)
    w.writerow(["Designator", "Qty", "Manufacturer", "Mfg Part #", "Description/Value", "Package/Footprint",
                "LCSC Part #"])
    for refs, (fab, mpn, desc, huella, lcsc) in bom:
        w.writerow([",".join(refs), len(refs), fab, mpn, desc, huella, lcsc])
refs_bom = {r for refs, _ in bom for r in refs}

# ---------------------------------------------------------------- CPL
ruta_cpl = SALIDA / f"{PROY}-CPL-PCBWay.csv"
refs_cpl = set()
with ruta_cpl.open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["Ref", "Val", "Package", "PosX", "PosY", "Rot", "Side"])
    for f in sorted(filas_pos, key=lambda f: natural(f["Ref"])):
        if FUERA.match(f["Ref"]):
            continue
        refs_cpl.add(f["Ref"])
        w.writerow([f["Ref"], TRADUCCION.get(f["Val"], f["Val"]), f["Package"], f["PosX"], f["PosY"], f["Rot"],
                    f["Side"]])

# ---------------------------------------------------------------- comprobación cruzada
solo_bom, solo_cpl = refs_bom - refs_cpl, refs_cpl - refs_bom
print(f"BOM: {len(bom)} líneas, {len(refs_bom)} piezas -> {ruta_bom.relative_to(RAIZ)}")
print(f"CPL: {len(refs_cpl)} piezas -> {ruta_cpl.relative_to(RAIZ)}")
print("DNP fuera:", ", ".join(sorted(dnp, key=natural)))
print("sólo en BOM:", sorted(solo_bom) or "—", "| sólo en CPL:", sorted(solo_cpl) or "—")
if solo_bom or solo_cpl:
    raise SystemExit("BOM y CPL no cuadran")
