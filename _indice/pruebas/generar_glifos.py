#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera la hoja de glifos del banco de pruebas: un PNG por carácter.

Es el peldaño 1(b) de `12 · 09 §5.2` aplicado a tipografía, y la tercera salida de
la Trampa 12: una fuente de sprite propia, con tildes, sin `.ttf` que distribuir y
sin abrir el IDE. Lo que el banco comprueba después, ejecutando, es que el resultado
mide lo que debe — sobre todo el espacio, que sin barra sólida lo decide el motor.

    python3 _indice/pruebas/generar_glifos.py <carpeta de salida>

Escribe `g_000.png … g_NNN.png` y `mapa.txt` con el `string_map` en el mismo orden.
"""
import os
import sys

# Sin `"` ni `\`: los dos hay que escaparlos dentro del literal de GML y es la vía
# más fácil de romper una cadena sin darse cuenta (04 · 58 §2).
MAPA = (" ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        "0123456789.,:;!?-+()áéíóúüñÁÉÍÓÚÜÑ¿¡")
ANCHO, ALTO = 10, 12
TAMANO = 10

CANDIDATAS = [
    "/System/Library/Fonts/Supplemental/Verdana Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    salida = sys.argv[1]
    os.makedirs(salida, exist_ok=True)

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("✗ Falta Pillow: no se han generado los glifos (no es que estén bien).")
        return 2

    ruta = next((c for c in CANDIDATAS if os.path.exists(c)), None)
    if ruta is None:
        print("✗ No encuentro ninguna .ttf del sistema entre: %s" % ", ".join(CANDIDATAS))
        return 2
    fuente = ImageFont.truetype(ruta, TAMANO)

    for i, c in enumerate(MAPA):
        im = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if c == " ":
            # La barra sólida del espacio. Si la sub-imagen va vacía, el ancho del
            # espacio lo decide el motor y no tú: el banco lo mide con string_width().
            d.rectangle([0, 0, 3, ALTO - 1], fill=(255, 255, 255, 255))
        else:
            d.text((0, 0), c, font=fuente, fill=(255, 255, 255, 255))

        # Umbral duro: sin antialias no hay halo de alfa parcial, así que el resultado
        # es pixel art de verdad y la puerta del peldaño 2 bis lo deja en paz.
        px = im.load()
        for y in range(ALTO):
            for x in range(ANCHO):
                px[x, y] = (255, 255, 255, 255) if px[x, y][3] > 128 else (0, 0, 0, 0)
        im.save(os.path.join(salida, "g_%03d.png" % i))

    with open(os.path.join(salida, "mapa.txt"), "w", encoding="utf-8") as f:
        f.write(MAPA)
    print("%d glifos de %dx%d en %s (fuente: %s)"
          % (len(MAPA), ANCHO, ALTO, salida, os.path.basename(ruta)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
