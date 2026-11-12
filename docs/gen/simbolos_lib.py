"""Pin lists (number, name, electrical type, side) for the project symbols in libs/meshnode.kicad_sym,
written from each datasheet's pin table. Prints JSON ready for Konnect create_symbol.
Usage: python simbolos_lib.py <SYMBOL>  (ME54BS13 | E22-900MM22S | E108-GN04S | nPM1300 | SHT41 | OLED | UFL | USBC | TPD4E05 | HYG5020A)

Sources:
  ME54BS13      Minew datasheet v1.0.0 p.6-9 + nRF54LM20A datasheet v1.0 table p.1240 (AIN, NFC, clock pins "/CK")
  E22-900MM22S  Ebyte E22-M user manual §3.1
  E108-GN04S    Ebyte E108-GN04 user manual V1.3 §3.2
  nPM1300       Nordic nPM1300 PS v1.3 table 34
  SHT41-P-NF    Nyfea datasheet §4 ; OLED HS91L02W2C01 datasheet §1.5
"""
import json
import sys

from me54bs13_pads import pinmap as ME_PADS

P = 2.54

# nRF54LM20A pin functions worth showing on the symbol (datasheet v1.0 p.1240-1243)
AIN = {"P1.00": "AIN0", "P1.31": "AIN1", "P1.30": "AIN2", "P1.29": "AIN3", "P1.06": "AIN4", "P1.05": "AIN5",
       "P1.04": "AIN6", "P1.03": "AIN7"}
NFC = {"P1.01": "NFC1", "P1.02": "NFC2"}
CLK = {"P0.03", "P0.04", "P0.06", "P0.07", "P1.03", "P1.04", "P1.07", "P1.13", "P1.14", "P1.17", "P1.18", "P1.23",
       "P1.24", "P2.01", "P2.06", "P3.03", "P3.04"}
UARTE00 = {"P2.02": "U00TX", "P2.07": "U00RX"}


def gpio_name(port_pin):
    extra = AIN.get(port_pin) or NFC.get(port_pin) or UARTE00.get(port_pin)
    name = port_pin + ("/" + extra if extra else "")
    return name + ("/CK" if port_pin in CLK else "")


def column(entries, x, angle, top):
    """entries: list of (number, name, type) or None for a gap; returns pins top->bottom (y grows up)."""
    pins, y = [], top
    for e in entries:
        if e is not None:
            n, nm, t = e
            pins.append({"number": n, "name": nm, "type": t, "x": x, "y": round(y, 2), "angle": angle,
                         "length": P})
        y -= P
    return pins


def me54bs13():
    by_name = {}
    for pad, nm in ME_PADS.items():
        by_name.setdefault(nm, []).append(pad)
    port = lambda p: [(by_name[f"P{p}.{i:02d}"][0], gpio_name(f"P{p}.{i:02d}"), "bidirectional")
                      for i in range(32) if f"P{p}.{i:02d}" in by_name]
    left = [("19", "VCC", "power_in"), ("9", "VBUS", "power_in"), ("8", "D+", "bidirectional"),
            ("7", "D-", "bidirectional"), None, ("4", "nRESET", "input"), ("5", "SWDIO", "bidirectional"),
            ("6", "SWDCLK", "input"), ("2", "RF", "passive"), None] + port(0) + [None] + port(3)
    right = port(1) + [None] + port(2)
    top = (max(len(left), len(right)) - 1) * P / 2
    top = round(round(top / P) * P, 2)
    pins = column(left, -25.4, 0, top) + column(right, 25.4, 180, top)
    gnds = sorted(by_name["GND"], key=lambda s: (len(s), s))
    bottom_y = round(top - max(len(left), len(right)) * P - P, 2)
    for i, n in enumerate(gnds):
        # 2.54 apart as in the library (numbers crowd a bit; Konnect delete_symbol failed to replace it, 09-11)
        pins.append({"number": n, "name": "GND", "type": "power_in", "x": round((i - (len(gnds) - 1) / 2) * P, 2),
                     "y": bottom_y, "angle": 90, "length": P})
    assert len(pins) == 80 and len({p["number"] for p in pins}) == 80
    return pins


def simple(left, right, x=12.7):
    top = round(round((max(len(left), len(right)) - 1) * P / 2 / P) * P, 2)
    return column(left, -x, 0, top) + column(right, x, 180, top)


def e22():
    left = [("1", "VCC", "power_in"), None, ("3", "NRST", "input"), None, ("14", "NSS", "input"),
            ("15", "SCK", "input"), ("13", "MOSI", "input"), ("12", "MISO", "tri_state"), None,
            ("2", "GND", "power_in"), ("7", "GND", "power_in"), ("16", "GND", "power_in")]
    right = [("6", "ANT", "passive"), None, ("9", "TXEN", "input"), ("10", "RXEN", "input"), None,
             ("11", "BUSY", "output"), ("20", "DIO1", "bidirectional"), ("19", "DIO2", "bidirectional"),
             ("18", "DIO3", "bidirectional"), None, ("4", "NC", "no_connect"), ("5", "NC", "no_connect"),
             ("8", "NC", "no_connect"), ("17", "NC", "no_connect")]
    return simple(left, right)


def e108():
    left = [("23", "VCC", "power_in"), ("22", "V_BCKP", "power_in"), None, ("21", "RXD", "input"),
            ("20", "TXD", "output"), None, ("8", "RESET_N", "input"), ("2", "SAFEBOOT_N", "input"),
            ("4", "EXTINT", "input"), ("3", "1PPS", "output"), None,
            ("10", "GND", "power_in"), ("12", "GND", "power_in"), ("13", "GND", "power_in"), ("24", "GND", "power_in")]
    right = [("11", "RF_IN", "passive"), ("9", "VCC_RF", "power_out"), ("14", "LNA_EN", "output"), None] + \
            [(n, "NC", "no_connect") for n in ("1", "5", "6", "7", "15", "16", "17", "18", "19")]
    return simple(left, right, x=15.24)


def npm1300():
    left = [("21", "VBUS", "power_in"), ("22", "VBUSOUT", "power_out"), ("23", "CC1", "passive"),
            ("24", "CC2", "passive"), None, ("19", "VBAT", "passive"), ("18", "NTC", "passive"), None,
            ("12", "VDDIO", "power_in"), ("13", "SDA", "bidirectional"), ("14", "SCL", "input"), None,
            ("7", "GPIO0", "bidirectional"), ("8", "GPIO1", "bidirectional"), ("9", "GPIO2", "bidirectional"),
            ("10", "GPIO3", "bidirectional"), ("11", "GPIO4", "bidirectional"), None,
            ("15", "SHPHLD", "input"), ("17", "VSET1", "passive"), ("16", "VSET2", "passive")]
    right = [("20", "VSYS", "power_out"), ("4", "PVDD", "power_in"), None,
             ("3", "SW1", "passive"), ("1", "VOUT1", "power_out"), ("2", "PVSS1", "power_in"), None,
             ("5", "SW2", "passive"), ("32", "VOUT2", "power_out"), ("6", "PVSS2", "power_in"), None,
             ("28", "LSIN1/VINLDO1", "power_in"), ("29", "LSOUT1/VOUTLDO1", "power_out"),
             ("30", "LSIN2/VINLDO2", "power_in"), ("31", "LSOUT2/VOUTLDO2", "power_out"), None,
             ("25", "LED0", "open_collector"), ("26", "LED1", "open_collector"), ("27", "LED2", "open_collector"),
             None, ("33", "AVSS", "power_in")]
    return simple(left, right, x=17.78)


def sht41():
    return simple([("3", "VDD", "power_in"), ("4", "VSS", "power_in")],
                  [("1", "SDA", "bidirectional"), ("2", "SCL", "input")], x=10.16)


def oled():
    return simple([("2", "VCC", "power_in"), ("1", "GND", "power_in")],
                  [("4", "SDA", "bidirectional"), ("3", "SCL", "input")], x=10.16)


def ufl():
    return simple([("1", "SIG", "passive")], [("2", "GND", "passive"), ("3", "GND", "passive")], x=7.62)


def usbc():
    """Kinghelm KH-TYPE-C-16P (C709357): plano del fabricante (tabla de pines A/B) + huella
    easyeda2kicad:USB-C-SMD_KH-TYPE-C-16P (1-4 = patas del blindaje). Conector ⇒ VBUS/GND pasivos (PWR_FLAG)."""
    left = [("A4", "VBUS", "passive"), ("A9", "VBUS", "passive"), ("B4", "VBUS", "passive"), ("B9", "VBUS", "passive"),
            None, ("A5", "CC1", "bidirectional"), ("B5", "CC2", "bidirectional"), None,
            ("A6", "DP1", "bidirectional"), ("B6", "DP2", "bidirectional"), ("A7", "DN1", "bidirectional"),
            ("B7", "DN2", "bidirectional"), None, ("A8", "SBU1", "bidirectional"), ("B8", "SBU2", "bidirectional")]
    right = [("A1", "GND", "passive"), ("A12", "GND", "passive"), ("B1", "GND", "passive"), ("B12", "GND", "passive"),
             None, ("1", "SHIELD", "passive"), ("2", "SHIELD", "passive"), ("3", "SHIELD", "passive"),
             ("4", "SHIELD", "passive")]
    return simple(left, right, x=10.16)


def tpd4e05():
    """TPD4E05U06DQAR (DOWO C22390021, DFN2510-10): I/O 1,2,4,5 · GND 3,8 · 6,7,9,10 NC «flow-through».
    Cada NC queda enfrente de su I/O (10↔1, 9↔2, 7↔4, 6↔5) y se une a su red para que la pista pase
    por encima de los dos pads sin errores de DRC ⇒ pasivos, no no_connect."""
    left = [("1", "D1+", "passive"), ("2", "D1-", "passive"), ("4", "D2+", "passive"), ("5", "D2-", "passive")]
    right = [("10", "NC(D1+)", "passive"), ("9", "NC(D1-)", "passive"), ("7", "NC(D2+)", "passive"),
             ("6", "NC(D2-)", "passive"), None, ("3", "GND", "passive"), ("8", "GND", "passive")]
    return simple(left, right, x=10.16)


def hyg5020a():
    """Zumbador magnético pasivo HYG-5020A (C7544810): plano §3-1 (vista superior: «+» abajo a la izquierda,
    junto al punto; «−» abajo a la derecha; arriba a la izquierda, pata sólo mecánica) = huella
    easyeda2kicad:BUZ-SMD_3P-L5.0-W5.0-P3.50-BL pads 1 (−2,2; +1,77), 2 (+2,2; +1,73), 3 (−2,2; −1,77)."""
    return simple([("1", "+", "passive"), ("2", "-", "passive")], [("3", "NC", "no_connect")], x=7.62)


SYMBOLS = {"ME54BS13": me54bs13, "E22-900MM22S": e22, "E108-GN04S": e108, "nPM1300": npm1300,
           "SHT41": sht41, "OLED": oled, "UFL": ufl, "USBC": usbc, "TPD4E05": tpd4e05, "HYG5020A": hyg5020a}

if __name__ == "__main__":
    pins = SYMBOLS[sys.argv[1]]()
    print(json.dumps(pins, separators=(",", ":")))
