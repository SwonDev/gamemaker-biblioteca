#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Icono del ejecutable, a partir del mismo sprite de la nave.

El icono y la identidad visual del juego tienen que ser la misma cosa (07 · 24): si el
icono es un logotipo ajeno al arte, lo primero que ve alguien de tu juego no se parece
al juego. Aquí se dibuja con la misma paleta y la misma nave.

Existe porque `auditar-juego-completo.py` comprueba «icono o splash propios en
options/» y la receta no lo producía: quien la seguía al pie de la letra sacaba un ✗ en
el auditor de la propia biblioteca. Encontrado por un auditor externo reconstruyendo el
juego solo con el README.

    python3 herramientas/generar_icono.py <carpeta de arte> <carpeta de salida>
"""
import os
import sys

from PIL import Image, ImageDraw

# Windows: sin esto, imprimir un ✓ revienta con UnicodeEncodeError en cuanto la salida
# no es una consola interactiva.
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ARTE = sys.argv[1] if len(sys.argv) > 1 else "arte"
SALIDA = sys.argv[2] if len(sys.argv) > 2 else "icono"
N = 1024                      # `options set property=icon_png` EXIGE 1024×1024 exactos


def main():
    base = os.path.join(ARTE, "spr_nave_1.png")
    if not os.path.isfile(base):
        print("✗ Falta «%s»: genera antes el arte con generar_arte.py." % base)
        print("  NO se ha creado ningún icono.")
        return 2
    os.makedirs(SALIDA, exist_ok=True)
    nave = Image.open(base).convert("RGBA")

    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Disco con degradado radial dibujado a mano: sin dependencias de más.
    for r in range(N // 2, 0, -2):
        t = 1 - r / (N / 2)
        c = (int(13 + t * 40), int(15 + t * 34), int(28 + t * 70), 255)
        d.ellipse([N / 2 - r, N / 2 - r, N / 2 + r, N / 2 + r], fill=c)
    d.ellipse([18, 18, N - 18, N - 18], outline=(250, 196, 84, 255), width=22)
    g = nave.resize((nave.width * 26, nave.height * 26), Image.NEAREST)
    im.alpha_composite(g, ((N - g.width) // 2, (N - g.height) // 2 - 20))

    ruta = os.path.join(SALIDA, "icono_1024.png")
    im.save(ruta)
    ancho, alto = Image.open(ruta).size
    if (ancho, alto) != (N, N):
        print("✗ El icono salió %dx%d y `options set` exige %dx%d." % (ancho, alto, N, N))
        return 1
    print("✓ icono %dx%d en %s" % (ancho, alto, ruta))
    return 0


if __name__ == "__main__":
    sys.exit(main())
