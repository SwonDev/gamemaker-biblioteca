#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convierte un atlas de `sprite-gen` en sprites de GameMaker.

`sprite-gen` (https://github.com/aldegad/sprite-gen, Apache-2.0) es hoy la mejor
tubería de generación de sprites para un agente: de un solo dibujo saca una hoja
con alfa de verdad y un `manifest.json` con los **rectángulos absolutos** de cada
fotograma. Exporta a Aseprite, Phaser y Flame — **no a GameMaker**, y ese es
justo el paso que falta aquí.

Este script lo cierra. Del manifiesto saca cada fotograma como PNG suelto y
escribe el lote de `resourcetool` que los importa, porque `SPRITE ADDFRAME` añade
**un fotograma por archivo** (12 · 09 §0, Trampa 12): una hoja entera no se
trocea sola.

    python3 _indice/atlas-a-gamemaker.py <run-dir> --salida <carpeta> [--prefijo spr_heroe]

`<run-dir>` es la carpeta de sprite-gen con `manifest.json` y
`sprite-sheet-alpha.png`. Deja en `<carpeta>`:

    <prefijo>_<estado>/000.png …     un PNG por fotograma
    lote-resourcetool.txt            un `resource create` + N `sprite addframe`
    animacion.gml                    los fps y el loop de cada estado, en GML

Y luego, una sola llamada:

    gm-cli resourcetool script <carpeta>/lote-resourcetool.txt <proyecto.yyp>

Sale con 0 si escribió todo, 2 si no pudo mirar (sin Pillow, sin manifiesto,
manifiesto sin `frame_layout`). Cero fotogramas NO es «nada que hacer»: es que
no se ha extraído nada, y eso sale con 2.
"""
import argparse
import json
import os
import re
import sys


def _pillow():
    try:
        from PIL import Image
        return Image
    except ImportError:
        print("✗ Falta Pillow, así que NO se ha extraído ningún fotograma.")
        print("  No es que el atlas esté mal: es que no se ha podido abrir.")
        print("  python3 -m pip install --user Pillow")
        return None


def nombre_gm(texto):
    """Un nombre de recurso de GameMaker: ASCII, minúsculas, sin tildes ni eñes.

    Los identificadores de GML son ASCII puro (`función añadir()` no compila), y
    un estado que venga como «ataque_básico» rompería el recurso.
    """
    tabla = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")
    limpio = texto.translate(tabla).lower()
    limpio = re.sub(r"[^a-z0-9_]+", "_", limpio).strip("_")
    return limpio or "estado"


def cargar_manifiesto(run_dir):
    ruta = os.path.join(run_dir, "manifest.json")
    if not os.path.isfile(ruta):
        print(f"✗ No hay manifest.json en {run_dir}.")
        print("  ¿Es una carpeta de ejecución de sprite-gen? La crea `compose-atlas`.")
        return None
    try:
        with open(ruta, encoding="utf-8") as f:
            man = json.load(f)
    except ValueError as e:
        print(f"✗ manifest.json no es JSON válido: {e}")
        return None
    if "frame_layout" not in man or "rows" not in man.get("frame_layout", {}):
        print("✗ El manifiesto no trae `frame_layout.rows`, que es donde viven los")
        print("  rectángulos de cada fotograma. Sin eso no hay nada que recortar.")
        return None
    return man


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir", help="carpeta de sprite-gen (con manifest.json)")
    ap.add_argument("--salida", required=True, help="carpeta donde dejar los PNG y el lote")
    ap.add_argument("--prefijo", default="spr", help="prefijo de los sprites (por defecto «spr»)")
    ap.add_argument("--atlas", default=None,
                    help="ruta del PNG del atlas (por defecto, el del manifiesto)")
    args = ap.parse_args()

    Image = _pillow()
    if Image is None:
        return 2

    man = cargar_manifiesto(args.run_dir)
    if man is None:
        return 2

    atlas_rel = args.atlas or man.get("game_input") or "sprite-sheet-alpha.png"
    atlas = atlas_rel if os.path.isabs(atlas_rel) else os.path.join(args.run_dir, atlas_rel)
    if not os.path.isfile(atlas):
        print(f"✗ No encuentro el atlas: {atlas}")
        return 2

    hoja = Image.open(atlas).convert("RGBA")
    layout = man["frame_layout"]["rows"]
    animacion = (man.get("animation") or {}).get("rows") or {}

    os.makedirs(args.salida, exist_ok=True)
    lote = []
    gml = ["// GENERADO por _indice/atlas-a-gamemaker.py desde un atlas de sprite-gen.",
           "// Los fps y el bucle vienen del manifiesto; en GameMaker se aplican en código.",
           ""]
    total_fotogramas = 0

    for estado, rects in sorted(layout.items()):
        if not rects:
            continue
        spr = "%s_%s" % (args.prefijo, nombre_gm(estado))
        carpeta = os.path.join(args.salida, spr)
        os.makedirs(carpeta, exist_ok=True)

        lote.append("resource create type=sprite name=%s" % spr)
        for i, r in enumerate(rects):
            try:
                x, y, w, h = int(r["x"]), int(r["y"]), int(r["w"]), int(r["h"])
            except (KeyError, TypeError, ValueError):
                print(f"✗ El rectángulo {i} de «{estado}» no tiene x/y/w/h enteros: {r}")
                return 2
            if w <= 0 or h <= 0:
                print(f"✗ El rectángulo {i} de «{estado}» mide {w}x{h}: no se puede recortar.")
                return 2
            destino = os.path.join(carpeta, "%03d.png" % i)
            hoja.crop((x, y, x + w, y + h)).save(destino)
            lote.append("sprite addframe name=%s path=%s" % (spr, os.path.abspath(destino)))
            total_fotogramas += 1

        info = animacion.get(estado) or {}
        fps = info.get("fps")
        bucle = info.get("loop")
        gml.append("// %s — %d fotograma(s)%s%s" % (
            spr, len(rects),
            (", %s fps" % fps) if fps else "",
            (", en bucle" if bucle else ", una sola vez") if bucle is not None else ""))
        if fps:
            # En GameMaker la velocidad es relativa al framerate del juego: los fps
            # del manifiesto se traducen dividiendo por `game_get_speed`.
            gml.append("//   image_speed = %s / game_get_speed(gamespeed_fps);" % fps)
        if bucle is False:
            gml.append("//   una sola vez: para el sprite en el último fotograma.")
        gml.append("")

    if total_fotogramas == 0:
        print("✗ CERO fotogramas extraídos. El manifiesto tiene `frame_layout.rows`,")
        print("  pero ninguna fila con rectángulos. No es «nada que hacer»: es que no")
        print("  se ha extraído nada.")
        return 2

    ruta_lote = os.path.join(args.salida, "lote-resourcetool.txt")
    with open(ruta_lote, "w", encoding="utf-8") as f:
        f.write("\n".join(lote) + "\n")
    with open(os.path.join(args.salida, "animacion.gml"), "w", encoding="utf-8") as f:
        f.write("\n".join(gml))

    print("✓ %d fotograma(s) en %d sprite(s), de %s"
          % (total_fotogramas, len(layout), os.path.basename(atlas)))
    print("  PNG y lote en: %s" % args.salida)
    print()
    print("  Ahora, UNA sola llamada (el lote evita una invocación por fotograma):")
    print("      gm-cli resourcetool script %s <proyecto.yyp>" % ruta_lote)
    print()
    print("  Y lee de vuelta, que «Saved successfully» no es verificación:")
    print("      gm-cli resourcetool eval \"resource list type=sprite\" <proyecto.yyp>")
    return 0


def autoprueba():
    """Los invariantes del puente, con un atlas de mentira del formato real.

    El puente existe porque `sprite-gen` exporta a Aseprite, Phaser y Flame pero
    no a GameMaker. Sus dos formas de fallar son caras: recortar mal (sprites
    corridos que nadie mira hasta que se ven en pantalla) o callarse cuando no ha
    recortado nada.
    """
    import tempfile
    Image = _pillow()
    if Image is None:
        return 2
    fallos = []

    def revisar(nombre, condicion, detalle=""):
        if condicion:
            print("  \u2713 " + nombre)
        else:
            fallos.append(nombre)
            print("  \u2717 %s  ->  %s" % (nombre, detalle))

    revisar("un estado con tilde se pasa a ASCII, que es lo que exige GML",
            nombre_gm("ataque_básico") == "ataque_basico", nombre_gm("ataque_básico"))
    revisar("y un estado con espacios y mayúsculas también",
            nombre_gm("Correr Rápido") == "correr_rapido", nombre_gm("Correr Rápido"))
    revisar("un nombre que se queda vacío no genera un recurso sin nombre",
            nombre_gm("###") == "estado", nombre_gm("###"))

    with tempfile.TemporaryDirectory() as tmp:
        run = os.path.join(tmp, "run")
        os.makedirs(run)
        celda = 8
        hoja = Image.new("RGBA", (celda * 2, celda), (0, 0, 0, 0))
        hoja.paste(Image.new("RGBA", (celda, celda), (255, 0, 0, 255)), (0, 0))
        hoja.paste(Image.new("RGBA", (celda, celda), (0, 255, 0, 255)), (celda, 0))
        hoja.save(os.path.join(run, "sprite-sheet-alpha.png"))
        man = {"game_input": "sprite-sheet-alpha.png",
               "animation": {"rows": {"idle": {"fps": 8, "loop": True}}},
               "frame_layout": {"rows": {"idle": [
                   {"x": 0, "y": 0, "w": celda, "h": celda},
                   {"x": celda, "y": 0, "w": celda, "h": celda}]}}}
        json.dump(man, open(os.path.join(run, "manifest.json"), "w", encoding="utf-8"))

        salida = os.path.join(tmp, "out")
        sys.argv = ["x", run, "--salida", salida, "--prefijo", "spr_p"]
        revisar("un run correcto sale con 0", main() == 0)
        revisar("recorta un PNG por fotograma",
                len([f for f in os.listdir(os.path.join(salida, "spr_p_idle"))
                     if f.endswith(".png")]) == 2)
        recorte = Image.open(os.path.join(salida, "spr_p_idle", "001.png")).convert("RGBA")
        revisar("y recorta el rectángulo CORRECTO, no el de al lado",
                recorte.size == (celda, celda) and recorte.getpixel((0, 0))[:3] == (0, 255, 0),
                recorte.getpixel((0, 0)))
        lote = open(os.path.join(salida, "lote-resourcetool.txt"), encoding="utf-8").read()
        revisar("el lote crea el sprite y añade sus dos fotogramas",
                lote.count("resource create type=sprite") == 1
                and lote.count("sprite addframe") == 2, lote[:80])
        gml = open(os.path.join(salida, "animacion.gml"), encoding="utf-8").read()
        revisar("y el GML lleva los fps del manifiesto", "8 / game_get_speed" in gml, gml[-90:])

        # Un manifiesto sin filas NO puede salir con 0.
        run2 = os.path.join(tmp, "run2")
        os.makedirs(run2)
        Image.new("RGBA", (4, 4)).save(os.path.join(run2, "sprite-sheet-alpha.png"))
        json.dump({"frame_layout": {"rows": {}}},
                  open(os.path.join(run2, "manifest.json"), "w", encoding="utf-8"))
        sys.argv = ["x", run2, "--salida", os.path.join(tmp, "out2")]
        revisar("cero fotogramas NO sale con 0", main() == 2)

        # Y un rectángulo imposible se dice, no se recorta a lo loco.
        run3 = os.path.join(tmp, "run3")
        os.makedirs(run3)
        Image.new("RGBA", (4, 4)).save(os.path.join(run3, "sprite-sheet-alpha.png"))
        json.dump({"frame_layout": {"rows": {"idle": [{"x": 0, "y": 0, "w": 0, "h": 4}]}}},
                  open(os.path.join(run3, "manifest.json"), "w", encoding="utf-8"))
        sys.argv = ["x", run3, "--salida", os.path.join(tmp, "out3")]
        revisar("un rectángulo de ancho cero NO sale con 0", main() == 2)

    if fallos:
        print("\n\u2717 %d comprobación(es) de la autoprueba fallan." % len(fallos))
        return 1
    print("\n\u2713 Las 10 comprobaciones de la autoprueba pasan.")
    return 0


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    sys.exit(main())
