"""Hoja 05 · Interfaz — bus I²C (SHT41, OLED, Qwiic), botones, LED y zumbador (docs/05_interfaz.svg). Refs 5xx.
Fuentes: Nyfea SHT41-P-NF (pinout §4, 0x44), HS91L02W2C01 (SSD1306 0x3C, LDO 662K y pull-ups 4k7 propios),
nPM1300 PS v1.3 §6.11 (dirección 0b1101011 = 0x6B), HX TS35CA (pata 2 señal; 1, 3, 4 a GND, como ai_instruments)."""
import os

from svgkit import *  # noqa: F401,F403

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "05_interfaz.svg"))


def dibujar():
    W, H = 1720, 1440
    nueva(W, H, "05 · Interfaz — sensores, IMU, pantalla, botones, LED y zumbador",
          "nrf54lm20-meshnode · hoja 5 · referencias 5xx · intención de 05_interfaz.kicad_sch")
    leyenda(760, 40)

    # ---------------------------------------------------------------- A · bus I2C
    frame(20, 76, 540, 300, "A · Bus I²C (TWIM30, 400 kHz)")
    for x, ref, net in ((120, "R501", "I2C_SDA"), (300, "R502", "I2C_SCL")):
        label(x, 130, "3V3", "pwr", "middle"); P([(x, 139), (x, 150)])
        res_v(x, 150, ref, "4,7 kΩ", 50); P([(x, 200), (x, 215)]); label(x, 224, net, "sig", "middle")
    tabla(20, 248, 540, [40, 120, 260], ["Dir.", "Dispositivo", "Nota"],
          [("0x6B", "nPM1300 (hoja 01)", "PMIC; el firmware lo configura al arrancar"),
           ("0x6A", "LSM6DS3TR-C (U502)", "IMU · SA0 a GND (0x6B está ocupada)"),
           ("0x44", "SHT41-P-NF (U501)", "temperatura y humedad"),
           ("0x3C", "OLED HS91L02W2C01", "SSD1306 128×32 (0x78 en 8 bits)"),
           ("—", "Qwiic J501", "sensores externos")], dy=20, mono=(0,))

    # ---------------------------------------------------------------- B · SHT41
    frame(580, 76, 540, 300, "B · Temperatura y humedad — SHT41-P-NF")
    e, _ = ic2(760, 140, 110, "U501", "SHT41-P-NF · DFN-4", [("3", "VDD"), ("4", "VSS")], [("1", "SDA"), ("2", "SCL")],
               pitch=26)
    pin_labels(e, {"3": ("3V3", "pwr"), "4": ("", "gnd"), "1": ("I2C_SDA", "sig"), "2": ("I2C_SCL", "sig")})
    caps_to_gnd(700, 250, "3V3", "pwr", [("C501", "100 nF")])
    notes(600, 330, ["En un canto, con ranura de aislamiento térmico; lejos del nPM1300, LEDs y E22.",
                     "Hueco en la caja frente al sensor. Meshtastic lo detecta solo (SHT4x)."])

    # ---------------------------------------------------------------- C · OLED + Qwiic
    frame(1140, 76, 560, 300, "C · Pantalla OLED 0,91\" y conector Qwiic")
    e, _ = ic2(1270, 140, 100, "DS501", "HS91L02W2C01", [("2", "VCC"), ("1", "GND")], [("4", "SDA"), ("3", "SCL")],
               pitch=26)
    pin_labels(e, {"2": ("3V3", "pwr"), "1": ("", "gnd"), "4": ("I2C_SDA", "sig"), "3": ("I2C_SCL", "sig")})
    caps_to_gnd(1200, 250, "3V3", "pwr", [("C502", "1 µF")])
    e, _ = ic2(1560, 230, 70, "J501", "1.0T-4P · Qwiic", [("1", "GND"), ("2", "3V3"), ("3", "SDA"), ("4", "SCL")], [],
               pitch=22, stub=16)
    pin_labels(e, {"1": ("", "gnd"), "2": ("3V3", "pwr"), "3": ("I2C_SDA", "sig"), "4": ("I2C_SCL", "sig")})
    notes(1156, 345, ["OLED en tira de 4 pines a 2,54 (38×12 mm): sus pull-ups de 4k7 van a su LDO.",
                      ("🚨 Siempre alimentados: si se cortara 3V3, hundirían el I²C del PMIC.", "tw")])

    # ---------------------------------------------------------------- D · botones
    frame(20, 390, 540, 300, "D · Botones laterales (HX TS35CA, ángulo recto)")
    for i, (ref, net, txt) in enumerate((("SW501", "BTN_UP", "↑"), ("SW502", "BTN_OK", "OK"),
                                          ("SW503", "BTN_DOWN", "↓"))):
        x = 110 + i * 160
        label(x, 445, net, "sig", "middle"); P([(x, 454), (x, 466)])
        sw_v(x, 466, ref, txt, 56); gnd(x, 522)
    notes(40, 580, ["Pata 2 = señal; 1, 3 y 4 (pestañas) a GND, como en ai_instruments.",
                    "Pull-up interno del nRF54 (BUTTON_NEED_PULLUP); antirrebote por software.",
                    "OK = BUTTON1 de Meshtastic (corta: siguiente pantalla · larga: menú);",
                    "↑/↓ = entrada de navegación (menús y canned messages).",
                    "En el canto opuesto a las antenas; el botón PWR (hoja 01) aparte."], dy=18)

    # ---------------------------------------------------------------- E · LED
    frame(580, 390, 360, 300, "E · LED de estado del MCU")
    label(700, 445, "LED_STAT", "sig", "middle"); P([(700, 454), (700, 466)])
    res_v(700, 466, "R503", "470 Ω", 50); led_v(700, 516, "D501", "verde XL-1608UGC", 44); gnd(700, 560)
    notes(596, 610, ["Activo alto desde P2.00 (PIN_LED1, LED_STATE_ON 1).",
                     "Vf 2,4–3,0 V a 20 mA (≈ 2,4 V a 2 mA) ⇒ (3,3−2,4)/470",
                     "≈ 1,9 mA: se ve y gasta poco."])

    # ---------------------------------------------------------------- F · zumbador
    frame(960, 390, 740, 300, "F · Zumbador magnético HYG-5020A (PWM)")
    X = 1180
    label(X, 432, "VSYS", "pwr", "middle"); P([(X, 441), (X, 452)]); dot(X, 452)
    P([(X - 22, 452), (X + 22, 452)]); P([(X - 22, 488), (X + 22, 488)]); dot(X, 488)
    res_v(X - 22, 452, "R506", "10 Ω", 36, side="l"); res_v(X + 22, 452, "R507", "10 Ω", 36)
    P([(X, 488), (X, 498)]); dot(X, 498)
    buzzer(X, 498, "BZ501", "HYG-5020A")
    T(X + 20, 498 + 51, "pata 3 NC", "pn")
    P([(X, 498), (X + 110, 498)]); diode_v(X + 110, 498, "D502", "1N4148W", 54); P([(X, 552), (X + 110, 552)])
    dot(X, 552); P([(X, 552), (X, 562)])
    nmos(X, 562, "Q501", "BSS138"); gnd(X, 622)
    label(1060, 592, "BUZZER", "sig", "end"); res_h(1060, 592, "R504", "220 Ω", 52); P([(1112, 592), (X - 34, 592)])
    dot(1126, 592); res_v(1126, 592, "R505", "100 kΩ", 36, side="l"); gnd(1126, 628)
    notes(1372, 436, ["Magnético, resuena a 4 kHz; bobina 12 ± 5 Ω;",
                      "2–4 Vp-p (3 V nominal ⇒ 110 mA a 50 %).",
                      "Desde VSYS (batería 3,0–4,2 V; ≈ 5 V con USB):",
                      "los bucks dan 200 mA y el E22 ya pide 140 en TX.",
                      "R506 ∥ R507 = 5 Ω: con 5 V la bobina ve 3,2 V",
                      "(0,27 A de pico); con 3,6 V, 2,3 V. ≈ 0,1 W en",
                      "cada 0603 sólo mientras suena.",
                      "D502 libre circulación · R505 corta Q501 con",
                      "el pin en alta impedancia · PIN_BUZZER P1.09."], dy=18)
    notes(1372, 622, ["BSS138 (HT): 0,34 A cont., 1,5 Ω típ. a 4,5 V;",
                      "1N4148W: 300 mA cont. ⇒ los dos aguantan 0,27 A."], dy=18)

    # ---------------------------------------------------------------- tabla
    rows = [("R501 R502", "4,7 kΩ 1 %", "Yageo RC0402FR-074K7L", "0402", "C105871", "cajón #39"),
            ("U501", "temp./humedad", "Nyfea SHT41-P-NF", "DFN-4 1,5×1,5", "C55108905", "cajón #58 (3)"),
            ("C501", "100 nF", "Samsung CL05B104KO5NNNC", "0402", "C1525", "cajón #22"),
            ("DS501", "OLED 0,91\" 128×32", "HS HS91L02W2C01", "TH 4p 2,54", "C5248081", "COMPRAR"),
            ("C502", "1 µF 25 V", "Samsung CL05A105KA5NQNC", "0402", "C52923", "cajón #23"),
            ("J501", "Qwiic 1 mm (á. recto)", "BOOMELE 1.0T-4P (clon SH)", "SMD", "C970137", "cajón #203"),
            ("SW501-SW503", "pulsador lateral", "Hanxia HX TS35CA 160gf", "SMD á. recto", "C25168837", "cajón #65"),
            ("R503", "470 Ω", "UNI-ROYAL 0402WGF4700TCE", "0402", "C25117", "cajón #35"),
            ("D501", "LED verde", "XINGLIGHT XL-1608UGC-06A", "0603", "C7371903", "cajón #42"),
            ("BZ501", "zumbador magnético 4 kHz", "Huayu HYG-5020A", "SMD 5×5", "C7544810", "COMPRAR"),
            ("R506 R507", "10 Ω 5 % (∥ = 5 Ω)", "genérica 125 mW", "0603", "—", "cajón #139"),
            ("Q501", "N-MOS", "HT BSS138", "SOT-23", "C27140738", "cajón #151"),
            ("D502", "diodo", "JSMSEMI 1N4148W", "SOD-123", "C917030", "cajón #51"),
            ("R504", "220 Ω 1 %", "UNI-ROYAL 0402WGF2200TCE", "0402", "C25091", "cajón #32"),
            ("R505", "100 kΩ 1 %", "Yageo RC0402FR-07100KL", "0402", "C60491", "cajón #11"),
            ("U502", "IMU 6 ejes (acel. + giro)", "ST LSM6DS3TR-C", "LGA-14 2,5×3", "C967633", "COMPRAR"),
            ("C503 C504", "100 nF 16 V X7R", "Samsung CL05B104KO5NNNC", "0402", "C1525", "cajón #22")]

    # ---------------------------------------------------------------- G · IMU
    frame(20, 704, 1680, 300, "G · IMU LSM6DS3TR-C — despertar al mover la placa")
    e, _ = ic2(330, 770, 130, "U502", "LSM6DS3TR-C · LGA-14",
               [("8", "VDD"), ("5", "VDDIO"), ("12", "CS"), None, ("1", "SDO/SA0"), ("2", "SDx"), ("3", "SCx"), None,
                ("6", "GND"), ("7", "GND")],
               [("14", "SDA"), ("13", "SCL"), None, ("4", "INT1"), ("9", "INT2"), None, ("10", "NC"), ("11", "NC")],
               pitch=21, top_pad=16)
    pin_labels(e, {"8": ("3V3", "pwr"), "5": ("3V3", "pwr"), "12": ("3V3", "pwr"), "1": ("", "gnd"),
                   "2": ("", "gnd"), "3": ("", "gnd"), "6": ("", "gnd"), "7": ("", "gnd"),
                   "14": ("I2C_SDA", "sig"), "13": ("I2C_SCL", "sig"), "4": ("IMU_INT1", "sig"),
                   "9": ("IMU_INT2", "sig"), "10": ("", "nc"), "11": ("", "nc")})
    caps_to_gnd(660, 780, "3V3", "pwr", [("C503", "100 nF"), ("C504", "100 nF")], dx=80)
    notes(600, 880, ["C503 junto a VDD (8), C504 junto a VDDIO (5)."])
    notes(900, 750, [
        "Uso principal: despertar el nodo al moverlo (wake-up del acelerómetro → INT1).",
        "INT1 → P0.02: el puerto P0 tiene «sense» y despierta al nRF54LM20 de System OFF (P2 no).",
        "INT2 → P0.05 (doble toque, orientación…). Salidas push-pull, activas a nivel alto y a 0",
        "tras el reset ⇒ sin pull-ups. En 3V3 siempre vivo: acelerómetro a 12,5 Hz ≈ 9 µA.",
        "SA0 a GND ⇒ 0x6A (0x6B es del nPM1300; Meshtastic busca el LSM6DS3 en 0x6A).",
        "CS a 3V3 = modo I²C · SDx/SCx (maestro I²C auxiliar) a GND · 10 y 11 al aire, soldados.",
        "Pegado al PCB, lejos del zumbador; la orientación da igual (la corrige el firmware)."], dy=19)
    add('<rect x="892" y="896" width="796" height="94" rx="4" class="symp"/>')
    notes(900, 914, [
        "Firmware: el driver LSM6DS3 de Meshtastic sólo sondea shake() con el MCU despierto. Para",
        "despertar: enrutar el wake-up a INT1 (configInt1 …, wakeup), enclavarla (LIR) y armar SENSE alto",
        "en P0.02 antes de System OFF. Además, el escáner I²C toma 0x6B (nPM1300) por un «QMI8658»:",
        "la variante debe evitarlo."], "tp", dy=19)

    frame(20, 1018, 1680, 400, "Piezas de la hoja")
    tabla(20, 1058, 1680, [40, 200, 420, 760, 940, 1100], ["Ref.", "Qué es", "Pieza", "Encapsulado", "LCSC", "Stock"],
          rows, dy=20, mono=(0, 4))
    guardar(OUT)


if __name__ == "__main__":
    dibujar()
