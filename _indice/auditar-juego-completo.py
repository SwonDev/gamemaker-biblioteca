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

Calibrado contra juegos reales, no solo contra la idea
------------------------------------------------------
Un detector de ausencias que marca ausencias falsas es peor que no tenerlo: empuja a
deshacer lo que estaba bien. Así que se pasó por los 22 proyectos con `.yyp` de
`11 - Código descargado`, y la separación es limpia:

  · Juegos terminados — Kirby ~ Soft & Wet, SpelunkyClassicHD, nt-recreated,
    OrbinautFramework → **todas las piezas ✓**.
  · Juegos a los que de verdad les falta una — ChapterMaster (sin mando: es una
    estrategia de ratón), FVM-Reborn / Undertale-Engine / tldr-engine / Harmony-Framework
    (sin créditos) → señalan **exactamente** eso y nada más.
  · Demos, muestras y librerías — ImGUI-Sample, ExternalLibraryExample, los `pfb-*`,
    GM3D-Samples → les falta casi todo, que es la verdad: no son juegos.

De ahí salió el único falso positivo sistemático de la primera versión, corregido: los
juegos reales **no** arrancan en el menú, arrancan en una sala de inicialización
(`rm_boot`, `rm_Startup`) que salta al menú. Eso es lo correcto, y estaba marcado como
fallo. Ver el comentario en la comprobación de arranque.

El detector de rectángulos se probó con un control positivo construido a mano: dos
objetos con `spriteId: null` que dibujan figuras (los caza) y uno con sprite que llama a
`draw_self()` (lo ignora).

Código de salida
----------------
1 si falta alguna pieza del envoltorio (para que un agente no pueda ignorarlo), 0 si están
todas. Con `--laxo`, siempre 0: para cuando ya has justificado los recortes por escrito.
"""
import os, re, sys, json, argparse
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


DRAW_GUI = "Draw_64.gml"      # número real verificado en 12/09 §2.3

# Cada pieza: (clave, título, patrón sobre nombres de recurso, patrón sobre el GML,
#              tipos de recurso cuyo nombre vale como prueba)
# Un recurso cuenta si su NOMBRE casa Y es de un tipo válido; el GML cuenta si alguna
# línea casa. Basta uno.
#
# El quinto campo existe por un falso VERDE medido: «Pantalla de opciones» salía en ✓
# sobre un proyecto que no tenía ninguna, porque la librería de entrada de terceros
# incluye `__InputConfig`, `__InputCursorConfig`, `__InputIconConfigXbox`… Diez scripts
# ajenos con «config» en el nombre bastaban para dar por hecha una pantalla.
#
# En GameMaker una pantalla es un OBJETO o una SALA. Un script llamado `scr_ajustes` es
# el sitio donde viven los ajustes, no la pantalla donde se tocan. Restringir el tipo no
# pierde nada: si la pantalla existe sin objeto ni sala, su código la delata igual por el
# patrón de GML.
PANTALLA = ("objects", "rooms")
PIEZAS = [
    ("menu",      "Menú principal",
     r"menu|men[uú]|titulo|t[ií]tulo|title|portada|inicio",
     r"\b(men[uú]_|obj_menu|rm_menu|estado_menu)\w*",
     PANTALLA),
    ("opciones",  "Pantalla de opciones",
     r"opcion|option|ajuste|setting|config",
     r"\b(opciones|ajustes|settings)\w*\s*[=\(\.]",
     PANTALLA),
    # La pausa casi nunca es `global.pausa`: en un juego con gestor de escenas es un
    # estado dentro de la máquina del nivel (`estado = "pausa"`, `menu_pausa`). La primera
    # versión de este patrón solo miraba la global y daba un falso NEGATIVO sobre un juego
    # que sí la tenía — el error más caro aquí, porque deja pasar la ausencia que buscas.
    ("pausa",     "Pausa que congela el mundo",
     r"pausa|pause",
     r"instance_deactivate_all|\bpausad[oa]\b|\bis_paused\b"
     r"|[\"']paus[ae][\"']|\bmenu_paus[ae]\b|\b\w*_paus[ae]\b|\bpaus[ae]_\w+",
     PANTALLA),
    ("guardado",  "Guardar y cargar la partida",
     r"save|guardar|partida",
     r"\b(game_save|file_text_open_write|buffer_save|json_stringify)\s*\(",
     PANTALLA),
    ("creditos",  "Créditos",
     r"credito|cr[eé]dito|credit",
     r"\bcr[eé]ditos?\b",
     PANTALLA),
    ("game_over", "Muerte / Game Over / cierre",
     r"gameover|game_over|derrota|muerte|final|ending",
     r"\b(game_over|derrota|has_muerto|reintentar)\w*",
     PANTALLA),
    ("sonido",    "Sonido en el juego",
     r"^snd_|^mus_|^sfx_",
     r"\baudio_play_sound\s*\(",
     ("sounds",)),
    ("mando",     "Se juega también con mando",
     r"",
     r"\bgamepad_\w+\s*\(",
     ()),
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


# Las carpetas que GameMaker usa para recursos. Lo demás —`datafiles`, `options`,
# `notes`— no lo es, y meterlo aquí daría falsos positivos.
CARPETAS_RECURSO = (
    "sprites", "objects", "rooms", "scripts", "sounds", "fonts", "tilesets",
    "shaders", "paths", "timelines", "sequences", "animcurves", "particles",
)


def recursos_huerfanos(ruta, nombres_en_yyp):
    """Carpetas de recurso que existen en disco y NO están en el `.yyp`.

    Esto detecta una pérdida de trabajo **silenciosa y medida**: `resourcetool`
    reescribe el `.yyp` ENTERO, así que dos procesos creando recursos a la vez se
    pisan. El que pierde no se entera de nada.

    Reproducido en un proyecto limpio (2026-09-10): se crea `spr_del_rol_A`, otro
    proceso escribe el `.yyp` que había leído antes, y crea `spr_del_rol_B`.
    Resultado: **A desaparece del `.yyp` y su carpeta se queda en disco**. Y
    `gm-cli compile` sale con **0 sin decir una palabra**.

    Lo peligroso es la dirección del engaño. El consejo de siempre —«comprueba el
    disco, no la salida del comando»— aquí da un FALSO VERDE: los PNG están donde
    los dejaste. Para saber si un recurso está registrado hay que mirar el `.yyp`.
    """
    dentro = set(nombres_en_yyp)
    huerfanos = []
    for carpeta in CARPETAS_RECURSO:
        base = os.path.join(ruta, carpeta)
        if not os.path.isdir(base):
            continue
        try:
            hijos = sorted(os.listdir(base))
        except OSError:
            continue
        for n in hijos:
            d_hijo = os.path.join(base, n)
            # Una carpeta de recurso de verdad lleva su propio `<nombre>.yy` dentro.
            # Exigirlo descarta carpetas sueltas que no son recursos.
            if not os.path.isdir(d_hijo):
                continue
            if not os.path.isfile(os.path.join(d_hijo, n + ".yy")):
                continue
            if n not in dentro:
                huerfanos.append((carpeta, n))
    return huerfanos


def sin_comentarios(texto):
    """El GML con los comentarios fuera, respetando las cadenas.

    Nace de un falso VERDE medido. Este script daba por existentes «Menú
    principal», «Opciones», «Pausa» y «Créditos» sobre un proyecto que no tenía
    ninguna de las cuatro pantallas, porque un comentario decía:

        // arco (splash → menu → intro → juego → final → creditos) con un fundido

    Una palabra en un comentario es documentación, no implementación. Y este es el
    fallo más caro de un auditor: un ✗ se investiga, un ✓ falso se cree y se
    publica. Lo encontró un agente que desconfió de sus propios ticks.

    No basta con partir por «//»: una cadena puede contener «//» (una URL) y
    cortarla ahí destruiría código de verdad. Por eso se recorre carácter a
    carácter llevando la cuenta de si estamos dentro de una cadena.
    """
    salida = []
    i, n = 0, len(texto)
    comilla = None
    while i < n:
        c = texto[i]
        if comilla:
            salida.append(c)
            if c == "\\" and i + 1 < n:
                salida.append(texto[i + 1])
                i += 2
                continue
            if c == comilla:
                comilla = None
            i += 1
            continue
        if c in ('"', "'"):
            comilla = c
            salida.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and texto[i + 1] == "/":
            while i < n and texto[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and texto[i + 1] == "*":
            fin = texto.find("*/", i + 2)
            trozo = texto[i:fin] if fin != -1 else texto[i:]
            salida.append("\n" * trozo.count("\n"))   # conservar los números de línea
            i = (fin + 2) if fin != -1 else n
            continue
        salida.append(c)
        i += 1
    return "".join(salida)


def gml_del_proyecto(ruta):
    fuera = {"node_modules", ".git", "datafiles", "extensions"}
    out = []
    for base, dirs, files in os.walk(ruta):
        dirs[:] = [d for d in dirs if d not in fuera]
        for f in files:
            if f.endswith(".gml"):
                out.append(os.path.join(base, f))
    return out


# Scripts que reparte esta biblioteca: sus `show_debug_message` son rutas de error
# suyas, no trazas que el juego se haya dejado puestas.
SCRIPTS_BIBLIOTECA = {
    "scr_audio", "scr_camera", "scr_debug", "scr_grid_pathfinding", "scr_input_buffer",
    "scr_math_util", "scr_nivel_mapa", "scr_pool", "scr_save_load", "scr_state_machine",
    "scr_tiempo", "scr_tween", "scr_ui_confirmar",
}
# Una función que se llama así ES el registro: sus llamadas son el canal, no el ruido.
REGISTRADOR = re.compile(r"\b(?:registrar|registro|log|logger|trace|traza|depurar|debug)\w*\b",
                         re.I)


def contar_trazas(ruta):
    """Separa las trazas que sobran de las que son infraestructura.

    Contar ocurrencias de `show_debug_message` a secas da un número que no dice nada:
    mezcla el `show_debug_message("aqui llego")` que hay que quitar antes de publicar
    con el canal de error de un guardado y con el propio registrador por niveles que
    recomienda `13 · 10 §7.2` — que está hecho, precisamente, de llamadas a
    `show_debug_message`. Un agente que lo hizo todo bien seguía viendo «11 llamadas»
    (r15 §2.12), y un aviso que salta cuando no toca se aprende a ignorar.

    Devuelve (sueltas, infraestructura).
    """
    sueltas = infra = 0
    for fp in gml_del_proyecto(ruta):
        nombre = os.path.splitext(os.path.basename(fp))[0]
        texto = leer(fp)
        de_la_biblioteca = nombre in SCRIPTS_BIBLIOTECA
        # Se atribuye cada llamada a la última `function` declarada por encima.
        funcion_actual = ""
        for linea in texto.split("\n"):
            m = re.search(r"\bfunction\s+(\w+)\s*\(", linea)
            if m:
                funcion_actual = m.group(1)
            n = len(re.findall(r"\bshow_debug_message\s*\(", linea))
            if not n:
                continue
            if de_la_biblioteca or REGISTRADOR.search(funcion_actual):
                infra += n
            else:
                sueltas += n
    return sueltas, infra


# Raíz de la biblioteca, para poder comparar un script del proyecto con el nuestro.
BIBLIOTECA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lo que la gente reescribe, y lo que ya existe. No es una lista de prohibiciones:
# es el paso «antes de escribir un sistema, mira 11 · _CATALOGO.md» convertido en
# comprobación, porque en prosa se lo han saltado dos agentes seguidos
# (r15 §4: «no consulté el catálogo antes de escribir scr_input, scr_idioma y scr_ui»).
YA_EXISTE = [
    (re.compile(r"^(scr_|obj_)?(input|entrada|controles?|mando|gamepad)\w*$", re.I),
     "`Input` (offalynne, MIT) — el estándar de facto: teclado, ratón, mando, "
     "multijugador local, remapeo, buffers y detección de dispositivo"),
    (re.compile(r"^(scr_|obj_)?(texto|text|tipograf\w*|fuente|font)\w*$", re.I),
     "`Scribble` (JujuAdams, MIT) — formato enriquecido, efectos por carácter, "
     "ajuste de línea y máquina de escribir"),
    (re.compile(r"^(scr_|obj_)?(dialog\w*|conversacion|charla)\w*$", re.I),
     "`Chatterbox` (JujuAdams, MIT) — intérprete de Yarn: diálogo ramificado sin parser"),
    (re.compile(r"^(scr_|obj_)?(json|serial\w*|csv|xml)\w*$", re.I),
     "`SNAP` (JujuAdams, MIT) — JSON, CSV, XML, YAML, TOML y binario"),
    (re.compile(r"^(scr_|obj_)?(astar|a_estrella|pathfind\w*|camino)\w*$", re.I),
     "`06 · scr_grid_pathfinding.gml` de esta biblioteca — `mp_grid` y A* con coste por celda"),
    (re.compile(r"^(scr_|obj_)?(fsm|estado(s)?|state_?machine)\w*$", re.I),
     "`06 · scr_state_machine.gml` de esta biblioteca — FSM con structs, sin objetos"),
    (re.compile(r"^(scr_|obj_)?(tween|interpolac\w*|easing)\w*$", re.I),
     "`06 · scr_tween.gml` de esta biblioteca — tweens por delta time con callbacks"),
    (re.compile(r"^(scr_|obj_)?(guardar|save|savegame|partida)\w*$", re.I),
     "`06 · scr_save_load.gml` de esta biblioteca — structs + JSON, escritura segura y migración"),
    (re.compile(r"^(scr_|obj_)?(idioma|locale|i18n|traducc\w*|lang\w*)$", re.I),
     "`04 · 21 — Localización e idiomas` de esta biblioteca — la receta completa, con el "
     "flujo de traducción por IA"),
]


def _es_nuestro(nombre, texto):
    """¿Este script del proyecto es una copia del que reparte la biblioteca?"""
    if nombre not in SCRIPTS_BIBLIOTECA:
        return False
    nuestro = os.path.join(BIBLIOTECA, "06 - Assets y Scripts", nombre + ".gml")
    if not os.path.isfile(nuestro):
        return False
    return leer(nuestro)[:200].strip() == texto[:200].strip()


def reinventos(ruta):
    """Sistemas del proyecto que ya existen hechos, probados y con licencia MIT.

    Se reporta como informativo, nunca como fallo: un juego puede tener razones para
    escribir el suyo. Lo que no puede es no haberse enterado.
    """
    avisos = []
    vistos = set()
    for fp in gml_del_proyecto(ruta):
        nombre = os.path.splitext(os.path.basename(fp))[0]
        # Los eventos de un objeto se llaman Create_0, Step_0…: el nombre útil es la carpeta.
        if re.match(r"^(Create|Step|Draw|Alarm|Other|Collision|Key|Mouse|Clean)", nombre):
            nombre = os.path.basename(os.path.dirname(fp))
        if nombre in vistos:
            continue
        for patron, sugerencia in YA_EXISTE:
            if patron.match(nombre):
                if _es_nuestro(nombre, leer(fp)):
                    break            # es el nuestro, copiado tal cual: eso es lo que se pedía
                vistos.add(nombre)
                avisos.append((nombre, sugerencia))
                break
    return avisos


# Las funciones que preguntan «¿hay un X aquí?». Todas dependen de que X tenga
# máscara de colisión: sin sprite ni maskSpriteId, NINGUNA lo encuentra jamás.
COLISION_CONTRA = re.compile(
    r"\b(?:place_meeting|position_meeting|instance_place|instance_position|instance_nearest|"
    r"collision_point|collision_rectangle|collision_circle|collision_line|"
    r"place_free|place_empty)\s*\([^)]*?\b(obj_\w+)", re.S)


def objetos_sin_mascara(ruta):
    """Objetos contra los que el código colisiona y que no tienen máscara.

    Un objeto sin sprite y sin `maskSpriteId` no tiene máscara de colisión, así que
    `place_meeting()` e `instance_position()` **no lo encuentran nunca**. Un
    `obj_muro` creado por CLI y sin sprite es invisible Y atravesable, sin un solo
    error: el jugador cruza las paredes y no hay nada que depurar. Le pasa justo a
    quien monta los objetos por CLI y deja el arte para después — es decir, a un
    agente. Detalle en `12 · 09 §3 bis.1 ter`.
    """
    dir_obj = os.path.join(ruta, "objects")
    if not os.path.isdir(dir_obj):
        return []

    # 1 · Contra quién colisiona el código.
    objetivos = set()
    for fp in gml_del_proyecto(ruta):
        for m in COLISION_CONTRA.finditer(leer(fp)):
            objetivos.add(m.group(1))

    # 2 · De esos, cuáles no tienen máscara.
    sin_mascara = []
    for nombre in sorted(objetivos):
        yy = os.path.join(dir_obj, nombre, nombre + ".yy")
        if not os.path.isfile(yy):
            continue                       # no es un objeto de este proyecto
        crudo = leer(yy).replace(" ", "").replace("\n", "")
        if '"spriteId":null' in crudo and '"maskSpriteId":null' in crudo:
            sin_mascara.append(nombre)
    return sin_mascara


# Un sprite de personaje que es un color plano ES el rectángulo de color prohibido,
# solo que guardado como PNG en vez de dibujado con `draw_rectangle`. El detector de
# `objetos_rectangulo()` no lo ve, porque el objeto SÍ tiene sprite.
ACTOR = re.compile(
    r"^spr_(?:jugador|player|pj|heroe|héroe|protagonista|enemigo|enemy|monstruo|"
    r"npc|aliado|jefe|boss|mob|bicho|criatura|personaje)\w*$", re.I)
# Y estos son planos por buenas razones: no son arte, son herramientas.
PLANO_LEGITIMO = re.compile(
    r"(mascara|máscara|mask|sombra|shadow|fuente|font|glifo|particula|partícula|"
    r"dano|daño|damage|flash|hit|silueta|silhouette|contorno|outline|blanco|white|"
    r"solido|sólido|relleno|fill|pixel|punto|dot|barra|bar|degradado|gradient)", re.I)


def sprites_planos(ruta):
    """Sprites de PERSONAJE que son un color plano: el rectángulo, en PNG.

    No se marca cualquier sprite de pocos colores: medido sobre tres juegos reales,
    los planos legítimos son fuentes de sprite, sombras, máscaras de colisión,
    partículas y destellos de daño — herramientas, no arte. Lo que sí es el fallo
    que persigue la skill es `spr_jugador` siendo un cuadrado de un solo color.
    Devuelve [] si Pillow no está: no poder mirar NO es «está todo bien», y por eso
    `main()` lo dice en vez de callarse.
    """
    try:
        from PIL import Image
    except ImportError:
        return None
    dir_spr = os.path.join(ruta, "sprites")
    if not os.path.isdir(dir_spr):
        return []
    planos = []
    for nombre in sorted(os.listdir(dir_spr)):
        if not ACTOR.match(nombre) or PLANO_LEGITIMO.search(nombre):
            continue
        pngs = sorted(f for f in os.listdir(os.path.join(dir_spr, nombre))
                      if f.lower().endswith(".png"))
        if not pngs:
            continue
        try:
            im = Image.open(os.path.join(dir_spr, nombre, pngs[0])).convert("RGBA")
        except Exception:
            continue
        crudo = im.tobytes()
        visibles = {crudo[i:i + 4] for i in range(0, len(crudo), 4) if crudo[i + 3] > 0}
        if len(visibles) <= 2:
            planos.append((nombre, len(visibles), im.size))
    return planos


# Un `draw_text` con el texto escrito a pelo no se puede traducir, y `04 · 00` lo
# pide explícitamente: «todo el texto por `txt(clave)`». Es la clase de cosa que se
# arregla en diez minutos al empezar y en dos días cuando ya hay cien pantallas.
TEXTO_LITERAL = re.compile(
    r'\bdraw_text\w*\s*\([^)]*?,\s*("[^"]{4,}"|\'[^\']{4,}\')', re.S)
# Un literal que NO es texto de interfaz: formatos, separadores y depuración.
LITERAL_TECNICO = re.compile(r"^[\s\-_=|/\\.,:;#*+~<>%0-9]*$|^(fps|debug|test|todo)", re.I)


def textos_sin_traducir(ruta):
    """Llamadas a draw_text con la cadena escrita a pelo. [(archivo, texto)]"""
    hallados = []
    for fp in gml_del_proyecto(ruta):
        nombre = os.path.basename(os.path.dirname(fp))
        if nombre in SCRIPTS_BIBLIOTECA:
            continue                      # nuestros scripts traen sus propios rótulos
        for m in TEXTO_LITERAL.finditer(leer(fp)):
            crudo = m.group(1)[1:-1]
            if LITERAL_TECNICO.match(crudo):
                continue
            hallados.append((os.path.relpath(fp, ruta), crudo[:40]))
    return hallados


def hay_draw_gui(ruta):
    """¿Algún objeto dibuja en Draw GUI? El HUD y los menús viven ahí (13 · 05 §3.1)."""
    dir_obj = os.path.join(ruta, "objects")
    if not os.path.isdir(dir_obj):
        return False
    for base, _dirs, files in os.walk(dir_obj):
        for f in files:
            if f in ("Draw_64.gml", "Draw_65.gml", "Draw_72.gml", "Draw_73.gml"):
                return True
    return False


# Pantallas por las que el jugador PASA y que tiene que poder saltarse. Una intro
# que no se salta es lo primero que odia quien vuelve a jugar — y `04 · 00` la pide
# saltable dos veces, para el splash y para el prólogo.
PASO_OBLIGADO = re.compile(r"^obj_(splash|intro|prologo|prólogo|logo|cinematica|cinemática)\w*$", re.I)


def pantallas_no_saltables(ruta):
    """Objetos de splash/intro cuyo código no consulta ninguna entrada.

    Ojo con la laxitud al revés, que es el error que cometió la primera versión:
    buscaba una LLAMADA (`entrada_pulsado()`), y un proyecto real que hacía lo
    correcto —consultar `global.entrada.cualquiera`, un campo de un struct de
    entrada centralizado— salía marcado como «no se puede saltar» sin serlo. Un
    aviso falso sobre algo que está bien hecho es de lo peor que puede tener un
    auditor: enseña a ignorarlo. Se aceptan las tres formas que se usan de verdad:
    la llamada cruda al runtime, un envoltorio propio del proyecto, y el acceso a
    un struct o global de entrada.
    """
    dir_obj = os.path.join(ruta, "objects")
    if not os.path.isdir(dir_obj):
        return []
    envoltorios = envoltorios_de_entrada(ruta)
    pat_envoltorio = (re.compile(r"\b(?:%s)\b" % "|".join(re.escape(n) for n in envoltorios))
                      if envoltorios else None)
    # Las formas reales de consultar la entrada centralizada, y hubo que ampliarla
    # DOS veces contra proyectos que la usaban bien: primero `global.entrada.campo`,
    # y luego `var _e = global.entrada;` seguido de `_e.aceptar` — donde el nombre
    # ya no aparece junto al campo. Basta con que se nombre el struct de entrada.
    pat_struct = re.compile(
        r"\bglobal\.(?:entrada|input|controles|mando)\b"
        r"|\b(?:entrada|input|controles|mando)\.\w+", re.I)

    sin_salida = []
    for nombre in sorted(os.listdir(dir_obj)):
        carpeta = os.path.join(dir_obj, nombre)
        if not os.path.isdir(carpeta) or not PASO_OBLIGADO.match(nombre):
            continue
        texto = ""
        for f in sorted(os.listdir(carpeta)):
            if f.endswith(".gml"):
                texto += leer(os.path.join(carpeta, f))
        if ENTRADA_CRUDA.search(texto):           continue
        if pat_struct.search(texto):              continue
        if pat_envoltorio and pat_envoltorio.search(texto): continue
        sin_salida.append(nombre)
    return sin_salida


def objetos_rectangulo(ruta):
    """Objetos SIN sprite cuyo evento Draw pinta figuras a mano.

    Es la firma exacta del «rectángulo de color como personaje» que prohíbe la skill.
    Un objeto sin sprite que dibuja un rectángulo puede ser legítimo (una zona de
    disparo, una caja de depuración), así que esto se reporta como aviso y con nombres:
    quien lo lee decide cuáles son de verdad un personaje sin arte.
    """
    dir_obj = os.path.join(ruta, "objects")
    if not os.path.isdir(dir_obj):
        # Dos listas, no una: el llamante desempaqueta `rect, rect_ui`. Devolver `[]`
        # aquí reventaba con «not enough values to unpack» ante un proyecto recién
        # creado, sin ningún objeto todavía — que es justo cuando más falta hace poder
        # auditarlo. Encontrado auditando un proyecto de una sola prueba.
        return [], []
    figuras = re.compile(r"\bdraw_(rectangle|circle|ellipse|roundrect|triangle)\w*\s*\(")
    # Un objeto de interfaz o de control dibuja figuras porque ese es su trabajo: paneles,
    # barras de vida, fundidos, cartelas. Meterlo en la misma lista que un personaje sin
    # arte convierte el aviso en ruido, y un aviso ruidoso se ignora entero. Se separan.
    interfaz = re.compile(
        r"^obj_(menu|splash|titulo|hud|ui|gui|credito|creditos|intro|prologo|epilogo|final|"
        r"fundido|transicion|pausa|opciones|ajustes|nivel|gestor|control|camara|director|"
        r"debug|dialogo|minimapa|inventario|tienda|cargando|selector|"
        # Añadidas tras r15 §2.12: la pantalla de selección de nivel se llamaba
        # `obj_seleccion` y caía en la lista de sospechosos junto a los personajes
        # sin arte, que es justo lo que convierte el aviso en ruido. El resto son de
        # la misma familia —pantallas, paneles y adornos de HUD— y estaban por el
        # mismo motivo a un carácter de distancia.
        r"selec|pantalla|panel|boton|barra|marcador|contador|reloj|cursor|puntero|mira|"
        r"mensaje|aviso|tutorial|pista|ayuda|logro|galeria|galería)\w*$", re.I)
    sospechosos = []
    solo_gui = set()
    for nom in sorted(os.listdir(dir_obj)):
        carpeta = os.path.join(dir_obj, nom)
        yy = os.path.join(carpeta, nom + ".yy")
        if not os.path.isfile(yy):
            continue
        if '"spriteId":null' not in leer(yy).replace(" ", ""):
            continue                      # tiene sprite: no es el caso
        en_mundo, en_gui = False, False
        for ev, marca in (("Draw_0.gml", "mundo"), (DRAW_GUI, "gui")):
            q = os.path.join(carpeta, ev)
            if os.path.isfile(q) and figuras.search(leer(q)):
                if marca == "mundo":
                    en_mundo = True
                else:
                    en_gui = True
        if en_mundo or en_gui:
            sospechosos.append(nom)
            if en_gui and not en_mundo:
                solo_gui.add(nom)
    # Dos criterios, y el estructural manda sobre el del nombre.
    #
    # **Draw GUI es espacio de PANTALLA, no de mundo**: lo que se dibuja ahí no se
    # mueve con la cámara, así que no puede ser un personaje, un enemigo ni un objeto
    # con el que se choca — es HUD, panel, cartela o fundido, siempre. Un objeto que
    # solo pinta figuras ahí es interfaz por construcción, se llame como se llame.
    #
    # Antes solo existía la lista de nombres de abajo, que crece sin fin: cayó
    # `obj_seleccion` en r15, y `obj_juego` —el director de partida, un nombre de lo
    # más común— en la prueba del juego «Enjambre». Cada palabra que se añade tapa un
    # caso y deja fuera el siguiente. La regla estructural los cubre todos de golpe.
    def es_interfaz(nombre):
        return nombre in solo_gui or bool(interfaz.match(nombre))
    return ([s for s in sospechosos if not es_interfaz(s)],
            [s for s in sospechosos if es_interfaz(s)])


ENTRADA_CRUDA = re.compile(r"\b(keyboard_check_pressed|gamepad_button_check_pressed|"
                     r"mouse_check_button_pressed|keyboard_check|device_mouse_check_button_pressed)\s*\(")
# Cómo se llama, en la práctica, «ahora no aceptes entrada»: una pausa, una transición
# en curso, un diálogo abierto, una confirmación encima.
#
# Ojo con la laxitud. La primera versión aceptaba cualquier palabra con «confirmar»
# dentro, y una función de ENTRADA llamada `entrada_confirmar()` la satisfacía: el
# detector daba por bueno justo el objeto que no tenía guarda. Por eso ahora se exige
# (a) una forma de nombre que solo tiene una guarda —terminada en _activo/_activa/
# _abierto/_en_curso/_cambiando, o una global de pausa— y (b) que aparezca en una
# línea con `if`, que es donde vive una guarda y no una acción.
GUARDA = re.compile(
    # Raíces que solo aparecen en algo que BLOQUEA, nunca en una función de entrada.
    # `confirmar` y `menu` quedan fuera a propósito: chocaban con `entrada_confirmar()`
    # y `menu_elegir()`, que son acciones, y hacían pasar por bueno el objeto sin guarda.
    r"\b\w*(?:paus|transicion|transición|fundido|dialog|diálog|congel|bloquea|"
    r"cambiando|escena_)\w*"
    # …más los nombres concretos que sí son guardas aunque no lleven esas raíces.
    r"|\bconfirmar_activ[oa]\b|\bis_paused\b|\binstance_deactivate_all\b"
    r"|\binstance_exists\s*\(\s*obj_(?:pausa|transicion|dialogo)",
    re.I)


def tiene_guarda(texto):
    """Una guarda vive en una línea con `if`; una acción, no."""
    for linea in texto.split("\n"):
        if "if" in linea and GUARDA.search(linea):
            return True
    return False


def envoltorios_de_entrada(ruta):
    """Nombres de las funciones PROPIAS del proyecto que leen la entrada.

    Un juego bien hecho no llama a `keyboard_check_pressed` desde cada objeto: lo
    centraliza en un script (`entrada_pulsado()`, `input_check()`…). La primera
    versión de este detector solo buscaba las llamadas crudas y por eso daba CERO
    sobre un proyecto real que hacía justamente lo correcto. Se recogen aquí para
    que contar como «lee entrada» funcione con los dos estilos.
    """
    nombres = set()
    dir_scr = os.path.join(ruta, "scripts")
    if not os.path.isdir(dir_scr):
        return nombres
    for base, _, files in os.walk(dir_scr):
        for fi in files:
            if not fi.endswith(".gml"):
                continue
            texto = leer(os.path.join(base, fi))
            # Cada `function nombre(` y el trozo de cuerpo que le sigue hasta la
            # siguiente declaración: si ahí dentro hay entrada cruda, es un envoltorio.
            trozos = re.split(r"\bfunction\s+(\w+)\s*\(", texto)
            for i in range(1, len(trozos) - 1, 2):
                if ENTRADA_CRUDA.search(trozos[i + 1][:4000]):
                    nombres.add(trozos[i])
    return nombres


def objetos_sin_guarda(ruta):
    """Objetos que leen entrada y NO mencionan ninguna guarda de pausa/transición.

    Es el fallo que las dos pruebas a ciegas cometieron, y el mismo las dos veces: un
    único objeto de pantalla se quedó sin la guarda que sí tenían los otros cinco, y
    durante el fundido de salida seguía aceptando entrada — abriendo pantallas cuyos
    métodos morían con la instancia. Compila limpio, no hay error en ningún log, y el
    checklist que lo habría cazado está enlazado desde una casilla que se puede marcar
    sin abrirlo (`04/00` → `04/41 §4`).

    La comprobación es COMPARATIVA a propósito: solo se avisa si el proyecto YA usa
    guardas en algún sitio. Un juego que no tiene ninguna no está incumpliendo nada
    —quizá no tiene pausa—; lo sospechoso es tenerlas en cinco objetos y no en el sexto.
    """
    dir_obj = os.path.join(ruta, "objects")
    if not os.path.isdir(dir_obj):
        return [], 0

    envoltorios = envoltorios_de_entrada(ruta)
    if envoltorios:
        lee = re.compile(ENTRADA_CRUDA.pattern + "|\\b(" +
                         "|".join(re.escape(x) for x in sorted(envoltorios)) + r")\s*\(")
    else:
        lee = ENTRADA_CRUDA

    con_entrada, con_guarda = [], 0
    for nom in sorted(os.listdir(dir_obj)):
        carpeta = os.path.join(dir_obj, nom)
        if not os.path.isdir(carpeta):
            continue
        texto = "".join(leer(os.path.join(carpeta, e))
                        for e in sorted(os.listdir(carpeta)) if e.endswith(".gml"))
        if not lee.search(texto):
            continue
        if tiene_guarda(texto):
            con_guarda += 1
        else:
            con_entrada.append(nom)
    return con_entrada, con_guarda


def audio_en_pausa(gml):
    """¿La pausa hace algo con el audio? Punto 3 del checklist de 04/41 §4."""
    return bool(re.search(r"\baudio_(pause_all|resume_all|pause_sound|group_set_gain|"
                          r"sound_gain|master_gain)\s*\(", gml))


# Recursos que GameMaker NO recoge solo. Los 16 pares están verificados uno a uno
# contra el índice de símbolos (`buscar.py`), no escritos de memoria.
#
# **Por qué merece una comprobación propia.** Es la clase de fallo que describe la
# regla 6 de `game-quality-gates` («cambiar de escena = limpieza completa») llevada
# a GameMaker, y aquí muerde más fuerte: un `ds_map` no es un objeto de JavaScript
# que el recolector se lleve cuando nadie lo mira. Vive hasta que alguien llama a
# `ds_map_destroy`, y si nadie lo hace, la memoria crece cada vez que se entra en la
# sala. El juego funciona perfectamente en la demo de dos minutos y se muere a la
# media hora — el bug que no sale probando cada función por separado.
#
# **Calibrado para no dar un solo falso positivo:** solo avisa si el destructor no
# aparece NI UNA VEZ en toda la carpeta del proyecto. Con que exista una llamada en
# cualquier sitio, se calla — puede estar mal puesta, pero eso ya no lo decide una
# expresión regular, y un aviso que salta cuando no toca se aprende a ignorar.
PARES_RECURSOS = [
    ("ds_map_create",        "ds_map_destroy",        "un ds_map"),
    ("ds_list_create",       "ds_list_destroy",       "una ds_list"),
    ("ds_grid_create",       "ds_grid_destroy",       "una ds_grid"),
    ("ds_stack_create",      "ds_stack_destroy",      "una ds_stack"),
    ("ds_queue_create",      "ds_queue_destroy",      "una ds_queue"),
    ("ds_priority_create",   "ds_priority_destroy",   "una ds_priority"),
    ("surface_create",       "surface_free",          "una superficie"),
    ("part_system_create",   "part_system_destroy",   "un sistema de partículas"),
    ("part_type_create",     "part_type_destroy",     "un tipo de partícula"),
    ("part_emitter_create",  "part_emitter_destroy",  "un emisor de partículas"),
    ("buffer_create",        "buffer_delete",         "un buffer"),
    ("audio_emitter_create", "audio_emitter_free",    "un emisor de audio"),
    ("vertex_create_buffer", "vertex_delete_buffer",  "un vertex buffer"),
]

# Segundo nivel: recursos que **una sola vez** son legítimos. Una fuente o un sprite
# cargados al arrancar y usados toda la partida no son una fuga: son un recurso que
# vive lo que vive el juego. Un time source persistente para el reloj del mundo,
# igual. Solo delatan una fuga si se crean MÁS DE UNA VEZ sin que nadie los libere,
# porque entonces la cuenta crece.
#
# Medido sobre los 20 juegos completos de `11 - Código descargado/juegos_y_motores`:
# tratar `font_add` como fuga sin más disparaba en 6 de 20, todos legítimos. Ese es
# el aviso que hace que se deje de leer el informe entero.
PARES_UNA_VEZ = [
    ("time_source_create",   "time_source_destroy",   "un time source"),
    ("sprite_add",           "sprite_delete",         "un sprite cargado en caliente"),
    ("font_add",             "font_delete",           "una fuente cargada en caliente"),
]


def recursos_sin_liberar(gml):
    """[(crear, destruir, humano, veces)] de lo que se crea y nunca se destruye.

    Los de `PARES_UNA_VEZ` solo cuentan si se crean más de una vez: crearlos una
    sola vez al arrancar es un uso legítimo, no una fuga.
    """
    sueltos = []
    for lista, minimo in ((PARES_RECURSOS, 1), (PARES_UNA_VEZ, 2)):
        for crear, destruir, humano in lista:
            # `part_system_create_layer` cuenta como `part_system_create`: el
            # destructor es el mismo. `\w*` cubre la familia sin una fila aparte.
            veces = len(re.findall(r"\b" + crear + r"\w*\s*\(", gml))
            if veces >= minimo and not re.search(r"\b" + destruir + r"\s*\(", gml):
                sueltos.append((crear, destruir, humano, veces))
    return sueltos


def icono_y_version(ruta):
    """Icono puesto y versión distinta de la de fábrica (05/02 §4.4)."""
    dir_opt = os.path.join(ruta, "options")
    icono, version = False, None
    if os.path.isdir(dir_opt):
        for base, _, files in os.walk(dir_opt):
            if os.path.basename(base) in ("icons", "splash") and files:
                icono = True
            for fi in files:
                if fi.endswith(".yy"):
                    m = re.search(r'"option_\w+_version"\s*:\s*"([^"]+)"', leer(os.path.join(base, fi)))
                    if m and version is None:
                        version = m.group(1)
    return icono, version


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
              "  Pásame la CARPETA del proyecto: la que contiene el .yyp, no una de dentro.\n"
              "  Si el proyecto es de GameMaker Studio 1.x (.gmx) o es un volcado de código\n"
              "  suelto sin proyecto —como varios de `11 - Código descargado`—, este script no\n"
              "  puede auditarlo: necesita el .yyp para saber qué recursos y qué orden de salas\n"
              "  tiene el juego." % ruta)
        return 2

    nombres = [n for n, _ in proy["recursos"]]
    tipos = {}
    for n, p in proy["recursos"]:
        tipos.setdefault(p.split("/", 1)[0], []).append(n)

    gml = "\n".join(leer(f) for f in gml_del_proyecto(ruta))

    # Las piezas se buscan en el CÓDIGO, no en lo que el código dice de sí mismo.
    gml_codigo = sin_comentarios(gml)

    # Cada ✓ dice QUÉ lo puso en verde. Sin eso, un tick es una afirmación que nadie
    # puede comprobar — y este script ya ha dado por existentes pantallas que no
    # estaban. Un ✗ es una pregunta; un ✓ mudo es una respuesta que no se puede
    # contrastar. Enseñar la prueba convierte las dos cosas en revisables.
    res, faltan, pruebas = {}, [], {}
    for clave, titulo, pat_nom, pat_gml, tipos_ok in PIEZAS:
        hay = False
        if pat_nom:
            r = re.compile(pat_nom, re.I)
            # Solo cuentan los recursos del tipo adecuado: un script con «config» en el
            # nombre no es una pantalla de opciones, y una librería de terceros trae diez.
            candidatos = ([n for t in tipos_ok for n in tipos.get(t, [])]
                          if tipos_ok else nombres)
            casan = [n for n in candidatos if r.search(n)]
            if casan:
                hay = True
                pruebas[clave] = "recurso " + ", ".join(sorted(casan)[:3])
        if not hay and pat_gml:
            m = re.search(pat_gml, gml_codigo, re.I)
            if m:
                hay = True
                linea = gml_codigo[:m.start()].count("\n") + 1
                fragmento = gml_codigo.splitlines()[linea - 1].strip()[:64]
                pruebas[clave] = "código «%s»" % fragmento
        res[clave] = hay
        if not hay:
            faltan.append(titulo)

    # El arranque: la PRIMERA sala del orden es por donde entra el jugador.
    #
    # Vale tanto una portada (menú, splash, logo, intro) como una sala de ARRANQUE
    # —`rm_boot`, `rm_Startup`, `rm_init`— que inicializa y salta al menú. Esa segunda
    # forma es la que usan los juegos reales, y en la primera versión de este script
    # salía marcada como fallo: comprobado contra ChapterMaster (`rm_boot`) y
    # Kirby ~ Soft & Wet (`rm_Startup`) de `11 - Código descargado`, ambos juegos
    # completos con menú, opciones, pausa, guardado y créditos. Era un falso positivo,
    # y de los caros: habría empujado a un agente a deshacer la estructura correcta.
    #
    # Lo que sigue siendo un fallo es entrar directo al nivel — o quedarse con el
    # `Room1` que crea la plantilla, que es la huella de no haber montado nada.
    primera = proy["orden_salas"][0] if proy["orden_salas"] else None
    arranque_ok = bool(primera and re.search(
        r"menu|men[uú]|titulo|t[ií]tulo|title|splash|logo|intro|inicio|portada"
        r"|boot|startup|start_up|init|arranque|carga|loading|preload",
        primera, re.I))
    res["arranque"] = arranque_ok

    rect, rect_ui = objetos_rectangulo(ruta)
    n_sprites = len(tipos.get("sprites", []))
    debug, debug_infra = contar_trazas(ruta)
    sin_guarda, con_guarda = objetos_sin_guarda(ruta)
    audio_pausa = audio_en_pausa(gml)
    fugas = recursos_sin_liberar(gml)
    icono, version = icono_y_version(ruta)
    reinv = reinventos(ruta)
    sin_mascara = objetos_sin_mascara(ruta)
    planos = sprites_planos(ruta)
    literales = textos_sin_traducir(ruta)
    draw_gui = hay_draw_gui(ruta)
    no_saltables = pantallas_no_saltables(ruta)

    if a.json:
        print(json.dumps({"proyecto": proy["yyp"], "piezas": res, "primera_sala": primera,
                          "objetos_sin_sprite_que_dibujan_figuras": rect,
                          "objetos_de_interfaz_que_dibujan_figuras": rect_ui,
                          "sprites": n_sprites, "show_debug_message": debug,
                          "show_debug_message_infraestructura": debug_infra,
                          "objetos_que_leen_entrada_sin_guarda": sin_guarda,
                          "objetos_con_guarda": con_guarda,
                          "pausa_toca_el_audio": audio_pausa,
                          "recursos_creados_y_nunca_liberados":
                              [{"crear": c, "destruir": d, "veces": v} for c, d, _h, v in fugas],
                          "icono_propio": icono, "version": version,
                          "sistemas_que_ya_existen": [{"tuyo": n, "existe": e} for n, e in reinv],
                          "objetos_sin_mascara_contra_los_que_se_colisiona": sin_mascara,
                          "sprites_de_personaje_de_color_plano":
                              None if planos is None else [n for n, _c, _t in planos],
                          "textos_sin_txt": [t for _f, t in literales],
                          "hay_draw_gui": draw_gui,
                          "pantallas_que_no_se_pueden_saltar": no_saltables},
                         ensure_ascii=False, indent=2))
    else:
        print("Proyecto: %s" % proy["yyp"])
        print("Recursos: " + " · ".join("%s %d" % (t, len(v)) for t, v in sorted(tipos.items())))
        print()
        print("Envoltorio (lista maestra de 04/00):")
        for clave, titulo, _, _, _ in PIEZAS:
            print("  %s %s" % ("✓" if res[clave] else "✗", titulo))
            if res[clave] and clave in pruebas:
                print("      lo pone en verde: %s" % pruebas[clave])
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
            print("  ✓ Ningún objeto de juego sin sprite pintando figuras a mano")
        if rect_ui:
            print("  · %d objeto(s) de interfaz dibujan figuras (normal: paneles, barras,"
                  % len(rect_ui))
            print("    fundidos). No los cuento como el rectángulo prohibido:")
            print("      " + ", ".join(rect_ui))
        print()
        if debug:
            print("  ⚠ %d llamada(s) sueltas a show_debug_message. Míralas una a una: una"
                  % debug)
            print("    traza de depuración («aqui llego») sobra en el build final, pero una")
            print("    ruta de error («no se pudo guardar») hace falta — y entonces lo que")
            print("    toca no es quitarla, sino meterla por el registrador de 13/10 §7.2,")
            print("    que la apaga sola en release.")
        if debug_infra:
            print("  · %d más están dentro del registrador o de los scripts de la biblioteca:"
                  % debug_infra)
            print("    son el canal de log, no trazas olvidadas. No las cuento.")
        if planos is None:
            print("  · sprites: no se ha podido mirar el color (falta Pillow). NO es que estén")
            print("    bien: es que no se ha comprobado. `python3 -m pip install --user Pillow`")
        elif planos:
            print("  ⚠ %d sprite(s) de PERSONAJE son un color plano — es el rectángulo"
                  % len(planos))
            print("    prohibido, guardado como PNG en vez de dibujado:")
            for n, c, t in planos:
                print("      %-28s %d color(es), %dx%d" % (n, c, t[0], t[1]))
            print("    La escalera para salir de ahí está en 12/09 §5.2.")
        if sin_mascara:
            print("  ⚠ %d objeto(s) contra los que colisiona tu código NO tienen máscara"
                  % len(sin_mascara))
            print("    (ni sprite ni maskSpriteId): " + ", ".join(sin_mascara))
            print("    `place_meeting()` e `instance_position()` NO los encuentran nunca. Son")
            print("    invisibles y además atravesables, sin un solo error. Dales un sprite")
            print("    (y `visible = false` si tienen que seguir sin verse) — 12/09 §3 bis.1 ter.")
        if reinv:
            print("  · %d sistema(s) que ya existían hechos. No es un fallo —puedes tener"
                  % len(reinv))
            print("    motivos— pero que sea una decisión, no un descuido (11 · _CATALOGO.md):")
            for nombre, sugerencia in reinv:
                print("      %-22s ya existe: %s" % (nombre, sugerencia))
        print("  %s Alguien dibuja en Draw GUI (donde viven el HUD y los menús)"
              % ("✓" if draw_gui else "✗"))
        if literales:
            print("  ⚠ %d texto(s) escritos a pelo en un `draw_text`: no se pueden traducir"
                  % len(literales))
            print("    (04/00 pide todo el texto por `txt(clave)` — 04 · 21):")
            for f, t in literales[:6]:
                print("      %-34s «%s»" % (f, t))
            if len(literales) > 6:
                print("      … y %d más" % (len(literales) - 6))
        if no_saltables:
            print("  ⚠ %d pantalla(s) de paso obligado sin forma de saltarlas: %s"
                  % (len(no_saltables), ", ".join(no_saltables)))
            print("    Su código no lee ninguna entrada. `04/00` las pide saltables.")
        print()
        print("Las listas que 04/00 enlaza y casi nadie abre:")
        if sin_guarda and con_guarda:
            print("  ⚠ %d objeto(s) leen entrada SIN ninguna guarda de pausa/transición,"
                  % len(sin_guarda))
            print("    mientras que otros %d sí la tienen:" % con_guarda)
            print("      " + ", ".join(sin_guarda[:8]))
            print("    Es el fallo exacto que 04/41 §4 pide comprobar: durante un fundido")
            print("    de salida, un objeto sin guarda sigue aceptando entrada y puede abrir")
            print("    una pantalla cuyos métodos mueren al cambiar de sala.")
        elif con_guarda:
            print("  ✓ Todos los objetos que leen entrada consultan alguna guarda")
        else:
            print("  · Ningún objeto usa guardas de pausa/transición (¿el juego tiene pausa?)")
        print("  %s La pausa hace algo con el audio (04/41 §4)"
              % ("✓" if audio_pausa else "✗"))
        if fugas:
            print("  ✗ Recursos que se crean y NUNCA se liberan en todo el proyecto:")
            for crear, destruir, humano, veces in fugas:
                print("      · %s() aparece %d vez(ces) y %s() ni una: se crea %s"
                      % (crear, veces, destruir, humano))
            print("    GameMaker no recoge esto solo. No es un objeto que el recolector se")
            print("    lleve cuando nadie lo mira: vive hasta que alguien lo destruye.")
            print("    La pregunta que decide si es una fuga de verdad: **¿se vuelve a crear")
            print("    cada vez que se entra en la sala?** Si sí, la memoria crece sin parar y")
            print("    el juego que va perfecto en una demo de dos minutos se muere a la media")
            print("    hora. Si se crea una sola vez al arrancar y dura toda la partida, no")
            print("    crece — pero libéralo igual en **Clean Up**, que cuesta una línea y te")
            print("    ahorra la duda. Ese evento se dispara tanto al destruir la instancia")
            print("    como al terminar la sala, que es justo lo que hace falta.")
        else:
            print("  ✓ Todo recurso manual que se crea tiene su destructor en alguna parte")
        print("  %s Icono o splash propios en options/ (05/02 §4.4)"
              % ("✓" if icono else "✗"))
        if version:
            print("  %s Versión del ejecutable: %s%s"
                  % ("✓" if version != "1.0.0.0" else "⚠", version,
                     "  ← la de fábrica; súbela antes de publicar" if version == "1.0.0.0" else ""))
        # Recursos que existen en disco pero se cayeron del `.yyp`. Va aquí, con el
        # resto del informe, porque no es un defecto de diseño: es trabajo perdido.
        huerfanos = recursos_huerfanos(ruta, nombres)
        if huerfanos:
            print("  \033[1m✗ %d recurso(s) que están en DISCO pero NO en el .yyp:\033[0m"
                  % len(huerfanos))
            for carpeta, n in huerfanos[:12]:
                print("      %s/%s" % (carpeta, n))
            if len(huerfanos) > 12:
                print("      … y %d más" % (len(huerfanos) - 12))
            print("    Es trabajo perdido, no un aviso de estilo. `resourcetool` reescribe el")
            print("    `.yyp` entero, así que dos procesos creando recursos a la vez se pisan y")
            print("    el que pierde NO se entera: sus archivos siguen ahí y `gm-cli compile`")
            print("    sale con 0 sin decir nada. Medido en un proyecto limpio.")
            print("    Vuelve a registrarlos con `resourcetool`, de uno en uno y sin nadie más")
            print("    escribiendo a la vez.")
        print()
        if faltan or not arranque_ok or huerfanos:
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


# ─────────────────────────────────────────────────────────────────────────────
# Autoprueba
#
# Este script ya ha tenido cuatro calibraciones contra proyectos reales, y cada
# una podía haber roto una anterior sin que nadie se enterara: un detector que
# deja de detectar no falla, simplemente calla — y un aviso que no salta se lee
# igual que «está todo bien». Los casos de abajo son los que han mordido de
# verdad, montados como proyectos de mentira en un directorio temporal.
#
#   python3 _indice/auditar-juego-completo.py --autoprueba
# ─────────────────────────────────────────────────────────────────────────────

def _proyecto_falso(base, objetos=None, scripts=None):
    """Monta el esqueleto mínimo que este script sabe leer."""
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, "falso.yyp"), "w", encoding="utf-8") as f:
        f.write('{"resources":[],"RoomOrderNodes":[]}')
    for nombre, datos in (objetos or {}).items():
        d = os.path.join(base, "objects", nombre)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, nombre + ".yy"), "w", encoding="utf-8") as f:
            f.write('{"spriteId":null,"name":"%s"}' % nombre if datos.get("sin_sprite", True)
                    else '{"spriteId":{"name":"spr_x"},"name":"%s"}' % nombre)
        for evento, codigo in datos.get("eventos", {}).items():
            with open(os.path.join(d, evento + ".gml"), "w", encoding="utf-8") as f:
                f.write(codigo)
    for nombre, codigo in (scripts or {}).items():
        d = os.path.join(base, "scripts", nombre)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, nombre + ".gml"), "w", encoding="utf-8") as f:
            f.write(codigo)
    return base


def autoprueba():
    import tempfile
    fallos = []
    # Contadas, no escritas a mano: un número fijo en el mensaje deja de coincidir
    # en cuanto alguien añade un caso, y entonces el propio informe miente.
    _hechas = [0]

    def revisar(nombre, condicion, detalle=""):
        _hechas[0] += 1
        if condicion:
            print("  ✓ " + nombre)
        else:
            fallos.append(nombre)
            print("  ✗ %s  ->  %s" % (nombre, detalle))

    with tempfile.TemporaryDirectory() as tmp:
        # 1 · El rectángulo de color como personaje SÍ se señala…
        p1 = _proyecto_falso(os.path.join(tmp, "p1"), objetos={
            "obj_jugador": {"eventos": {"Draw_0": "draw_rectangle(x, y, x+16, y+16, false);"}},
        })
        rect, rect_ui = objetos_rectangulo(p1)
        revisar("un objeto de juego sin sprite que pinta figuras se señala",
                "obj_jugador" in rect, rect)

        # 2 · …y una pantalla de interfaz NO. Es la calibración de r15 §2.12.
        p2 = _proyecto_falso(os.path.join(tmp, "p2"), objetos={
            "obj_seleccion": {"eventos": {"Draw_0": "draw_rectangle(0, 0, 100, 20, false);"}},
            "obj_menu":      {"eventos": {"Draw_0": "draw_rectangle(0, 0, 100, 20, false);"}},
        })
        rect2, rect_ui2 = objetos_rectangulo(p2)
        revisar("una pantalla de interfaz NO se cuenta como rectángulo prohibido",
                rect2 == [] and "obj_seleccion" in rect_ui2 and "obj_menu" in rect_ui2,
                "sospechosos=%s interfaz=%s" % (rect2, rect_ui2))

        # 3 · Entrada sin guarda: se señala.
        p3 = _proyecto_falso(os.path.join(tmp, "p3"), objetos={
            "obj_jugador": {"eventos": {"Step_0": "if (keyboard_check_pressed(vk_space)) saltar();"}},
        })
        sin, con = objetos_sin_guarda(p3)
        revisar("un objeto que lee entrada sin guarda se señala", "obj_jugador" in sin, sin)

        # 4 · Con guarda de pausa: NO se señala.
        p4 = _proyecto_falso(os.path.join(tmp, "p4"), objetos={
            "obj_jugador": {"eventos": {"Step_0":
                "if (!global.pausa && keyboard_check_pressed(vk_space)) saltar();"}},
        })
        sin4, _ = objetos_sin_guarda(p4)
        revisar("con guarda de pausa NO se señala", sin4 == [], sin4)

        # 5 · La laxitud que hubo que quitar: `entrada_confirmar()` NO es una guarda.
        p5 = _proyecto_falso(os.path.join(tmp, "p5"), objetos={
            "obj_jugador": {"eventos": {"Step_0":
                "if (entrada_confirmar()) aceptar();"}},
        }, scripts={"scr_entrada": "function entrada_confirmar() { return keyboard_check_pressed(vk_enter); }"})
        sin5, _ = objetos_sin_guarda(p5)
        revisar("una función de ENTRADA no cuela como guarda", "obj_jugador" in sin5, sin5)

        # 6 · Trazas sueltas frente a canal de error (r15 §2.12).
        p6 = _proyecto_falso(os.path.join(tmp, "p6"), scripts={
            "scr_juego":    'function paso() { show_debug_message("aqui llego"); }',
            "scr_registro": 'function registrar(_t) { show_debug_message(_t); }',
            "scr_save_load": 'function save_game() { show_debug_message("error"); }',
        })
        sueltas, infra = contar_trazas(p6)
        revisar("una traza suelta se cuenta", sueltas == 1, sueltas)
        revisar("el registrador y los scripts de la biblioteca no", infra == 2, infra)

        # 7 quater · Texto a pelo, Draw GUI y pantallas que no se pueden saltar.
        p7d = _proyecto_falso(os.path.join(tmp, "p7d"), objetos={
            "obj_hud":    {"eventos": {"Draw_64": 'draw_text(8, 8, "Vidas restantes");'}},
            "obj_bien":   {"eventos": {"Draw_0":  'draw_text(8, 8, txt("vidas"));'}},
            "obj_splash": {"eventos": {"Step_0":  "temporizador--;"}},
            "obj_intro":  {"eventos": {"Step_0":  "if (keyboard_check_pressed(vk_space)) saltar();"}},
        })
        _lit = [t for _f, t in textos_sin_traducir(p7d)]
        revisar("un draw_text con el texto a pelo se señala", "Vidas restantes" in _lit, _lit)
        revisar("y uno con txt() no", len(_lit) == 1, _lit)
        revisar("detecta que hay Draw GUI", hay_draw_gui(p7d))
        _ns = pantallas_no_saltables(p7d)
        revisar("un splash que no lee entrada se señala", "obj_splash" in _ns, _ns)
        revisar("y una intro que sí la lee, no", "obj_intro" not in _ns, _ns)

        # La forma que se me escapó en la primera versión: un struct de entrada
        # centralizado, sin paréntesis. Un proyecto real que lo hacía bien salía
        # marcado como si estuviera mal.
        p7e = _proyecto_falso(os.path.join(tmp, "p7e"), objetos={
            "obj_splash": {"eventos": {"Step_0":
                "if (temporizador > 160 || global.entrada.cualquiera) ir_a_escena(rm_menu);"}},
        })
        revisar("un splash que consulta `global.entrada.cualquiera` NO se señala",
                pantallas_no_saltables(p7e) == [], pantallas_no_saltables(p7e))

        # Y la segunda forma que se me escapó: guardar el struct en una local.
        p7f = _proyecto_falso(os.path.join(tmp, "p7f"), objetos={
            "obj_intro": {"eventos": {"Step_0":
                "var _e = global.entrada;\nif (_e.aceptar || _e.salto_pulsado) avanzar();"}},
        })
        revisar("una intro que guarda `global.entrada` en una local tampoco",
                pantallas_no_saltables(p7f) == [], pantallas_no_saltables(p7f))

        # 7 ter · Un sprite de personaje que es un cuadrado de color.
        try:
            from PIL import Image as _Im
            p7c = os.path.join(tmp, "p7c")
            _proyecto_falso(p7c)
            for _n, _col in (("spr_jugador", (200, 40, 40, 255)),
                             ("spr_sombra", (0, 0, 0, 120)),
                             ("spr_enemigo", None)):
                _d = os.path.join(p7c, "sprites", _n)
                os.makedirs(_d, exist_ok=True)
                if _col is None:
                    # Un sprite con arte de verdad: varios colores.
                    _im = _Im.new("RGBA", (8, 8))
                    _im.putdata([(i * 7 % 255, i * 13 % 255, i * 29 % 255, 255) for i in range(64)])
                else:
                    _im = _Im.new("RGBA", (8, 8), _col)
                _im.save(os.path.join(_d, _n + ".png"))
            _pl = [n for n, _c, _t in sprites_planos(p7c)]
            revisar("un spr_jugador de color plano se señala", "spr_jugador" in _pl, _pl)
            revisar("una sombra plana NO se señala", "spr_sombra" not in _pl, _pl)
            revisar("y un sprite con arte de verdad tampoco", "spr_enemigo" not in _pl, _pl)
        except ImportError:
            print("  · (sin Pillow: los 3 casos de sprites planos no se han ejecutado)")

        # 7 bis · Un objeto sin máscara contra el que se colisiona.
        p7b = os.path.join(tmp, "p7b")
        _proyecto_falso(p7b, objetos={"obj_muro": {}}, scripts={
            "scr_mover": "function choca() { return place_meeting(x, y, obj_muro); }"})
        # `_proyecto_falso` escribe spriteId null; hace falta también maskSpriteId.
        _yy = os.path.join(p7b, "objects", "obj_muro", "obj_muro.yy")
        open(_yy, "w", encoding="utf-8").write('{"spriteId":null,"maskSpriteId":null,"name":"obj_muro"}')
        revisar("un objeto sin máscara contra el que se colisiona se señala",
                "obj_muro" in objetos_sin_mascara(p7b), objetos_sin_mascara(p7b))
        # Y con sprite, no.
        open(_yy, "w", encoding="utf-8").write(
            '{"spriteId":{"name":"spr_x"},"maskSpriteId":null,"name":"obj_muro"}')
        revisar("y con sprite NO se señala", objetos_sin_mascara(p7b) == [],
                objetos_sin_mascara(p7b))

        # 7 · Sistemas que ya existen hechos (r15 §4).
        p7 = _proyecto_falso(os.path.join(tmp, "p7"), scripts={
            "scr_input":  "function input_x() { return 0; }",
            "scr_propio": "function algo_mio() { return 1; }",
        })
        rein = [n for n, _ in reinventos(p7)]
        revisar("avisa de que `Input` ya existe", "scr_input" in rein, rein)
        revisar("y no se inventa avisos para lo demás", "scr_propio" not in rein, rein)

        # --- Draw GUI es interfaz, se llame como se llame ---------------------------
        # El caso real: `obj_juego`, el director de partida del juego «Enjambre», pintaba
        # su HUD en Draw GUI y salía en la lista de sospechosos de «rectángulo de color
        # como personaje». Un nombre más en la lista habría tapado ese caso y dejado
        # fuera el siguiente; la regla estructural los cubre todos.
        _b = _proyecto_falso(os.path.join(tmp, "gui"), objetos={
            "obj_zzdirector": {"sin_sprite": True, "eventos": {
                "Draw_64": "draw_rectangle(0, 0, 100, 20, false);"}},
            "obj_bicho": {"sin_sprite": True, "eventos": {
                "Draw_0": "draw_circle(x, y, 8, false);"}},
        })
        _malos, _ui = objetos_rectangulo(_b)
        revisar("un objeto que solo pinta en Draw GUI cuenta como interfaz",
                "obj_zzdirector" in _ui and "obj_zzdirector" not in _malos, str((_malos, _ui)))
        revisar("y uno que pinta en el Draw del MUNDO sigue siendo sospechoso",
                "obj_bicho" in _malos, str((_malos, _ui)))

    # --- recursos creados y nunca liberados -------------------------------------
    # La comprobación se calibra por los dos lados: tiene que saltar con la fuga
    # y CALLARSE en cuanto el destructor aparece en cualquier parte del proyecto.
    # Un aviso que salta cuando no toca se aprende a ignorar, y con él se ignoran
    # los que sí importaban.
    _fuga = recursos_sin_liberar("var _m = ds_map_create();\nds_map_set(_m, 0, 1);")
    revisar("un ds_map creado y nunca destruido salta",
            [c for c, _d, _h, _v in _fuga] == ["ds_map_create"], str(_fuga))

    _ok = recursos_sin_liberar("var _m = ds_map_create();\nds_map_destroy(_m);")
    revisar("y con su ds_map_destroy en el proyecto se calla", _ok == [], str(_ok))

    # El destructor puede estar en OTRO archivo: el auditor concatena todo el GML
    # del proyecto justo para que esto no dé un falso positivo.
    _ok2 = recursos_sin_liberar("obj_a: var _s = surface_create(64, 64);\n"
                                "obj_b (Clean Up): surface_free(global.s);")
    revisar("el destructor vale aunque esté en otro objeto", _ok2 == [], str(_ok2))

    # `part_system_create_layer` es de la misma familia y se destruye igual.
    _ok3 = recursos_sin_liberar("part_system_create_layer(\"Efectos\", true);\n"
                                "part_system_destroy(global.ps);")
    revisar("part_system_create_layer cuenta como part_system_create", _ok3 == [], str(_ok3))

    # Un time source creado UNA vez es el reloj del mundo: legítimo. Dos ya es un
    # patrón que crece, y las alarmas —que sí mueren con la instancia— no sirven de
    # excusa: un time source sobrevive a su creador.
    _uno = recursos_sin_liberar("global.ts = time_source_create(time_source_game, 1, "
                                "time_source_units_seconds, function() {});")
    revisar("un time source creado UNA vez no se denuncia", _uno == [], str(_uno))

    _dos = recursos_sin_liberar("time_source_create(time_source_game, 1, s, f);\n"
                                "time_source_create(time_source_game, 2, s, g);")
    revisar("creado dos veces y nunca destruido, sí",
            [c for c, _d, _h, _v in _dos] == ["time_source_create"], str(_dos))

    _fuentes = recursos_sin_liberar("font_add(\"a\", 12, false, false, 32, 128);")
    revisar("una fuente cargada una sola vez no es una fuga", _fuentes == [], str(_fuentes))

    # Y lo que NO es una fuga: un proyecto que no crea nada manual no debe salir
    # en el informe con avisos vacíos.
    revisar("un proyecto sin recursos manuales no genera aviso",
            recursos_sin_liberar("x += 1;\ndraw_self();") == [])

    # sin_comentarios: el falso VERDE que encontró un agente desconfiando de sus ticks.
    revisar("una palabra en un comentario de línea NO cuenta como código",
            "creditos" not in sin_comentarios("// arco: menu -> final -> creditos\nx = 1;"))
    revisar("ni en un comentario de bloque",
            "pausa" not in sin_comentarios("/* aqui ira la pausa */\nvar _a = 1;"))
    revisar("pero la MISMA palabra en codigo si cuenta",
            "creditos" in sin_comentarios("estado = creditos;"))
    revisar("y dentro de una cadena tambien, que es evidencia legitima",
            '"pausa"' in sin_comentarios('estado = "pausa";'))
    revisar("una // dentro de una cadena NO parte la linea",
            "https://ejemplo.com" in sin_comentarios('var _u = "https://ejemplo.com"; x = 1;')
            and "x = 1" in sin_comentarios('var _u = "https://ejemplo.com"; x = 1;'))
    revisar("un comentario de bloque conserva los saltos de linea",
            sin_comentarios("/*\n\n*/\nx = 1;").count("\n") == 3,
            repr(sin_comentarios("/*\n\n*/\nx = 1;")))
    revisar("un comentario de bloque sin cerrar no se come lo de antes",
            sin_comentarios("x = 1;\n/* abierto").startswith("x = 1;"))

    # ── El recurso que se cae del `.yyp` y se queda en disco.
    #
    # Reproducido en un proyecto limpio (2026-09-10): se crea `spr_del_rol_A`, otro
    # proceso escribe el `.yyp` que había leído ANTES, y crea `spr_del_rol_B`. A
    # desaparece del `.yyp`, su carpeta se queda en disco, y `gm-cli compile` sale
    # con 0 sin decir una palabra. `resourcetool` reescribe el `.yyp` entero.
    #
    # Lo venenoso es la DIRECCIÓN del engaño: el consejo de siempre —«comprueba el
    # disco, no la salida del comando»— aquí da un falso VERDE, porque los archivos
    # están donde los dejaste. Lo que hay que mirar es el `.yyp`.
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, "huerfanos")
        for carpeta, nombre in (("sprites", "spr_registrado"), ("sprites", "spr_perdido"),
                                ("objects", "obj_registrado")):
            dd = os.path.join(base, carpeta, nombre)
            os.makedirs(dd, exist_ok=True)
            with open(os.path.join(dd, nombre + ".yy"), "w", encoding="utf-8") as f:
                f.write('{"resourceType":"GMSprite",}')
        # Una carpeta suelta que NO es un recurso: no lleva su `.yy` dentro.
        os.makedirs(os.path.join(base, "sprites", "_borradores"), exist_ok=True)
        # Y una carpeta que no es de recursos en absoluto.
        os.makedirs(os.path.join(base, "datafiles", "idiomas"), exist_ok=True)

        h = recursos_huerfanos(base, ["spr_registrado", "obj_registrado"])
        revisar("caza el recurso que está en disco y no en el .yyp",
                h == [("sprites", "spr_perdido")], str(h))
        revisar("y NO marca los que sí están registrados",
                not any(n in ("spr_registrado", "obj_registrado") for _, n in h), str(h))
        revisar("una carpeta sin su .yy dentro no cuenta como recurso",
                not any(n == "_borradores" for _, n in h), str(h))
        revisar("y `datafiles` no se mira siquiera",
                not any(c == "datafiles" for c, _ in h), str(h))
        revisar("con todo registrado, no hay huérfanos",
                recursos_huerfanos(base, ["spr_registrado", "spr_perdido",
                                          "obj_registrado"]) == [])
        revisar("un proyecto sin carpetas de recurso no revienta",
                recursos_huerfanos(os.path.join(tmp, "no-existe"), []) == [])

        # Y el fallo que apareció al auditar un proyecto recién creado, sin objetos.
        revisar("un proyecto sin carpeta objects devuelve DOS listas, no revienta",
                objetos_rectangulo(os.path.join(tmp, "no-existe")) == ([], []),
                str(objetos_rectangulo(os.path.join(tmp, "no-existe"))))

    if fallos:
        print("\n✗ %d comprobación(es) de la autoprueba fallan." % len(fallos))
        return 1
    print("\n✓ Las %d comprobaciones de la autoprueba pasan." % _hechas[0])
    return 0


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    sys.exit(main())
