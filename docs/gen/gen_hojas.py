"""Genera los SVG de intención de nrf54lm20-meshnode (docs/NN_*.svg): python gen_hojas.py [00 01 02 03 04 05]
Convención (la de ai_instruments): rojo = alimentación global (símbolo de power), azul = etiqueta jerárquica
(sale de la hoja), marrón = etiqueta local; amarillo discontinuo = pendiente / a confirmar; gris discontinuo = DNP.
Referencias por hoja: 1xx alimentación · 2xx MCU · 3xx LoRa · 4xx GNSS · 5xx interfaz. Una hoja = hojaNN.py."""
import importlib
import sys

ALL = ["00", "01", "02", "03", "04", "05"]

if __name__ == "__main__":
    for k in (sys.argv[1:] or ALL):
        importlib.import_module(f"hoja{k}").dibujar()
