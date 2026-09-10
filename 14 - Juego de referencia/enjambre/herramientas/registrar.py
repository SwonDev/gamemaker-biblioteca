#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Registra sprites y sonidos en el .yyp con `resourcetool`, NUNCA a mano.

La regla dura de la biblioteca: el `.yy`/`.yyp` no se edita a mano porque su formato es
frágil. Y la otra: «Saved successfully» no es verificación — al final se lee de vuelta
cada recurso y se compara con lo que se pidió.
"""
import os
import subprocess
import sys

PROY = sys.argv[1]
ARTE = os.path.join(PROY, "arte")
SON = os.path.join(PROY, "sonido")

# (nombre, [ficheros de fotograma], origen)  — el origen importa: un sprite que gira
# alrededor de su esquina superior izquierda se comporta mal y no hay forma de arreglarlo
# en el código sin llenarlo de restas.
SPRITES = [
    ("spr_nave",       ["spr_nave_quieta"], "centro"),
    ("spr_nave_prop",  ["spr_nave_0", "spr_nave_1", "spr_nave_2"], "centro"),
    ("spr_rastreador", ["spr_rastreador_%d" % i for i in range(4)], "centro"),
    ("spr_veloz",      ["spr_veloz_%d" % i for i in range(4)], "centro"),
    ("spr_divisor",    ["spr_divisor_%d" % i for i in range(4)], "centro"),
    ("spr_celda",      ["spr_celda_%d" % i for i in range(4)], "centro"),
    ("spr_bala",       ["spr_bala_0"], "centro"),
    ("spr_bala_enemiga", ["spr_bala_enemiga_0"], "centro"),
    ("spr_explosion",  ["spr_explosion_%d" % i for i in range(6)], "centro"),
    ("spr_estrella",   ["spr_estrella_0"], "centro"),
    ("spr_estrella2",  ["spr_estrella_1"], "centro"),
]
SONIDOS = ["snd_disparo", "snd_impacto", "snd_estallido", "snd_recoger",
           "snd_herido", "snd_oleada", "snd_clic", "snd_musica"]

# La hoja de glifos: 89 sub-imágenes, una por carácter, que `font_add_sprite_ext`
# convierte en la fuente del juego. Iba suelta y había que acordarse de importarla a
# mano — se descubrió reconstruyendo el juego desde cero con solo lo publicado: el
# resultado compilaba y no dibujaba una sola letra. Una receta que hay que completar
# de memoria no es una receta.
GLIFOS = "glifos"


def ev(orden, silencioso=True):
    r = subprocess.run(["gm-cli", "resourcetool", "eval", orden], cwd=PROY,
                       capture_output=True, text=True)
    ok = "Saved successfully" in r.stdout or "Success" in r.stdout
    if not ok and not silencioso:
        print("   ! ", orden, "->", (r.stdout + r.stderr).strip()[-200:])
    return ok, r.stdout


def glob_iconos(proy):
    """PNG dentro de options/: la prueba de que el icono llegó de verdad."""
    fuera = []
    base = os.path.join(proy, "options")
    for r, _d, fs in os.walk(base):
        fuera += [os.path.join(r, f) for f in fs if f.lower().endswith(".png")]
    return fuera


def tam(png):
    from PIL import Image
    with Image.open(png) as im:
        return im.size


def main():
    fallos = []
    for nombre, ficheros, origen in SPRITES:
        ev("resource create type=sprite name=%s" % nombre)
        for f in ficheros:
            ruta = os.path.join(ARTE, f + ".png")
            ok, _ = ev('sprite addframe name=%s path="%s"' % (nombre, ruta))
            if not ok:
                fallos.append("addframe %s <- %s" % (nombre, f))
        if origen == "centro":
            w, h = tam(os.path.join(ARTE, ficheros[0] + ".png"))
            ev("resource set expr=%s.origin value=Custom" % nombre)
            ev("resource set expr=%s.sequence.xorigin value=%d" % (nombre, w // 2))
            ev("resource set expr=%s.sequence.yorigin value=%d" % (nombre, h // 2))
        print("  sprite %-18s %d fotograma(s)" % (nombre, len(ficheros)))

    for s in SONIDOS:
        ev("resource create type=sound name=%s" % s)
        # El subcomando es **SOUND SETFILE**. `sound set` y `sound import` NO existen —y
        # lo peor: no fallan de forma reconocible. La salida contiene «Success» (del
        # guardado del proyecto, no del import), así que un script que busque esa palabra
        # da por importados ocho sonidos que dejaron su carpeta vacía. El juego compila
        # entonces con ocho `Failed to convert audio file … does not exist`.
        # (12 · 09 §0 trampa 16, encontrada dos veces: la segunda, aquí.)
        ev('sound setfile name=%s path="%s"' % (s, os.path.join(SON, s + ".wav")))
        # La verificación NO es la salida del comando: es el archivo en el disco.
        destino = os.path.join(PROY, "sounds", s)
        hay = os.path.isdir(destino) and any(
            f.lower().endswith((".wav", ".ogg", ".mp3")) for f in os.listdir(destino))
        if not hay:
            fallos.append("sonido %s: la carpeta del proyecto no tiene audio dentro" % s)
        print("  sonido %-18s %s" % (s, "audio en disco ✓" if hay else "✗ CARPETA VACÍA"))

    # --- la hoja de glifos ------------------------------------------------------
    dir_glifos = os.path.join(PROY, GLIFOS)
    if os.path.isdir(dir_glifos):
        marcos = sorted(f for f in os.listdir(dir_glifos)
                        if f.startswith("g_") and f.endswith(".png"))
        ev("resource create type=sprite name=spr_glifos")
        for f in marcos:
            ok, _ = ev('sprite addframe name=spr_glifos path="%s"'
                       % os.path.join(dir_glifos, f))
            if not ok:
                fallos.append("glifo %s" % f)
        print("  sprite %-18s %d glifo(s)" % ("spr_glifos", len(marcos)))
        if not marcos:
            fallos.append("la carpeta de glifos existe pero está vacía")
    else:
        fallos.append("falta la carpeta «%s»: genérala con generar_glifos.py" % GLIFOS)

    # --- el icono del ejecutable -------------------------------------------------
    # `auditar-juego-completo.py` lo exige (05/02 §4.4) y la receta no lo producía.
    # OJO: el argumento es `property=`, no `name=` — con `name=` responde
    # «Ignoring Argument: NAME» y no escribe nada (12 · 09 §0 trampa 16).
    icono = os.path.join(PROY, "icono", "icono_1024.png")
    if os.path.isfile(icono):
        ev('options set platform=mac property=icon_png value="%s"' % icono)
        hay_icono = bool(glob_iconos(PROY))
        print("  icono  %-18s %s" % ("icon_png",
                                     "en options/ ✓" if hay_icono else "✗ NO llegó"))
        if not hay_icono:
            fallos.append("el icono no llegó a options/")
    else:
        fallos.append("falta el icono: genéralo con generar_icono.py")

    print("\n--- verificación: se lee de vuelta lo escrito ---")
    for nombre, ficheros, _o in SPRITES:
        _ok, out = ev("resource info expr=%s" % nombre)
        hay = nombre in out
        print("  %-18s %s" % (nombre, "leído del .yy ✓" if hay else "✗ NO aparece"))
        if not hay:
            fallos.append("verificación %s" % nombre)

    if fallos:
        print("\n✗ %d problema(s):" % len(fallos))
        for f in fallos[:12]:
            print("   ·", f)
        return 1
    print("\n✓ %d sprites y %d sonidos registrados y verificados." % (len(SPRITES), len(SONIDOS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
