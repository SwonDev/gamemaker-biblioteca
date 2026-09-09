#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera un WAV mínimo para el banco de pruebas de audio.

`scr_audio.gml` es el único script reutilizable que no se podía EJECUTAR: sus
funciones reciben ids de sonido, y un proyecto en blanco no tiene ninguno.
Esto lo resuelve sin descargar nada ni depender de una licencia ajena: medio
segundo de tono a 440 Hz con la biblioteca estándar de Python.

    python3 _indice/pruebas/generar_sonido.py <archivo.wav>
"""
import math
import struct
import sys
import wave

FRECUENCIA = 440.0
SEGUNDOS = 0.5
MUESTREO = 22050


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    destino = sys.argv[1]
    n = int(MUESTREO * SEGUNDOS)
    with wave.open(destino, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(MUESTREO)
        marcos = b"".join(
            struct.pack("<h", int(16000 * math.sin(2 * math.pi * FRECUENCIA * i / MUESTREO)))
            for i in range(n)
        )
        w.writeframes(marcos)
    print("%s · %.1f s a %d Hz" % (destino, SEGUNDOS, FRECUENCIA))
    return 0


if __name__ == "__main__":
    sys.exit(main())
