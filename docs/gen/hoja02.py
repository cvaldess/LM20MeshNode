"""Hoja 02 · MCU — ME54BS13 (nRF54LM20A), desacoplo, SWD, UART de depuración (docs/02_mcu.svg). Referencias 2xx.
Fuentes: Minew ME54BS13 datasheet v1.0.0 (pinout p.6-9, §7 PCB), nRF54LM20A datasheet v1.0 (clock pins p.1240,
SERIALxx por puerto, GPIOTE por puerto). El mapa de pines MAPA es la fuente para la captura y para la variante."""
import os

from svgkit import *  # noqa: F401,F403
from me54bs13_pads import pinmap as PADS  # pad -> nombre de puerto

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "02_mcu.svg"))

# señal -> (puerto, tipo de etiqueta, periférico / nota)
MAPA = {
    "LORA_SCK": ("P1.17", "sig", "SPIM22 SCK (clock pin) · castellado 16"),
    "LORA_MOSI": ("P1.16", "sig", "SPIM22 MOSI · castellado 17"),
    "LORA_MISO": ("P1.15", "sig", "SPIM22 MISO · castellado 18"),
    "LORA_NSS": ("P1.18", "sig", "GPIO · castellado 15"),
    "LORA_BUSY": ("P1.19", "sig", "GPIO entrada · castellado 14"),
    "LORA_DIO1": ("P1.23", "sig", "GPIOTE20 (IRQ) · castellado 13"),
    "LORA_NRST": ("P1.26", "sig", "GPIO · castellado 12"),
    "LORA_RXEN": ("P1.13", "sig", "GPIO (RadioLib RXEN)"),
    "LORA_TXEN": ("P1.12", "sig", "GPIO opcional (R302 DNP)"),
    "I2C_SDA": ("P0.03", "sig", "TWIM30 SDA (como la DK)"),
    "I2C_SCL": ("P0.04", "sig", "TWIM30 SCL (clock pin)"),
    "IMU_INT1": ("P0.02", "sig", "GPIOTE30 ← INT1 del LSM6DS3TR-C"),
    "IMU_INT2": ("P0.05", "sig", "GPIOTE30 ← INT2 del LSM6DS3TR-C"),
    "GNSS_TX": ("P1.03", "sig", "UARTE20 TXD → RXD del GNSS"),
    "GNSS_RX": ("P1.29", "sig", "UARTE20 RXD ← TXD del GNSS"),
    "GNSS_PPS": ("P1.04", "sig", "GPIOTE20 (PIN_GPS_PPS)"),
    "GNSS_RST": ("P1.00", "sig", "salida en drenador abierto"),
    "GNSS_EN": ("P1.05", "sig", "→ GPIO0 del nPM1300 (PIN_GPS_EN)"),
    "PMIC_INT": ("P1.06", "sig", "GPIOTE20 ← GPIO1 del nPM1300"),
    "VBAT_SENSE": ("P1.30", "sig", "AIN2 (BATTERY_PIN)"),
    "BTN_UP": ("P1.27", "sig", "GPIOTE20, pull-up interno"),
    "BTN_OK": ("P1.28", "sig", "GPIOTE20, pull-up interno (BUTTON1)"),
    "BTN_DOWN": ("P1.25", "sig", "GPIOTE20, pull-up interno"),
    "BUZZER": ("P1.09", "sig", "PWM20 (PIN_BUZZER)"),
    "LED_STAT": ("P2.00", "sig", "GPIO salida (PIN_LED1)"),
    "DBG_TX": ("P2.02", "loc", "UARTE00 TXD (pin dedicado) → TP201"),
    "DBG_RX": ("P2.07", "loc", "UARTE00 RXD (pin dedicado) ← TP202"),
}
PORT2PAD = {v: k for k, v in PADS.items() if v.startswith("P")}
NET_OF_PORT = {p: (n, k) for n, (p, k, _) in MAPA.items()}


def dibujar():
    W, H = 1720, 1340
    nueva(W, H, "02 · MCU — ME54BS13 (nRF54LM20A)",
          "nrf54lm20-meshnode · hoja 2 · referencias 2xx · intención de 02_mcu.kicad_sch · mapa de pines elegido por mí (revisar con las huellas en el PCB)")
    leyenda(760, 40)

    # ---------------------------------------------------------------- A · módulo
    frame(20, 76, 800, 1250, "A · U201 ME54BS13 — nRF54LM20A, antena PCB, cristales y DCDC internos")
    from simbolos_lib import me54bs13  # misma disposición que el símbolo de libs/meshnode.kicad_sym
    pins = me54bs13()
    left = sorted([p for p in pins if p["angle"] == 0], key=lambda p: -p["y"])
    right = sorted([p for p in pins if p["angle"] == 180], key=lambda p: -p["y"])
    top = max(p["y"] for p in pins if p["angle"] in (0, 180))

    def rows(side):
        out, prev = [], None
        for p in side:
            if prev is not None:
                out += [None] * (round((prev - p["y"]) / 2.54) - 1)
            out.append((p["number"], p["name"])); prev = p["y"]
        return out
    lr, rr = rows(left), rows(right)
    lr = [None] * round((top - left[0]["y"]) / 2.54) + lr
    e, h = ic2(300, 140, 250, "U201", "ME54BS13 · Minew", lr, rr, pitch=18.5, stub=22)
    spec = {}
    for p in pins:
        num, nm = p["number"], p["name"]
        port = nm.split("/")[0]
        if p["angle"] == 90:
            continue
        if port in NET_OF_PORT:
            spec[num] = NET_OF_PORT[port]
        elif nm.startswith("P"):
            spec[num] = ("", "nc")
    spec.update({"19": ("VCC_MCU", "loc"), "9": ("VBUS_MCU", "sig"), "8": ("USB_DP", "sig"), "7": ("USB_DM", "sig"),
                 "4": ("SWD_RST", "loc"), "5": ("SWDIO", "loc"), "6": ("SWDCLK", "loc"), "2": ("", "nc")})
    pin_labels(e, spec)
    gy = 140 + h + 10
    gnds = [p["number"] for p in pins if p["angle"] == 90]
    T(425, gy + 8, "GND: " + " · ".join(gnds) + "  (todas, con vía cada una)", "td", "middle")
    gnd(425, gy + 16)
    notes(40, gy + 56, [
        "Castellado 2 (RF) sin conectar: antena PCB del módulo (configuración por defecto).",
        "P1.01/P1.02 = NFC por defecto · P1.20/P1.21 = cristal de 32 kHz interno (no salen).",
        "Los GPIO libres quedan sin conectar (NC): el pad del módulo se suelda igual."])

    # ---------------------------------------------------------------- B · alimentación del módulo
    frame(840, 76, 860, 250, "B · Alimentación del módulo (Minew §7.3: π reservada junto a VCC)")
    label(890, 140, "3V3", "pwr", "end"); P([(890, 140), (980, 140)], "pw"); dot(940, 140)
    cap_v(940, 140, "C201", "10 µF", 44, "l"); gnd(940, 184)
    res_h(980, 140, "FB201", "0 Ω (o ferrita 600 Ω)", 90, sym="symp")
    P([(1070, 140), (1220, 140)], "pw"); dot(1110, 140); dot(1170, 140)
    cap_v(1110, 140, "C202", "10 µF", 44); gnd(1110, 184)
    cap_v(1170, 140, "C203", "100 nF", 44); gnd(1170, 184)
    label(1220, 140, "VCC_MCU", "loc")
    notes(860, 240, ["FB201 = π de Minew: 0 Ω de serie; ferrita (CBW160808U601T, cajón) si el",
                     "buck mete ruido en el BLE. C202/C203 a ≤ 0,5 mm de la pata 19, 2 vías a GND."])
    caps_to_gnd(1430, 140, "VBUS_MCU", "sig", [("C204", "1 µF 25 V")])
    notes(1350, 240, ["VBUS del módulo (pata 9): alimenta", "el regulador del PHY USB interno."])

    # ---------------------------------------------------------------- C · SWD
    frame(840, 340, 430, 270, "C · SWD — cabecera Cortex 2×5 1,27 mm")
    ej, _ = ic2(990, 400, 100, "J201", "2×5 1,27 SMD", [("1", "VTref"), ("3", "GND"), ("5", "GND"), ("7", "KEY"), ("9", "GNDdet")],
                [("2", "SWDIO"), ("4", "SWCLK"), ("6", "SWO"), ("8", "NC"), ("10", "nRESET")], pitch=24, stub=20)
    pin_labels(ej, {"1": ("VCC_MCU", "loc"), "3": ("", "gnd"), "5": ("", "gnd"), "7": ("", "nc"), "9": ("", "gnd"),
                    "2": ("SWDIO", "loc"), "4": ("SWDCLK", "loc"), "6": ("", "nc"), "8": ("", "nc"),
                    "10": ("SWD_RST", "loc")})
    notes(856, 560, ["Sólo para grabar el bootloader la primera vez (luego UF2/DFU por USB).",
                     "SWO sin conectar: P2.07 se usa como RXD de depuración."])

    # ---------------------------------------------------------------- D · UART de depuración
    frame(1290, 340, 410, 270, "D · UART de depuración (UARTE00)")
    tp(1340, 410, "TP201"); label(1390, 410, "DBG_TX", "loc")
    tp(1340, 450, "TP202"); label(1390, 450, "DBG_RX", "loc")
    tp(1340, 490, "TP203"); label(1390, 490, "GND", "pwr")
    notes(1306, 536, ["Pines dedicados de UARTE00: TXD P2.02 y RXD P2.07.",
                      "Por si el USB nativo no arranca (consola del core).",
                      "Huella TestPoint:TestPoint_Pad_D1.0mm (todos los TP)."], dy=19)

    # ---------------------------------------------------------------- E · mapa de pines
    frame(840, 624, 860, 702, "E · Mapa de pines (base de la variante de Meshtastic)")
    rows_ = []
    for sig, (port, kind, note) in MAPA.items():
        pad = PORT2PAD[port]
        rows_.append((sig, port, pad, note))
    tabla(840, 664, 860, [860, 990, 1060, 1110], ["Señal", "Puerto", "Pad", "Periférico / nota"], rows_, dy=20,
          mono=(0, 1, 2))
    notes(856, 1262, [
        "Reglas del nRF54LM20A: SERIAL2x sólo en P1/P3, SERIAL30 en P0, SERIAL00 en P2; IRQ y SENSE sólo en P0/P1/P3;",
        "SCK/SCL en clock pins. LoRa: SPIM22 (como la DK) · GNSS: UARTE20 · I²C: TWIM30 · depuración: UARTE00.",
        ("E22 con cristal pasivo ⇒ la variante NO define SX126X_DIO3_TCXO_VOLTAGE.", "tw")], dy=18)
    guardar(OUT)


if __name__ == "__main__":
    dibujar()
