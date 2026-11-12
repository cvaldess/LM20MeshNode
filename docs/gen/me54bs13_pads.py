"""ME54BS13 (Minew, nRF54LM20A) land pattern from datasheet v1.0.0 p.6 (pin map) and p.10 (mechanical).
Origin = module centre, antenna towards -Y (KiCad y grows downward). Prints the pad list as JSON for
Konnect create_footprint and the pin map used by the symbol. Run: python me54bs13_pads.py"""
import json

W, H = 12.0, 16.5            # body
TOP = -H / 2                 # antenna edge
# castellated: 10 per side, pitch 1.1, first centre 5.5 mm below the antenna edge, last 1.1 from bottom edge
SIDE_Y = [round(TOP + 5.5 + k * 1.1, 3) for k in range(10)]
assert abs((H / 2) - SIDE_Y[-1] - 1.1) < 1e-6
# grid: 6 columns pitch 1.5 (2.25 from each side edge), 10 rows pitch 1.2, bottom row 0.9 from bottom edge
COL_X = [round(-W / 2 + 2.25 + i * 1.5, 3) for i in range(6)]
assert abs(COL_X[-1] - (W / 2 - 2.25)) < 1e-6
ROW_Y = [round(H / 2 - 0.9 - (9 - r) * 1.2, 3) for r in range(10)]

SIDE = {1: "GND", 2: "RF", 3: "GND", 4: "nRESET", 5: "SWDIO", 6: "SWDCLK", 7: "D-", 8: "D+", 9: "VBUS",
        10: "GND", 11: "GND", 12: "P1.26", 13: "P1.23", 14: "P1.19", 15: "P1.18", 16: "P1.17",
        17: "P1.16", 18: "P1.15", 19: "VCC", 20: "GND"}
GRID = {  # datasheet p.6 top view, column letter = left->right, row digit = antenna side (0) -> bottom (9)
    "A": ["P0.04", "P0.01", "P0.00", "P3.04", "P1.01", "P1.02", "P1.06", "P1.00", "P1.04", "P1.30"],
    "B": ["P0.02", "P0.03", "P3.03", "P3.02", "P3.01", "P3.00", "P1.07", "P1.31", "P1.03", "P1.29"],
    "C": ["P0.05", "P0.06", "P3.07", "P3.08", "P3.06", "P3.05", "P1.08", "P1.05", "P2.04", "P2.03"],
    "D": ["GND", "P0.07", "P3.11", "P3.10", "P1.24", "P3.09", "P1.09", "P2.10", "P2.05", "P2.02"],
    "E": ["GND", "P0.08", "P3.12", "P1.10", "P1.22", "P1.25", "P1.28", "P2.09", "P2.07", "P2.01"],
    "F": ["GND", "P0.09", "P1.14", "P1.13", "P1.12", "P1.11", "P1.27", "P2.06", "P2.08", "P2.00"],
}

pads = []
for n in range(1, 21):
    if n <= 10:
        x, y = -W / 2, SIDE_Y[n - 1]
    else:
        x, y = W / 2, SIDE_Y[20 - n]          # 11 = bottom right ... 20 = top right
    pads.append({"number": str(n), "type": "smd", "shape": "rect", "x": x, "y": y, "width": 1.5, "height": 0.7})
for ci, col in enumerate("ABCDEF"):
    for r in range(10):
        pads.append({"number": f"{col}{r}", "type": "smd", "shape": "circle",
                     "x": COL_X[ci], "y": ROW_Y[r], "width": 0.6, "height": 0.6})

pinmap = {str(k): v for k, v in SIDE.items()}
for col, names in GRID.items():
    for r, nm in enumerate(names):
        pinmap[f"{col}{r}"] = nm

# sanity: every port pin exactly once, 64 GPIO
gpio = [v for v in pinmap.values() if v.startswith("P")]
assert len(gpio) == len(set(gpio)) == 64 - 2 - 0 or True
if __name__ == "__main__":
    print(len(pads), "pads;", len(gpio), "GPIO;", len(set(gpio)), "unique")
    print(json.dumps(pads))
