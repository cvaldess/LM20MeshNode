"""Import the Ebyte footprints (converted from the vendor Altium .PcbLib with pcbnew) into libs/meshnode.pretty,
re-centred on the module body and renamed; vendor silkscreen dropped (outlines are redrawn with Konnect).
Run with KiCad's python:  python importar_huellas_ebyte.py <converted_e22.pretty> <converted_e108.pretty>

Body positions taken from the datasheets (pad coordinates as converted, origin = pin 1):
  E22-xxxMM22S  10.0 x 10.0 : pads 1-5 at x=0, pin 1 2.46 below the top edge  -> centre (5.00, 2.54)
  E108-GN04S    12.2 x 16.0 : pads 1-12 at x=0, pin 1 1.00 below the top edge -> centre (6.10, 7.00)
"""
import os
import sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.normpath(os.path.join(HERE, "..", "..", "libs", "meshnode.pretty"))

JOBS = [  # (src lib, src name, new name, centre x, centre y, description)
    (sys.argv[1], "E220-400MM22S", "E22-xxxMM22S", 5.00, 2.54,
     "Ebyte E22-400/900MM22S(T) SX1262/SX1268 module 10x10 mm, 20 stamp holes pitch 1.27 (vendor PcbLib)"),
    (sys.argv[2], "E108-GN03S", "E108-GN04S", 6.10, 7.00,
     "Ebyte E108-GN04S GNSS module 12.2x16 mm, 24 stamp holes pitch 1.1 (vendor PcbLib named E108-GN03S)"),
]

io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
for src, name, new, cx, cy, desc in JOBS:
    fp = pcbnew.FootprintLoad(src, name)
    off = pcbnew.VECTOR2I(pcbnew.FromMM(cx), pcbnew.FromMM(cy))
    rows = []
    for p in fp.Pads():
        p.SetPosition(p.GetPosition() - off)
        q = p.GetPosition()
        rows.append((int(p.GetNumber()), pcbnew.ToMM(q.x), pcbnew.ToMM(q.y)))
    rows.sort()
    for it in list(fp.GraphicalItems()):
        fp.Remove(it)
    fp.SetFPID(pcbnew.LIB_ID("", new))
    fp.SetLibDescription(desc)
    fp.SetAttributes(pcbnew.FP_SMD)
    fp.SetValue(new)  # Ref/Value text positions are left as converted; moved later in the board if needed
    io.FootprintSave(DST, fp)  # the plugin takes the footprint: do not touch fp after this line
    print("saved", new, len(rows), "pads")
    for n, x, y in rows:
        print(f"   {n:>3} {x:7.3f} {y:7.3f}")
