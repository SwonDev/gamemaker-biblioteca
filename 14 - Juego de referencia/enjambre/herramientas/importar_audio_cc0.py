#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sustituye el sonido sintetizado por audio **CC0 real**, si está disponible.

**Por qué es opcional y no obligatorio.** El juego tiene que poder reconstruirse en
cualquier máquina sin depender de una biblioteca de 376 GB que solo existe en un disco.
Por eso el sonido por defecto se **genera con código** (`generar_sonido.py`) y esto es un
peldaño de mejora, no un requisito: si los assets no están, lo dice y se va sin tocar
nada — el juego sigue sonando.

**Por qué CC0 y no cualquier cosa.** La regla número uno de esta biblioteca es la
licencia (`07 · 09 §1`). Los packs de Kenney traen un `License.txt` que dice, literal:

    License: (Creative Commons Zero, CC0)
    This content is free to use in personal, educational and commercial projects.
    Support us by crediting Kenney or www.kenney.nl (this is not mandatory)

Eso permite usarlo Y redistribuirlo. Este script **comprueba esa licencia antes de copiar
nada**: si el `License.txt` de un pack no dice CC0, ese pack no se usa. No se fía del
nombre de la carpeta ni de lo que diga un índice.

    python3 herramientas/importar_audio_cc0.py <proyecto> [<raíz de los assets>]

Sale con 0 si sustituyó el audio · 2 si no había assets (NO es un fallo) · 1 si los
había pero algo no cuadró.
"""
import os
import shutil
import subprocess
import sys

for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

PROY = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
RAIZ_ASSETS = sys.argv[2] if len(sys.argv) > 2 else \
    "/Volumes/NVMETEAM/ASSETS/Biblioteca de Assets"
KENNEY = os.path.join(RAIZ_ASSETS, "5-bundles",
                      "Kenney All-in-1 (2D, 3D, audio, UI)", "Audio")

# sonido del juego → (pack, archivo). El pack se elige por lo que SUENA, no por lo que
# se llama: el disparo de un dron es un láser corto, el impacto es metal, la muerte del
# enemigo es una explosión con cuerpo.
PIEZAS = {
    "snd_disparo":   ("Digital Audio", "laser5.ogg"),
    "snd_impacto":   ("Sci-Fi Sounds", "impactMetal_002.ogg"),
    "snd_estallido": ("Sci-Fi Sounds", "explosionCrunch_002.ogg"),
    "snd_recoger":   ("Digital Audio", "highUp.ogg"),
    "snd_herido":    ("Digital Audio", "lowDown.ogg"),
    "snd_oleada":    ("Digital Audio", "phaserUp1.ogg"),
    "snd_clic":      ("Interface Sounds", "click_002.ogg"),
    "snd_musica":    ("Music Loops", "Space Cadet.ogg"),
}


def licencia_cc0(pack):
    """¿El License.txt de este pack dice CC0? No se copia nada sin comprobarlo."""
    ruta = os.path.join(KENNEY, pack, "License.txt")
    if not os.path.isfile(ruta):
        return False, "sin License.txt"
    try:
        t = open(ruta, encoding="utf-8", errors="replace").read()
    except OSError as e:
        return False, str(e)
    if "creative commons zero" in t.lower() or "cc0" in t.lower():
        return True, "CC0"
    return False, "el License.txt NO dice CC0"


def ev(orden):
    r = subprocess.run(["gm-cli", "resourcetool", "eval", orden], cwd=PROY,
                       capture_output=True, text=True)
    return r.stdout + r.stderr


def main():
    if not os.path.isdir(KENNEY):
        print("· No está la biblioteca de assets en «%s»." % RAIZ_ASSETS)
        print("  El juego se queda con su sonido generado por código, que funciona.")
        print("  Esto NO es un fallo: es un peldaño de mejora que aquí no aplica.")
        return 2
    if not os.path.isdir(os.path.join(PROY, "sounds")):
        print("✗ «%s» no parece el proyecto: no tiene carpeta sounds/." % PROY)
        return 1

    destino = os.path.join(PROY, "sonido_cc0")
    os.makedirs(destino, exist_ok=True)
    fallos, hechos = [], 0
    packs_vistos = {}

    for nombre, (pack, fichero) in sorted(PIEZAS.items()):
        if pack not in packs_vistos:
            packs_vistos[pack] = licencia_cc0(pack)
        ok_lic, motivo = packs_vistos[pack]
        if not ok_lic:
            fallos.append("%s: %s (%s)" % (nombre, motivo, pack))
            print("  ✗ %-14s %s — %s" % (nombre, pack, motivo))
            continue
        origen = os.path.join(KENNEY, pack, fichero)
        if not os.path.isfile(origen):
            # Buscar el archivo por si el pack reorganizó sus carpetas.
            encontrado = None
            for r, _d, fs in os.walk(os.path.join(KENNEY, pack)):
                if fichero in fs:
                    encontrado = os.path.join(r, fichero)
                    break
            if not encontrado:
                fallos.append("%s: no encuentro %s en %s" % (nombre, fichero, pack))
                print("  ✗ %-14s falta %s" % (nombre, fichero))
                continue
            origen = encontrado
        copia = os.path.join(destino, nombre + os.path.splitext(fichero)[1])
        shutil.copy2(origen, copia)
        ev('sound setfile name=%s path="%s"' % (nombre, copia))
        # La verificación es el DISCO, no la salida del comando (trampa 16).
        carpeta = os.path.join(PROY, "sounds", nombre)
        real = [f for f in os.listdir(carpeta)] if os.path.isdir(carpeta) else []
        entro = any(f.lower().endswith((".ogg", ".wav", ".mp3")) for f in real)
        if entro:
            hechos += 1
            print("  ✓ %-14s ← %s / %s  (%s)" % (nombre, pack, fichero, motivo))
        else:
            fallos.append("%s: el audio no llegó al proyecto" % nombre)
            print("  ✗ %-14s no llegó a sounds/%s/" % (nombre, nombre))

    # La atribución no es obligatoria en CC0, pero se pone: cuesta una línea y es lo
    # que hace que la gente siga publicando assets libres.
    creditos = os.path.join(PROY, "CREDITOS-ASSETS.md")
    with open(creditos, "w", encoding="utf-8") as f:
        f.write("# Créditos de assets\n\n"
                "Sonido y música: **Kenney** (<https://kenney.nl>), licencia "
                "**CC0 1.0** — dominio público.\n\n"
                "La atribución no es obligatoria en CC0. Se pone porque cuesta una línea "
                "y es lo que hace que la gente siga publicando assets libres.\n\n"
                "| Sonido del juego | Pack | Archivo |\n|---|---|---|\n")
        for nombre, (pack, fichero) in sorted(PIEZAS.items()):
            f.write("| `%s` | %s | `%s` |\n" % (nombre, pack, fichero))

    print()
    if fallos:
        print("✗ %d pieza(s) no se pudieron sustituir:" % len(fallos))
        for x in fallos[:8]:
            print("   ·", x)
        return 1
    print("✓ %d sonidos sustituidos por audio CC0 de Kenney, con la licencia comprobada"
          " pack a pack." % hechos)
    print("  Créditos escritos en CREDITOS-ASSETS.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
