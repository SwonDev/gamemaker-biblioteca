#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""¿Le falta algo a la biblioteca? Géneros, recursos, herramientas de IA y repos.

**Por qué existe.** La pregunta «¿qué le falta?» se contestaba mirando y opinando, y una
opinión no se puede repetir ni auditar: la siguiente sesión vuelve a empezar de cero y no
sabe qué se miró ya. Esto la convierte en una medición.

**Cómo funciona.** Cada fila de las listas de abajo es una cosa que un juego real necesita.
Para cada una se busca evidencia en los documentos: o hay un documento dedicado, o hay una
sección que la cubre, o **no está**. La lista se escribe a mano —es un juicio sobre qué
debería cubrir la biblioteca— pero la comprobación es automática y el resultado, reproducible.

**Calibrado para no mentir en ninguna dirección**: una cobertura se da por buena solo si el
término aparece en un documento de contenido (no en una auditoría, no en el catálogo de código
ajeno), y se exige un mínimo de apariciones para que una mención de pasada no cuente como
cobertura. Lo que está cubierto «por otro nombre» se declara con su sinónimo, no se adivina.

    python3 _indice/auditar-cobertura.py            # informe completo
    python3 _indice/auditar-cobertura.py --breve    # solo lo que falta
    python3 _indice/auditar-cobertura.py --autoprueba

Sale con 0 si no falta nada, 1 si falta algo, 2 si no pudo comprobar.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argumentos import exigir_sin_rutas  # noqa: E402

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


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Carpetas que SÍ son contenido de la biblioteca. Las auditorías quedan fuera a
# propósito: un género mencionado solo en un informe de trabajo no está cubierto para
# quien venga a hacer un juego.
CARPETAS = ["01 - Fundamentos", "02 - Novedades 2026", "04 - Recetas por género",
            "05 - Referencia", "06 - Assets y Scripts", "07 - Ecosistema",
            "08 - Referencia GML completa", "12 - Utilidades e integraciones",
            "13 - Diseño y producción de videojuegos"]

# (qué, [términos que lo evidencian], mínimo de documentos distintos)
GENEROS = [
    ("Plataformas 2D",            ["plataforma", "coyote time"], 2),
    ("Cenital / twin-stick",      ["cenital", "twin-stick", "twin stick"], 2),
    ("Shoot'em up",               ["shmup", "shoot em up", "shoot'em up"], 1),
    ("RPG / Action RPG",          ["RPG"], 3),
    ("Roguelike",                 ["roguelike", "roguelite"], 2),
    ("Metroidvania",              ["metroidvania"], 1),
    ("Puzzle / match-3",          ["match-3", "match 3", "puzle", "puzzle"], 2),
    ("Tower defense",             ["tower defense", "torres"], 1),
    ("Survival y crafting",       ["crafting", "supervivencia"], 2),
    ("Visual novel / narrativa",  ["visual novel", "novela visual"], 1),
    ("Arcade / un botón",         ["un botón", "arcade"], 1),
    ("Carreras y vehículos",      ["carreras", "derrape", "vehículo"], 1),
    ("Estrategia y gestión",      ["estrategia", "gestión"], 2),
    ("Multijugador",              ["multijugador"], 2),
    ("Ritmo",                     ["ritmo", "BPM"], 1),
    ("Físicas (Box2D)",           ["Box2D"], 1),
    ("Combate cuerpo a cuerpo",   ["hitbox", "hurtbox", "combo"], 1),
    ("Combate a distancia",       ["balística", "munición"], 1),
    ("Por turnos / táctico",      ["por turnos", "táctic"], 1),
    ("Beat'em up",                ["beat em up", "beat'em up", "brawler"], 1),
    ("Aventura gráfica",          ["point and click", "aventura gráfica"], 1),
    ("Deportes / física de mesa", ["deportes", "pinball", "billar"], 1),
    ("Juego de lucha",            ["juego de lucha", "fighting"], 1),
    ("Colonia / city builder",    ["colonia", "trabajadores autónomos"], 1),
    ("Souls-like",                ["souls-like", "souls like", "hoguera"], 1),
    ("Bullet heaven / deckbuilder", ["bullet heaven", "autobattler", "deckbuilder"], 1),
    ("Party games / minijuegos",  ["party game", "minijuego"], 1),
    ("Sigilo",                    ["sigilo", "cono de visión"], 1),
    ("Horror",                    ["horror"], 1),
    ("Granja / cozy",             ["granja", "cultivo"], 1),
    ("Idle / incremental",        ["idle", "incremental", "progreso offline"], 1),
    ("Mundo destructible",        ["chunk", "tilemap_set"], 1),
    ("Runner infinito",           ["endless runner", "runner"], 1),
    ("Eje Z falso / altura",      ["eje Z", "altura falsa"], 1),
    ("3D",                        ["3D"], 3),
    ("Móvil / táctil",            ["táctil", "móvil"], 2),
]

RECURSOS = [
    ("Bancos de sprites libres",  ["Kenney", "OpenGameArt"], 1),
    ("Tilesets y Tiled",          ["Tiled"], 1),
    ("Tipografías con acentos",   ["fuente de sprite", "font_add_sprite", "tipografía"], 2),
    ("Tipografías de píxel",      ["monogram", "Pixel Operator", "m5x7"], 1),
    ("Bancos de sonido",          ["Freesound"], 1),
    ("Música libre",              ["música libre", "Incompetech", "banco de música"], 1),
    ("Generadores de sonido",     ["bfxr", "sfxr", "ChipTone"], 1),
    ("Modelos 3D libres",         ["Quaternius", "Kenney 3D", "ambientCG"], 1),
    ("Iconos de UI",              ["iconos de UI", "Game-icons", "game-icons"], 1),
    ("Paletas de color",          ["Lospec", "paleta"], 1),
    ("Herramientas de pixel art", ["Aseprite", "Libresprite"], 1),
    ("Licencias de assets",       ["CC0", "licencia"], 3),
    ("Shaders de referencia",     ["GM Shaders", "shader"], 3),
]

IA = [
    ("MCP oficial de recursos",   ["gamemaker-resource-tool"], 2),
    ("MCP de terceros",           ["gms-mcp", "gamemaker-mcp"], 2),
    ("Skills para otros CLI",     ["skills", "SKILL.md"], 2),
    ("Generación de sprites",     ["sprite-gen", "Retro Diffusion"], 1),
    ("Reparación de pixel art",   ["pixel-art-fixer", "pixeldetector"], 1),
    ("Generación de audio",       ["stable-audio", "audiocraft", "audio por IA"], 1),
    ("Generación de imagen",      ["gpt-image", "codex exec"], 1),
    ("Traducción por IA",         ["traducción por IA", "traducir con IA"], 1),
    ("Estado legal de lo generado", ["Copyright Office", "declararlo en Steam"], 1),
    ("Transpiladores y linters",  ["TypeScript", "linter", "GoboCat"], 2),
    ("Editor externo / LSP",      ["GMEdit", "LSP"], 2),
]


def _docs():
    """{ruta: texto} de los documentos de contenido."""
    out = {}
    for c in CARPETAS:
        base = os.path.join(RAIZ, c)
        if not os.path.isdir(base):
            continue
        for r, ds, fs in os.walk(base):
            ds[:] = [d for d in ds if d not in (".git", "auditorias")]
            for f in fs:
                if f.endswith(".md"):
                    p = os.path.join(r, f)
                    try:
                        out[os.path.relpath(p, RAIZ)] = open(
                            p, encoding="utf-8", errors="replace").read()
                    except OSError:
                        pass
    return out


def cubierto(docs, terminos, minimo):
    """(cuántos documentos lo mencionan, los tres primeros)."""
    pats = [re.compile(re.escape(t), re.I) for t in terminos]
    donde = [ruta for ruta, txt in sorted(docs.items())
             if any(p.search(txt) for p in pats)]
    return len(donde) >= minimo, donde[:3]


def revisar_bloque(docs, titulo, filas, breve):
    faltan = []
    if not breve:
        print("\n\033[1m%s\033[0m" % titulo)
    for que, terminos, minimo in filas:
        ok, donde = cubierto(docs, terminos, minimo)
        if ok:
            if not breve:
                print("  ✓ %-30s %s" % (que, os.path.basename(donde[0])[:46]))
        else:
            faltan.append((que, terminos, len(donde)))
            print("  ✗ %-30s solo en %d documento(s) (pide %d): %s"
                  % (que, len(donde), minimo, ", ".join(terminos)))
    return faltan


def main():
    breve = "--breve" in sys.argv
    docs = _docs()
    if len(docs) < 50:
        print("✗ Solo encuentro %d documentos de contenido. ¿Es esta la carpeta de la"
              " biblioteca? No se ha comprobado nada." % len(docs))
        return 2
    print("Auditoría de cobertura sobre %d documentos de contenido." % len(docs))

    faltan = []
    faltan += revisar_bloque(docs, "Géneros", GENEROS, breve)
    faltan += revisar_bloque(docs, "Recursos", RECURSOS, breve)
    faltan += revisar_bloque(docs, "Herramientas de IA", IA, breve)

    # Repos: que el catálogo cuadre con lo que hay en disco lo comprueba
    # `actualizar.py` paso 3; aquí solo se cuenta, para tener la cifra en el mismo sitio.
    rutas = os.path.join(RAIZ, "11 - Código descargado", "_RUTAS.json")
    if os.path.isfile(rutas):
        import json
        try:
            d = json.load(open(rutas, encoding="utf-8"))
            n = len(d) if isinstance(d, list) else len(d.get("repos", d))
            print("\n\033[1mRepositorios\033[0m\n  · %d catalogados en _RUTAS.json"
                  " (la coherencia con el disco la comprueba actualizar.py paso 3)" % n)
        except (ValueError, OSError):
            print("\n  ⚠ _RUTAS.json no se pudo leer")

    print()
    if faltan:
        print("\033[1m✗ %d hueco(s) de cobertura.\033[0m Cada uno es una pregunta, no una"
              " acusación:" % len(faltan))
        print("  o falta de verdad, o está cubierto con OTRAS palabras — y entonces lo que")
        print("  toca es añadir el sinónimo a la lista de este script, no un documento nuevo.")
        return 1
    print("\033[1m✓ Sin huecos.\033[0m Los %d puntos de las tres listas tienen respaldo en"
          " los documentos." % (len(GENEROS) + len(RECURSOS) + len(IA)))
    return 0


def autoprueba():
    fallos = []

    def revisar(nombre, ok, detalle=""):
        if ok:
            print("  ✓ " + nombre)
        else:
            fallos.append(nombre)
            print("  ✗ %s  ->  %s" % (nombre, detalle))

    falsos = {"a.md": "aquí se habla de metroidvania y de coyote time",
              "b.md": "otro documento sobre metroidvania"}
    ok, donde = cubierto(falsos, ["metroidvania"], 1)
    revisar("encuentra un término presente", ok and len(donde) == 2, str(donde))

    ok, _ = cubierto(falsos, ["metroidvania"], 3)
    revisar("y respeta el mínimo de documentos", not ok)

    ok, _ = cubierto(falsos, ["pinball"], 1)
    revisar("un término ausente NO se da por cubierto", not ok)

    ok, _ = cubierto(falsos, ["METROIDVANIA"], 1)
    revisar("la búsqueda no distingue mayúsculas", ok)

    # Un término con caracteres de expresión regular no debe reventar ni casar de más.
    ok, _ = cubierto({"c.md": "texto con shoot'em up dentro"}, ["shoot'em up"], 1)
    revisar("un término con apóstrofo se busca literal", ok)
    ok, _ = cubierto({"c.md": "texto sin nada"}, ["a.b"], 1)
    revisar("y el punto no hace de comodín", not ok)

    # El caso que hace inútil a un auditor: un árbol vacío que dice «todo bien».
    revisar("las tres listas tienen contenido",
            len(GENEROS) > 30 and len(RECURSOS) > 10 and len(IA) > 8,
            "%d/%d/%d" % (len(GENEROS), len(RECURSOS), len(IA)))

    if fallos:
        print("\n✗ %d comprobación(es) de la autoprueba fallan." % len(fallos))
        return 1
    print("\n✓ Las 7 comprobaciones de la autoprueba pasan.")
    return 0


if __name__ == "__main__":
    _sobra = exigir_sin_rutas(
        "Audita ESTA biblioteca; no toma ninguna ruta.", ("--autoprueba", "--breve"))
    if _sobra:
        sys.exit(_sobra)
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    sys.exit(main())
