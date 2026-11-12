"""Compara el netlist de KiCad con la intención de cada hoja (escrita A MANO desde docs/gen/hojaNN.py, no desde el
planificador, para que el control sea independiente). Detecta patas repartidas en varias redes, nombres de red mal
puestos, fusiones (patas de más) y patas que deberían ir al aire.
Uso: python check_netlist.py <netlist.net> NN [NN…]
     (kicad-cli sch export netlist --format kicadsexpr nrflm20-meshnode.kicad_sch -o x.net)"""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
RAILES = {"GND", "3V3", "VSYS", "VBAT", "V_GNSS", "VBUS"}

# ---------------------------------------------------------------------------------------------------- hoja 01
H01 = {
    "hoja": "/01_alimentacion/",
    "jerarquicas": {"USB_DP", "USB_DM", "VBUS_MCU", "I2C_SDA", "I2C_SCL", "GNSS_EN", "PMIC_INT", "VBAT_SENSE"},
    "intent": {
        # A · USB-C + ESD
        "VBUS": ["J101.A4", "J101.A9", "J101.B4", "J101.B9", "D101.1", "U101.21", "C101.1", "TP101.1"],
        "CC1": ["J101.A5", "U102.4", "U102.7", "U101.23"],
        "CC2": ["J101.B5", "U102.5", "U102.6", "U101.24"],
        "USB_DP": ["J101.A6", "J101.B6", "U102.1", "U102.10"],
        "USB_DM": ["J101.A7", "J101.B7", "U102.2", "U102.9"],
        # B · nPM1300
        "VBUS_MCU": ["U101.22", "C102.1"],
        "VBAT": ["U101.19", "J102.1", "C106.1", "R103.1", "TP102.1"],
        "NTC": ["U101.18", "RT101.1"],
        "3V3": ["U101.12", "U101.32", "L102.2", "C108.1", "C110.1", "TP104.1"],
        "I2C_SDA": ["U101.13"], "I2C_SCL": ["U101.14"],
        "GNSS_EN": ["U101.7"], "PMIC_INT": ["U101.8"],
        "SHPHLD": ["U101.15", "SW101.2"],
        "VSET1": ["U101.17", "R101.1"], "VSET2": ["U101.16", "R102.1"],
        "VSYS": ["U101.20", "U101.4", "C103.1", "C104.1", "C105.1", "D102.2", "D103.2", "TP103.1"],
        "SW1": ["U101.3", "L101.1"], "SW2": ["U101.5", "L102.1"],
        "V_GNSS": ["U101.1", "L101.2", "C107.1", "TP105.1"],
        "LED0": ["U101.25", "D102.1"], "LED1": ["U101.26", "D103.1"],
        # F · VBAT_SENSE
        "VBAT_SENSE": ["R103.2", "R104.1", "C111.1"],
        "GND": ["J101.A1", "J101.A12", "J101.B1", "J101.B12", "J101.1", "J101.2", "J101.3", "J101.4", "D101.2",
                "U102.3", "U102.8", "U101.2", "U101.6", "U101.28", "U101.29", "U101.30", "U101.31", "U101.33",
                "C101.2", "C102.2", "C103.2", "C104.2", "C105.2", "C106.2", "C107.2", "C108.2", "C110.2", "C111.2",
                "R101.2", "R102.2", "R104.2", "RT101.2", "J102.2", "SW101.1", "SW101.3", "SW101.4", "TP106.1"],
    },
    "al_aire": ["J101.A8", "J101.B8", "U101.9", "U101.10", "U101.11", "U101.27", "J102.MP"],
}

# ---------------------------------------------------------------------------------------------------- hoja 02
# Mapa de pines copiado A MANO de la tabla E de docs/02_mcu.svg (señal: pad del ME54BS13)
_MAPA02 = {"LORA_SCK": "16", "LORA_MOSI": "17", "LORA_MISO": "18", "LORA_NSS": "15", "LORA_BUSY": "14",
           "LORA_DIO1": "13", "LORA_NRST": "12", "LORA_RXEN": "F3", "LORA_TXEN": "F4", "I2C_SDA": "B1",
           "I2C_SCL": "A0", "IMU_INT1": "B0", "IMU_INT2": "C0", "GNSS_TX": "B8", "GNSS_RX": "B9", "GNSS_PPS": "A8",
           "GNSS_RST": "A7", "GNSS_EN": "C7", "PMIC_INT": "A6", "VBAT_SENSE": "A9", "BTN_UP": "F6", "BTN_OK": "E6",
           "BTN_DOWN": "E5", "BUZZER": "D6", "LED_STAT": "F9"}
H02 = {
    "hoja": "/02_mcu/",
    "jerarquicas": set(_MAPA02) | {"VBUS_MCU", "USB_DP", "USB_DM"},
    "intent": {**{s: [f"U201.{p}"] for s, p in _MAPA02.items()},
               "VBUS_MCU": ["U201.9", "C204.1"], "USB_DP": ["U201.8"], "USB_DM": ["U201.7"],
               "VCC_MCU": ["U201.19", "FB201.2", "C202.1", "C203.1", "J201.1"],
               "3V3": ["FB201.1", "C201.1"],
               "SWD_RST": ["U201.4", "J201.10"], "SWDIO": ["U201.5", "J201.2"], "SWDCLK": ["U201.6", "J201.4"],
               "DBG_TX": ["U201.D9", "TP201.1"], "DBG_RX": ["U201.E8", "TP202.1"],
               "GND": ["U201.1", "U201.3", "U201.10", "U201.11", "U201.20", "U201.D0", "U201.E0", "U201.F0",
                       "C201.2", "C202.2", "C203.2", "C204.2", "J201.3", "J201.5", "J201.9", "TP203.1"]},
    "al_aire": ["U201.2", "J201.6", "J201.7", "J201.8"],
}
# GPIO libres del módulo: todos los pads de puerto que no salen en el mapa (fuente: me54bs13_pads.pinmap)
from me54bs13_pads import pinmap as _PADS  # noqa: E402
_usados = {p.split(".")[1] for v in H02["intent"].values() for p in v if p.startswith("U201.")}
H02["al_aire"] += [f"U201.{pad}" for pad, nm in _PADS.items() if nm.startswith("P") and pad not in _usados]

# ---------------------------------------------------------------------------------------------------- hoja 03
H03 = {
    "hoja": "/03_lora/",
    "jerarquicas": {"LORA_SCK", "LORA_MOSI", "LORA_MISO", "LORA_NSS", "LORA_BUSY", "LORA_DIO1", "LORA_NRST",
                    "LORA_RXEN", "LORA_TXEN"},
    "intent": {
        "3V3": ["U301.1", "C301.1", "C302.1"],
        "LORA_NRST": ["U301.3"], "LORA_NSS": ["U301.14"], "LORA_SCK": ["U301.15"], "LORA_MOSI": ["U301.13"],
        "LORA_MISO": ["U301.12"], "LORA_BUSY": ["U301.11"], "LORA_DIO1": ["U301.20"],
        "LORA_RXEN": ["U301.10", "R303.1"], "LORA_TXEN": ["R302.1"],
        "TXEN": ["U301.9", "R301.2", "R302.2"], "DIO2": ["U301.19", "R301.1"],
        "LORA_ANT": ["U301.6", "C303.1", "R304.1"], "LORA_RF": ["R304.2", "C304.1", "J301.1"],
        "GND": ["U301.2", "U301.7", "U301.16", "R303.2", "C303.2", "C304.2", "C301.2", "C302.2", "J301.2", "J301.3"],
    },
    "al_aire": ["U301.18", "U301.4", "U301.5", "U301.8", "U301.17"],
}

# ---------------------------------------------------------------------------------------------------- hoja 04
H04 = {
    "hoja": "/04_gnss/",
    "jerarquicas": {"GNSS_TX", "GNSS_RX", "GNSS_PPS", "GNSS_RST"},
    "intent": {
        "V_GNSS": ["U401.23", "C401.1", "C402.1", "R404.2"], "3V3": ["R401.1", "R404.1"],
        "V_BCKP": ["U401.22", "R401.2", "C403.1"],
        "GNSS_RXD": ["U401.21", "R402.2"], "GNSS_TXD": ["U401.20", "R403.2"],
        "GNSS_TX": ["R402.1"], "GNSS_RX": ["R403.1"], "GNSS_RST": ["U401.8"], "GNSS_PPS": ["U401.3"],
        "SAFEBOOT": ["U401.2", "TP401.1"],
        "GNSS_RFIN": ["U401.11", "C404.2"], "VCC_RF": ["U401.9", "L401.2"],
        "GNSS_ANT": ["J401.1", "C404.1", "L401.1"],
        "GND": ["U401.10", "U401.12", "U401.13", "U401.24", "C401.2", "C402.2", "C403.2", "J401.2", "J401.3"],
    },
    "al_aire": ["U401.4", "U401.14"] + [f"U401.{n}" for n in (1, 5, 6, 7, 15, 16, 17, 18, 19)],
}

# ---------------------------------------------------------------------------------------------------- hoja 05
H05 = {
    "hoja": "/05_interfaz/",
    "jerarquicas": {"I2C_SDA", "I2C_SCL", "IMU_INT1", "IMU_INT2", "BTN_UP", "BTN_OK", "BTN_DOWN", "BUZZER",
                    "LED_STAT"},
    "intent": {
        "I2C_SDA": ["R501.2", "U501.1", "DS501.4", "J501.3", "U502.14"],
        "I2C_SCL": ["R502.2", "U501.2", "DS501.3", "J501.4", "U502.13"],
        "3V3": ["R501.1", "R502.1", "U501.3", "C501.1", "DS501.2", "C502.1", "J501.2", "U502.8", "U502.5",
                "U502.12", "C503.1", "C504.1"],
        "IMU_INT1": ["U502.4"], "IMU_INT2": ["U502.9"],
        "BTN_UP": ["SW501.2"], "BTN_OK": ["SW502.2"], "BTN_DOWN": ["SW503.2"],
        "LED_STAT": ["R503.1"], "D501_A": ["R503.2", "D501.2"],
        "VSYS": ["R506.1", "R507.1"], "BZ_P": ["R506.2", "R507.2", "BZ501.1", "D502.1"],
        "BZ_N": ["BZ501.2", "D502.2", "Q501.3"], "BUZZER": ["R504.1"], "BZ_G": ["R504.2", "R505.1", "Q501.1"],
        "GND": ["U501.4", "C501.2", "DS501.1", "C502.2", "J501.1", "U502.1", "U502.2", "U502.3", "U502.6", "U502.7",
                "C503.2", "C504.2", "SW501.1", "SW501.3", "SW501.4", "SW502.1", "SW502.3", "SW502.4", "SW503.1",
                "SW503.3", "SW503.4", "D501.1", "Q501.2", "R505.2"],
    },
    "al_aire": ["J501.MP", "U502.10", "U502.11", "BZ501.3"],
}

HOJAS = {"01": H01, "02": H02, "03": H03, "04": H04, "05": H05}


def read_netlist(path):
    s = open(path, encoding="utf-8").read()
    got = {}
    for m in re.finditer(r'\(net\s+\(code "?\d+"?\)\s+\(name "([^"]*)"\)(.*?)(?=\(net\s+\(code|\Z)', s, re.S):
        for r, p in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', m.group(2)):
            got[f"{r}.{p}"] = m.group(1)
    return got


def check(got, H):
    fallos = 0
    want = {}
    for net, pins in H["intent"].items():
        names = {got.get(p, "<FALTA>") for p in pins}
        if len(names) != 1 or "<FALTA>" in names:
            fallos += 1
            print(f"✗ {net}: patas repartidas en {sorted(names)}")
            continue
        kn = names.pop()
        if net in RAILES:
            ok = kn == net
        elif net in H["jerarquicas"]:
            ok = kn.endswith("/" + net)
        else:
            ok = kn == H["hoja"] + net
        if not ok:
            fallos += 1
            print(f"✗ {net}: KiCad la llama {kn}")
        want[kn] = set(pins)
    for p in H["al_aire"]:
        if not got.get(p, "").startswith("unconnected-"):
            fallos += 1
            print(f"✗ {p} debería ir al aire y está en {got.get(p, '<FALTA>')}")
    mias = {p.split(".")[0] for v in H["intent"].values() for p in v} | {p.split(".")[0] for p in H["al_aire"]}
    for kn, pins in want.items():
        extra = {p for p, n in got.items() if n == kn and p.split(".")[0] in mias} - pins
        if extra:
            fallos += 1
            print(f"✗ {kn}: patas de más {sorted(extra)}")
    todas = {p for v in H["intent"].values() for p in v} | set(H["al_aire"])
    sobran = sorted(p for p in got if p.split(".")[0] in mias and p not in todas)
    print(f"{H['hoja']}: patas en la intención {len(todas)} · de la hoja en el netlist "
          f"{sum(1 for p in got if p.split('.')[0] in mias)} · fuera de la intención {sobran}")
    return fallos + len(sobran)


def check_entre_hojas(got, hojas):
    """Cada red jerárquica o raíl debe ser UNA sola red de KiCad con las patas de todas las hojas."""
    fallos, redes = 0, {}
    for H in hojas:
        for net, pins in H["intent"].items():
            if net in H["jerarquicas"] or net in RAILES:
                redes.setdefault(net, []).extend(pins)
    for net, pins in sorted(redes.items()):
        names = {got.get(p, "<FALTA>") for p in pins}
        if len(names) != 1:
            fallos += 1
            print(f"✗ entre hojas {net}: {sorted(names)}")
        elif net not in RAILES and names != {"/" + net}:
            fallos += 1
            print(f"✗ entre hojas {net}: se llama {names.pop()} (esperado /{net})")
    print(f"entre hojas: {len(redes)} redes comprobadas")
    return fallos


if __name__ == "__main__":
    got = read_netlist(sys.argv[1])
    total = sum(check(got, HOJAS[n]) for n in sys.argv[2:])
    if len(sys.argv[2:]) > 1:
        total += check_entre_hojas(got, [HOJAS[n] for n in sys.argv[2:]])
    print("todo bien" if total == 0 else f"{total} FALLOS")
    sys.exit(1 if total else 0)
