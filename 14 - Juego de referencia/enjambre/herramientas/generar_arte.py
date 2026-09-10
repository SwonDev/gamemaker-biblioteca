#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera TODO el pixel art de «Enjambre» por código, sobre una paleta cerrada.

Por qué por código y no un PNG bajado: `12 · 09 §5.2` prohíbe entregar el rectángulo de
color, y la escalera dice que el peldaño 1 —dibujo por código con criterio— es una salida
digna. «Con criterio» significa silueta legible a 1×, sombreado en tres tonos, luz
consistente desde arriba-izquierda y contorno más oscuro que el relleno. Un cuadrado no es
ninguna de esas cosas.
"""
import math
import os
import sys

from PIL import Image, ImageDraw

SALIDA = sys.argv[1] if len(sys.argv) > 1 else "arte"
os.makedirs(SALIDA, exist_ok=True)

# Paleta cerrada de 16. Cerrada a propósito: es lo que hace que 40 sprites dibujados en
# ratos distintos parezcan del mismo juego (13 · 03 §4).
P = {
    "vacio":   (0, 0, 0, 0),
    "tinta":   (13, 15, 28, 255),
    "sombra":  (32, 38, 66, 255),
    "acero":   (74, 88, 128, 255),
    "acero2":  (112, 132, 178, 255),
    "hielo":   (176, 196, 232, 255),
    "nieve":   (238, 244, 255, 255),
    "ambar":   (250, 196, 84, 255),
    "ambar2":  (206, 140, 42, 255),
    "fuego":   (240, 108, 62, 255),
    "sangre":  (176, 48, 66, 255),
    "veneno":  (128, 220, 128, 255),
    "veneno2": (66, 150, 88, 255),
    "plasma":  (126, 214, 234, 255),
    "plasma2": (56, 138, 172, 255),
    "violeta": (150, 96, 196, 255),
}


def lienzo(w, h):
    return Image.new("RGBA", (w, h), P["vacio"])


def guardar(im, nombre, escala=1):
    if escala != 1:
        im = im.resize((im.width * escala, im.height * escala), Image.NEAREST)
    ruta = os.path.join(SALIDA, nombre + ".png")
    im.save(ruta)
    return ruta


def simetrico(d, x, y, cx, color):
    """Pinta el píxel y su espejo respecto al eje vertical `cx`."""
    d.point((x, y), color)
    d.point((2 * cx - x, y), color)


# ─────────────────────────────────────────────────────────────────────────────
# La nave: 20×20, morro arriba. Silueta de punta de flecha con alas cortas —
# se reconoce a 1× y su dirección se lee sin dudar, que es lo único que importa
# en un cenital que gira.
# ─────────────────────────────────────────────────────────────────────────────
def nave(llama=0):
    """24×22. Alas anchas y morro estrecho: la silueta tiene que decir «hacia dónde
    apunta» a 1×, antes de que se distinga ningún detalle. La primera versión era un
    huso sin alas —se veía como una gota— y eso solo salta MIRANDO el PNG, no leyendo
    el código que lo dibuja."""
    im = lienzo(24, 22)
    d = ImageDraw.Draw(im)
    # Alas: dos cuñas anchas y bajas. Son la mitad de la lectura de la silueta.
    d.polygon([(1, 16), (8, 9), (8, 17), (4, 19)], fill=P["acero"], outline=P["tinta"])
    d.polygon([(22, 16), (15, 9), (15, 17), (19, 19)], fill=P["acero"], outline=P["tinta"])
    d.polygon([(2, 16), (8, 11), (8, 16)], fill=P["sombra"])
    d.polygon([(21, 16), (15, 11), (15, 16)], fill=P["acero2"])
    # Fuselaje: morro de punta, cuerpo recto, cola marcada.
    d.polygon([(12, 0), (15, 7), (16, 17), (13, 20), (10, 20), (7, 17), (8, 7)],
              fill=P["acero2"], outline=P["tinta"])
    d.polygon([(12, 2), (14, 8), (14, 16), (12, 18), (11, 18), (9, 16), (9, 8)],
              fill=P["hielo"])
    d.polygon([(13, 6), (15, 9), (15, 16), (13, 18)], fill=P["acero"])   # sombra derecha
    # Cabina, que es lo que hace que parezca pilotada y no un misil.
    d.ellipse([10, 5, 13, 10], fill=P["plasma"], outline=P["plasma2"])
    d.point((11, 6), P["nieve"])
    # Cañones en las puntas de las alas: dicen de dónde saldrá el disparo.
    for x in (5, 18):
        d.rectangle([x, 12, x + 1, 16], fill=P["hielo"], outline=P["tinta"])
    if llama:
        largo = [3, 6, 4][llama - 1]
        d.polygon([(10, 20), (13, 20), (12, 20 + largo), (11, 20 + largo)], fill=P["ambar"])
        d.polygon([(11, 20), (12, 20), (12, 19 + largo), (11, 19 + largo)], fill=P["nieve"])
        d.point((9, 20), P["ambar2"]); d.point((14, 20), P["ambar2"])
    return im


# ─────────────────────────────────────────────────────────────────────────────
# Enemigos: tres siluetas DISTINTAS entre sí, no el mismo bicho recoloreado.
# Que se distingan de un vistazo es diseño, no adorno: decide si el jugador
# reacciona a tiempo (13 · 03 §5).
# ─────────────────────────────────────────────────────────────────────────────
def rastreador(f=0):
    """Lento y macizo: hexágono con núcleo que late."""
    im = lienzo(18, 18)
    d = ImageDraw.Draw(im)
    r = 8
    pts = [(9 + r * math.cos(math.radians(60 * i - 90)),
            9 + r * math.sin(math.radians(60 * i - 90))) for i in range(6)]
    d.polygon(pts, fill=P["veneno2"], outline=P["tinta"])
    pts2 = [(9 + (r - 3) * math.cos(math.radians(60 * i - 90)),
             9 + (r - 3) * math.sin(math.radians(60 * i - 90))) for i in range(6)]
    d.polygon(pts2, fill=P["veneno"])
    latido = [2, 3, 2, 1][f % 4]
    d.ellipse([9 - latido, 9 - latido, 9 + latido, 9 + latido], fill=P["nieve"])
    d.point((7, 6), P["nieve"])
    return im


def veloz(f=0):
    """Rápido y frágil: rombo afilado con estela."""
    im = lienzo(16, 16)
    d = ImageDraw.Draw(im)
    d.polygon([(8, 0), (13, 8), (8, 15), (3, 8)], fill=P["sangre"], outline=P["tinta"])
    d.polygon([(8, 2), (11, 8), (8, 12), (5, 8)], fill=P["fuego"])
    d.polygon([(8, 4), (9, 8), (8, 10), (7, 8)], fill=P["ambar"])
    est = [0, 1, 2, 1][f % 4]
    if est:
        d.line([(8, 15), (8, 15 + est)], fill=P["fuego"])
    return im


def divisor(f=0):
    """Se parte al morir: círculo con costuras que se abren."""
    im = lienzo(20, 20)
    d = ImageDraw.Draw(im)
    d.ellipse([1, 1, 18, 18], fill=P["violeta"], outline=P["tinta"])
    d.ellipse([4, 3, 15, 14], fill=P["plasma2"])
    sep = [0, 1, 2, 1][f % 4]
    d.line([(10 - sep, 1), (10 - sep, 18)], fill=P["tinta"])
    d.line([(1, 10 + sep), (18, 10 + sep)], fill=P["tinta"])
    d.ellipse([7, 7, 12, 12], fill=P["nieve"])
    d.point((6, 5), P["nieve"])
    return im


def celda(f=0):
    """La recompensa: brilla para que se vea entre el caos."""
    im = lienzo(12, 12)
    d = ImageDraw.Draw(im)
    b = [0, 1, 2, 1][f % 4]
    d.polygon([(6, 0), (11, 6), (6, 11), (1, 6)], fill=P["ambar2"], outline=P["tinta"])
    d.polygon([(6, 2), (9, 6), (6, 9), (3, 6)], fill=P["ambar"])
    d.ellipse([5 - b, 5 - b, 6 + b, 6 + b], fill=P["nieve"])
    return im


def bala(color1, color2):
    im = lienzo(8, 8)
    d = ImageDraw.Draw(im)
    d.ellipse([1, 1, 6, 6], fill=color2, outline=P["tinta"])
    d.ellipse([2, 2, 5, 5], fill=color1)
    d.point((3, 3), P["nieve"])
    return im


def explosion(f):
    """Seis fotogramas: crece, se abre en anillo y se apaga. Sin esto, un enemigo
    desaparece de golpe y el impacto no se siente (04 · 39)."""
    im = lienzo(32, 32)
    d = ImageDraw.Draw(im)
    c = 16
    radios = [4, 9, 13, 16, 15, 12]
    r = radios[f]
    if f < 2:
        d.ellipse([c - r, c - r, c + r, c + r], fill=P["nieve"])
        d.ellipse([c - r + 2, c - r + 2, c + r - 2, c + r - 2], fill=P["ambar"])
    elif f < 4:
        d.ellipse([c - r, c - r, c + r, c + r], fill=P["ambar"], outline=P["nieve"])
        d.ellipse([c - r + 4, c - r + 4, c + r - 4, c + r - 4], fill=P["fuego"])
    else:
        d.ellipse([c - r, c - r, c + r, c + r], outline=P["fuego"], width=3)
        d.ellipse([c - r + 5, c - r + 5, c + r - 5, c + r - 5], outline=P["ambar2"], width=2)
    # Esquirlas: rompen el círculo perfecto, que es lo que delata una explosión hecha
    # con una elipse y ya está.
    for i in range(8):
        a = math.radians(i * 45 + f * 7)
        x1, y1 = c + math.cos(a) * (r - 1), c + math.sin(a) * (r - 1)
        x2, y2 = c + math.cos(a) * (r + 3), c + math.sin(a) * (r + 3)
        d.line([(x1, y1), (x2, y2)], fill=P["ambar"] if f < 3 else P["fuego"])
    return im


def estrella(tam, color):
    im = lienzo(tam, tam)
    d = ImageDraw.Draw(im)
    d.point((tam // 2, tam // 2), color)
    if tam > 2:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            d.point((tam // 2 + dx, tam // 2 + dy), P["sombra"])
    return im


def generar():
    hechos = []
    for i in range(3):
        hechos.append(guardar(nave(i + 1), "spr_nave_%d" % i))
    hechos.append(guardar(nave(0), "spr_nave_quieta"))
    for i in range(4):
        hechos.append(guardar(rastreador(i), "spr_rastreador_%d" % i))
        hechos.append(guardar(veloz(i), "spr_veloz_%d" % i))
        hechos.append(guardar(divisor(i), "spr_divisor_%d" % i))
        hechos.append(guardar(celda(i), "spr_celda_%d" % i))
    hechos.append(guardar(bala(P["plasma"], P["plasma2"]), "spr_bala_0"))
    hechos.append(guardar(bala(P["fuego"], P["sangre"]), "spr_bala_enemiga_0"))
    for i in range(6):
        hechos.append(guardar(explosion(i), "spr_explosion_%d" % i))
    hechos.append(guardar(estrella(3, P["hielo"]), "spr_estrella_0"))
    hechos.append(guardar(estrella(2, P["acero2"]), "spr_estrella_1"))
    return hechos


if __name__ == "__main__":
    hechos = generar()
    print("%d PNG generados en %s/" % (len(hechos), SALIDA))
