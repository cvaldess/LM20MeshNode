"""Genera lista_compra.txt (raíz del proyecto) con lo que hay que comprar y lo que sale del cajón.
Datos sacados de las tablas de piezas de las hojas (docs/gen/hojaNN.py) y del inventario (09-11-2026)."""
import io
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

LCSC = [  # (placa, sugerido, ref, pieza, lcsc, nota)
    ("1", "2", "U101", "Nordic nPM1300-QEAA (QFN32 5×5, EP)", "C7501206", "uno de repuesto: QFN con pad central"),
    ("2", "4", "L101 L102", "APV APH201610C2R2MP01 · 2,2 µH 0806", "C42455301", "130 mΩ, Isat 2,8 A (pide ≤ 400 mΩ, > 350 mA)"),
    ("1", "2", "BZ501", "Huayu HYG-5020A · zumbador magnético 4 kHz", "C7544810", "5×5 SMD, bobina 12 Ω"),
    ("1", "2", "DS501", "HS HS91L02W2C01 · OLED 0,91\" 128×32", "C5248081", "SSD1306, tira de 4 pines 2,54"),
    ("1", "2", "U502", "ST LSM6DS3TR-C · IMU 6 ejes LGA-14 2,5×3", "C967633", "despertar al mover la placa (INT1 → P0.02)"),
    ("1", "2", "J102", "JST S2B-PH-SM4-TB(LF)(SN) · PH 2.0, 2 pines", "C295747", "conector de batería (código confirmado)"),
    ("1", "2", "J201", "HX PZ1.27-2x5P TP · SWD 2×5 1,27 SMD", "C41376037", "Cortex Debug"),
    ("1", "100", "R102", "Yageo RC0402JR-07330KL · 330 kΩ 5 % 0402", "C137882", "5 % basta: VSET2 acepta 250–500 kΩ"),
    ("1", "100", "C404", "Samsung CL05C560JB5NNNC · 56 pF C0G 0402", "C84707", "bloqueo de DC de la antena GNSS"),
    ("1", "10", "L401", "Murata LQG15HS82NJ02D · 82 nH 0402", "C98002", "SÓLO si la antena GNSS es activa"),
]
FUERA = [  # (placa, ref, pieza, nota)
    ("1", "U201", "Minew ME54BS13 (nRF54LM20A)",
     "no aparece en distribuidores: tienda Minew (store.minewsemi.com) o minewsemi@minew.com"),
    ("1", "—", "Antena LoRa 868 MHz con U.FL (IPEX1)", "no está en el inventario"),
    ("1", "—", "Antena GNSS 1575 MHz con U.FL (IPEX1), activa o pasiva", "activa ⇒ montar L401"),
    ("1", "—", "LiPo 1S 3,7 V con protección (PCM) y JST PH 2.0, 1000–1500 mAh",
     "🚨 la polaridad de los PH 2.0 NO es estándar: comprobar antes de enchufar (pata 1 = +)"),
    ("1", "—", "PCB 4 capas + stencil", "cuando esté el layout"),
]
CAJON = [  # (refs, pieza, lcsc, cajón)
    ("J101", "Kinghelm KH-TYPE-C-16P", "C709357", "#112"),
    ("U102", "TPD4E05U06DQAR (DOWO) · Cj 0,4 pF, vale", "C22390021", "#20"),
    ("D101", "onsemi ESD5Z6.0T1G (SOD-523)", "C82323", "#205"),
    ("U301", "Ebyte E22-900MM22S", "—", "#195"),
    ("U401", "Ebyte E108-GN04S", "—", "#196"),
    ("U501", "Nyfea SHT41-P-NF", "C55108905", "#58"),
    ("J301 J401", "BWU.FL-IPEX1", "C5137195", "#210"),
    ("J501", "BOOMELE 1.0T-4P (Qwiic, clon SH 1 mm)", "C970137", "#203"),
    ("SW101 SW501-SW503", "Hanxia HX TS35CA 160gf", "C25168837", "#65"),
    ("D102", "XINGLIGHT XL-1608UBC-06A (azul)", "C7371904", "#41"),
    ("D103 D501", "XINGLIGHT XL-1608UGC-06A (verde)", "C7371903", "#42"),
    ("Q501", "HT BSS138", "C27140738", "#151"),
    ("D502", "JSMSEMI 1N4148W", "C917030", "#51"),
    ("RT101", "Murata NCP15XH103F0SRC (NTC 10k B3380)", "C91636", "#61"),
    ("FB201", "0 Ω 0603 (o ferrita FH CBW160808U601T 0603)", "—", "#137 (ferrita C139183 #4)"),
    ("R101 R301 R304", "Yageo RC0402FR-070RL · 0 Ω", "C106231", "#10"),
    ("R103 R104", "Yageo RC0402FR-071ML · 1 MΩ", "C138033", "#13"),
    ("R303 R505", "Yageo RC0402FR-07100KL · 100 kΩ", "C60491", "#11"),
    ("R401-R403", "UNI-ROYAL 0402WGF1001TCE · 1 kΩ", "C11702", "#31"),
    ("R501 R502", "Yageo RC0402FR-074K7L · 4,7 kΩ", "C105871", "#39"),
    ("R503", "UNI-ROYAL 0402WGF4700TCE · 470 Ω", "C25117", "#35"),
    ("R504", "UNI-ROYAL 0402WGF2200TCE · 220 Ω", "C25091", "#32"),
    ("R506 R507", "10 Ω 5 % 0603", "—", "#139"),
    ("C101 C102 C204 C502", "Samsung CL05A105KA5NQNC · 1 µF 25 V 0402", "C52923", "#23"),
    ("C103-C105 C107 C108 C201 C202 C401", "10 µF 10 V X7R 0603", "—", "#147"),
    ("C106", "Samsung CL10A225KO8NNNC · 2,2 µF 0603", "C23630", "#60"),
    ("C110 C111 C203 C302 C402 C403 C501 C503 C504", "Samsung CL05B104KO5NNNC · 100 nF 0402", "C1525", "#22"),
    ("C301", "22 µF 10 V X7R 0603", "—", "#146"),
    ("TP101-TP106 TP201-TP203 TP401", "TestPoint_Pad_D1.0mm (sólo cobre)", "—", "—"),
]
YA_NO = [
    "LED rojo para ERROR (D102)  → va el azul XL-1608UBC-06A del cajón (#41)",
    "R 100 Ω 0402 (R504)         → va 220 Ω 0402 del cajón (#32)",
    "TI TPD4E05U06DQAR (U102)    → el DOWO del cajón tiene Cj 0,4 pF típ. / 0,5 máx.: vale para USB HS",
    "JST SM04B-SRSS-TB (J501)    → va el BOOMELE 1.0T-4P del cajón (#203)",
]


def tabla(cab, filas, anchos):
    out = ["  ".join(c.ljust(w) for c, w in zip(cab, anchos)).rstrip(),
           "  ".join("─" * w for w in anchos)]
    for f in filas:
        out.append("  ".join(str(c).ljust(w) for c, w in zip(f, anchos)).rstrip())
    return out


L = ["LISTA DE COMPRA · nrf54lm20-meshnode (nodo Meshtastic de bolsillo)",
     "═" * 68,
     "Fecha: 09-11-2026. Sale de las tablas de piezas de docs/00…05_*.svg y del inventario.",
     "Regenerar con: docs/gen/lista_compra.py",
     "«Placa» = cantidad por placa. «Sugerido» = una placa y repuestos para montar a mano; si LCSC",
     "exige un mínimo mayor (los pasivos 0402 suelen ir de 100 en 100), manda el mínimo.", "",
     "1) LCSC", "───────"]
L += tabla(["Placa", "Sug.", "Ref.", "Pieza", "LCSC", "Nota"], LCSC, [5, 4, 9, 44, 9, 46])
L += ["", "2) Fuera de LCSC", "────────────────"]
for placa, ref, pieza, nota in FUERA:
    L.append(f"{placa:<5}  {ref:<5}  {pieza}")
    L.append(f"{'':<14}{nota}")
L += ["", "3) Ya en el cajón (no comprar)", "──────────────────────────────"]
L += tabla(["Ref.", "Pieza", "LCSC", "Cajón"], CAJON, [46, 44, 9, 24])
L += ["Sin montar (DNP): R302, R404, C303, C304.", "",
      "4) Ya NO hace falta comprar (decidido el 09-11-2026)", "────────────────────────────────────────────────────"]
L += ["• " + t for t in YA_NO]
dst = os.path.join(ROOT, "lista_compra.txt")
io.open(dst, "w", encoding="utf-8", newline="\r\n").write("\n".join(L) + "\n")
print(dst, len(L), "líneas")
