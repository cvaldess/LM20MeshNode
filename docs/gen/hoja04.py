"""Hoja 04 · GNSS — E108-GN04S y U.FL para antena activa o pasiva (docs/04_gnss.svg). Referencias 4xx.
Fuentes: Ebyte E108-GN04 user manual V1.3 §3.2 (pinout), §4.2 (circuito), §2.3 (consumo 25-27 mA, sin sleep);
«Recommended wiring diagram of GNSS module antenna» V1.0 (82 nH desde VCC_RF, 56 pF en serie)."""
import os

from svgkit import *  # noqa: F401,F403

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "04_gnss.svg"))


def dibujar():
    W, H = 1720, 1000
    nueva(W, H, "04 · GNSS — E108-GN04S (BDS/GPS/GLONASS/Galileo)",
          "nrf54lm20-meshnode · hoja 4 · referencias 4xx · intención de 04_gnss.kicad_sch")
    leyenda(760, 40)

    frame(20, 76, 860, 610, "A · U401 E108-GN04S")
    L = [("23", "VCC"), ("22", "V_BCKP"), None, ("21", "RXD"), ("20", "TXD"), None, ("8", "RESET_N"),
         ("2", "SAFEBOOT_N"), ("4", "EXTINT"), ("3", "1PPS"), None, ("10", "GND"), ("12", "GND"), ("13", "GND"),
         ("24", "GND")]
    R = [("11", "RF_IN"), ("9", "VCC_RF"), ("14", "LNA_EN"), None] + [(n, "NC") for n in
                                                                      ("1", "5", "6", "7", "15", "16", "17", "18", "19")]
    e, h = ic2(360, 150, 180, "U401", "E108-GN04S · Ebyte", L, R, pitch=26)
    pin_labels(e, {"23": ("V_GNSS", "pwr"), "22": ("V_BCKP", "loc"), "21": ("GNSS_RXD", "loc"),
                   "20": ("GNSS_TXD", "loc"), "8": ("GNSS_RST", "sig"), "2": ("SAFEBOOT", "loc"), "4": ("", "nc"),
                   "3": ("GNSS_PPS", "sig"), "10": ("", "gnd"), "12": ("", "gnd"), "13": ("", "gnd"),
                   "24": ("", "gnd"), "11": ("GNSS_RFIN", "loc"), "9": ("VCC_RF", "loc"), "14": ("", "nc"),
                   **{n: ("", "nc") for n in ("1", "5", "6", "7", "15", "16", "17", "18", "19")}})
    notes(40, 150 + h + 36, [
        "Consumo 25–27 mA (§2.3) y SIN modo sleep documentado ⇒ se le corta VCC: V_GNSS = BUCK1 del nPM1300.",
        "V_BCKP desde 3V3 (siempre vivo): mantiene RTC y efemérides con VCC cortado ⇒ arranque en caliente (~1 s).",
        "RESET_N: pull-up interno, «dejar al aire si no se usa» ⇒ el MCU sólo lo baja (drenador abierto).",
        "EXTINT y LNA_EN sin uso (al aire, §3.2). SAFEBOOT_N a un punto de prueba (recuperación de firmware).",
        "UART 38400 baudios por defecto, NMEA 4.11 / UBX."], dy=19)

    # ---------------------------------------------------------------- B · UART y backup
    frame(900, 76, 800, 330, "B · UART, backup y puntos de prueba")
    label(990, 140, "GNSS_TX", "sig", "end"); res_h(990, 140, "R402", "1 kΩ", 80); label(1070, 140, "GNSS_RXD", "loc")
    label(990, 190, "GNSS_RX", "sig", "end"); res_h(990, 190, "R403", "1 kΩ", 80); label(1070, 190, "GNSS_TXD", "loc")
    label(1330, 140, "3V3", "pwr", "end"); res_h(1330, 140, "R401", "1 kΩ", 80); P([(1410, 140), (1450, 140)])
    dot(1450, 140); label(1470, 140, "V_BCKP", "loc"); P([(1450, 140), (1470, 140)])
    cap_v(1450, 140, "C403", "100 nF", 40, "l"); gnd(1450, 180)
    tp(1000, 250, "TP401"); label(1050, 250, "SAFEBOOT", "loc")
    notes(920, 300, ["R402/R403 1 kΩ: Ebyte pide resistencias de protección en la UART; además limitan la",
                     "corriente que entra por RXD con el GNSS apagado (el firmware deja TX en baja/entrada).",
                     "R401: V_BCKP «también puede cargar una pila» ⇒ 1 kΩ limita cualquier conflicto (15 µA ⇒ 15 mV)."])

    # ---------------------------------------------------------------- C · antena
    frame(900, 420, 800, 266, "C · Antena 1575 MHz por U.FL — activa o pasiva")
    ej, _ = ic2(940, 500, 110, "J401", "BWU.FL-IPEX1", [], [("1", "SIG"), ("2", "GND"), ("3", "GND")], pitch=24)
    for k in ("2", "3"):
        x, y = ej[k]; P([(x, y), (x + 10, y)]); gnd(x + 10, y)
    x0, y0 = ej["1"]
    P([(x0, y0), (1180, y0)], "rf"); dot(1180, y0)
    cap_h(1180, y0, "C404", "56 pF C0G", 90); P([(1270, y0), (1330, y0)], "rf"); label(1330, y0, "GNSS_RFIN", "loc")
    P([(1180, y0), (1180, y0 + 20)])
    add(f'<g opacity="0.75">'); ind_v(1180, y0 + 20, "L401", "82 nH (sólo activa)", 60); add('</g>')
    label(1180, y0 + 100, "VCC_RF", "loc", "middle")
    notes(920, 656, ["Pasiva: sólo C404 (DC block). Activa: montar L401 ⇒ la antena recibe VCC_RF (= V_GNSS, 3,3 V)",
                     "por el coaxial; el módulo detecta y protege la antena activa. 50 Ω en coplanar, corto."])

    # ---------------------------------------------------------------- D · alimentación
    frame(20, 700, 860, 250, "D · Alimentación del GNSS")
    caps_to_gnd(120, 760, "V_GNSS", "pwr", [("C401", "10 µF"), ("C402", "100 nF")], dx=90)
    label(500, 760, "3V3", "pwr", "end"); res_h(500, 760, "R404", "0 Ω DNP", 80, sym="dnp"); label(580, 760, "V_GNSS", "pwr")
    notes(40, 860, ["Rizado < 50 mV (§5): V_GNSS sale de su propio buck, separado de los picos de TX del E22.",
                    "R404 sin montar: rectificación si BUCK1 diera guerra (GNSS siempre encendido desde 3V3).",
                    ("🚨 Con R404 montada, BUCK1 debe quedar APAGADO (dos fuentes unidas).", "tw")], dy=19)

    rows = [("U401", "GNSS multibanda", "Ebyte E108-GN04S", "SMD 12,2×16", "—", "cajón #196 (4)"),
            ("J401", "conector antena", "BWU.FL-IPEX1", "SMD", "C5137195", "cajón #210"),
            ("C404", "56 pF C0G", "Samsung CL05C560JB5NNNC", "0402", "C84707", "COMPRAR"),
            ("L401", "82 nH (activa)", "Murata LQG15HS82NJ02D", "0402", "C98002", "COMPRAR"),
            ("R401-R403", "1 kΩ 1 %", "UNI-ROYAL 0402WGF1001TCE", "0402", "C11702", "cajón #31"),
            ("R404", "0 Ω (DNP)", "—", "0402", "—", "—"),
            ("C401", "10 µF 10 V X7R", "—", "0603", "—", "cajón #147"),
            ("C402 C403", "100 nF 16 V X7R", "Samsung CL05B104KO5NNNC", "0402", "C1525", "cajón #22"),
            ("TP401", "punto de prueba", "TestPoint_Pad_D1.0mm", "Ø1 mm", "—", "—")]
    frame(900, 700, 800, 290, "Piezas de la hoja")
    tabla(900, 740, 800, [920, 1010, 1140, 1350, 1450, 1540], ["Ref.", "Qué es", "Pieza", "Encaps.", "LCSC", "Stock"],
          rows, dy=24, mono=(0, 4))
    guardar(OUT)


if __name__ == "__main__":
    dibujar()
