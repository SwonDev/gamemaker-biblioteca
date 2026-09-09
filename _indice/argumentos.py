#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guardián de argumentos para las herramientas que NO reciben rutas.

**El problema, que es fino y por eso muerde.** Varias herramientas de `_indice/`
trabajan siempre sobre esta biblioteca: no toman una carpeta, la deducen de su
propia ubicación. Si alguien escribe

    python3 _indice/validar-codigo-gml.py ~/MiJuego

Python se traga el argumento sin rechistar, el script analiza **la biblioteca**,
imprime un verde impecable y sale con 0. Quien lo lanzó entiende otra cosa: que su
proyecto está limpio. Se queda tranquilo con un proyecto que nadie ha mirado.

Un verde ajeno es peor que un rojo propio: el rojo se investiga, el verde se cree.

**La regla.** Si sobra un argumento, no se ejecuta nada y se sale con **2**
(«no se ha comprobado»), diciendo qué herramienta sí acepta esa ruta.
"""

import sys

# Windows: en cuanto la salida no es una consola interactiva (pipes, «> archivo», o el
# propio actualizar.py capturando la salida vía subprocess), sys.stdout usa la página de
# códigos ANSI del sistema en vez de UTF-8 — y los ✓/✗/⚠ de este código no caben ahí.
#
# **Medido, ya no supuesto** (2026-09-09, Python 3.12.7 de Windows bajo Wine 11):
#     UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'
# La autoprueba reventaba en la primera línea que imprimía un ✓. Las herramientas que ya
# llevaban estas seis líneas pasaron; las que no, murieron.
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


__all__ = ["exigir_sin_rutas"]


def exigir_sin_rutas(alternativa=None, permitidos=()):
    """Devuelve 2 si sobran argumentos (tras imprimir el motivo), o 0 si no.

    `permitidos` son las banderas que el script sí entiende (`--autoprueba`,
    `--resumen`…). Todo lo demás sobra — **incluida `--autoprueba` si esa
    herramienta no tiene autoprueba**: dejarla pasar haría que
    `construir-indices.py --autoprueba` lanzase una reconstrucción completa
    fingiendo que obedece, que es la misma clase de engaño que este guardián
    existe para impedir.
    """
    permitidos = set(permitidos)
    sobra = [a for a in sys.argv[1:] if a not in permitidos]
    if not sobra:
        return 0
    guion = sys.argv[0].rsplit("/", 1)[-1]
    print(f"✗ «{guion}» no acepta esa clase de argumento: {', '.join(sobra)}")
    print("  Trabaja SIEMPRE sobre esta biblioteca, no sobre la ruta que le pases.")
    if alternativa:
        print("  " + alternativa)
    print("  NO se ha comprobado nada: se sale con 2 en vez de dar por bueno algo")
    print("  que ni siquiera se ha mirado.")
    if permitidos:
        print("  Banderas que sí entiende: " + ", ".join(sorted(permitidos)))
    else:
        print("  No entiende ninguna bandera: se ejecuta sin argumentos.")
    return 2


def autoprueba():
    """Se comprueba ejecutándose a sí misma con y sin argumentos de sobra."""
    import os
    import subprocess

    yo = os.path.abspath(__file__)
    fallos = []

    def revisar(nombre, ok, detalle=""):
        if ok:
            print("  ✓ " + nombre)
        else:
            fallos.append(nombre)
            print("  ✗ %s  ->  %s" % (nombre, detalle))

    guion = ("import sys, os; sys.path.insert(0, %r); "
             "from argumentos import exigir_sin_rutas; "
             "sys.exit(exigir_sin_rutas('Usa otra-cosa.py', %s))")
    base = os.path.dirname(yo)

    r = subprocess.run([sys.executable, "-c", guion % (base, "()")],
                       capture_output=True, text=True)
    revisar("sin argumentos devuelve 0", r.returncode == 0, "exit %d" % r.returncode)

    r = subprocess.run([sys.executable, "-c", guion % (base, "()"), "/ruta/de/alguien"],
                       capture_output=True, text=True)
    revisar("una ruta de sobra devuelve 2", r.returncode == 2, "exit %d" % r.returncode)
    revisar("y dice qué usar en su lugar", "otra-cosa.py" in r.stdout, r.stdout[:80])

    r = subprocess.run([sys.executable, "-c", guion % (base, "()"), "--autoprueba"],
                       capture_output=True, text=True)
    revisar("--autoprueba se rechaza si la herramienta NO tiene autoprueba",
            r.returncode == 2, "exit %d" % r.returncode)

    r = subprocess.run([sys.executable, "-c", guion % (base, "('--autoprueba',)"), "--autoprueba"],
                       capture_output=True, text=True)
    revisar("y se acepta si la declara", r.returncode == 0, "exit %d" % r.returncode)

    r = subprocess.run([sys.executable, "-c", guion % (base, "('--resumen',)"), "--resumen"],
                       capture_output=True, text=True)
    revisar("una bandera declarada se acepta", r.returncode == 0, "exit %d" % r.returncode)

    r = subprocess.run([sys.executable, "-c", guion % (base, "('--resumen',)"), "--inventada"],
                       capture_output=True, text=True)
    revisar("una bandera NO declarada se rechaza", r.returncode == 2, "exit %d" % r.returncode)

    if fallos:
        print("\n✗ %d comprobación(es) de la autoprueba fallan." % len(fallos))
        return 1
    print("\n✓ Las 7 comprobaciones de la autoprueba pasan.")
    return 0


if __name__ == "__main__":
    sys.exit(autoprueba() if "--autoprueba" in sys.argv else 0)
