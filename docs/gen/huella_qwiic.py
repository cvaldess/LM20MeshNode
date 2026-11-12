"""J501 · Qwiic BOOMELE 1.0T-4P (C970137, cajón #203): copia de easyeda2kicad:CONN-SMD_1.0T-4P-LT (la del código
viejo C145961, misma pieza según el usuario 09-11-2026) con los dos pads de anclaje renombrados «0» → «MP», para
casar con Connector_Generic_MountingPin:Conn_01x04_MountingPin. Pads de señal 0,4×1,6 a paso 1,0 (= plano C970137).
Se guarda con el serializador de KiCad (pcbnew), no editando texto. Ejecutar con el python de KiCad."""
import os
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.normpath(os.path.join(HERE, "..", "..", "libs", "meshnode.pretty"))
SRC = r"C:/Users/cvald/Documents/KiCad/easyeda2kicad/easyeda2kicad.pretty"
NAME = "BOOMELE_1.0T-4P_1x04-1MP_P1.00mm_Horizontal"

fp = pcbnew.FootprintLoad(SRC, "CONN-SMD_1.0T-4P-LT")
n_mp = 0
for p in fp.Pads():
    if p.GetNumber() == "0":
        p.SetNumber("MP")
        n_mp += 1
assert n_mp == 2, n_mp
fp.SetFPID(pcbnew.LIB_ID("", NAME))
fp.SetLibDescription("BOOMELE 1.0T-4P (LCSC C970137, antes C145961): JST SH 1 mm, 4 pines, SMD ángulo recto (Qwiic)")
fp.SetKeywords("Qwiic SH 1.0 4P horizontal")
print("pads:", sorted(p.GetNumber() for p in fp.Pads()))
io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
io.FootprintSave(DST, fp)  # el plugin se queda con fp: no tocarlo después
print("guardada", NAME, "en", DST)
