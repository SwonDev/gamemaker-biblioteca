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
    """Quita comentarios y literales de cadena: ahí «palabra(» no es una llamada."""
    codigo = COMENTARIO.sub(" ", codigo)
    codigo = CADENA.sub('""', codigo)
    return codigo


def simbolos_runtime():
    d = json.load(open(os.path.join(IND, "simbolos.json"), encoding="utf-8"))
    return set(d["simbolos"])


def funciones_externas():
    """Nombres de función definidos en las extensiones y librerías descargadas.

    admob_*, steam_*, scribble_*, input_*… no están en GmlSpec (son de extensión),
    pero SÍ existen: su definición está en 11 - Código descargado. Reconocerlas
    evita marcarlas como inventadas. La lista sale del código real, no de una
    lista escrita a mano que caducaría.
    """
    ext = set()
    base = os.path.join(RAIZ, "11 - Código descargado")
    if not os.path.isdir(base):
        return ext
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
    runtime = simbolos_runtime()
    externas = funciones_externas()

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
    sospechosas = {}
    for fp, txt in docs:
        f = os.path.basename(fp)
        codigo = limpiar(txt if f.endswith(".gml") else "\n".join(BLOQUE.findall(txt)))
        for m in LLAMADA.finditer(codigo):
            nom = m.group(1)
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
          f"extensiones/librerías: {len(externas)}")
    print(f"{len(propias)} funciones propias de ejemplo (informativo) · "
          f"{len(graves)} posibles funciones del runtime INVENTADAS")

    if graves:
        print("\n\033[1mFUNCIONES DEL RUNTIME QUE NO EXISTEN — a corregir:\033[0m")
        for nom, docs_ in sorted(graves.items(), key=lambda kv: -len(kv[1])):
            for d in sorted(set(docs_)):
                print(f"  ✗ {nom}()  ·  {d}")
    else:
        print("\nNingún nombre con prefijo del runtime sin resolver: el código no inventa funciones.")
    return 1 if (graves or no_ascii or escrituras_wd) else 0


if __name__ == "__main__":
    sys.exit(main())
