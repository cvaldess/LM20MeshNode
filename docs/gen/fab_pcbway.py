"""Salidas de fabricación para PCBWay desde la placa GUARDADA (kicad-cli 10).

Ajustes = plugin oficial de PCBWay para KiCad (github.com/pcbway/PCBWay-Plug-in-for-Kicad, process.py): Gerber X2
con atributos de red, máscara restada de la serigrafía, PTH/NPTH separados, netlist IPC-D-356. Diferencias:
taladros en mm (no en pulgadas), extensiones Protel y cabecera Excellon completa. Sin B.Paste (vacía) ni
User.Comments (sólo dibujos internos de huellas).

Uso (Python de KiCad):  python fab_pcbway.py [carpeta_salida]
Por defecto rehace fab/pcbway/gerber/ (la borra antes), el zip para subir y fab/pcbway/drc_<fecha>.json.
"""
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PROY = "nrflm20-meshnode"
REV = "rev0.1"
KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
CAPAS = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"
EN_ZIP = {".gtl", ".g1", ".g2", ".gbl", ".gtp", ".gto", ".gbo", ".gts", ".gbs", ".gm1", ".drl", ".ipc"}

base = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else RAIZ / "fab" / "pcbway"
ger = base / "gerber"
pcb = RAIZ / f"{PROY}.kicad_pcb"


def kicad(*args):
    r = subprocess.run([KICAD_CLI, *args], capture_output=True, text=True, cwd=RAIZ)
    if r.returncode not in (0, 5):          # 5 = DRC con violaciones
        raise SystemExit(f"kicad-cli {' '.join(args[:3])} falló:\n{r.stdout}\n{r.stderr}")
    return r


if ger.exists():
    shutil.rmtree(ger)
ger.mkdir(parents=True)

hoy = datetime.date.today().strftime("%Y%m%d")
drc = base / f"drc_{hoy}.json"
kicad("pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity", "--units", "mm",
      "-o", str(drc), str(pcb))
kicad("pcb", "export", "gerbers", "-l", CAPAS, "--subtract-soldermask", "-o", str(ger), str(pcb))
kicad("pcb", "export", "drill", "--format", "excellon", "--excellon-units", "mm",
      "--excellon-zeros-format", "decimal", "--excellon-oval-format", "route", "--excellon-separate-th",
      "--drill-origin", "absolute", "--generate-map", "--map-format", "pdf", "--generate-report",
      "--report-path", str(ger / f"{PROY}-drill_report.txt"), "-o", str(ger), str(pcb))
kicad("pcb", "export", "ipcd356", "-o", str(ger / f"{PROY}.ipc"), str(pcb))

fs = sorted(f for f in ger.iterdir() if f.suffix in EN_ZIP)
z = base / f"{PROY}_{REV}_pcbway.zip"
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in fs:
        if f.stat().st_size == 0:
            raise SystemExit(f"fichero vacío: {f.name}")
        zf.write(f, f.name)

d = json.loads(drc.read_text(encoding="utf-8"))
print(f"placa  {pcb.name} sha256 {hashlib.sha256(pcb.read_bytes()).hexdigest()}")
print(f"DRC    {len(d['violations'])} violaciones, {len(d['unconnected_items'])} sin conectar, "
      f"{len(d['schematic_parity'])} paridad -> {drc.name}")
for t in sorted({v['type'] for v in d['violations']}):
    print(f"         {t}: {sum(v['type'] == t for v in d['violations'])}")
print(f"zip    {z.name}: {len(fs)} ficheros, {z.stat().st_size} bytes")
