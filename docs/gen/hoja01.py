"""Hoja 01 · Alimentación — USB-C, nPM1300, batería (docs/01_alimentacion.svg). Referencias 1xx.
Fuentes: nPM1300 PS v1.3 (§6.1 VBUS 100 mA por defecto, tablas 17/18 VSET, tabla 11 NTC, §8 aplicación,
§9.3 Configuration 1 y 3), KH-TYPE-C-16P (símbolo global), TPD4E05U06 (KiCad Power_Protection)."""
import os

from svgkit import *  # noqa: F401,F403

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "01_alimentacion.svg"))


def dibujar():
    W, H = 1720, 1690
    nueva(W, H, "01 · Alimentación — USB-C, nPM1300, batería",
          "nrf54lm20-meshnode · hoja 1 · referencias 1xx · intención de 01_alimentacion.kicad_sch")
    leyenda(760, 40)

    # ---------------------------------------------------------------- A · USB-C + ESD
    frame(20, 76, 600, 470, "A · USB-C (KH-TYPE-C-16P) + ESD")
    e, _ = conn_l(50, 130, "J101", "KH-TYPE-C-16P · C709357",
                  [("A4/B9", "VBUS"), ("A9/B4", "VBUS"), None, ("A5", "CC1"), ("B5", "CC2"), None,
                   ("A6/B6", "DP1/DP2"), ("A7/B7", "DN1/DN2"), None, ("A8", "SBU1"), ("B8", "SBU2"), None,
                   ("A1/B12", "GND"), ("A12/B1", "GND"), ("SH1-4", "SHIELD")], pitch=22, w=140, stub=40)
    xr, y1, y2 = e["A4/B9"][0], e["A4/B9"][1], e["A9/B4"][1]
    P([e["A9/B4"], (xr + 14, y2), (xr + 14, y1)]); dot(xr + 14, y1)
    P([(xr, y1), (xr + 130, y1)], "pw"); dot(xr + 70, y1)
    diode_v(xr + 70, y1, "D101", "ESD5Z6.0", 44, "r", "tvs"); gnd(xr + 70, y1 + 44)
    label(xr + 130, y1, "VBUS", "pwr")
    label(e["A5"][0], e["A5"][1], "CC1", "loc"); label(e["B5"][0], e["B5"][1], "CC2", "loc")
    label(e["A6/B6"][0], e["A6/B6"][1], "USB_DP", "sig"); label(e["A7/B7"][0], e["A7/B7"][1], "USB_DM", "sig")
    nc(*e["A8"]); nc(*e["B8"])
    for k in ("A1/B12", "A12/B1", "SH1-4"):
        x, y = e[k]; P([(x, y), (x + 14, y)]); gnd(x + 14, y)
    notes(36, 506, ["DP1/DP2 y DN1/DN2 unidos en el conector (USB 2.0 reversible). SBU sin uso.",
                    "Blindaje directo a GND (aparato a batería, sin chasis)."])
    e2, h2 = ic2(410, 226, 100, "U102", "TPD4E05U06DQAR · DOWO", [("1", "D1+"), ("2", "D1-"), ("4", "D2+"), ("5", "D2-")],
                 [("10", "NC·D1+"), ("9", "NC·D1-"), ("7", "NC·D2+"), ("6", "NC·D2-"), None, ("3", "GND"),
                  ("8", "GND")], pitch=22, top_pad=16, stub=18)
    for a, b, n, kind in (("1", "10", "USB_DP", "sig"), ("2", "9", "USB_DM", "sig"), ("4", "7", "CC1", "loc"),
                          ("5", "6", "CC2", "loc")):
        label(e2[a][0], e2[a][1], n, kind, "end"); label(e2[b][0], e2[b][1], n, kind)
    for k in ("3", "8"):
        x, y = e2[k]; P([(x, y), (x + 10, y)]); gnd(x + 10, y)
    notes(330, 410, ["Cj 0,4 pF típ. / 0,5 máx. (I/O–GND, datasheet",
                     "DOWO) ⇒ vale para USB HS: el del cajón sirve.",
                     "NC 10/9/7/6 enfrente de 1/2/4/5 y unidos a su",
                     "red: la pista cruza recta los dos pads."], dy=18)

    # ---------------------------------------------------------------- B · nPM1300
    frame(640, 76, 600, 720, "B · PMIC nPM1300-QEAA (QFN32, EP = AVSS)")
    L = [("21", "VBUS"), ("22", "VBUSOUT"), ("23", "CC1"), ("24", "CC2"), None, ("19", "VBAT"), ("18", "NTC"), None,
         ("12", "VDDIO"), ("13", "SDA"), ("14", "SCL"), None, ("7", "GPIO0"), ("8", "GPIO1"), ("9", "GPIO2"),
         ("10", "GPIO3"), ("11", "GPIO4"), None, ("15", "SHPHLD"), ("17", "VSET1"), ("16", "VSET2")]
    R = [("20", "VSYS"), ("4", "PVDD"), None, ("3", "SW1"), ("1", "VOUT1"), ("2", "PVSS1"), None, ("5", "SW2"),
         ("32", "VOUT2"), ("6", "PVSS2"), None, ("28", "LSIN1/VINLDO1"), ("29", "LSOUT1/VOUTLDO1"),
         ("30", "LSIN2/VINLDO2"), ("31", "LSOUT2/VOUTLDO2"), None, ("25", "LED0"), ("26", "LED1"), ("27", "LED2"),
         None, ("33", "AVSS (EP)")]
    eb, hb = ic2(850, 140, 190, "U101", "nPM1300-QEAA · C7501206", L, R, pitch=26)
    pin_labels(eb, {"21": ("VBUS", "pwr"), "22": ("VBUS_MCU", "sig"), "23": ("CC1", "loc"), "24": ("CC2", "loc"),
                    "19": ("VBAT", "pwr"), "18": ("NTC", "loc"), "12": ("3V3", "pwr"), "13": ("I2C_SDA", "sig"),
                    "14": ("I2C_SCL", "sig"), "7": ("GNSS_EN", "sig"), "8": ("PMIC_INT", "sig"), "9": ("", "nc"),
                    "10": ("", "nc"), "11": ("", "nc"), "15": ("SHPHLD", "loc"), "17": ("VSET1", "loc"),
                    "16": ("VSET2", "loc"), "20": ("VSYS", "pwr"), "4": ("VSYS", "pwr"), "3": ("SW1", "loc"),
                    "1": ("V_GNSS", "pwr"), "2": ("", "gnd"), "5": ("SW2", "loc"), "32": ("3V3", "pwr"),
                    "6": ("", "gnd"), "28": ("", "gnd"), "29": ("", "gnd"), "30": ("", "gnd"), "31": ("", "gnd"),
                    "25": ("LED0", "loc"), "26": ("LED1", "loc"), "27": ("", "nc"), "33": ("", "gnd")})
    notes(656, 140 + hb + 22, [
        "GPIO0 ← MCU: el firmware la asigna a BUCKENCTRL (enciende BUCK1 = GNSS) ⇒ PIN_GPS_EN.",
        "GPIO1 → MCU: interrupción (VBUS, carga, botón). GPIO2-4 libres (pull-down interno de serie).",
        "LSIN/LSOUT 1-2 sin uso ⇒ a GND, como la «Configuration 3» de Nordic (PS v1.3 §9.3.3).",
        "PVSS1/2 a GND con vía junto al pad · EP con 5 vías térmicas (huella nPM1300-QFN32-EP3.5)."])

    # ---------------------------------------------------------------- C · bucks
    frame(1260, 76, 440, 300, "C · Bucks (L 2,2 µH APH201610C2R2MP01, 0806)")
    for yy, sw, ref, cref, net, txt in (
            (140, "SW1", "L101", "C107", "V_GNSS", ["BUCK1 = raíl del GNSS: APAGADO al arrancar (VSET1 a GND).",
                                                    "El firmware lo pone a 3,3 V y lo enciende con GPIO0."]),
            (270, "SW2", "L102", "C108", "3V3", ["BUCK2 = 3V3 principal desde el arranque (VSET2 330 kΩ).",
                                                 "Pico: E22 140 + MCU ~15 + OLED ~20 = 175 de 200 mA."])):
        label(1300, yy, sw, "loc", "end"); ind_h(1300, yy, ref, "2,2 µH", 90); P([(1390, yy), (1470, yy)], "pw")
        dot(1430, yy); cap_v(1430, yy, cref, "10 µF", 44); gnd(1430, yy + 44); label(1470, yy, net, "pwr")
        notes(1280, yy + 72, txt)

    # ---------------------------------------------------------------- D · VSET
    frame(1260, 390, 440, 180, "D · Tensión de arranque de los bucks (tablas 17/18)")
    label(1330, 440, "VSET1", "loc", "end"); P([(1330, 440), (1350, 440)]); res_v(1350, 440, "R101", "0 Ω", 50)
    gnd(1350, 490)
    label(1510, 440, "VSET2", "loc", "end"); P([(1510, 440), (1530, 440)])
    res_v(1530, 440, "R102", "330 kΩ 5 %", 50); gnd(1530, 490)
    notes(1280, 530, ["R101 0 Ω ⇒ BUCK1 apagado (con 330 kΩ arrancaría a 2,7 V).",
                      "R102 250–500 kΩ ⇒ 3,3 V: 330 kΩ 5 % (313–347 kΩ) basta. Comprar."])

    # ---------------------------------------------------------------- G · botón y LEDs
    frame(1260, 584, 440, 330, "G · Botón de encendido y LEDs de carga")
    label(1310, 640, "SHPHLD", "loc", "end"); P([(1310, 640), (1330, 640)]); sw_v(1330, 640, "SW101", "PWR · HX TS35CA", 56)
    gnd(1330, 696)
    notes(1280, 740, ["Pata 2 = SHPHLD; 1, 3, 4 a GND.", "Sale del ship mode;", "larga = reset duro."])
    for yy, ref, val, net in ((630, "D102", "azul · ERROR", "LED0"), (740, "D103", "verde · CARGA", "LED1")):
        label(1570, yy, "VSYS", "pwr", "end"); P([(1570, yy), (1590, yy)])
        led_v(1590, yy, ref, val, 44); P([(1590, yy + 44), (1590, yy + 56)]); label(1590, yy + 65, net, "loc", "middle")
    notes(1280, 846, ["LEDDRV = sumidero de 5 mA: sin resistencia (como la referencia).",
                      "Por defecto LED0 = error del cargador, LED1 = cargando. LED2 sin uso.",
                      "Azul Vf 2,6–3,4 V: lucen con USB (VSYS ≈ VBUS), que es cuando carga."], dy=19)

    # ---------------------------------------------------------------- E · desacoplo
    frame(20, 560, 600, 380, "E · Desacoplo del nPM1300 (BOM de la Configuration 1)")
    caps_to_gnd(110, 620, "VBUS", "pwr", [("C101", "1 µF 25 V")])
    caps_to_gnd(110, 730, "VBUS_MCU", "sig", [("C102", "1 µF 25 V")])
    caps_to_gnd(380, 620, "VSYS", "pwr", [("C103", "10 µF"), ("C104", "10 µF"), ("C105", "10 µF")])
    caps_to_gnd(380, 730, "VBAT", "pwr", [("C106", "2,2 µF 16 V")])
    caps_to_gnd(380, 840, "3V3", "pwr", [("C110", "100 nF")])
    notes(36, 836, ["C101/C102 junto a VBUS/VBUSOUT; C103-C105", "repartidos entre VSYS (20) y PVDD (4);",
                    "C110 en VDDIO (12). VBUS_MCU = VBUSOUT (OVP,", "7,5 Ω) → VBUS del ME54BS13: sólo PHY USB."])

    # ---------------------------------------------------------------- H · puntos de prueba
    frame(640, 810, 600, 110, "H · Puntos de prueba")
    for i, (r, n) in enumerate((("TP101", "VBUS"), ("TP102", "VBAT"), ("TP103", "VSYS"),
                                ("TP104", "3V3"), ("TP105", "V_GNSS"), ("TP106", "GND"))):
        x, y = 668 + (i % 3) * 190, 856 + (i // 3) * 36
        tp(x, y, r); label(x + 52, y, n, "pwr")

    # ---------------------------------------------------------------- F · batería
    frame(640, 934, 1060, 250, "F · Batería LiPo 1S (JST PH 2.0) · NTC · medida de VBAT")
    e3, _ = conn_l(670, 1004, "J102", "JST PH 2.0 SMD 2p", [("1", "+"), ("2", "−")], pitch=26, w=110)
    label(e3["1"][0], e3["1"][1], "VBAT", "pwr"); P([e3["2"], (e3["2"][0] + 12, e3["2"][1])]); gnd(e3["2"][0] + 12, e3["2"][1])
    notes(660, 1096, [("🚨 La polaridad de los packs PH 2.0 NO es estándar:", "tw"),
                      "comprobarla antes de enchufar (pata 1 = +).",
                      "El pack debe llevar su protección (PCM): el nPM1300",
                      "no corta por sobredescarga ni sobrecorriente."])
    label(1090, 990, "NTC", "loc", "end"); P([(1090, 990), (1110, 990)]); res_v(1110, 990, "RT101", "NTC 10k B3380", 50)
    gnd(1110, 1040)
    notes(1040, 1088, ["NCP15XH103F0SRC (cajón): 10 kΩ ±1 %,", "B25/50 3380 K = tabla 11 del nPM1300.",
                       "Junto al conector de batería (el pack", "no trae NTC)."])
    label(1400, 990, "VBAT", "pwr", "end"); P([(1400, 990), (1420, 990)]); res_v(1420, 990, "R103", "1 MΩ", 46)
    dot(1420, 1036); P([(1420, 1036), (1440, 1036)]); label(1440, 1036, "VBAT_SENSE", "sig")
    res_v(1420, 1036, "R104", "1 MΩ", 46, side="l"); gnd(1420, 1082)
    P([(1540, 1036), (1600, 1036)]); dot(1600, 1036)
    cap_v(1600, 1036, "C111", "100 nF", 40); gnd(1600, 1076)
    notes(1330, 1120, ["VBAT/2 → AIN2 (P1.30); 2 µA de consumo.", "Respaldo para BATTERY_PIN si no hay driver."])

    # ---------------------------------------------------------------- I · firmware
    frame(20, 954, 600, 250, "I · Lo que tiene que hacer el firmware (driver nPM1300)", "framep")
    notes(36, 992, [
        "Tras un reset: cargador APAGADO, VTERM 3,60 V, ICHG 32 mA, VBUS 100 mA, BUCK1 apagado.",
        "1. VBUSINILIM0 = 500 mA tras leer CC (USBCDETECTSTATUS) + TASK.UPDATE.ILIMSW.",
        "2. ADCNTCRSEL = 10 k · BCHGVTERM = 4,20 V · BCHGISET = 0,5 C · BCHGENABLESET = 1.",
        "3. BUCK1NORMVOUT = 3,3 V + BUCKSWCTRLSEL · BUCKENCTRL: GPIO0 → BUCK1.",
        "4. GPIOMODE1 = salida de IRQ (→ PMIC_INT): VBUS, carga y SHPHLD.",
        "5. Batería: ADC del nPM1300 por I²C, o VBAT_SENSE con BATTERY_PIN.",
        ("🚨 Sin driver: LoRa y BLE van (3V3 arranca solo); NO carga y el GNSS no enciende.", "tw"),
        ("🚨 Sólo USB, sin batería: 100 mA de VBUS no dan para TX LoRa hasta subir el límite.", "tw"),
    ], dy=19)

    # ---------------------------------------------------------------- notas y tabla
    frame(20, 1218, 600, 456, "Notas de diseño")
    notes(36, 1250, [
        "• nPM1300 a ≥ 20 mm del ME54BS13 (Minew §7.2: DC-DC lejos).",
        "• Bucles SW–L–C mínimos; inductores blindados; PVSS con su vía.",
        "• VBUS_MCU sólo para el PHY USB del módulo: no es una fuente.",
        "• 3V3 = raíl de E/S de todo lo digital ⇒ sin problemas de niveles.",
        "• OLED y Qwiic SIEMPRE en 3V3: sus pull-ups hundirían el I²C del PMIC",
        "  si se les cortara la alimentación.",
        "• Huellas: J102 = Connector_JST:JST_PH_S2B-PH-SM4-TB (KiCad,",
        "  pads MP sin conectar); D101 = SOD-523 easyeda (1 = cátodo).",
    ], dy=21)
    rows = [
        ("J101", "USB-C 16P", "Kinghelm KH-TYPE-C-16P", "SMD", "C709357", "cajón #112"),
        ("U101", "PMIC", "Nordic nPM1300-QEAA", "QFN32 5×5", "C7501206", "COMPRAR"),
        ("U102", "ESD 4 líneas", "TPD4E05U06DQAR (DOWO)", "DFN2510-10", "C22390021", "cajón #20"),
        ("D101", "ESD de VBUS", "onsemi ESD5Z6.0T1G", "SOD-523", "C82323", "cajón #205"),
        ("L101 L102", "2,2 µH 130 mΩ 2,8 A", "APV APH201610C2R2MP01", "0806 (2016)", "C42455301", "COMPRAR"),
        ("C101 C102", "1 µF 25 V X5R", "Samsung CL05A105KA5NQNC", "0402", "C52923", "cajón #23"),
        ("C103-105 C107 C108", "10 µF 10 V X7R", "—", "0603", "—", "cajón #147"),
        ("C106", "2,2 µF 16 V X5R", "Samsung CL10A225KO8NNNC", "0603", "C23630", "cajón #60"),
        ("C110 C111", "100 nF 16 V X7R", "Samsung CL05B104KO5NNNC", "0402", "C1525", "cajón #22"),
        ("R101", "0 Ω", "Yageo RC0402FR-070RL", "0402", "C106231", "cajón #10"),
        ("R102", "330 kΩ 5 %", "Yageo RC0402JR-07330KL", "0402", "C137882", "COMPRAR"),
        ("R103 R104", "1 MΩ 1 %", "Yageo RC0402FR-071ML", "0402", "C138033", "cajón #13"),
        ("RT101", "NTC 10k B3380", "Murata NCP15XH103F0SRC", "0402", "C91636", "cajón #61"),
        ("J102", "batería", "JST S2B-PH-SM4-TB", "SMD", "C295747", "COMPRAR"),
        ("SW101", "pulsador lateral", "Hanxia HX TS35CA 160gf", "SMD á. recto", "C25168837", "cajón #65"),
        ("D102 / D103", "LED azul / verde", "XL-1608UBC-06A / UGC-06A", "0603", "C7371904/03", "cajón #41 / #42"),
        ("TP101-106", "punto de prueba", "TestPoint_Pad_D1.0mm", "Ø1 mm", "—", "—"),
    ]
    frame(640, 1198, 1060, 476, "Piezas de la hoja")
    tabla(640, 1238, 1060, [660, 830, 960, 1210, 1320, 1430],
          ["Ref.", "Qué es", "Pieza", "Encapsulado", "LCSC", "Stock"], rows, dy=24, mono=(0, 4))
    guardar(OUT)


if __name__ == "__main__":
    dibujar()
