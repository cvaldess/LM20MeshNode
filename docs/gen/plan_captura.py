"""Planificador de la CAPTURA en KiCad (Konnect) de las hojas de nrf54lm20-meshnode. Método estándar del usuario
(memoria feedback_esquemas_en_svg): la intención es docs/gen/hojaNN.py; esto calcula coordenadas, la red de cada pata,
etiquetas jerárquicas, NC, símbolos de alimentación en cada pata y PWR_FLAG, con asserts de rejilla y de patas
coincidentes. Escribe plan_NN.json para lanzar las llamadas de Konnect. Uso: python plan_captura.py NN <dir_salida>

Convenciones (09-11-2026):
- Raíles (GND, 3V3, VSYS, VBAT, V_GNSS, VBUS): etiqueta local en cada pata + UN símbolo de alimentación por raíl y
  hoja con su propia etiqueta (power:GND, power:+3V3 con Value 3V3, power:VCC con Value VSYS/V_GNSS, power:+BATT con
  Value VBAT, power:VBUS). Un símbolo en cada pata quedaba más limpio, pero batch_place_components devuelve ~2 KB por
  pieza (hueco #1 de Konnect) y 70 símbolos por hoja desbordan el contexto.
- PWR_FLAG con su propia etiqueta, en la misma esquina que los símbolos de alimentación.
- Señales locales: etiqueta en cada pata; en integrados y conectores (U*, J*) con cable de 13,97 mm.
- Señales entre hojas: UNA etiqueta jerárquica en la primera pata de la red (pegada) y locales en las demás.
"""
import json
import os
import sys

from kicad_pins import lib_pins, load_lib, place_pins

HERE = os.path.dirname(os.path.abspath(__file__))
KSYM = "C:/Program Files/KiCad/10.0/share/kicad/symbols/"
LIBS = {"meshnode": os.path.join(HERE, "..", "..", "libs", "meshnode.kicad_sym"),
        "easyeda2kicad": "C:/Users/cvald/Documents/KiCad/easyeda2kicad/easyeda2kicad.kicad_sym"}
DS = "${KIPRJMOD}/datasheets/"
STUB_IC = 13.97
_cache = {}


def symbol_pins(lib_id):
    lib, name = lib_id.split(":")
    path = LIBS.get(lib, KSYM + lib + ".kicad_sym")
    if path not in _cache:
        _cache[path] = load_lib(path)
    return lib_pins(_cache[path], name)


def g(n):
    """n pasos de 2,54 mm → mm."""
    return round(n * 2.54, 2)


# raíl → (lib_id, ángulo hacia el que apunta el cuerpo con giro 0)
RAILS = {"GND": ("power:GND", 270), "3V3": ("power:+3V3", 90), "VSYS": ("power:VCC", 90),
         "V_GNSS": ("power:VCC", 90), "VBAT": ("power:+BATT", 90), "VBUS": ("power:VBUS", 90)}

# Huellas
R0402, C0402, C0603 = "Resistor_SMD:R_0402_1005Metric", "Capacitor_SMD:C_0402_1005Metric", "Capacitor_SMD:C_0603_1608Metric"
R0603, LED0603 = "Resistor_SMD:R_0603_1608Metric", "LED_SMD:LED_0603_1608Metric"
TPFP = "TestPoint:TestPoint_Pad_D1.0mm"
# Piezas del cajón / compra: valor → (huella, campos)
PARTS = {
    "100n": (C0402, {"LCSC Part": "C1525", "MPN": "CL05B104KO5NNNC", "Manufacturer": "Samsung"}),
    "1u": (C0402, {"LCSC Part": "C52923", "MPN": "CL05A105KA5NQNC", "Manufacturer": "Samsung"}),
    "2u2": (C0603, {"LCSC Part": "C23630", "MPN": "CL10A225KO8NNNC", "Manufacturer": "Samsung"}),
    "10u": (C0603, {"Description": "10 µF 10 V X7R 0603 (cajón #147)"}),
    "22u": (C0603, {"Description": "22 µF 10 V X7R 0603 (cajón #146)"}),
    "56p": (C0402, {"LCSC Part": "C84707", "MPN": "CL05C560JB5NNNC", "Manufacturer": "Samsung"}),
    "0R": (R0402, {"LCSC Part": "C106231", "MPN": "RC0402FR-070RL", "Manufacturer": "Yageo"}),
    "1M": (R0402, {"LCSC Part": "C138033", "MPN": "RC0402FR-071ML", "Manufacturer": "Yageo"}),
    "330k": (R0402, {"LCSC Part": "C137882", "MPN": "RC0402JR-07330KL", "Manufacturer": "Yageo"}),
    "100k": (R0402, {"LCSC Part": "C60491", "MPN": "RC0402FR-07100KL", "Manufacturer": "Yageo"}),
    "4k7": (R0402, {"LCSC Part": "C105871", "MPN": "RC0402FR-074K7L", "Manufacturer": "Yageo"}),
    "1k": (R0402, {"LCSC Part": "C11702", "MPN": "0402WGF1001TCE", "Manufacturer": "UNI-ROYAL"}),
    "470R": (R0402, {"LCSC Part": "C25117", "MPN": "0402WGF4700TCE", "Manufacturer": "UNI-ROYAL"}),
    "220R": (R0402, {"LCSC Part": "C25091", "MPN": "0402WGF2200TCE", "Manufacturer": "UNI-ROYAL"}),
    "10R": (R0603, {"Description": "10 Ω 5 % 0603 125 mW (cajón #139)"}),
}


class Plan:
    def __init__(self, num, hier):
        self.num = num                  # "01"…
        self.hier = hier                # red jerárquica → forma (input/output/bidirectional)
        self.comps, self.fields, self.pins, self.intent = [], {}, {}, {}
        self.flags, self.texts = [], []
        self.npwr = 0
        self.override = {}              # "REF.n" → (stub, dirección) para patas verticales de IC

    # ------------------------------------------------------------------ colocación
    def place(self, ref, lib_id, x, y, rot=0, value=None, fp=None, nets=None, **fields):
        x, y = round(x, 2), round(y, 2)
        for v in (x, y):
            assert abs(v / 1.27 - round(v / 1.27)) < 1e-6, (ref, v)
        c = {"lib_id": lib_id, "reference": ref, "x": x, "y": y, "rotation": rot}
        if value:
            c["value"] = value
        if fp:
            c["footprint"] = fp
        self.comps.append(c)
        if fields:
            self.fields[ref] = {k: v for k, v in fields.items() if v}
        for num, px, py, d, typ in place_pins(symbol_pins(lib_id), x, y, rot):
            self.pins[f"{ref}.{num}"] = (round(px, 2), round(py, 2), d)
        for p, n in (nets or {}).items():
            k = f"{ref}.{p}"
            assert k in self.pins, k
            self.intent[k] = n

    def two(self, ref, lib_id, x, y, val, a, b, fp=None, value=None, **f):
        """pasivo de 2 patas en horizontal: pata 1 a la izquierda (red a), pata 2 a la derecha (red b)."""
        pfp, pf = PARTS.get(val, (None, {}))
        self.place(ref, lib_id, x, y, 90, value or val, fp or pfp, {"1": a, "2": b}, **{**pf, **f})

    def text(self, x, y, s):
        self.texts.append({"x": x, "y": y, "text": s})

    def rails_at(self, x, y):
        """Esquina donde van UN símbolo por raíl de la hoja (y los PWR_FLAG), en fila cada 12,7 mm."""
        self.rail_xy = [x, y]

    def _corner(self, lib_id, ref, value, net):
        x, y = self.rail_xy
        self.rail_xy[0] = round(x + 12.7, 2)
        self.place(ref, lib_id, x, y, 0, value, None, {"1": net})

    def flag(self, net):
        """PWR_FLAG con su propia etiqueta de la red (raíl o red local alimentada por un pasivo)."""
        self._corner("power:PWR_FLAG", f"#FLG{self.num}{len(self.flags) + 1:02d}", "PWR_FLAG", net)
        self.flags.append(net)

    # ------------------------------------------------------------------ salida
    def build(self):
        for n in sorted({n for n in self.intent.values() if n in RAILS}):   # un símbolo por raíl y hoja
            self.npwr += 1
            self._corner(RAILS[n][0], f"#PWR{self.num}{self.npwr:03d}", n, n)
        nets = {}
        for p, n in self.intent.items():
            nets.setdefault(n, []).append(p)
        seen, stacked = {}, set()
        for p in sorted(self.intent):
            x, y, d = self.pins[p]
            for v in (x, y):
                assert abs(v / 1.27 - round(v / 1.27)) < 1e-6, (p, v)
            k = (x, y)
            if k in seen and self.intent[seen[k]] == self.intent[p] and p.split(".")[0] == seen[k].split(".")[0]:
                stacked.add(p)          # patas apiladas del mismo símbolo y la misma red (GND 6/7 del LSM6DS3)
                continue
            assert k not in seen, (p, seen.get(k))
            seen[k] = p
        missing = sorted(p for p in self.pins if p not in self.intent)
        assert not missing, f"patas sin intención: {missing}"
        hier, conn, nc = [], {}, []
        for n, plist in sorted(nets.items()):
            plist = sorted(plist)
            if n == "NC":
                nc += [{"x": self.pins[p][0], "y": self.pins[p][1]} for p in plist]
                continue
            plist = [p for p in plist if p not in stacked]
            rest = plist
            if n in self.hier:
                first = sorted(plist, key=lambda p: (not p.startswith(("U", "J")), p))[0]
                x, y, d = self.pins[first]
                hier.append({"net": n, "x": x, "y": y, "rotation": d, "shape": self.hier[n]})
                rest = [p for p in plist if p != first]
            for p in rest:
                ref, num = p.split(".")
                d = self.pins[p][2]
                stub = STUB_IC if ref.startswith(("U", "J")) else 0
                direction = "auto"   # en patas verticales sale a 0° (hueco #8): cosmético, ahorra llamadas
                stub, direction = self.override.get(p, (stub, direction))
                conn.setdefault(f"{n}|{stub}|{direction}", []).append({"reference": ref, "pin_number": num})
        assert set(self.hier) <= set(nets), set(self.hier) - set(nets)
        groups = [{"net_name": k.split("|")[0], "stub_length": float(k.split("|")[1]), "direction": k.split("|")[2],
                   "pins": v} for k, v in sorted(conn.items())]
        edits = [{"reference": r, "fields": f} for r, f in sorted(self.fields.items())]
        return {"comps": self.comps, "edits": edits, "groups": groups, "hier": hier, "nc": nc,
                "texts": self.texts, "intent": self.intent,
                "stats": {"componentes": len(self.comps), "pwr_flag": len(self.flags),
                          "grupos_etiquetas": len(groups), "jerarquicas": len(hier), "nc": len(nc),
                          "redes": len(nets)}}


# ====================================================================================================== hoja 01
def hoja01():
    P = Plan("01", {"USB_DP": "bidirectional", "USB_DM": "bidirectional", "VBUS_MCU": "output",
                    "I2C_SDA": "bidirectional", "I2C_SCL": "bidirectional", "GNSS_EN": "input",
                    "PMIC_INT": "output", "VBAT_SENSE": "output"})
    # A · USB-C + ESD
    P.place("J101", "meshnode:KH-TYPE-C-16P", g(24), g(30), 0, "KH-TYPE-C-16P", "easyeda2kicad:USB-C-SMD_KH-TYPE-C-16P",
            {"A4": "VBUS", "A9": "VBUS", "B4": "VBUS", "B9": "VBUS", "A5": "CC1", "B5": "CC2", "A6": "USB_DP",
             "B6": "USB_DP", "A7": "USB_DM", "B7": "USB_DM", "A8": "NC", "B8": "NC", "A1": "GND", "A12": "GND",
             "B1": "GND", "B12": "GND", "1": "GND", "2": "GND", "3": "GND", "4": "GND"},
            **{"LCSC Part": "C709357", "MPN": "KH-TYPE-C-16P", "Manufacturer": "Kinghelm",
               "Datasheet": DS + "KH-TYPE-C-16P.pdf"})
    P.place("D101", "Device:D_TVS", g(24), g(44), 0, "ESD5Z6.0T1G", "easyeda2kicad:SOD-523F_L1.2-W0.8-LS1.7-RD",
            {"1": "VBUS", "2": "GND"}, **{"LCSC Part": "C82323", "MPN": "ESD5Z6.0T1G", "Manufacturer": "onsemi",
                                          "Datasheet": DS + "ESD5Z6.0T1G.pdf"})
    P.place("U102", "meshnode:TPD4E05U06DQAR", g(55), g(30), 0,  # movido el 09-11 (etiquetas chocaban con J101)
            "TPD4E05U06DQAR",
            "easyeda2kicad:DFN2510-10_L2.5-W1.0-P0.50-BL",
            {"1": "USB_DP", "10": "USB_DP", "2": "USB_DM", "9": "USB_DM", "4": "CC1", "7": "CC1", "5": "CC2",
             "6": "CC2", "3": "GND", "8": "GND"},
            **{"LCSC Part": "C22390021", "MPN": "TPD4E05U06DQAR", "Manufacturer": "DOWO",
               "Datasheet": DS + "TPD4E05U06DQAR.pdf"})
    # B · nPM1300
    P.place("U101", "meshnode:nPM1300-QEAA", g(86), g(44), 0, "nPM1300-QEAA", "meshnode:nPM1300-QFN32-EP3.5",
            {"21": "VBUS", "22": "VBUS_MCU", "23": "CC1", "24": "CC2", "19": "VBAT", "18": "NTC", "12": "3V3",
             "13": "I2C_SDA", "14": "I2C_SCL", "7": "GNSS_EN", "8": "PMIC_INT", "9": "NC", "10": "NC", "11": "NC",
             "15": "SHPHLD", "17": "VSET1", "16": "VSET2", "20": "VSYS", "4": "VSYS", "3": "SW1", "1": "V_GNSS",
             "2": "GND", "5": "SW2", "32": "3V3", "6": "GND", "28": "GND", "29": "GND", "30": "GND", "31": "GND",
             "25": "LED0", "26": "LED1", "27": "NC", "33": "GND"},
            **{"LCSC Part": "C7501206", "MPN": "nPM1300-QEAA", "Manufacturer": "Nordic Semiconductor",
               "Datasheet": DS + "nPM1300_PS_v1.3.pdf"})
    # C/D · bucks y VSET (columna 1)
    X1, Y0, DY = g(114), g(22), 7.62
    LF = {"LCSC Part": "C42455301", "MPN": "APH201610C2R2MP01", "Manufacturer": "APV",
          "Datasheet": DS + "APH201610C2R2MP01.pdf"}
    P.two("L101", "Device:L", X1, Y0, "2u2", "SW1", "V_GNSS", fp="Inductor_SMD:L_Changjiang_FTC201610S", **LF)
    P.two("C107", "Device:C", X1, Y0 + DY, "10u", "V_GNSS", "GND")
    P.two("L102", "Device:L", X1, Y0 + 2 * DY, "2u2", "SW2", "3V3", fp="Inductor_SMD:L_Changjiang_FTC201610S", **LF)
    P.two("C108", "Device:C", X1, Y0 + 3 * DY, "10u", "3V3", "GND")
    P.two("R101", "Device:R", X1, Y0 + 5 * DY, "0R", "VSET1", "GND")
    P.two("R102", "Device:R", X1, Y0 + 6 * DY, "330k", "VSET2", "GND", value="330k 5%")
    # E · desacoplo (columna 2)
    X2 = g(132)
    for i, (ref, val, a) in enumerate((("C101", "1u", "VBUS"), ("C102", "1u", "VBUS_MCU"), ("C103", "10u", "VSYS"),
                                       ("C104", "10u", "VSYS"), ("C105", "10u", "VSYS"), ("C106", "2u2", "VBAT"),
                                       ("C110", "100n", "3V3"), ("C111", "100n", "VBAT_SENSE"))):
        P.two(ref, "Device:C", X2, Y0 + i * DY, val, a, "GND",
              value={"1u": "1u 25V", "10u": "10u 10V", "2u2": "2u2 16V", "100n": "100n"}[val])
    # F · VBAT, NTC · G · LEDs (columna 3)
    X3 = g(152)
    P.two("R103", "Device:R", X3, Y0, "1M", "VBAT", "VBAT_SENSE")
    P.two("R104", "Device:R", X3, Y0 + DY, "1M", "VBAT_SENSE", "GND")
    P.two("RT101", "Device:Thermistor_NTC", X3, Y0 + 3 * DY, "10k", "NTC", "GND", fp=R0402, value="10k B3380",
          **{"LCSC Part": "C91636", "MPN": "NCP15XH103F0SRC", "Manufacturer": "Murata",
             "Datasheet": DS + "NCP15XH103F0SRC.pdf"})
    P.place("D102", "Device:LED", X3, Y0 + 5 * DY, 0, "LED azul", LED0603, {"1": "LED0", "2": "VSYS"},
            **{"LCSC Part": "C7371904", "MPN": "XL-1608UBC-06A", "Manufacturer": "XINGLIGHT",
               "Datasheet": DS + "XL-1608UBC-06A.pdf"})
    P.place("D103", "Device:LED", X3, Y0 + 6 * DY, 0, "LED verde", LED0603, {"1": "LED1", "2": "VSYS"},
            **{"LCSC Part": "C7371903", "MPN": "XL-1608UGC-06A", "Manufacturer": "XINGLIGHT",
               "Datasheet": DS + "XL-1608UGC-06A.pdf"})
    # Batería, botón, puntos de prueba (abajo)
    P.place("J102", "Connector_Generic_MountingPin:Conn_01x02_MountingPin", g(24), g(64), 0, "S2B-PH-SM4-TB",
            "Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal", {"1": "VBAT", "2": "GND", "MP": "NC"},
            **{"LCSC Part": "C295747", "MPN": "S2B-PH-SM4-TB(LF)(SN)", "Manufacturer": "JST",
               "Datasheet": DS + "S2B-PH-SM4-TB(LF)(SN).pdf"})
    P.place("SW101", "easyeda2kicad:HXTS35CA160GF", g(24), g(76), 0, "HX TS35CA 160gf",
            "easyeda2kicad:KEY-SMD_HX-TS35CA-250GF", {"2": "SHPHLD", "1": "GND", "3": "GND", "4": "GND"},
            **{"LCSC Part": "C25168837", "MPN": "HX TS35CA 160gf", "Manufacturer": "Hanxia",
               "Datasheet": DS + "HX_TS35CA_160gf_C25168837.pdf"})
    for i, (ref, net) in enumerate((("TP101", "VBUS"), ("TP102", "VBAT"), ("TP103", "VSYS"), ("TP104", "3V3"),
                                    ("TP105", "V_GNSS"), ("TP106", "GND"))):
        P.place(ref, "Connector:TestPoint", g(50 + 6 * i), g(70), 0 if net == "GND" else 180, "TP", TPFP, {"1": net})
    P.rails_at(g(50), g(84))
    P.flag("VBUS")
    for x, y, s in ((g(16), g(8), "A · USB-C (KH-TYPE-C-16P) y ESD"), (g(70), g(8), "B · PMIC nPM1300-QEAA"),
                    (g(106), g(18), "C/D · Bucks y VSET"), (g(126), g(18), "E · Desacoplo"),
                    (g(146), g(18), "F/G · VBAT, NTC y LEDs de carga"),
                    (g(16), g(60), "Batería (JST PH 2.0) y botón de encendido"), (g(48), g(64), "Puntos de prueba"),
                    (g(16), g(96), "Intención y cálculos: docs/01_alimentacion.svg")):
        P.text(x, y, s)
    return P


# ====================================================================================================== hoja 02
def hoja02():
    from hoja02 import MAPA
    out_ = {"VBUS_MCU": "input", "USB_DP": "bidirectional", "USB_DM": "bidirectional", "I2C_SDA": "bidirectional",
            "I2C_SCL": "bidirectional", "GNSS_EN": "output", "PMIC_INT": "input", "VBAT_SENSE": "input",
            "LORA_SCK": "output", "LORA_MOSI": "output", "LORA_MISO": "input", "LORA_NSS": "output",
            "LORA_BUSY": "input", "LORA_DIO1": "input", "LORA_NRST": "output", "LORA_RXEN": "output",
            "LORA_TXEN": "output", "GNSS_TX": "output", "GNSS_RX": "input", "GNSS_PPS": "input", "GNSS_RST": "output",
            "IMU_INT1": "input", "IMU_INT2": "input", "BTN_UP": "input", "BTN_OK": "input", "BTN_DOWN": "input",
            "BUZZER": "output", "LED_STAT": "output"}
    P = Plan("02", out_)
    X, Y = g(40), g(40)
    nets = {"19": "VCC_MCU", "9": "VBUS_MCU", "8": "USB_DP", "7": "USB_DM", "4": "SWD_RST", "5": "SWDIO",
            "6": "SWDCLK", "2": "NC"}
    port_net = {port: sig for sig, (port, _, _) in MAPA.items()}
    for num, nm, typ, px, py, a, u in symbol_pins("meshnode:ME54BS13"):
        if nm == "GND":
            nets[num] = "GND"
        elif nm.startswith("P"):
            nets[num] = port_net.get(nm.split("/")[0], "NC")
    P.place("U201", "meshnode:ME54BS13", X, Y, 0, "ME54BS13", "meshnode:ME54BS13", nets,
            **{"MPN": "ME54BS13 (nRF54LM20A)", "Manufacturer": "Minew",
               "Datasheet": DS + "ME54BS13-nRF54LM20A_Datesheet_K_EN.pdf"})
    for k, n in nets.items():
        if n == "GND":
            P.override[f"U201.{k}"] = (2.54, "down")
    # B · alimentación del módulo (π de Minew) y VBUS
    X1, Y0, DY = g(90), g(20), 7.62
    P.two("C201", "Device:C", X1, Y0, "10u", "3V3", "GND", value="10u 10V")
    P.two("FB201", "Device:R", X1, Y0 + DY, "0R", "3V3", "VCC_MCU", fp=R0603, value="0R",
          **{"LCSC Part": "", "MPN": "", "Manufacturer": "",
             "Description": "0 Ω 0603 (cajón #137) o ferrita FH CBW160808U601T 600 Ω@100 MHz (C139183, cajón #4)"})
    P.two("C202", "Device:C", X1, Y0 + 2 * DY, "10u", "VCC_MCU", "GND", value="10u 10V")
    P.two("C203", "Device:C", X1, Y0 + 3 * DY, "100n", "VCC_MCU", "GND")
    P.two("C204", "Device:C", X1, Y0 + 5 * DY, "1u", "VBUS_MCU", "GND", value="1u 25V")
    # C · SWD
    P.place("J201", "Connector_Generic:Conn_02x05_Odd_Even", X1, g(50), 0, "SWD 2x5 1.27",
            "Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD",
            {"1": "VCC_MCU", "2": "SWDIO", "3": "GND", "4": "SWDCLK", "5": "GND", "6": "NC", "7": "NC", "8": "NC",
             "9": "GND", "10": "SWD_RST"},
            **{"LCSC Part": "C41376037", "MPN": "HX PZ1.27-2x5P TP", "Manufacturer": "HANXIA",
               "Datasheet": DS + "HX_PZ1.27-2x5P_TP_C41376037.pdf"})
    # D · UART de depuración
    for i, (ref, net) in enumerate((("TP201", "DBG_TX"), ("TP202", "DBG_RX"), ("TP203", "GND"))):
        P.place(ref, "Connector:TestPoint", g(114 + 6 * i), g(50), 0, "TP", TPFP, {"1": net})
    P.rails_at(g(100), g(80))
    P.flag("VCC_MCU")
    return P


UFL = {"LCSC Part": "C5137195", "MPN": "BWU.FL-IPEX1", "Manufacturer": "BAT WIRELESS"}
UFL_FP = "easyeda2kicad:IPEX-SMD_BWIPX-1-001E"


# ====================================================================================================== hoja 03
def hoja03():
    P = Plan("03", {"LORA_SCK": "input", "LORA_MOSI": "input", "LORA_MISO": "output", "LORA_NSS": "input",
                    "LORA_BUSY": "output", "LORA_DIO1": "output", "LORA_NRST": "input", "LORA_RXEN": "input",
                    "LORA_TXEN": "input"})
    P.place("U301", "meshnode:E22-900MM22S", g(40), g(36), 0, "E22-900MM22S", "meshnode:E22-xxxMM22S",
            {"1": "3V3", "3": "LORA_NRST", "14": "LORA_NSS", "15": "LORA_SCK", "13": "LORA_MOSI", "12": "LORA_MISO",
             "2": "GND", "7": "GND", "16": "GND", "6": "LORA_ANT", "9": "TXEN", "10": "LORA_RXEN", "11": "LORA_BUSY",
             "20": "LORA_DIO1", "19": "DIO2", "18": "NC", "4": "NC", "5": "NC", "8": "NC", "17": "NC"},
            **{"MPN": "E22-900MM22S", "Manufacturer": "Ebyte",
               "Datasheet": DS + "E22-M+Series+Module_UserManual_EN.pdf"})
    X1, Y0, DY = g(80), g(24), 7.62
    P.two("R301", "Device:R", X1, Y0, "0R", "DIO2", "TXEN")
    P.two("R302", "Device:R", X1, Y0 + DY, "0R", "LORA_TXEN", "TXEN", value="0R DNP")
    P.two("R303", "Device:R", X1, Y0 + 2 * DY, "100k", "LORA_RXEN", "GND")
    P.two("C303", "Device:C", X1, Y0 + 4 * DY, "56p", "LORA_ANT", "GND", value="DNP",
          **{"LCSC Part": "", "MPN": "", "Manufacturer": "", "Description": "shunt de la π, C0G según medida (DNP)"})
    P.two("R304", "Device:R", X1, Y0 + 5 * DY, "0R", "LORA_ANT", "LORA_RF")
    P.two("C304", "Device:C", X1, Y0 + 6 * DY, "56p", "LORA_RF", "GND", value="DNP",
          **{"LCSC Part": "", "MPN": "", "Manufacturer": "", "Description": "shunt de la π, C0G según medida (DNP)"})
    P.two("C301", "Device:C", X1, Y0 + 8 * DY, "22u", "3V3", "GND", value="22u 10V")
    P.two("C302", "Device:C", X1, Y0 + 9 * DY, "100n", "3V3", "GND")
    P.place("J301", "meshnode:BWU.FL-IPEX1", g(110), g(30), 0, "U.FL LoRa", UFL_FP,
            {"1": "LORA_RF", "2": "GND", "3": "GND"}, **UFL)
    P.rails_at(g(80), g(80))
    return P


# ====================================================================================================== hoja 04
def hoja04():
    P = Plan("04", {"GNSS_TX": "input", "GNSS_RX": "output", "GNSS_PPS": "output", "GNSS_RST": "input"})
    nets = {"23": "V_GNSS", "22": "V_BCKP", "21": "GNSS_RXD", "20": "GNSS_TXD", "8": "GNSS_RST", "2": "SAFEBOOT",
            "4": "NC", "3": "GNSS_PPS", "10": "GND", "12": "GND", "13": "GND", "24": "GND", "11": "GNSS_RFIN",
            "9": "VCC_RF", "14": "NC"}
    nets.update({n: "NC" for n in ("1", "5", "6", "7", "15", "16", "17", "18", "19")})
    P.place("U401", "meshnode:E108-GN04S", g(40), g(36), 0, "E108-GN04S", "meshnode:E108-GN04S", nets,
            **{"MPN": "E108-GN04S", "Manufacturer": "Ebyte", "Datasheet": DS + "E108-GN04+Series_UserManual_EN_V1.3.pdf"})
    X1, Y0, DY = g(80), g(24), 7.62
    P.two("R402", "Device:R", X1, Y0, "1k", "GNSS_TX", "GNSS_RXD")
    P.two("R403", "Device:R", X1, Y0 + DY, "1k", "GNSS_RX", "GNSS_TXD")
    P.two("R401", "Device:R", X1, Y0 + 3 * DY, "1k", "3V3", "V_BCKP")
    P.two("C403", "Device:C", X1, Y0 + 4 * DY, "100n", "V_BCKP", "GND")
    P.two("C401", "Device:C", X1, Y0 + 6 * DY, "10u", "V_GNSS", "GND", value="10u 10V")
    P.two("C402", "Device:C", X1, Y0 + 7 * DY, "100n", "V_GNSS", "GND")
    P.two("R404", "Device:R", X1, Y0 + 8 * DY, "0R", "3V3", "V_GNSS", value="0R DNP")
    X2 = g(110)
    P.two("C404", "Device:C", X2, Y0, "56p", "GNSS_ANT", "GNSS_RFIN", value="56p C0G",
          **{"Datasheet": ""})
    P.two("L401", "Device:L", X2, Y0 + DY, "82n", "GNSS_ANT", "VCC_RF", fp="Inductor_SMD:L_0402_1005Metric",
          value="82nH (activa)", **{"LCSC Part": "C98002", "MPN": "LQG15HS82NJ02D", "Manufacturer": "Murata",
                                   "Description": "sólo con antena GNSS activa"})
    P.place("J401", "meshnode:BWU.FL-IPEX1", X2, Y0 + 4 * DY, 0, "U.FL GNSS", UFL_FP,
            {"1": "GNSS_ANT", "2": "GND", "3": "GND"}, **UFL)
    P.place("TP401", "Connector:TestPoint", X2, Y0 + 8 * DY, 0, "TP", TPFP, {"1": "SAFEBOOT"})
    P.rails_at(g(80), g(84))
    P.flag("V_BCKP")
    return P


# ====================================================================================================== hoja 05
def hoja05():
    P = Plan("05", {"I2C_SDA": "bidirectional", "I2C_SCL": "bidirectional", "IMU_INT1": "output",
                    "IMU_INT2": "output", "BTN_UP": "output", "BTN_OK": "output", "BTN_DOWN": "output",
                    "BUZZER": "input", "LED_STAT": "input"})
    X1, Y0, DY = g(24), g(20), 7.62
    # A · pull-ups del bus
    P.two("R501", "Device:R", X1, Y0, "4k7", "3V3", "I2C_SDA")
    P.two("R502", "Device:R", X1, Y0 + DY, "4k7", "3V3", "I2C_SCL")
    # B · SHT41 · C · OLED + Qwiic
    P.place("U501", "meshnode:SHT41-P-NF", g(64), g(22), 0, "SHT41-P-NF", "easyeda2kicad:DFN-4_L1.5-W1.5-SHT41-AD1B-R2",
            {"3": "3V3", "4": "GND", "1": "I2C_SDA", "2": "I2C_SCL"},
            **{"LCSC Part": "C55108905", "MPN": "SHT41-P-NF", "Manufacturer": "Nyfea",
               "Datasheet": DS + "Nyfea SHT41-P-NF.pdf"})
    P.place("DS501", "meshnode:HS91L02W2C01", g(64), g(34), 0, "HS91L02W2C01",
            "easyeda2kicad:OLED-TH_L38.0-W12.0_HS91L02W2C01",
            {"2": "3V3", "1": "GND", "4": "I2C_SDA", "3": "I2C_SCL"},
            **{"LCSC Part": "C5248081", "MPN": "HS91L02W2C01", "Manufacturer": "HS", "Datasheet": DS + "HS91L02W2C01.pdf"})
    P.place("J501", "Connector_Generic_MountingPin:Conn_01x04_MountingPin", g(64), g(48), 0, "Qwiic 1.0T-4P",
            "meshnode:BOOMELE_1.0T-4P_1x04-1MP_P1.00mm_Horizontal",
            {"1": "GND", "2": "3V3", "3": "I2C_SDA", "4": "I2C_SCL", "MP": "NC"},
            **{"LCSC Part": "C970137", "MPN": "1.0T-4P", "Manufacturer": "BOOMELE", "Datasheet": DS + "1.0T-4P.pdf"})
    P.two("C501", "Device:C", X1, Y0 + 3 * DY, "100n", "3V3", "GND")
    P.two("C502", "Device:C", X1, Y0 + 4 * DY, "1u", "3V3", "GND", value="1u 25V")
    # G · IMU
    P.place("U502", "Sensor_Motion:LSM6DS3", g(110), g(30), 0, "LSM6DS3TR-C", "easyeda2kicad:LGA-14_L3.0-W2.5-P0.50-TL",
            {"8": "3V3", "5": "3V3", "12": "3V3", "1": "GND", "2": "GND", "3": "GND", "6": "GND", "7": "GND",
             "14": "I2C_SDA", "13": "I2C_SCL", "4": "IMU_INT1", "9": "IMU_INT2", "10": "NC", "11": "NC"},
            **{"LCSC Part": "C967633", "MPN": "LSM6DS3TR-C", "Manufacturer": "STMicroelectronics",
               "Datasheet": DS + "LSM6DS3TR-C.pdf"})
    for k, d in (("5", "up"), ("8", "up"), ("6", "down"), ("7", "down")):
        P.override[f"U502.{k}"] = (2.54, d)
    P.two("C503", "Device:C", X1, Y0 + 6 * DY, "100n", "3V3", "GND")
    P.two("C504", "Device:C", X1, Y0 + 7 * DY, "100n", "3V3", "GND")
    # D · botones · E · LED
    SWF = {"LCSC Part": "C25168837", "MPN": "HX TS35CA 160gf", "Manufacturer": "Hanxia",
           "Datasheet": DS + "HX_TS35CA_160gf_C25168837.pdf"}
    for i, (ref, net) in enumerate((("SW501", "BTN_UP"), ("SW502", "BTN_OK"), ("SW503", "BTN_DOWN"))):
        P.place(ref, "easyeda2kicad:HXTS35CA160GF", g(24), g(64 + 6 * i), 0, "HX TS35CA 160gf",
                "easyeda2kicad:KEY-SMD_HX-TS35CA-250GF", {"2": net, "1": "GND", "3": "GND", "4": "GND"}, **SWF)
    P.two("R503", "Device:R", g(64), g(64), "470R", "LED_STAT", "D501_A")
    P.place("D501", "Device:LED", g(64), g(64) + DY, 180, "LED verde", LED0603, {"2": "D501_A", "1": "GND"},
            **{"LCSC Part": "C7371903", "MPN": "XL-1608UGC-06A", "Manufacturer": "XINGLIGHT",
               "Datasheet": DS + "XL-1608UGC-06A.pdf"})
    # F · zumbador
    X3, Y3 = g(110), g(64)
    P.two("R506", "Device:R", X3, Y3, "10R", "VSYS", "BZ_P", value="10R 0603")
    P.two("R507", "Device:R", X3, Y3 + DY, "10R", "VSYS", "BZ_P", value="10R 0603")
    P.place("BZ501", "meshnode:HYG-5020A", X3, Y3 + 3 * DY, 0, "HYG-5020A", "easyeda2kicad:BUZ-SMD_3P-L5.0-W5.0-P3.50-BL",
            {"1": "BZ_P", "2": "BZ_N", "3": "NC"},
            **{"LCSC Part": "C7544810", "MPN": "HYG-5020A", "Manufacturer": "Huayu", "Datasheet": DS + "HYG-5020A.pdf"})
    P.place("D502", "Diode:1N4148W", X3, Y3 + 5 * DY, 0, "1N4148W", "Diode_SMD:D_SOD-123", {"1": "BZ_P", "2": "BZ_N"},
            **{"LCSC Part": "C917030", "MPN": "1N4148W", "Manufacturer": "JSMSEMI", "Datasheet": DS + "1N4148W.pdf"})
    P.place("Q501", "Transistor_FET:BSS138", g(140), Y3 + 3 * DY, 0, "BSS138", "Package_TO_SOT_SMD:SOT-23",
            {"3": "BZ_N", "2": "GND", "1": "BZ_G"},
            **{"LCSC Part": "C27140738", "MPN": "BSS138", "Manufacturer": "HT (Jin Yu)", "Datasheet": DS + "BSS138.pdf"})
    P.two("R504", "Device:R", g(140), Y3, "220R", "BUZZER", "BZ_G")
    P.two("R505", "Device:R", g(140), Y3 + DY, "100k", "BZ_G", "GND")
    P.rails_at(g(80), g(92))
    return P


SHEETS = {"01": hoja01, "02": hoja02, "03": hoja03, "04": hoja04, "05": hoja05}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    num, out = sys.argv[1], sys.argv[2]
    plan = SHEETS[num]().build()
    json.dump(plan, open(os.path.join(out, f"plan_{num}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(plan["stats"], ensure_ascii=False))
