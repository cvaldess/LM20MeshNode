"""nPM1300 QFN32 footprint for hand stencil + hot plate: copy of easyeda2kicad QFN-32_L5.0-W5.0-P0.50-TL-EP3.5
(checked against nPM1300 PS v1.3 table 36: D2/E2 3.5, b 0.25, L 0.4, e 0.5) with
  * EP (pad 33, 3.5 x 3.5) without its own paste: 2 x 2 paste windows 1.2 x 1.2 mm (4 x 1.44 / 12.25 = 47 %),
    so the part does not float on the solder and the 0.5 mm pins still wet;
  * 5 thermal vias (drill 0.3 / 0.5 mm, tented: copper only) in the cross between the windows, numbered 33 (AVSS).
Run with KiCad's python: python huella_npm1300.py"""
import os
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.normpath(os.path.join(HERE, "..", "..", "libs", "meshnode.pretty"))
SRC = r"C:/Users/cvald/Documents/KiCad/easyeda2kicad/easyeda2kicad.pretty"
NAME = "nPM1300-QFN32-EP3.5"

mm = pcbnew.FromMM
fp = pcbnew.FootprintLoad(SRC, "QFN-32_L5.0-W5.0-P0.50-TL-EP3.5")
for p in fp.Pads():
    if p.GetNumber() == "33":
        ls = p.GetLayerSet()
        ls.RemoveLayer(pcbnew.F_Paste)
        p.SetLayerSet(ls)

for sx in (-1, 1):  # paste windows
    for sy in (-1, 1):
        w = pcbnew.PAD(fp)
        w.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        w.SetShape(pcbnew.PAD_SHAPE_RECT)
        w.SetSize(pcbnew.VECTOR2I(mm(1.2), mm(1.2)))
        w.SetPosition(pcbnew.VECTOR2I(mm(sx * 0.875), mm(sy * 0.875)))
        lp = pcbnew.LSET()
        lp.AddLayer(pcbnew.F_Paste)
        w.SetLayerSet(lp)
        w.SetNumber("")
        fp.Add(w)

for x, y in ((0, 0), (0, -1.2), (0, 1.2), (-1.2, 0), (1.2, 0)):  # thermal vias
    v = pcbnew.PAD(fp)
    v.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    v.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    v.SetSize(pcbnew.VECTOR2I(mm(0.5), mm(0.5)))
    v.SetDrillSize(pcbnew.VECTOR2I(mm(0.3), mm(0.3)))
    v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    v.SetLayerSet(pcbnew.LSET.AllCuMask())
    v.SetNumber("33")
    fp.Add(v)

fp.SetFPID(pcbnew.LIB_ID("", NAME))
fp.SetLibDescription("nPM1300-QEAA QFN32 5x5 P0.5, EP 3.5 with 2x2 paste windows (47 %) and 5 tented thermal vias")
fp.SetValue(NAME)
io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
io.FootprintSave(DST, fp)
print("saved", NAME)
