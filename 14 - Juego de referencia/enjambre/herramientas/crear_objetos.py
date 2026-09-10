#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crea objetos, eventos y salas con `resourcetool`. Y VERIFICA leyendo de vuelta.

Lección de esta misma sesión: `sound set` y `sound import` no existen —el subcomando es
`SOUND SETFILE`— y aun así el script anterior los dio por buenos porque la salida
contenía «Success» (de guardar el proyecto, no de importar el audio). Las carpetas de
sonido quedaron vacías. Aquí no se busca una palabra en la salida: se comprueba el disco.
"""
import os
import subprocess
import sys

PROY = sys.argv[1]

OBJETOS = {
    # objeto: [(tipo, subtipo, sufijo_del_gml)]
    "obj_control":  [("create", None, "Create_0"), ("step", "step_normal", "Step_0"),
                     ("other", "room_start", "Other_4"), ("cleanup", None, "CleanUp_0")],
    "obj_titulo":   [("create", None, "Create_0"), ("step", "step_normal", "Step_0"),
                     ("draw", "gui", "Draw_64")],
    "obj_juego":    [("create", None, "Create_0"), ("step", "step_normal", "Step_0"),
                     ("draw", "gui", "Draw_64"), ("cleanup", None, "CleanUp_0")],
    "obj_nave":     [("create", None, "Create_0"), ("step", "step_normal", "Step_0"),
                     ("draw", "draw_normal", "Draw_0")],
    "obj_enemigo":  [("create", None, "Create_0"), ("step", "step_normal", "Step_0"),
                     ("draw", "draw_normal", "Draw_0")],
    "obj_bala":     [("create", None, "Create_0"), ("step", "step_normal", "Step_0")],
    "obj_celda":    [("create", None, "Create_0"), ("step", "step_normal", "Step_0")],
    "obj_explosion": [("create", None, "Create_0"), ("step", "step_normal", "Step_0"),
                      ("draw", "draw_normal", "Draw_0")],
    "obj_estrella": [("create", None, "Create_0"), ("step", "step_normal", "Step_0"),
                     ("draw", "draw_normal", "Draw_0")],
}
SALAS = ["rm_titulo", "rm_juego"]


def ev(orden):
    r = subprocess.run(["gm-cli", "resourcetool", "eval", orden], cwd=PROY,
                       capture_output=True, text=True)
    return r.stdout + r.stderr


def main():
    for obj, eventos in OBJETOS.items():
        ev("resource create type=object name=%s" % obj)
        for tipo, subtipo, _suf in eventos:
            # Los eventos SIN subtipo (Create, CleanUp, Destroy) hay que pedirlos sin el
            # argumento: mandar `subtype=create` los rompe en silencio y no crea nada.
            # Medido en esta sesión; no está en ninguna documentación.
            orden = "object event findorcreate name=%s type=%s" % (obj, tipo)
            if subtipo:
                orden += " subtype=%s" % subtipo
            ev(orden)
        print("  objeto %-16s %d evento(s)" % (obj, len(eventos)))

    for sala in SALAS:
        ev("resource create type=room name=%s" % sala)
        print("  sala   %s" % sala)

    # --- lo que una sala necesita para SER una sala -----------------------------
    # Crear el recurso no basta: sin tamaño, sin instancias y sin orden, el juego
    # compila y arranca en una sala vacía. Estos tres pasos se hacían a mano y no
    # estaban en la receta; se descubrió reconstruyendo el juego desde cero con solo
    # lo publicado. Una receta que hay que completar de memoria no es una receta.

    # 1 · rm_juego mide 683×384 y la cámara la estira a la ventana (escala 2). Con la
    #     sala al tamaño de la ventana, una nave de 24 px se ve como una mota.
    ev("resource set expr=rm_juego.roomSettings.Width value=683")
    ev("resource set expr=rm_juego.roomSettings.Height value=384")

    # 2 · Las instancias. `obj_control` es persistente y va en las dos salas: es quien
    #     sostiene el estado global, la música y la fuente.
    for sala, objetos in (("rm_titulo", ["obj_control", "obj_titulo"]),
                          ("rm_juego",  ["obj_control", "obj_juego"])):
        for i, obj in enumerate(objetos):
            ev("room instance create room=%s object=%s x=%d y=32" % (sala, obj, 32 + i * 32))
        print("  instancias en %-10s %s" % (sala, ", ".join(objetos)))

    # 3 · El orden de salas: se entra por la portada, no por el nivel — lo comprueba
    #     `auditar-juego-completo.py`. `gm-cli init` deja `room1` la primera.
    for i, sala in enumerate(["rm_titulo", "rm_juego", "room1"]):
        ev("resource set expr=project.RoomOrderNodes[%d].roomId value=%s" % (i, sala))
    print("  orden de salas: rm_titulo → rm_juego → room1")

    print("\n--- verificación sobre el DISCO, no sobre la salida del comando ---")
    fallos = []
    for obj, eventos in OBJETOS.items():
        d = os.path.join(PROY, "objects", obj)
        if not os.path.isdir(d):
            fallos.append("falta la carpeta de %s" % obj)
            continue
        for _t, _s, suf in eventos:
            if not os.path.isfile(os.path.join(d, suf + ".gml")):
                fallos.append("%s: falta %s.gml" % (obj, suf))
    for sala in SALAS:
        if not os.path.isdir(os.path.join(PROY, "rooms", sala)):
            fallos.append("falta la sala %s" % sala)
    # El orden de salas se lee del .yyp en crudo: es la única forma de comprobar que
    # se entra por la portada, y «Saved successfully» no lo demuestra.
    # El .yyp se BUSCA, no se deduce del nombre de la carpeta: con `PROY = "."`
    # —que es como lo llama la receta— `os.path.basename(".")` da "." y el archivo
    # nunca aparecía. El síntoma era «la primera sala es None», que parecía un fallo
    # del orden de salas y era de esta línea.
    yyp = ""
    try:
        for _f in os.listdir(PROY):
            if _f.endswith(".yyp"):
                with open(os.path.join(PROY, _f), encoding="utf-8", errors="replace") as fh:
                    yyp = fh.read()
                break
    except OSError:
        pass
    import re as _re
    orden = _re.findall(r'"roomId":\{"name":"([a-z_0-9]+)"', yyp)
    if orden[:1] != ["rm_titulo"]:
        fallos.append("la primera sala del orden es %r, debería ser rm_titulo"
                      % (orden[0] if orden else None))
    else:
        print("  orden verificado en el .yyp: %s" % " → ".join(orden[:3]))
    if fallos:
        print("✗ %d problema(s):" % len(fallos))
        for f in fallos:
            print("   ·", f)
        return 1
    print("✓ %d objetos con todos sus .gml en disco, y %d salas."
          % (len(OBJETOS), len(SALAS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
