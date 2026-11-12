"""Check that every project symbol's pin numbers match its footprint's pad numbers 1:1 (read-only).
Run with KiCad's python: python check_lib.py"""
import os
import re
import sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SYM = os.path.join(ROOT, "libs", "meshnode.kicad_sym")
MESH = os.path.join(ROOT, "libs", "meshnode.pretty")
EASY = r"C:/Users/cvald/Documents/KiCad/easyeda2kicad/easyeda2kicad.pretty"
KSYM = r"C:/Program Files/KiCad/10.0/share/kicad/symbols"

PAIRS = [("ME54BS13", MESH, "ME54BS13"), ("E22-900MM22S", MESH, "E22-xxxMM22S"), ("E108-GN04S", MESH, "E108-GN04S"),
         ("nPM1300-QEAA", MESH, "nPM1300-QFN32-EP3.5"), ("SHT41-P-NF", EASY, "DFN-4_L1.5-W1.5-SHT41-AD1B-R2"),
         ("HS91L02W2C01", EASY, "OLED-TH_L38.0-W12.0_HS91L02W2C01"), ("BWU.FL-IPEX1", EASY, "IPEX-SMD_BWIPX-1-001E"),
         ("KH-TYPE-C-16P", EASY, "USB-C-SMD_KH-TYPE-C-16P"), ("TPD4E05U06DQAR", EASY, "DFN2510-10_L2.5-W1.0-P0.50-BL"),
         ("HYG-5020A", EASY, "BUZ-SMD_3P-L5.0-W5.0-P3.50-BL"),
         # (biblioteca de símbolos, símbolo, huellas, huella): símbolo estándar de KiCad con huella de easyeda2kicad
         (KSYM + "/Sensor_Motion.kicad_sym", "LSM6DS3", EASY, "LGA-14_L3.0-W2.5-P0.50-TL"),
         (KSYM + "/Connector_Generic_MountingPin.kicad_sym", "Conn_01x04_MountingPin", MESH,
          "BOOMELE_1.0T-4P_1x04-1MP_P1.00mm_Horizontal"),
         (KSYM + "/Connector_Generic_MountingPin.kicad_sym", "Conn_01x02_MountingPin",
          r"C:/Program Files/KiCad/10.0/share/kicad/footprints/Connector_JST.pretty",
          "JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal")]


def block(text, start):
    depth, i = 0, start
    while True:
        c = text[i]
        if c == '"':
            i = text.index('"', i + 1) + 1
            continue
        depth += c == "("
        depth -= c == ")"
        if depth == 0:
            return text[start:i + 1]
        i += 1


bad = 0
for pair in PAIRS:
    symlib, sym, fplib, fp = pair if len(pair) == 4 else (SYM,) + pair
    lib = open(symlib, encoding="utf-8").read()
    m = re.search(r'\(symbol "' + re.escape(sym) + r'"\s', lib)
    pins = re.findall(r'\(number "([^"]+)"', block(lib, m.start()))
    f = pcbnew.FootprintLoad(fplib, fp)
    pads = set()
    for p in f.Pads():
        if p.GetNumber():
            pads.add(p.GetNumber())
    ok = sorted(pins) == sorted(set(pins)) and set(pins) == pads
    bad += not ok
    print(f"{'OK ' if ok else 'BAD'} {sym:<14} pins={len(pins):>3} pads={len(pads):>3} -> {fp}"
          + ("" if ok else f"  only_sym={sorted(set(pins) - pads)} only_fp={sorted(pads - set(pins))}"))
sys.exit(1 if bad else 0)
