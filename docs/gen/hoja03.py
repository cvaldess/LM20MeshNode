"""Hoja 03 · LoRa — E22-900MM22S (SX1262, 22 dBm, cristal pasivo) y U.FL (docs/03_lora.svg). Referencias 3xx.
Fuente: Ebyte E22-M user manual §3.1 (pinout), §4.1-4.2 (TXEN/RXEN, tabla 1), §5.1 (circuito recomendado)."""
import os

from svgkit import *  # noqa: F401,F403

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "03_lora.svg"))


def dibujar():
    W, H = 1720, 1000
    nueva(W, H, "03 · LoRa — E22-900MM22S (SX1262, 22 dBm)",
          "nrf54lm20-meshnode · hoja 3 · referencias 3xx · intención de 03_lora.kicad_sch")
    leyenda(760, 40)

    frame(20, 76, 860, 600, "A · U301 E22-900MM22S")
    L = [("1", "VCC"), None, ("3", "NRST"), None, ("14", "NSS"), ("15", "SCK"), ("13", "MOSI"), ("12", "MISO"), None,
         ("2", "GND"), ("7", "GND"), ("16", "GND")]
    R = [("6", "ANT"), None, ("9", "TXEN"), ("10", "RXEN"), None, ("11", "BUSY"), ("20", "DIO1"), ("19", "DIO2"),
         ("18", "DIO3"), None, ("4", "NC"), ("5", "NC"), ("8", "NC"), ("17", "NC")]
    e, h = ic2(320, 150, 170, "U301", "E22-900MM22S · Ebyte", L, R, pitch=28)
    pin_labels(e, {"1": ("3V3", "pwr"), "3": ("LORA_NRST", "sig"), "14": ("LORA_NSS", "sig"),
                   "15": ("LORA_SCK", "sig"), "13": ("LORA_MOSI", "sig"), "12": ("LORA_MISO", "sig"),
                   "2": ("", "gnd"), "7": ("", "gnd"), "16": ("", "gnd"), "6": ("LORA_ANT", "loc"),
                   "9": ("TXEN", "loc"), "10": ("LORA_RXEN", "sig"), "11": ("LORA_BUSY", "sig"),
                   "20": ("LORA_DIO1", "sig"), "19": ("DIO2", "loc"), "18": ("", "nc"), "4": ("", "nc"),
                   "5": ("", "nc"), "8": ("", "nc"), "17": ("", "nc")})
    notes(40, 150 + h + 40, [
        "Interruptor de RF interno (tabla 1): TXEN=1/RXEN=0 ⇒ TX · TXEN=0/RXEN=1 ⇒ RX · 0/0 ⇒ apagado.",
        "DIO2 gobierna TXEN (SX126X_DIO2_AS_RF_SWITCH) y RadioLib mueve RXEN (SX126X_RXEN = P1.13).",
        "DIO3 sin conectar: el MM22S lleva cristal PASIVO (la versión «(T)» lleva TCXO y tiene la misma huella).",
        ("⇒ la variante NO define SX126X_DIO3_TCXO_VOLTAGE (la DK sí, con el E22-900M30S).", "tw"),
        "NRST con pull-up interno del SX1262: lo mueve el MCU (LORA_NRST)."], dy=19)

    # ---------------------------------------------------------------- B · TXEN / RXEN
    frame(900, 76, 800, 300, "B · Control del interruptor de antena")
    label(980, 140, "DIO2", "loc", "end"); res_h(980, 140, "R301", "0 Ω", 80); P([(1060, 140), (1150, 140)])
    dot(1150, 140); label(1170, 140, "TXEN", "loc"); P([(1150, 140), (1170, 140)])
    label(980, 200, "LORA_TXEN", "sig", "end"); res_h(980, 200, "R302", "0 Ω DNP", 80, sym="dnp")
    P([(1060, 200), (1150, 200), (1150, 140)])
    label(1330, 140, "LORA_RXEN", "sig", "end"); P([(1330, 140), (1360, 140)]); dot(1360, 140)
    res_v(1360, 140, "R303", "100 kΩ", 50); gnd(1360, 190)
    notes(920, 260, ["R301 montada: TXEN = DIO2 (lo que hace Meshtastic). R302 sin montar: alternativa con",
                     "TXEN desde el MCU (P1.12) si hiciera falta. R303: RXEN a 0 mientras el MCU arranca",
                     "(los GPIO salen en alta impedancia) ⇒ interruptor apagado, sin estado indefinido."])

    # ---------------------------------------------------------------- C · antena
    frame(900, 390, 800, 246, "C · Antena 868 MHz: π de adaptación + U.FL")
    label(960, 450, "LORA_ANT", "loc", "end"); P([(960, 450), (990, 450)], "rf")
    dot(990, 450); cap_v(990, 450, "C303", "DNP", 44, "l", pc="plated"); gnd(990, 494)
    res_h(990, 450, "R304", "0 Ω", 90, cls="rf")
    dot(1080, 450); cap_v(1080, 450, "C304", "DNP", 44, pc="plated"); gnd(1080, 494)
    P([(1080, 450), (1200, 450)], "rf")
    ej, _ = ic2(1220, 430, 110, "J301", "BWU.FL-IPEX1 · C5137195", [("1", "SIG")], [("2", "GND"), ("3", "GND")], pitch=24)
    P([(1200, 450), ej["1"]], "rf")
    for k in ("2", "3"):
        x, y = ej[k]; P([(x, y), (x + 10, y)]); gnd(x + 10, y)
    notes(920, 540, ["Pista de 50 Ω en coplanar con plano de GND (4 capas) desde la pata 6 hasta el U.FL;",
                     "π en 0402 pegada al módulo: 0 Ω de serie y los shunts sin montar salvo que haya que",
                     "adaptar midiendo. Vías de GND a lo largo de la pista. Lejos del U.FL del GNSS."])

    # ---------------------------------------------------------------- D · desacoplo
    frame(20, 690, 860, 150, "D · Desacoplo (E22 §5.1: «external ceramic filter capacitor recommended»)")
    caps_to_gnd(120, 745, "3V3", "pwr", [("C301", "22 µF 10 V"), ("C302", "100 nF")], dx=90)
    notes(340, 747, ["C301 cubre los picos de TX (140 mA a 22 dBm) sin tirar del buck;",
                     "C302 pegado a la pata 1. 3V3 llega del BUCK2 (hoja 01)."])

    rows = [("U301", "módulo LoRa SX1262", "Ebyte E22-900MM22S", "SMD 10×10", "—", "cajón #195 (2)"),
            ("J301", "conector antena", "BAT WIRELESS BWU.FL-IPEX1", "SMD", "C5137195", "cajón #210"),
            ("R301 R304", "0 Ω", "Yageo RC0402FR-070RL", "0402", "C106231", "cajón #10"),
            ("R302", "0 Ω (DNP)", "—", "0402", "—", "—"),
            ("R303", "100 kΩ 1 %", "Yageo RC0402FR-07100KL", "0402", "C60491", "cajón #11"),
            ("C301", "22 µF 10 V X7R", "—", "0603", "—", "cajón #146"),
            ("C302", "100 nF 16 V X7R", "Samsung CL05B104KO5NNNC", "0402", "C1525", "cajón #22"),
            ("C303 C304", "shunt π (DNP)", "C0G según medida", "0402", "—", "—")]
    frame(900, 650, 800, 300, "Piezas de la hoja")
    tabla(900, 690, 800, [920, 1010, 1150, 1350, 1440, 1530], ["Ref.", "Qué es", "Pieza", "Encaps.", "LCSC", "Stock"],
          rows, dy=24, mono=(0, 4))
    frame(20, 854, 860, 126, "Notas de colocación")
    notes(36, 894, ["• E22 a la derecha del ME54BS13: su SPI sale de los castellados 12-18 y va en superficie.",
                    "• Antena LoRa y antena BLE del módulo en cantos distintos; plano de GND sin cortes bajo el E22.",
                    "• Nada de pistas bajo el E22 salvo GND (manual §4.1)."], dy=20)
    guardar(OUT)


if __name__ == "__main__":
    dibujar()
