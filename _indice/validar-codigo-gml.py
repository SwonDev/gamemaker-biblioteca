#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validar-codigo-gml.py — comprueba que el código GML de la biblioteca no inventa funciones.

Extrae cada llamada `funcion(` de los bloques ```gml de los documentos propios (y de los
.gml sueltos) y comprueba que el nombre es real: o un símbolo del runtime (GmlSpec.xml), o
una función definida en la propia biblioteca (`function nombre(`), o una palabra clave del
lenguaje. Lo que no es nada de eso es una función inventada — el peor fallo posible aquí.

    python3 _indice/validar-codigo-gml.py

Sale con 0 solo si no hay ni una llamada sospechosa.
"""
import os, re, json, sys

# Windows: en cuanto la salida no es una consola interactiva (pipes, «> archivo», o el
# propio actualizar.py capturando la salida de este script vía subprocess), sys.stdout
# usa la página de códigos ANSI del sistema en vez de UTF-8 — y los símbolos ✗/⚠/→/…
# de este código no caben ahí: UnicodeEncodeError a mitad de ejecución. No verificado
# en Windows de verdad; aplica la solución estándar de Python 3.7+ (PEP 528 cubre la
# consola interactiva sola, no pipes ni redirecciones).
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IND = os.path.join(RAIZ, "_indice")

# bloques de código y llamadas a función dentro
BLOQUE = re.compile(r"```gml\n(.*?)```", re.S)
COMENTARIO = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)
CADENA = re.compile(r'"(?:[^"\\]|\\.)*"|\$"(?:[^"\\]|\\.)*"')
# nombre seguido de '(' que NO va precedido de '.' (eso sería un método de struct,
# cuya validez depende del struct, no del runtime) ni de otro carácter de palabra.
LLAMADA = re.compile(r"(?<![.\w])([a-z_][a-z0-9_]*)\s*\(")
DEFINE = re.compile(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
METODO = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*function\s*\(")
METODO_STRUCT = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*:\s*function\s*\(")
# prefijos de RECURSO del proyecto: un nombre así es un asset/objeto, no una función.
# (No incluye part_/path_/audio_ etc., que SÍ son familias de funciones del runtime.)
PREF_ASSET = ("spr_", "obj_", "snd_", "rm_", "bg_", "pth_", "fnt_", "tset_",
              "seq_", "vs_", "ts_", "anim_", "emit_")

# construcciones del lenguaje que llevan paréntesis pero no son funciones
PALABRAS = {
    "if","while","for","repeat","with","switch","return","do","until","else",
    "var","and","or","not","then","begin","end","exit","break","continue","case",
    "new","delete","typeof","instanceof","try","catch","throw","finally","static",
    "constructor","enum","globalvar","xor","mod","div","default","function",
}

# carpetas de contenido propio (no manual, no repos de terceros)
# «Lumbre» es el juego personal del usuario y «GameMaker_Fuentes» el almacén crudo de repos
# clonados: ninguno es documentación de la biblioteca y no se indexan ni se revisan.
EXCL = {"_indice", "09 - Manual oficial", "11 - Código descargado",
        "Lumbre", "GameMaker_Fuentes"}


def limpiar(codigo):
    """Quita literales de cadena y comentarios: ahí «palabra(» no es una llamada.

    Las cadenas se neutralizan PRIMERO. Un string en base64 o una URL puede
    contener `//` (p. ej. `"Ud93/wghI//D2cr/"` o `"https://..."`) — si el
    comentario se quitara antes, ese `//` interno se leería como el inicio de
    un comentario de línea y se comería el resto de la cadena (y su comilla de
    cierre), descuadrando las comillas de todo lo que viene después.
    """
    codigo = CADENA.sub('""', codigo)
    codigo = COMENTARIO.sub(" ", codigo)
    return codigo


def comillas_descuadradas(codigo):
    """¿Hay algún literal de cadena sin cerrar en este archivo?

    Nace de un caso real (`_indice/auditorias/r12-prueba-plataformas.md` §1.1): un
    generador escribió un `"` SIN escapar dentro de un literal de GML. El literal
    quedaba cerrado antes de tiempo, y a partir de ahí `limpiar()` interpretaba como
    cadena lo que era código y al revés — perdiendo dos definiciones de función reales.
    El agente que lo sufrió lo diagnosticó como un bug de `limpiar()`; no lo era, y por
    eso la comprobación va aquí y no en el regex: **el código de entrada estaba roto**,
    y lo que faltaba era decirlo en vez de dar una lista de nombres desconcertante.

    El daño de aquello no fue el falso positivo: fue que la salida mezclaba dos nombres
    falsos con UNO real, y eso enseña a desconfiar de la lista entera justo donde estaba
    el único fallo que iba a reventar el juego.

    Se cuenta por línea, tras quitar comentarios, y se ignoran las cadenas verbatim
    (`@"…"`, `@'…'`), que sí pueden abarcar varias líneas de forma legítima.
    """
    sin_com = COMENTARIO.sub(" ", codigo)
    # Las cadenas verbatim (@"…", @'…') SÍ pueden abarcar varias líneas de forma
    # legítima y no admiten escapes: se retiran enteras antes de contar, conservando
    # los saltos de línea para que los números que se devuelvan sigan siendo los del
    # archivo original.
    def _hueco(m):
        return "\n" * m.group(0).count("\n")
    sin_verbatim = re.sub(r'@"[^"]*"|@\'[^\']*\'', _hueco, sin_com, flags=re.S)

    rotas = []
    for i, linea in enumerate(sin_verbatim.split("\n"), 1):
        # Se quitan primero las secuencias escapadas (\\ y \") para no contarlas.
        limpia = re.sub(r'\\.', "", linea)
        if limpia.count('"') % 2:
            rotas.append(i)
    return rotas


def cargar_simbolos():
    ruta = os.path.join(IND, "simbolos.json")
    if not os.path.exists(ruta):
        print("✗ No existe _indice/simbolos.json todavía.")
        print("  Se genera (desde el GmlSpec.xml de tu runtime instalado) con:")
        print("      python3 _indice/actualizar.py")
        sys.exit(1)
    d = json.load(open(ruta, encoding="utf-8"))
    return d["simbolos"]


def simbolos_runtime():
    return set(cargar_simbolos())


def parsear_firma(firma):
    """(mínimo, máximo, variádica) de argumentos a partir de «nombre(a, [b], ...)».

    construir-indices.py envuelve cada parámetro opcional entre corchetes según el
    atributo `Optional` de GmlSpec.xml — el propio parámetro variádico `...`
    incluido: sin corchetes (`ds_list_add(id, ...)`) exige al menos un argumento
    más; entre corchetes (`show_debug_message(string_or_format, [...])`) deja la
    cola en cero o más. No hay parámetros anidados dentro de una firma (verificado
    contra las 2359 firmas del runtime 2026.0.0.23): separar por comas de nivel
    superior basta. `máximo` es `None` cuando la función es variádica (sin tope).
    """
    ini = firma.find("(")
    if ini == -1:
        return 0, 0, False
    profundidad = 0
    fin = None
    for i in range(ini, len(firma)):
        if firma[i] == "(":
            profundidad += 1
        elif firma[i] == ")":
            profundidad -= 1
            if profundidad == 0:
                fin = i
                break
    contenido = firma[ini + 1:fin] if fin is not None else ""
    tokens, actual, d = [], "", 0
    for ch in contenido:
        if ch in "([":
            d += 1
        elif ch in ")]":
            d -= 1
        if ch == "," and d == 0:
            tokens.append(actual.strip())
            actual = ""
        else:
            actual += ch
    if actual.strip():
        tokens.append(actual.strip())

    requeridos, opcionales, variadica = 0, 0, False
    for t in tokens:
        if not t:
            continue
        es_opcional = t.startswith("[") and t.endswith("]")
        interior = t[1:-1].strip() if es_opcional else t
        if interior == "...":
            variadica = True
        if es_opcional:
            opcionales += 1
        else:
            requeridos += 1
    maximo = None if variadica else requeridos + opcionales
    return requeridos, maximo, variadica


def aridades_funciones(simbolos):
    """{nombre: (mínimo, máximo|None, variádica)} de cada función con firma conocida."""
    out = {}
    for nom, s in simbolos.items():
        if s.get("tipo") == "función" and s.get("firma"):
            out[nom] = parsear_firma(s["firma"])
    return out


def contar_argumentos(codigo, pos_apertura):
    """Cuenta los argumentos de nivel superior de una llamada.

    `pos_apertura` es la posición justo DESPUÉS del '(' de apertura (donde ya
    empieza el primer argumento). Respeta paréntesis, corchetes y llaves
    anidados para no partir por una coma que está dentro de una sub-llamada,
    un array o un struct literal. Si el paréntesis nunca cierra dentro del
    bloque —un snippet ilustrativo incompleto, habitual en la documentación—
    devuelve `None`: mejor no evaluar que arriesgar un falso positivo.
    """
    profundidad = 1
    i = pos_apertura
    n = len(codigo)
    inicio = pos_apertura
    args = []
    while i < n:
        c = codigo[i]
        if c in "([{":
            profundidad += 1
        elif c in ")]}":
            profundidad -= 1
            if profundidad < 0:
                return None
            if profundidad == 0:
                trozo = codigo[inicio:i]
                if trozo.strip():
                    args.append(trozo)
                return len(args)
        elif c == "," and profundidad == 1:
            args.append(codigo[inicio:i])
            inicio = i + 1
        i += 1
    return None


def funciones_externas():
    """Nombres de función definidos en las extensiones y librerías descargadas.

    admob_*, steam_*, scribble_*, input_*… no están en GmlSpec (son de extensión),
    pero SÍ existen: su definición está en 11 - Código descargado. Reconocerlas
    evita marcarlas como inventadas. La lista sale del código real, no de una
    lista escrita a mano que caducaría.
    """
    ext = set()
    base = os.path.join(RAIZ, "11 - Código descargado")
    # El corpus es opcional: no viaja en el repositorio público (licencias de terceros).
    # Sin él no se puede DESCARTAR una función de extensión, así que lo que aquí sería un
    # descarte limpio se convertiría en un falso «inventada». Quien clone el repositorio
    # vería «hay código que llama a funciones que no existen» sin que sea cierto. Se
    # devuelve None —distinto de conjunto vacío— para que quien llama sepa que no puede
    # afirmar nada sobre las funciones de extensión, y lo diga en vez de acusar.
    if not os.path.isdir(base) or not any(
        os.path.isdir(os.path.join(base, d)) for d in os.listdir(base)
        if not d.startswith((".", "_"))
    ):
        return None
    for raiz, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if not d.startswith(".git")]
        for f in files:
            if not f.endswith((".gml", ".js", ".md")):
                continue
            try:
                txt = open(os.path.join(raiz, f), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for m in DEFINE.finditer(txt):
                ext.add(m.group(1))
            # las .js de extensión declaran funciones con function nombre() también
            for m in re.finditer(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)", txt):
                ext.add(m.group(1))
    return ext


# Los identificadores de GML son ASCII puro: `function añadir()` da «invalid token ñ»
# y NO compila. Es un error fácil de cometer escribiendo en español y que ningún
# corrector ortográfico detecta, porque la palabra está bien escrita.
NO_ASCII = re.compile(r"(?<![.\w])((?:function|var|globalvar|enum)\s+)?"
                      r"([A-Za-z_\u00C0-\u024F][A-Za-z0-9_\u00C0-\u024F]*)\s*(?=\(|=|;|,|\)|$)",
                      re.M)


def identificadores_no_ascii(docs):
    """Identificadores propios con tildes o eñes: no compilan en GameMaker."""
    malos = {}
    decl = re.compile(r"\b(?:function|var|globalvar|enum)\s+([A-Za-z_\u00C0-\u024F][A-Za-z0-9_\u00C0-\u024F]*)")
    llam = re.compile(r"(?<![.\w])([A-Za-z_\u00C0-\u024F][A-Za-z0-9_\u00C0-\u024F]*)\s*\(")
    for fp, txt in docs:
        f = os.path.basename(fp)
        codigo = limpiar(txt if f.endswith(".gml") else "\n".join(BLOQUE.findall(txt)))
        for pat in (decl, llam):
            for m in pat.finditer(codigo):
                nom = m.group(1)
                if any(ord(c) > 127 for c in nom):
                    malos.setdefault(nom, set()).add(os.path.relpath(fp, RAIZ))
    return malos


# Escribir en `working_directory` compila y funciona en el IDE, pero esa carpeta es de
# SOLO LECTURA en una build exportada (Windows empaquetado, movil, macOS con sandbox):
# ver 01 - Fundamentos/14 - Persistencia y archivos.md §1. La forma correcta —la que usa
# el propio 06 - Assets y Scripts/scr_save_load.gml— es `game_save_id`, o un nombre de
# archivo suelto que resuelve solo al area de guardado.
#
# Solo cuentan las funciones que ESCRIBEN un fichero: leer con working_directory (un
# Included File del bundle) sigue siendo correcto y no lo detecta este patron.
FUNCS_ESCRITURA_ARCHIVO = (
    "file_text_open_write", "file_text_open_append",
    "buffer_save", "buffer_save_ext", "buffer_save_async",
    "sprite_save",
)
ESCRITURA_WD = re.compile(
    r"\b(?:" + "|".join(FUNCS_ESCRITURA_ARCHIVO) + r")\s*\([^\n;]*\bworking_directory\b"
)


def escrituras_en_working_directory(docs):
    """Llamadas que ESCRIBEN un fichero usando `working_directory` como ruta.

    Se ejecuta sobre el mismo `codigo` que el resto de comprobaciones: solo bloques
    ```gml (o .gml sueltos) y con comentarios/cadenas ya vaciados por `limpiar()`, asi
    que ni la prosa que explica el problema (01/14 §1) ni un comentario de aviso como
    «NO uses working_directory» disparan un falso positivo: ahi no hay una llamada
    real a ninguna de estas funciones, solo texto.
    """
    malas = {}
    for fp, txt in docs:
        f = os.path.basename(fp)
        codigo = limpiar(txt if f.endswith(".gml") else "\n".join(BLOQUE.findall(txt)))
        for m in ESCRITURA_WD.finditer(codigo):
            linea = re.sub(r"\s+", " ", m.group(0)).strip()
            malas.setdefault(os.path.relpath(fp, RAIZ), []).append(linea)
    return malas


def main():
    simbolos = cargar_simbolos()
    runtime = set(simbolos)
    aridad = aridades_funciones(simbolos)
    externas = funciones_externas()
    corpus_instalado = externas is not None
    if not corpus_instalado:
        externas = set()   # no se puede descartar por extensión: se avisará al final

    solo_corpus = {}   # nombres que solo salva el corpus de terceros — ver el bucle de abajo
    FAMILIAS_PREFIJO = ("draw_", "audio_", "gpu_", "ds_", "camera_", "instance_", "sprite_",
                        "room_", "layer_", "surface_", "shader_", "buffer_", "window_",
                        "display_", "font_", "keyboard_", "mouse_", "gamepad_", "view_")

    # 1 · recolectar TODAS las funciones y métodos que la biblioteca define (son legítimas)
    definidas = set()
    docs = []
    for raiz, dirs, files in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if d not in EXCL and not d.startswith(".")]
        for f in files:
            if not f.endswith((".md", ".gml")):
                continue
            fp = os.path.join(raiz, f)
            try:
                txt = open(fp, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            docs.append((fp, txt))
            # las .gml son todas código; los .md solo sus bloques ```gml
            codigo = limpiar(txt if f.endswith(".gml") else "\n".join(BLOQUE.findall(txt)))
            for m in DEFINE.finditer(codigo): definidas.add(m.group(1))
            for m in METODO.finditer(codigo): definidas.add(m.group(1))
            for m in METODO_STRUCT.finditer(codigo): definidas.add(m.group(1))

    # 2 · buscar llamadas cuyo nombre no sea runtime, ni definido, ni palabra clave
    #     (y, de paso, la aridad de las que SÍ son del runtime: existir no basta,
    #     la firma completa dice cuántos argumentos hacen falta y cuántos caben)
    sospechosas = {}
    problemas_aridad = {}
    for fp, txt in docs:
        f = os.path.basename(fp)
        codigo = limpiar(txt if f.endswith(".gml") else "\n".join(BLOQUE.findall(txt)))
        for m in LLAMADA.finditer(codigo):
            nom = m.group(1)
            if nom in runtime and nom not in definidas and nom in aridad:
                minimo, maximo, variadica = aridad[nom]
                n_args = contar_argumentos(codigo, m.end())
                if n_args is not None:
                    if n_args < minimo:
                        rango = f"mínimo {minimo}" if variadica else f"entre {minimo} y {maximo}"
                        problemas_aridad.setdefault(nom, []).append(
                            (os.path.relpath(fp, RAIZ),
                             f"{n_args} argumento(s) — la firma exige {rango}"))
                    elif maximo is not None and n_args > maximo:
                        problemas_aridad.setdefault(nom, []).append(
                            (os.path.relpath(fp, RAIZ),
                             f"{n_args} argumento(s) — la firma admite entre {minimo} y {maximo}"))
            # Un nombre con prefijo de familia del runtime que NO está en el runtime ni
            # lo define la biblioteca, y que solo se salva porque alguna librería de
            # terceros lo declara, merece quedar anotado: ahí es donde se esconden
            # nuestras propias invenciones. `draw_polygon()` vivió meses en 01/11 —
            # dentro de una lista de funciones reales— porque el corpus la absolvía, y
            # solo apareció al validar un clon SIN corpus (09-09-2026).
            if (nom not in runtime and nom not in definidas and nom not in PALABRAS
                    and nom in externas and nom.startswith(FAMILIAS_PREFIJO)):
                solo_corpus.setdefault(nom, set()).add(os.path.relpath(fp, RAIZ))
            if nom in runtime or nom in definidas or nom in externas or nom in PALABRAS:
                continue
            if nom.startswith(PREF_ASSET):     # referencia a un recurso, no una función
                continue
            if nom.startswith("_"):            # variable local con un method() dentro
                continue
            sospechosas.setdefault(nom, []).append(os.path.relpath(fp, RAIZ))

    # 3 · clasificar. Un nombre con prefijo de FAMILIA del runtime que no existe
    #     es una función inventada (GRAVE): un LLM la copiaría y no compilaría.
    #     El resto son funciones propias de los ejemplos (temblar, saltar…): OK.
    FAMILIAS = ("draw_","audio_","gpu_","ds_","camera_","instance_","sprite_","room_",
        "layer_","surface_","shader_","buffer_","string_","file_","ini_","json_",
        "physics_","part_","path_","mp_","tile_","tilemap_","window_","display_",
        "os_","game_","font_","texture_","vertex_","matrix_","math_","keyboard_",
        "mouse_","gamepad_","view_","event_","object_","asset_","struct_","array_",
        "variable_","real","string","script_","method","time_","date_","lerp",
        "clamp","irandom","random","point_","lengthdir_","collision_","place_",
        "move_","distance_","angle_")
    def es_extension(n):   # steam_/admob_/gpb_… definidas en C++ del repo, no en .gml
        return n.startswith(("steam_","admob_","gpb_","appleiap_","gamecenter_",
                             "firebase_","levelplay_","facebook_"))
    no_ascii = identificadores_no_ascii(docs)
    if no_ascii:
        print(f"\n✗ {len(no_ascii)} identificadores con tilde o eñe (GML solo admite ASCII: no compilan):")
        for nom, donde in sorted(no_ascii.items()):
            print(f"    {nom}  →  en {', '.join(sorted(donde)[:3])}")

    escrituras_wd = escrituras_en_working_directory(docs)
    if escrituras_wd:
        print(f"\n✗ {sum(len(v) for v in escrituras_wd.values())} escritura(s) en `working_directory` "
              f"(GRAVE: solo lectura en una build exportada — usa `game_save_id`, ver 01/14 §1):")
        for fp, lineas in sorted(escrituras_wd.items()):
            for linea in lineas:
                print(f"    {fp}  →  {linea}")

    graves = {n: d for n, d in sospechosas.items()
              if n.startswith(FAMILIAS) and not es_extension(n)}
    propias = {n: d for n, d in sospechosas.items() if n not in graves and not es_extension(n)}

    print(f"runtime: {len(runtime)} símbolos · propias definidas: {len(definidas)} · "
          f"extensiones/librerías: {len(externas) if corpus_instalado else 'sin instalar'}")
    print(f"{len(propias)} funciones propias de ejemplo (informativo) · "
          f"{len(graves)} posibles funciones del runtime INVENTADAS")

    if graves and not corpus_instalado:
        # Sin el corpus de `11 - Código descargado` no se puede distinguir una función
        # inventada de una de extensión (steam_*, scribble_*, input_*…). Se informa, pero
        # NO se acusa ni se hace fallar: acusar en falso a quien acaba de clonar el
        # repositorio es peor que no comprobarlo.
        print(f"\n⚠ {len(graves)} nombre(s) sin resolver, pero el corpus de "
              "`11 - Código descargado` no está instalado:")
        for nom in sorted(graves):
            print(f"    · {nom}()")
        print("  Pueden ser funciones de extensión perfectamente válidas. Para comprobarlo,")
        print("  trae el corpus con `./reconstruir.sh codigo` y vuelve a ejecutar.")
        graves = {}

    # Un documento que YA avisa de que ese nombre no es del runtime está haciendo lo
    # correcto: dejarlo en la lista para siempre sería ruido, y el ruido enseña a
    # ignorar la lista. Se separa —no se silencia—, igual que los relevos de
    # validar-integracion.py.
    AVISOS = ("no es una función del runtime", "no es una funcion del runtime",
              "no son funciones del runtime", "NO existe", "no existe en el runtime")
    reconocidos = {}
    for nom in list(solo_corpus):
        docs_ = solo_corpus[nom]
        if all(any(a.lower() in open(os.path.join(RAIZ, d), encoding="utf-8",
                                     errors="replace").read().lower() for a in AVISOS)
               for d in docs_):
            reconocidos[nom] = solo_corpus.pop(nom)

    if reconocidos:
        print(f"\n· {len(reconocidos)} nombre(s) que solo salva el corpus, pero el documento ya "
              f"avisa de que no son del runtime: {', '.join(sorted(reconocidos))}")

    if solo_corpus:
        print(f"\n🔎 {len(solo_corpus)} nombre(s) con pinta de función del runtime que NO están")
        print("   en el runtime: solo los salva alguna librería de `11 - Código descargado`.")
        print("   Míralos: si tu documento los presenta como API de GameMaker, es un error")
        print("   nuestro que el corpus está tapando. Si son de una librería, dilo en el texto.")
        for nom, docs_ in sorted(solo_corpus.items()):
            print(f"    · {nom}()  —  {', '.join(sorted(docs_)[:2])}")

    if graves:
        print("\n\033[1mFUNCIONES DEL RUNTIME QUE NO EXISTEN — a corregir:\033[0m")
        for nom, docs_ in sorted(graves.items(), key=lambda kv: -len(kv[1])):
            for d in sorted(set(docs_)):
                print(f"  ✗ {nom}()  ·  {d}")
    else:
        print("\nNingún nombre con prefijo del runtime sin resolver: el código no inventa funciones.")

    if problemas_aridad:
        n_llamadas = sum(len(v) for v in problemas_aridad.values())
        print(f"\n\033[1m✗ {n_llamadas} llamada(s) a {len(problemas_aridad)} función(es) del runtime "
              f"con un número de argumentos que no cuadra con su firma:\033[0m")
        print("  (existir no basta: la firma completa es la que manda — ver `buscar.py <función>`)")
        for nom, casos in sorted(problemas_aridad.items()):
            for fp, msg in casos:
                print(f"  ✗ {nom}()  ·  {msg}  ·  {fp}")
    else:
        print("\nNinguna llamada al runtime con un número de argumentos que no cuadre con su firma.")

    return 1 if (graves or no_ascii or escrituras_wd or problemas_aridad) else 0


if __name__ == "__main__":
    sys.exit(main())
