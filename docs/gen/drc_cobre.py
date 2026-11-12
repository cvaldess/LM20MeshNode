"""Lista las violaciones DRC de cobre (no serigrafía/librería) con posición. uso: drc_cobre.py drc.json"""
import json
import sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
SALTAR = {"silk_overlap", "silk_over_copper", "silk_edge_clearance", "lib_footprint_issues", "lib_footprint_mismatch"}
for v in d["violations"]:
    if v["type"] in SALTAR:
        continue
    pos = "; ".join(f"({i['pos']['x']:.2f},{i['pos']['y']:.2f}) {i['description']}" for i in v.get("items", []))
    print(f"{v['type']:16s} {v['description'][:70]} || {pos}")
