#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""auditar-juego-completo.py — ¿este proyecto es un juego, o solo un bucle de juego?

    python3 "_indice/auditar-juego-completo.py" <ruta-del-proyecto> [--json] [--laxo]

El fallo más repetido de un agente al que le piden «hazme un juego» no es escribir mal
el GML: es entregar el bucle de juego SIN el juego alrededor. Sin menú, sin pausa, sin
guardado, sin créditos, con la historia recortada en silencio y con rectángulos de
colores donde debería haber sprites. Compila, se ejecuta, y no es un juego.

`04 - Recetas por género/00 - Anatomía de un juego completo.md` tiene la lista maestra
que evita eso, pero es una lista que hay que leer y comparar a mano — y justo por eso se
salta. Este script hace mecánicamente lo que se puede hacer mecánicamente: mira el `.yyp`,
los `.yy` de los objetos y todo el `.gml`, y dice qué piezas del envoltorio NO encuentra.

Qué es y qué NO es
------------------
Es un DETECTOR DE AUSENCIAS, no un juez de calidad. Encuentra un menú porque hay una room
que se llama `rm_menu`; no sabe si ese menú es bueno, ni siquiera si funciona. Al revés
también falla: un juego con el menú dentro de `rm_principal` y una variable `estado_ui`
saldrá marcado como «sin menú» y será un falso positivo.

Por eso **cada ✗ es una pregunta, no una acusación**. La regla de la biblioteca es que lo
que se recorta se dice: si tu juego no lleva créditos a propósito, escríbelo en tu informe
y sigue. Lo que este script impide es lo otro — que falte y nadie se dé cuenta.

Código de salida
----------------
1 si falta alguna pieza del envoltorio (para que un agente no pueda ignorarlo), 0 si están
todas. Con `--laxo`, siempre 0: para cuando ya has justificado los recortes por escrito.
"""
import os, re, sys, json, argparse

DRAW_GUI = "Draw_64.gml"      # número real verificado en 12/09 §2.3

# Cada pieza: (clave, título, patrón sobre nombres de recurso, patrón sobre el GML)
# Un recurso cuenta si su NOMBRE casa; el GML cuenta si alguna línea casa. Basta uno.
PIEZAS = [
    ("menu",      "Menú principal",
     r"menu|men[uú]|titulo|t[ií]tulo|title|portada|inicio",
     r"\b(men[uú]_|obj_menu|rm_menu|estado_menu)\w*"),
    ("opciones",  "Pantalla de opciones",
     r"opcion|option|ajuste|setting|config",
     r"\b(opciones|ajustes|settings)\w*\s*[=\(\.]"),
    ("pausa",     "Pausa que congela el mundo",
     r"pausa|pause",
     r"instance_deactivate_all|\bpausad[oa]\b|\bglobal\.pausa\b|\bis_paused\b"),
    ("guardado",  "Guardar y cargar la partida",
     r"save|guardar|partida",
     r"\b(game_save|file_text_open_write|buffer_save|json_stringify)\s*\("),
    ("creditos",  "Créditos",
     r"credito|cr[eé]dito|credit",
     r"\bcr[eé]ditos?\b"),
    ("game_over", "Muerte / Game Over / cierre",
     r"gameover|game_over|derrota|muerte|final|ending",
     r"\b(game_over|derrota|has_muerto|reintentar)\w*"),
    ("sonido",    "Sonido en el juego",
     r"^snd_|^mus_|^sfx_",
     r"\baudio_play_sound\s*\("),
    ("mando",     "Se juega también con mando",
     r"",
     r"\bgamepad_\w+\s*\("),
]


def leer(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def cargar_proyecto(ruta):
    yyps = [e for e in os.listdir(ruta) if e.endswith(".yyp")] if os.path.isdir(ruta) else []
    if not yyps:
        return None
    txt = leer(os.path.join(ruta, yyps[0]))
    # El .yy/.yyp de GameMaker lleva comas finales: no es JSON válido. Se lee con regex,
    # que además es inmune a los cambios de formato entre versiones del IDE.
    recursos = re.findall(r'"id":\{"name":"([^"]+)","path":"([^"]+)"', txt)
    orden    = re.findall(r'"roomId":\{"name":"([^"]+)"', txt)
    return {"yyp": yyps[0], "recursos": recursos, "orden_salas": orden}


def gml_del_proyecto(ruta):
    fuera = {"node_modules", ".git", "datafiles", "extensions"}
    out = []
    for base, dirs, files in os.walk(ruta):
        dirs[:] = [d for d in dirs if d not in fuera]
        for f in files:
            if f.endswith(".gml"):
                out.append(os.path.join(base, f))
    return out


def objetos_rectangulo(ruta):
    """Objetos SIN sprite cuyo evento Draw pinta figuras a mano.

    Es la firma exacta del «rectángulo de color como personaje» que prohíbe la skill.
    Un objeto sin sprite que dibuja un rectángulo puede ser legítimo (una zona de
    disparo, una caja de depuración), así que esto se reporta como aviso y con nombres:
    quien lo lee decide cuáles son de verdad un personaje sin arte.
    """
    dir_obj = os.path.join(ruta, "objects")
    if not os.path.isdir(dir_obj):
        return []
    figuras = re.compile(r"\bdraw_(rectangle|circle|ellipse|roundrect|triangle)\w*\s*\(")
    sospechosos = []
    for nom in sorted(os.listdir(dir_obj)):
        carpeta = os.path.join(dir_obj, nom)
        yy = os.path.join(carpeta, nom + ".yy")
        if not os.path.isfile(yy):
            continue
        if '"spriteId":null' not in leer(yy).replace(" ", ""):
            continue                      # tiene sprite: no es el caso
        for ev in ("Draw_0.gml", DRAW_GUI):
            p = os.path.join(carpeta, ev)
            if os.path.isfile(p) and figuras.search(leer(p)):
                sospechosos.append(nom)
                break
    return sospechosos


def main():
    ap = argparse.ArgumentParser(description="Audita el envoltorio de un juego GameMaker.")
    ap.add_argument("proyecto")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--laxo", action="store_true",
                    help="no falle aunque falten piezas (cuando ya justificaste los recortes)")
    a = ap.parse_args()

    ruta = os.path.abspath(os.path.expanduser(a.proyecto))
    proy = cargar_proyecto(ruta)
    if proy is None:
        print("✗ No encuentro ningún .yyp en «%s».\n"
              "  Pásame la CARPETA del proyecto, la que contiene el .yyp." % ruta)
        return 2

    nombres = [n for n, _ in proy["recursos"]]
    tipos = {}
    for n, p in proy["recursos"]:
        tipos.setdefault(p.split("/", 1)[0], []).append(n)

    gml = "\n".join(leer(f) for f in gml_del_proyecto(ruta))

    res, faltan = {}, []
    for clave, titulo, pat_nom, pat_gml in PIEZAS:
        hay = False
        if pat_nom:
            r = re.compile(pat_nom, re.I)
            hay = any(r.search(n) for n in nombres)
        if not hay and pat_gml:
            hay = bool(re.search(pat_gml, gml, re.I))
        res[clave] = hay
        if not hay:
            faltan.append(titulo)

    # El arranque: la PRIMERA sala del orden es por donde entra el jugador.
    primera = proy["orden_salas"][0] if proy["orden_salas"] else None
    arranque_ok = bool(primera and re.search(r"menu|men[uú]|titulo|t[ií]tulo|title|splash|logo|intro|inicio",
                                             primera, re.I))
    res["arranque"] = arranque_ok

    rect = objetos_rectangulo(ruta)
    n_sprites = len(tipos.get("sprites", []))
    debug = len(re.findall(r"\bshow_debug_message\s*\(", gml))

    if a.json:
        print(json.dumps({"proyecto": proy["yyp"], "piezas": res, "primera_sala": primera,
                          "objetos_sin_sprite_que_dibujan_figuras": rect,
                          "sprites": n_sprites, "show_debug_message": debug},
                         ensure_ascii=False, indent=2))
    else:
        print("Proyecto: %s" % proy["yyp"])
        print("Recursos: " + " · ".join("%s %d" % (t, len(v)) for t, v in sorted(tipos.items())))
        print()
        print("Envoltorio (lista maestra de 04/00):")
        for clave, titulo, _, _ in PIEZAS:
            print("  %s %s" % ("✓" if res[clave] else "✗", titulo))
        print("  %s El jugador entra por una sala de portada, no por el nivel"
              % ("✓" if arranque_ok else "✗"))
        if primera:
            print("      (primera sala del orden: «%s»)" % primera)
        print()
        print("Assets:")
        print("  %s %d sprite(s) en el proyecto" % ("✓" if n_sprites else "✗", n_sprites))
        if rect:
            print("  ⚠ %d objeto(s) SIN sprite que pintan figuras en su evento Draw:"
                  % len(rect))
            print("      " + ", ".join(rect))
            print("      Si alguno es un personaje, un enemigo o un objeto con el que el")
            print("      jugador interactúa, eso es el rectángulo de color que la skill")
            print("      prohíbe: 12/09 §5.2 da la escalera para salir de ahí. Si son")
            print("      volúmenes de lógica (triggers, zonas), están bien — dilo y sigue.")
        else:
            print("  ✓ Ningún objeto sin sprite pintando figuras a mano")
        print()
        if debug:
            print("  ⚠ %d llamada(s) a show_debug_message: quítalas del build final (13/10 §7.2)"
                  % debug)
        print()
        if faltan or not arranque_ok:
            print("Faltan piezas del envoltorio: %s%s"
                  % (", ".join(faltan) if faltan else "",
                     (", " if faltan else "") + "arranque por portada" if not arranque_ok else ""))
            print()
            print("Esto NO dice que tu código esté mal: dice que no encuentro esas piezas.")
            print("Puede ser un falso positivo (un menú que vive dentro de otra sala, otro")
            print("nombre para lo mismo) o puede faltar de verdad. La regla de la biblioteca")
            print("es la misma en los dos casos: compáralo con 04/00 y **di por escrito qué")
            print("recortaste y por qué**. Lo que no vale es el silencio.")
        else:
            print("Todas las piezas del envoltorio aparecen. Sigue faltando lo que ninguna")
            print("máquina puede juzgar: si el menú se entiende, si la historia se sostiene y")
            print("si el juego se siente bien. Eso lo mira una persona.")

    if a.laxo:
        return 0
    return 1 if (faltan or not arranque_ok) else 0


if __name__ == "__main__":
    sys.exit(main())
