"""Hoja 00 · Diagrama de bloques (raíz) de nrf54lm20-meshnode (docs/00_diagrama_bloques.svg).
Árbol de alimentación, buses entre hojas, matriz de estados de alimentación y presupuesto de consumo."""
import os

from svgkit import *  # noqa: F401,F403

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "00_diagrama_bloques.svg"))


def dibujar():
    W, H = 1720, 1240
    nueva(W, H, "00 · nrf54lm20-meshnode — diagrama de bloques",
          "Nodo Meshtastic de bolsillo: nRF54LM20A (BLE al móvil) + LoRa 868 + GNSS + OLED · LiPo 1S · USB-C · 4 capas")
    for i, (c, t) in enumerate((("pw", "alimentación"), ("sg", "señales"), ("df", "USB"), ("rf", "RF 50 Ω"),
                                ("gn", "conmutada por firmware"))):
        x = 960 + i * 150
        P([(x, 40), (x + 34, 40)], c); T(x + 40, 44, t, "ts")

    # ---------------------------------------------------------------- bloques
    blk(40, 110, 200, 90, "USB-C  J101", ["KH-TYPE-C-16P · ESD U102/D101", "hoja 01"], "blkp")
    blk(40, 270, 200, 80, "LiPo 1S  J102", ["JST PH 2.0 · NTC RT101", "hoja 01"], "blkp")
    blk(330, 110, 270, 300, "PMIC nPM1300  U101", ["cargador 32–800 mA (JEITA)", "BUCK2 → 3V3 (arranque)",
                                                    "BUCK1 → V_GNSS (firmware)", "VBUSOUT con OVP → VBUS_MCU",
                                                    "CC de USB-C (Rd interno)", "ship mode · botón PWR SW101",
                                                    "LEDs carga D102/D103", "I²C 0x6B · IRQ → MCU", "hoja 01"], "blkp")
    blk(700, 470, 300, 300, "MCU ME54BS13  U201", ["nRF54LM20A · M33 128 MHz", "2 MB RRAM · 512 KB RAM",
                                                   "BLE 6.0 antena PCB (al canto)", "USB 2.0 HS nativo (CDC/UF2)",
                                                   "SPIM22 · UARTE20 · TWIM30", "SWD J201 2×5 · UART TP201/202",
                                                   "VBAT_SENSE → AIN2", "π FB201 en VCC", "hoja 02"])
    blk(1130, 110, 260, 150, "LoRa E22-900MM22S  U301", ["SX1262 · 22 dBm · cristal pasivo",
                                                         "RXEN por MCU, TXEN = DIO2", "π + U.FL J301", "hoja 03"], "blkr")
    blk(1130, 330, 260, 150, "GNSS E108-GN04S  U401", ["BDS/GPS/GLO/GAL · 25 mA", "UART 38400 · PPS",
                                                       "U.FL J401 activa/pasiva", "hoja 04"], "blkg")
    blk(1130, 560, 260, 165, "Interfaz", ["SHT41 U501 (0x44) · OLED DS501 (0x3C)",
                                          "IMU U502 (0x6A): despertar al moverlo",
                                          "Qwiic J501 · botones ↑ OK ↓ · LED D501",
                                          "zumbador BZ501 (desde VSYS)", "hoja 05"])
    blk(1480, 145, 200, 70, "Antena 868 MHz", ["U.FL"], "blkr")
    blk(1480, 365, 200, 70, "Antena GNSS", ["U.FL (activa o pasiva)"], "blkg")
    blk(1480, 600, 200, 70, "Móvil (BLE)", ["app Meshtastic"])

    # ---------------------------------------------------------------- flechas
    arrow([(240, 140), (330, 140)], "pw"); T(285, 132, "VBUS", "al", "middle")
    arrow([(330, 175), (240, 175)], "sg"); T(285, 192, "CC1/CC2", "al", "middle")
    arrow([(240, 310), (330, 310)], "pw"); T(285, 302, "VBAT", "al", "middle")
    arrow([(40, 155), (25, 155), (25, 850), (760, 850), (760, 770)], "df"); T(390, 844, "USB_DP / USB_DM (90 Ω)", "al", "middle")
    arrow([(600, 150), (1130, 150)], "pw"); T(860, 142, "3V3 (BUCK2)", "al", "middle")
    arrow([(600, 380), (740, 380), (740, 470)], "pw"); T(670, 372, "3V3", "al", "middle")
    arrow([(600, 350), (820, 350), (820, 470)], "pw"); T(860, 342, "VBUS_MCU", "al", "middle")
    P([(600, 250), (1100, 250)], "gn"); T(860, 242, "V_GNSS (BUCK1 ⇐ PIN_GPS_EN)", "al", "middle")
    P([(1100, 250), (1100, 380)], "gn"); arrow([(1100, 380), (1130, 380)], "gn")
    arrow([(1000, 510), (1060, 510), (1060, 205), (1130, 205)], "sg"); T(1052, 300, "SPI · BUSY", "al", "end")
    T(1052, 314, "DIO1 · NRST", "al", "end"); T(1052, 328, "RXEN", "al", "end")
    arrow([(1000, 560), (1110, 560), (1110, 440), (1130, 440)], "sg"); T(1050, 552, "UART · PPS · RST", "al", "middle")
    arrow([(1000, 640), (1130, 640)], "sg"); T(1065, 632, "I²C · GPIO", "al", "middle")
    arrow([(700, 700), (460, 700), (460, 410)], "sg"); T(580, 692, "I²C · PMIC_INT · GNSS_EN", "al", "middle")
    arrow([(1390, 180), (1480, 180)], "rf"); arrow([(1390, 400), (1480, 400)], "rf")
    arrow([(1000, 745), (1440, 745), (1440, 635), (1480, 635)], "rf"); T(1220, 738, "BLE 2,4 GHz (antena del módulo)", "al", "middle")

    # ---------------------------------------------------------------- matriz de estados de alimentación
    frame(40, 880, 820, 340, "Matriz de estados de alimentación (¿quién queda apagado con otro vivo y qué los une?)")
    tabla(40, 920, 820, [56, 250, 470], ["Estado", "Líneas entre dominios", "Riesgo y quién lo resuelve"], [
        ("GNSS apagado (BUCK1 off)", "TX MCU→RXD (R402 1k), RX, PPS, RST", "TX alto alimentaría el GNSS por su ESD ⇒ FIRMWARE: TX a 0/entrada"),
        ("", "V_BCKP desde 3V3 (R401 1k)", "deseado: RTC y efemérides vivos"),
        ("OLED / SHT41 / IMU / Qwiic", "I²C con pull-ups propios", "siempre en 3V3 ⇒ no hay estado parcial (HARDWARE)"),
        ("E22 (en 3V3 siempre)", "SPI, BUSY, DIO1, NRST, RXEN", "mismo raíl que el MCU ⇒ sin riesgo"),
        ("Ship mode / batería a 0", "todo apagado salvo nPM1300", "370 nA; sale con SW101 o al enchufar USB"),
        ("Sólo USB, sin batería", "VBUS límite 100 mA por defecto", "TX LoRa o zumbador > 100 mA ⇒ FIRMWARE: 500 mA"),
        ("USB sin firmware de PMIC", "VBUS_MCU (VBUSOUT) al módulo", "USB CDC funciona; no carga hasta el driver"),
    ], dy=24, mono=())

    # ---------------------------------------------------------------- presupuesto y hojas
    frame(880, 880, 800, 340, "Consumo orientativo (3V3 desde LiPo) y hojas")
    tabla(880, 920, 800, [896, 1090, 1210], ["Consumidor", "Corriente", "Nota"], [
        ("E22 en RX continua", "≈ 7 mA", "Meshtastic escucha siempre (manual E22 §2.2)"),
        ("E22 en TX 22 dBm", "100–140 mA", "ráfagas; C301 22 µF + BUCK2"),
        ("nRF54LM20A + BLE", "≈ 1–3 mA medio", "conexión BLE con el móvil"),
        ("GNSS seguimiento", "25–27 mA", "conmutado por PIN_GPS_EN (BUCK1)"),
        ("OLED encendido", "10–23 mA", "se apaga por timeout (sleep ~3 µA)"),
        ("⇒ 1500 mAh", "≈ 7 días sin GNSS", "≈ 1,7 días con GNSS siempre encendido"),
    ], dy=22, mono=())
    notes(896, 1090, ["Hojas: 00 bloques (raíz) · 01 alimentación · 02 MCU · 03 LoRa · 04 GNSS · 05 interfaz.",
                      "Entre hojas: etiquetas jerárquicas (azul). Alimentación: símbolos globales GND, 3V3, VSYS,",
                      "VBAT, V_GNSS, VBUS (rojo). Las cifras de consumo son de los datasheets, no medidas:",
                      "medir con el INA en el banco antes de fiarse del cálculo de autonomía."], dy=19)
    guardar(OUT)


if __name__ == "__main__":
    dibujar()
