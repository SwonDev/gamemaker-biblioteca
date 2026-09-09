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
    # La pausa casi nunca es `global.pausa`: en un juego con gestor de escenas es un
    # estado dentro de la máquina del nivel (`estado = "pausa"`, `menu_pausa`). La primera
    # versión de este patrón solo miraba la global y daba un falso NEGATIVO sobre un juego
    # que sí la tenía — el error más caro aquí, porque deja pasar la ausencia que buscas.
    ("pausa",     "Pausa que congela el mundo",
     r"pausa|pause",
     r"instance_deactivate_all|\bpausad[oa]\b|\bis_paused\b"
     r"|[\"']paus[ae][\"']|\bmenu_paus[ae]\b|\b\w*_paus[ae]\b|\bpaus[ae]_\w+"),
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
    return ([s for s in sospechosos if not interfaz.match(s)],
            [s for s in sospechosos if interfaz.match(s)])


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
    icono, version = icono_y_version(ruta)
    reinv = reinventos(ruta)

    if a.json:
        print(json.dumps({"proyecto": proy["yyp"], "piezas": res, "primera_sala": primera,
                          "objetos_sin_sprite_que_dibujan_figuras": rect,
                          "objetos_de_interfaz_que_dibujan_figuras": rect_ui,
                          "sprites": n_sprites, "show_debug_message": debug,
                          "show_debug_message_infraestructura": debug_infra,
                          "objetos_que_leen_entrada_sin_guarda": sin_guarda,
                          "objetos_con_guarda": con_guarda,
                          "pausa_toca_el_audio": audio_pausa,
                          "icono_propio": icono, "version": version,
                          "sistemas_que_ya_existen": [{"tuyo": n, "existe": e} for n, e in reinv]},
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
        if reinv:
            print("  · %d sistema(s) que ya existían hechos. No es un fallo —puedes tener"
                  % len(reinv))
            print("    motivos— pero que sea una decisión, no un descuido (11 · _CATALOGO.md):")
            for nombre, sugerencia in reinv:
                print("      %-22s ya existe: %s" % (nombre, sugerencia))
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
        print("  %s Icono o splash propios en options/ (05/02 §4.4)"
              % ("✓" if icono else "✗"))
        if version:
            print("  %s Versión del ejecutable: %s%s"
                  % ("✓" if version != "1.0.0.0" else "⚠", version,
                     "  ← la de fábrica; súbela antes de publicar" if version == "1.0.0.0" else ""))
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

    def revisar(nombre, condicion, detalle=""):
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

        # 7 · Sistemas que ya existen hechos (r15 §4).
        p7 = _proyecto_falso(os.path.join(tmp, "p7"), scripts={
            "scr_input":  "function input_x() { return 0; }",
            "scr_propio": "function algo_mio() { return 1; }",
        })
        rein = [n for n, _ in reinventos(p7)]
        revisar("avisa de que `Input` ya existe", "scr_input" in rein, rein)
        revisar("y no se inventa avisos para lo demás", "scr_propio" not in rein, rein)

    if fallos:
        print("\n✗ %d comprobación(es) de la autoprueba fallan." % len(fallos))
        return 1
    print("\n✓ Las 9 comprobaciones de la autoprueba pasan.")
    return 0


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    sys.exit(main())
