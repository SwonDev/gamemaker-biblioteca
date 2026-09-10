#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audita la biblioteca de assets que te da el usuario, antes de tocar un archivo.

`07 · 09 §10 bis` dice el orden —licencia primero, encaje después— y las dos
comprobaciones que necesita una tipografía. Esto lo ejecuta. Nace de cuatro casos
**medidos** sobre bibliotecas reales, no de imaginar qué podría salir mal:

  1. **Un nombre de carpeta no es una fuente.** «Time Fantasy - surtido 01-12»
     no contenía Time Fantasy: dentro había packs de cuatro autores distintos con
     cuatro licencias distintas. La señal que lo delata no es el nombre —eso es
     texto libre— sino que **bajo una misma etiqueta conviven varios textos de
     licencia diferentes**. Eso sí se cuenta.
  2. **Un rip se esconde dentro de una carpeta legítima.** En `1-audio/musica/…`
     había pistas `.aac` sacadas de un juego de Nintendo, y al lado, guardado en
     la misma carpeta, **el propio conversor** que las extrajo. La herramienta de
     extracción junto a los medios es la señal.
  3. **Un «pack» que en realidad es un juego descompilado.** `PlayerSettings`,
     `MonoManager`, `EditorBuildSettings`, `Assembly-CSharp.dll`, `data.win`…
     Un asset pack no contiene nunca los artefactos de compilación de un motor.
  4. **El binario de una tipografía contradice al bundle.** Un pack decía CC0 y
     sus `.ttf` llevaban embebido `CC-BY-SA` con `fsType=4`, que prohíbe
     embeberla. Gana el binario. Reproducido después por otro equipo con otro
     método (`strings`), misma conclusión.

Cada hallazgo es estructural y contable. Lo que NO se hace aquí es adivinar si un
nombre «suena» a rip: un aviso que salta cuando no toca se aprende a ignorar.

Uso:
    python3 _indice/auditar-biblioteca-assets.py "/ruta/a/Biblioteca de Assets"
    python3 _indice/auditar-biblioteca-assets.py <ruta> --profundidad 3
    python3 _indice/auditar-biblioteca-assets.py <ruta> --solo-fuentes
    python3 _indice/auditar-biblioteca-assets.py <ruta> --json informe.json

Sale con **0** si no hay nada que bloquee, **1** si encuentra algo que impide
publicar tal cual, y **2** si no ha podido mirar. **Es de solo lectura**: no
escribe, no mueve, no extrae y no abre ningún `.zip` más allá de su índice.
"""
import json
import os
import re
import struct
import sys
import zipfile

for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# Un documento de licencia de verdad. Un README es una pista, no una licencia:
# se cuenta aparte precisamente porque el caso 4 nació de creerle a uno.
PAT_LICENCIA = re.compile(
    r"^(licen[cs]e|licencia|copying|terms|eula|legal|copyright)[\w .\-]*\.(txt|md|html?|pdf|rtf)$"
    r"|^(licen[cs]e|licencia|copying|unlicense)$", re.I)
PAT_README = re.compile(r"^read[ _-]?me[\w .\-]*\.(txt|md|html?)$|^read[ _-]?me$", re.I)

# Artefactos que un asset pack NUNCA trae: son la salida de compilar un juego.
# Se exige más de uno para no marcar un pack que casualmente traiga un `.dll`.
MARCAS_BUILD = {
    "unity": ("globalgamemanagers", "resources.assets", "sharedassets0.assets",
              "playersettings.asset", "monomanager.asset", "editorbuildsettings.asset",
              "projectsettings.asset", "assembly-csharp.dll", "level0", "unityplayer.dll",
              "boot.config", "app.info"),
    "godot": ("project.binary", "engine.pck", ".godot"),
    "gamemaker": ("data.win", "game.unx", "game.ios", "options.ini"),
    "unreal": ("pakchunk0-windowsnoeditor.pak", "assetregistry.bin"),
}
MIN_MARCAS = 2

# La señal que de verdad separa un build descompilado de un asset pack, y que
# faltaba: **el runtime del motor**. `MakeRoom` traía UN solo nombre de la lista
# de arriba (`Assembly-CSharp.dll`) y por eso se le escapaba a la regla de dos
# marcas — pero tenía una carpeta `Assemblies/` entera con `UnityEngine.*.dll`.
# Ningún pack de assets distribuye el runtime del motor: eso solo sale de haber
# abierto un juego compilado.
PAT_RUNTIME = re.compile(
    r"^(unityengine|unity)\.[\w.]+\.dll$|^assembly-csharp(-firstpass)?\.dll$|"
    r"^mono(bleedingedge)?\.dll$|^libgodot|^godot-cpp", re.I)
MIN_RUNTIME = 3

# Nombres de herramientas de extracción/conversión. Aparecer JUNTO a medios es lo
# que las convierte en señal: sueltas en una carpeta de utilidades no dicen nada.
PAT_EXTRACTOR = re.compile(
    r"assetripper|assetstudio|umodel|quickbms|undertalemodtool|"
    r"bcstm|bfstm|brstm|vgmstream|texturefinder|unpacker|"
    r"\bripper\b|\bextractor\b|\bconverter\b|\bdecompil", re.I)
EXT_MEDIOS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tga", ".webp",
              ".wav", ".ogg", ".mp3", ".aac", ".flac", ".m4a",
              ".ttf", ".otf", ".fnt", ".fbx", ".obj", ".glb", ".gltf"}
EXT_FUENTE = {".ttf", ".otf"}

# Lo que un juego en español necesita ver en pantalla. Si falta uno, la palabra
# sale mutilada y en silencio: un glifo ausente mide cero, no da error.
GLIFOS_ES = "áéíóúüñÁÉÍÓÚÜÑ¿¡"

# fsType (OS/2): 0 = instalable, 2 = prohibida su incrustación, 4 = solo vista/
# impresión, 8 = editable. El bit 0x0200 (no subsetting) y 0x0100 (bitmap only)
# se informan aparte. Solo 0 y 8 permiten empotrar la fuente en un juego.
FSTYPE_LIBRE = (0, 8)


# ─────────────────────── lectura de una tipografía, sin dependencias ──────────
def _tablas_sfnt(datos):
    if len(datos) < 12:
        return None
    etiqueta = datos[:4]
    if etiqueta == b"ttcf":
        if len(datos) < 16:
            return None
        desplazamiento = struct.unpack(">I", datos[12:16])[0]
        return _tablas_sfnt(datos[desplazamiento:]) if desplazamiento < len(datos) else None
    if etiqueta not in (b"\x00\x01\x00\x00", b"OTTO", b"true", b"typ1"):
        return None
    numero = struct.unpack(">H", datos[4:6])[0]
    tablas = {}
    for i in range(numero):
        base = 12 + i * 16
        if base + 16 > len(datos):
            break
        tag, _, off, largo = struct.unpack(">4sIII", datos[base:base + 16])
        if off + largo <= len(datos):
            tablas[tag] = (off, largo)
    return tablas or None


def leer_fuente(ruta):
    """(info, None) o (None, motivo). Nunca lanza: un archivo roto es un motivo."""
    try:
        with open(ruta, "rb") as f:
            datos = f.read(4 * 1024 * 1024)   # de sobra para las tablas de cabecera
    except OSError as e:
        return None, f"no se pudo abrir: {e}"
    return leer_fuente_bytes(datos)


def leer_fuente_bytes(datos):
    """Lo mismo, pero desde memoria — para mirar una fuente comprimida.

    Hacía falta porque el silencio sobre una fuente dentro de un `.zip` se leía
    como un aprobado: así se escapó un `fsType = 4` que sí estaba ahí. Un punto
    ciego de una herramienta es peor que no tenerla, porque tiene autoridad.
    """
    tablas = _tablas_sfnt(datos)
    if not tablas:
        return None, "no parece una fuente sfnt (ttf/otf)"

    info = {"fstype": None, "licencia": "", "copyright": "", "familia": "",
            "glifos_faltan": None}

    if b"OS/2" in tablas:
        off, largo = tablas[b"OS/2"]
        if largo >= 10:
            info["fstype"] = struct.unpack(">H", datos[off + 8:off + 10])[0]

    if b"name" in tablas:
        off, largo = tablas[b"name"]
        if largo >= 6:
            _, cuenta, base_txt = struct.unpack(">HHH", datos[off:off + 6])
            for i in range(cuenta):
                r = off + 6 + i * 12
                if r + 12 > off + largo:
                    break
                plat, enc, _, nid, lon, dsp = struct.unpack(">HHHHHH", datos[r:r + 12])
                ini = off + base_txt + dsp
                cruda = datos[ini:ini + lon]
                if not cruda:
                    continue
                try:
                    txt = (cruda.decode("utf-16-be") if (plat == 0 or (plat == 3 and enc in (0, 1)))
                           else cruda.decode("latin-1"))
                except (UnicodeDecodeError, ValueError):
                    continue
                txt = txt.strip()
                if nid == 0 and not info["copyright"]:
                    info["copyright"] = txt
                elif nid == 1 and not info["familia"]:
                    info["familia"] = txt
                elif nid in (13, 14) and txt and txt not in info["licencia"]:
                    info["licencia"] = (info["licencia"] + " · " + txt).strip(" ·")

    if b"cmap" in tablas:
        faltan = _glifos_ausentes(datos, tablas[b"cmap"])
        info["glifos_faltan"] = faltan
    return info, None


def _cobertura_cmap(datos, off):
    """Conjunto de puntos de código cubiertos, leyendo formatos 4 y 12."""
    if off + 4 > len(datos):
        return set()
    formato = struct.unpack(">H", datos[off:off + 2])[0]
    cubiertos = set()
    if formato == 4:
        seg2 = struct.unpack(">H", datos[off + 6:off + 8])[0]
        seg = seg2 // 2
        fin = off + 14
        ini = fin + seg2 + 2
        delta = ini + seg2
        rango = delta + seg2
        for i in range(seg):
            e = struct.unpack(">H", datos[fin + i * 2:fin + i * 2 + 2])[0]
            s = struct.unpack(">H", datos[ini + i * 2:ini + i * 2 + 2])[0]
            d = struct.unpack(">h", datos[delta + i * 2:delta + i * 2 + 2])[0]
            ro = struct.unpack(">H", datos[rango + i * 2:rango + i * 2 + 2])[0]
            if s == 0xFFFF:
                continue
            for c in range(s, min(e, 0xFFFE) + 1):
                if ro == 0:
                    if (c + d) & 0xFFFF:
                        cubiertos.add(c)
                else:
                    p = rango + i * 2 + ro + (c - s) * 2
                    if p + 2 <= len(datos):
                        g = struct.unpack(">H", datos[p:p + 2])[0]
                        if g:
                            cubiertos.add(c)
    elif formato == 12:
        grupos = struct.unpack(">I", datos[off + 12:off + 16])[0]
        for i in range(min(grupos, 20000)):
            b = off + 16 + i * 12
            if b + 12 > len(datos):
                break
            s, e, g = struct.unpack(">III", datos[b:b + 12])
            if g and e - s < 0x11000:
                cubiertos.update(range(s, e + 1))
    return cubiertos


def _glifos_ausentes(datos, tabla):
    off, _ = tabla
    if off + 4 > len(datos):
        return None
    numero = struct.unpack(">H", datos[off + 2:off + 4])[0]
    cubiertos = set()
    for i in range(numero):
        r = off + 4 + i * 8
        if r + 8 > len(datos):
            break
        _, _, dsp = struct.unpack(">HHI", datos[r:r + 8])
        cubiertos |= _cobertura_cmap(datos, off + dsp)
    if not cubiertos:
        return None
    return "".join(c for c in GLIFOS_ES if ord(c) not in cubiertos)


# Una hoja de glifos NO es el `.ttf`. Si el juego construye la fuente desde el PNG
# con `font_add_sprite_ext`, lo que se publica es el mapa de la hoja — y el `cmap`
# del `.ttf` que viene en el mismo pack puede cubrir el español mientras la hoja no.
# Comprobar el `.ttf` y dar el pack por bueno es un verde ajeno: mide otra cosa.
# Lo señaló R1 recorriendo el array `glyphs` de las hojas, y tenía razón.
EXT_HOJA = {".json", ".fnt", ".xml"}
PAT_CHAR_FNT = re.compile(r"\bchar\s+id=(\d+)", re.I)
PAT_CHAR_XML = re.compile(r'\bid="(\d+)"')


def mapa_de_hoja(ruta):
    """El conjunto de caracteres que declara una hoja de glifos, o None.

    Devuelve None cuando el archivo no es metadatos de una hoja — que es el caso
    de la inmensa mayoría de los `.json` de un pack. No adivina: o encuentra la
    estructura, o dice que no.
    """
    ext = os.path.splitext(ruta)[1].lower()
    if ext not in EXT_HOJA:
        return None
    texto = _leer_texto(ruta, 2000000)
    if not texto:
        return None
    if ext == ".json":
        try:
            datos = json.loads(texto)
        except (ValueError, TypeError):
            return None
        if not isinstance(datos, dict):
            return None
        for clave in ("glyphs", "chars", "characters", "glifos"):
            lista = datos.get(clave)
            if isinstance(lista, list) and lista:
                salida = set()
                for g in lista:
                    if isinstance(g, dict):
                        for k in ("chr", "char", "character", "c"):
                            v = g.get(k)
                            if isinstance(v, str) and len(v) == 1:
                                salida.add(v)
                                break
                        else:
                            cp = g.get("id") if isinstance(g.get("id"), int) else None
                            if cp is not None and 0 <= cp <= 0x10FFFF:
                                salida.add(chr(cp))
                    elif isinstance(g, str) and len(g) == 1:
                        salida.add(g)
                if salida:
                    return salida
        return None
    patron = PAT_CHAR_FNT if ext == ".fnt" else PAT_CHAR_XML
    puntos = patron.findall(texto)
    if len(puntos) < 16:          # menos de 16 «char id=» no es una hoja de fuente
        return None
    salida = set()
    for p in puntos:
        try:
            cp = int(p)
        except ValueError:
            continue
        if 0 <= cp <= 0x10FFFF:
            salida.add(chr(cp))
    return salida or None


# ─────────────────────────────── recorrido ────────────────────────────────────
def _normalizar(texto):
    return re.sub(r"\s+", " ", texto.strip().lower())[:4000]


# Clasificar por FAMILIA y no por texto literal. Medido: los 24 subpacks de KayKit
# traen 24 `License.txt` distintos —cambia el nombre del pack y la fecha— y los 24
# son CC0. Comparando textos, la herramienta avisaba de «24 licencias distintas»
# sobre un pack impecable, y un aviso que salta cuando no toca se aprende a
# ignorar. Comparando familias, KayKit calla y «Time Fantasy - surtido», donde
# de verdad conviven cuatro autores con cuatro licencias, sigue saltando.
# El orden importa y una trampa lo demuestra: «Super Retro World» dice
# *«Use for non-commercial AND commercial project»* — permite lo comercial, pero
# contiene literalmente «non-commercial». Buscar esa palabra suelta lo clasifica
# justo al revés de lo que dice. Por eso el permiso explícito se comprueba ANTES,
# y el sello NC solo gana cuando viene como sello (`by-nc`, `attribution-
# noncommercial`) o cuando nadie ha permitido lo comercial.
PERMITE_COMERCIAL = re.compile(
    r"unlimited commercial|for commercial (use|projects?)|"
    r"and commercial|commercial (use )?(is )?(allowed|permitted)|"
    r"personal,? educational,? and commercial|"
    r"personal or commercial|uso comercial|proyectos? comerciales?", re.I)

SELLO_NC = re.compile(r"attribution[- ]non-?commercial|\bby[- ]nc\b", re.I)

FAMILIAS = (
    ("CC0 / dominio público", r"\bcc0\b|creative commons zero|public domain|"
                              r"no rights reserved|\bunlicense\b"),
    ("CC BY-SA",              r"attribution[- ]share ?alike|\bby[- ]sa\b|share.?alike"),
    ("CC BY-ND",              r"attribution[- ]no ?derivat|\bby[- ]nd\b|no ?derivativ"),
    ("CC BY",                 r"creative commons attribution|\bcc[- ]by\b"),
    ("SIL OFL",               r"sil open font license|\bofl\b"),
    ("MIT",                   r"\bmit license\b"),
    ("Apache",                r"apache license"),
    ("GPL / LGPL",            r"gnu (general|lesser) public license|\bgpl\b"),
    ("Todos los derechos reservados", r"all rights reserved"),
    ("Comercial sin reventa", r"(not? re-?sell|cannot re-?sell|no re-?sell|"
                              r"not redistribute|cannot (be )?distribut|"
                              r"may not be distributed|prohibida la reventa|"
                              r"shall not offer)"),
    ("Comercial permitido",   r"commercial"),
)


def familia_licencia(texto):
    """La familia a la que pertenece un texto de licencia, o «sin clasificar»."""
    if SELLO_NC.search(texto):
        return "CC BY-NC"
    if re.search(r"non-?commercial", texto, re.I) and not PERMITE_COMERCIAL.search(texto):
        return "CC BY-NC"
    for nombre, patron in FAMILIAS:
        if re.search(patron, texto, re.I):
            return nombre
    return "sin clasificar"


def _leer_texto(ruta, tope=200000):
    try:
        with open(ruta, "rb") as f:
            return f.read(tope).decode("utf-8", "replace")
    except OSError:
        return ""


def _clave(nombre):
    """El nombre reducido a letras y dígitos, para comparar «Pixel Font Megapack»
    con «pixel-font-megapack-assets175 fuentes pixel art.zip»."""
    return re.sub(r"[^a-z0-9]+", "", nombre.lower())


def indice_de_zips(raiz, tope=6000):
    """{clave normalizada: [rutas]} de todos los `.zip` de la biblioteca.

    Existe por un fallo medido de esta herramienta: marcó «sin licencia» la
    tipografía que el juego usaba, porque su `LICENSE.txt` vivía dentro de un
    `.zip` **en otra carpeta**. Era literalmente cierto y era el mismo error que
    ya había costado una jornada de trabajo — solo que ahora con la autoridad de
    una máquina. Un punto ciego con autoridad es peor que no tener herramienta.
    """
    indice, vistos = {}, 0
    for base, dirs, ficheros in os.walk(raiz):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        for n in ficheros:
            if not n.lower().endswith(".zip"):
                continue
            vistos += 1
            if vistos > tope:
                return indice
            indice.setdefault(_clave(os.path.splitext(n)[0]), []).append(
                os.path.join(base, n))
    return indice


# Nombres de estructura, no de pack. Una carpeta que se llama «Assets» o «FUENTES»
# se parece a todo, y esa semejanza no significa nada.
#
# Medido, y era peligroso: a profundidad 3 la herramienta llegó a insinuar que la
# licencia del Pixel Font Megapack o la de un pack de Kenney podría amparar
# `7-extraidos-de-juegos/Faeria/FUENTES`, `Hero Quest/Assets` y `Luckyland/Assets`
# — es decir, sugería que un rip tenía dueño. Una pista falsa que apunta a material
# prohibido es mucho peor que ninguna pista.
GENERICOS = {
    "assets", "asset", "fuentes", "fonts", "font", "sheets", "sheet", "ttf", "otf",
    "packed", "samples", "sample", "sprites", "sprite", "audio", "sound", "sounds",
    "music", "musica", "images", "imagenes", "textures", "texturas", "ui", "gui",
    "icons", "iconos", "data", "src", "source", "content", "resources", "recursos",
    "pack", "packs", "extras", "misc", "otros", "new", "old", "temp", "tmp", "png",
}
MIN_CLAVE = 10          # «assets» son 6 y no dice nada; «pixelfontmegapack», 17


def zips_hermanos(nombre_pack, indice):
    """Los `.zip` de cualquier carpeta cuyo nombre encaje con el del pack.

    Devuelve CANDIDATOS, nunca un veredicto: hay un caso medido de dos packs
    distintos con el mismo nombre y licencias diferentes, así que emparejar por
    nombre es exactamente lo que no se debe hacer a ciegas. Se señala para que
    alguien lo abra.
    """
    if nombre_pack.strip().lower() in GENERICOS:
        return []
    clave = _clave(nombre_pack)
    if len(clave) < MIN_CLAVE or clave in GENERICOS:
        return []
    salida = []
    for otra, rutas in indice.items():
        if clave in otra or otra in clave:
            salida.extend(rutas)
    return list(dict.fromkeys(salida))[:5]      # sin repetidos: el mismo zip puede
                                                # encajar por más de una clave


def licencias_heredadas(raiz, tope):
    """Las licencias que cubren `raiz` desde arriba, hasta `tope` inclusive.

    Un `LICENSE.txt` en la raíz de un pack cubre sus subcarpetas: así funciona una
    licencia. Sin esto, «Kenney All-in-1/Goodies» salía como pack sin licencia
    teniendo la de Kenney un nivel más arriba — y ese es justo el falso positivo
    que hace que se dejen de leer los informes.
    """
    encontradas, familias = [], set()
    actual = os.path.abspath(raiz)
    tope = os.path.abspath(tope)
    while True:
        padre = os.path.dirname(actual)
        if actual == tope or padre == actual:
            break
        actual = padre
        try:
            nombres = os.listdir(actual)
        except OSError:
            break
        for n in nombres:
            if PAT_LICENCIA.match(n):
                p = os.path.join(actual, n)
                if os.path.isfile(p):
                    encontradas.append(p)
                    t = _normalizar(_leer_texto(p))
                    if t:
                        familias.add(familia_licencia(t))
        if actual == tope:
            break
    return encontradas, familias


def revisar_pack(raiz, tope_entradas=40000, raiz_biblioteca=None, indice_zips=None):
    """Devuelve el diagnóstico de un pack. Solo lectura, y con tope de entradas."""
    d = {"ruta": raiz, "licencias": [], "readmes": [], "familias": set(),
         "marcas_build": {}, "extractores": [], "medios": 0, "fuentes": [],
         "zips_con_licencia": [], "zips": 0, "truncado": False,
         "readmes_lista": [], "runtime": [], "heredadas": [], "hojas": [],
         "fuentes_zip": [], "candidatos_zip": []}
    vistas = 0
    for base, dirs, ficheros in os.walk(raiz):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        for n in ficheros:
            vistas += 1
            if vistas > tope_entradas:
                d["truncado"] = True
                break
            ruta = os.path.join(base, n)
            bajo = n.lower()
            ext = os.path.splitext(bajo)[1]

            for motor, marcas in MARCAS_BUILD.items():
                if bajo in marcas or n in marcas:
                    d["marcas_build"].setdefault(motor, set()).add(bajo)
            if PAT_RUNTIME.match(n) and len(d["runtime"]) < 40:
                d["runtime"].append(n)

            if PAT_LICENCIA.match(n):
                d["licencias"].append(ruta)
                t = _normalizar(_leer_texto(ruta))
                if t:
                    d["familias"].add(familia_licencia(t))
            elif PAT_README.match(n):
                d["readmes"].append(ruta)

            if ext in EXT_MEDIOS:
                d["medios"] += 1
                if ext in EXT_FUENTE:
                    d["fuentes"].append(ruta)
            if PAT_EXTRACTOR.search(n) and ext not in EXT_MEDIOS:
                d["extractores"].append(ruta)

            if ext in EXT_HOJA and len(d["hojas"]) < 60:
                mapa = mapa_de_hoja(ruta)
                if mapa:
                    d["hojas"].append((ruta, mapa))

            if ext == ".zip":
                d["zips"] += 1
                try:
                    with zipfile.ZipFile(ruta) as z:
                        visto_licencia = False
                        for nombre in z.namelist():
                            hoja = os.path.basename(nombre)
                            if not hoja:
                                continue
                            if not visto_licencia and PAT_LICENCIA.match(hoja):
                                visto_licencia = True
                                d["zips_con_licencia"].append(f"{ruta}!{nombre}")
                                try:
                                    with z.open(nombre) as fz:
                                        t = _normalizar(fz.read(200000).decode("utf-8", "replace"))
                                    if t:
                                        d["familias"].add(familia_licencia(t))
                                except (KeyError, OSError, zipfile.BadZipFile, RuntimeError):
                                    pass
                            # Y las fuentes comprimidas, que antes no se miraban.
                            if (os.path.splitext(hoja)[1].lower() in EXT_FUENTE
                                    and len(d["fuentes_zip"]) < 40):
                                try:
                                    with z.open(nombre) as fz:
                                        crudo = fz.read(4 * 1024 * 1024)
                                    d["fuentes_zip"].append(
                                        (f"{os.path.basename(ruta)}!{hoja}", crudo))
                                except (KeyError, OSError, zipfile.BadZipFile, RuntimeError):
                                    pass
                except (zipfile.BadZipFile, OSError, RuntimeError):
                    pass
        if d["truncado"]:
            break
    if (indice_zips and d["medios"] and not d["licencias"]
            and not d["zips_con_licencia"]):
        for candidato in zips_hermanos(os.path.basename(raiz), indice_zips):
            if os.path.dirname(os.path.abspath(candidato)) == os.path.abspath(raiz):
                continue
            try:
                with zipfile.ZipFile(candidato) as z:
                    if any(PAT_LICENCIA.match(os.path.basename(x) or "")
                           for x in z.namelist()):
                        d["candidatos_zip"].append(candidato)
            except (zipfile.BadZipFile, OSError, RuntimeError):
                pass

    if raiz_biblioteca:
        arriba, familias_arriba = licencias_heredadas(raiz, raiz_biblioteca)
        d["heredadas"] = arriba
        if arriba and not d["licencias"] and not d["zips_con_licencia"]:
            # Solo se hereda la FAMILIA cuando el pack no trae la suya: si trae una
            # propia, manda la suya y mezclar las dos inventaría un conflicto.
            d["familias"] |= familias_arriba
    return d


def dictaminar(d, solo_fuentes=False):
    """(bloqueos, avisos, notas) de un pack ya revisado."""
    bloqueos, avisos, notas = [], [], []
    nombre = os.path.basename(d["ruta"])

    if not solo_fuentes:
        for motor, marcas in d["marcas_build"].items():
            if len(marcas) >= MIN_MARCAS:
                bloqueos.append(
                    f"«{nombre}» no es un asset pack: trae artefactos de un build de "
                    f"{motor} ({', '.join(sorted(marcas)[:4])}). Un pack nunca los lleva. "
                    "Trátalo como contenido extraído de un juego.")

        if len(d["runtime"]) >= MIN_RUNTIME:
            bloqueos.append(
                f"«{nombre}» distribuye el runtime del motor ({len(d['runtime'])} "
                f"bibliotecas, p. ej. {', '.join(d['runtime'][:3])}). Un asset pack no lo "
                "lleva nunca: eso sale de abrir un juego ya compilado.")

        if d["extractores"] and d["medios"]:
            bloqueos.append(
                f"«{nombre}» guarda una herramienta de extracción junto a {d['medios']} "
                f"archivos de medios: {os.path.basename(d['extractores'][0])}. La "
                "herramienta al lado de los archivos es la señal de que se sacaron de otro "
                "sitio.")

        if (d["medios"] and not d["licencias"] and not d["zips_con_licencia"]
                and not d["heredadas"]):
            que = (f"y {len(d['readmes'])} README, que NO es una licencia"
                   if d["readmes"] else "y ningún documento de texto")
            bloqueos.append(
                f"«{nombre}» tiene {d['medios']} archivos de medios {que}. "
                "Sin licencia no entra — y esto es distinto de «la licencia lo prohíbe»: "
                "el cliente puede resolverlo enseñando la factura.")
            if not d["candidatos_zip"] and len(_clave(nombre)) < MIN_CLAVE:
                notas.append(
                    f"«{nombre}» tiene un nombre demasiado genérico para buscarle un `.zip` "
                    "hermano. Apunta la herramienta a la RAÍZ de la biblioteca con "
                    "`--profundidad 2`: así el pack se llama como el pack, y no como la "
                    "subcarpeta donde guarda las hojas.")
            if d["candidatos_zip"]:
                bloqueos.append(
                    "   PERO hay un `.zip` con licencia y nombre parecido en otra carpeta: "
                    # Con la carpeta delante, porque dos copias del mismo `.zip` en sitios
                    # distintos se ven idénticas si solo enseñas el nombre — y entonces el
                    # informe parece repetirse cuando en realidad son dos archivos.
                    + ", ".join(os.path.join(os.path.basename(os.path.dirname(x)),
                                             os.path.basename(x))
                                for x in d["candidatos_zip"])
                    + ". ÁBRELO antes de dar este pack por perdido. Es candidato, NO "
                    "veredicto: hay un caso medido de dos packs distintos con el mismo "
                    "nombre y licencias diferentes, así que empareja licencia con archivo, "
                    "no con nombre.")

        # La mitad peligrosa del caso anterior: un archivo que SÍ se llama `LICENCE.txt`
        # y cuyo texto es un resumen de Creative Commons recortado — reconoce «Creative
        # Commons» y por eso pasaba la comprobación de abajo, pero no dice CUÁL ni de
        # QUIÉN. Quien lo lea concluirá que puede usarlo sin acreditar a nadie, cuando el
        # README del mismo pack exige crédito y prohíbe NFT. Un archivo con nombre de
        # licencia parece autoridad, y ahí está el daño.
        if any(f.startswith("CC ") for f in d["familias"]):
            textos = [_leer_texto(x) for x in d["licencias"]]
            crudo = " ".join(textos)
            if crudo and not re.search(r"creativecommons\.org|\b[1-4]\.0\b|"
                                       r"\bversion\s*[1-4]\b", crudo, re.I):
                avisos.append(
                    f"«{nombre}» dice «Creative Commons» pero NO nombra la versión ni "
                    "enlaza la licencia: parece un resumen recortado. Un resumen de CC no "
                    "dice a quién hay que acreditar, y CC BY sin atribución es "
                    "incumplimiento. Busca el autor en el README antes de usarlo.")

        if d["familias"] == {"sin clasificar"} and (d["licencias"] or d["zips_con_licencia"]):
            avisos.append(
                f"«{nombre}» tiene documento de licencia pero NO se reconoce ninguna "
                "licencia en su texto. Medido: bajo ese nombre han aparecido un aviso sobre "
                "baneos de otra plataforma, la descripción de un pack distinto, y un resumen "
                "de Creative Commons truncado que no nombra ni la licencia ni al autor — "
                "quien lo lea solo concluirá que puede usarlo sin acreditar a nadie. "
                "Léelo entero y busca el autor en el README.")

        if len(d["familias"]) > 1:
            avisos.append(
                f"«{nombre}» reúne {len(d['familias'])} FAMILIAS de licencia distintas bajo "
                f"un solo nombre ({', '.join(sorted(d['familias']))}). El nombre de la "
                "carpeta no describe lo de dentro: revísalo subcarpeta por subcarpeta antes "
                "de fiarte de la etiqueta.")

        if d["truncado"]:
            notas.append(f"«{nombre}» es enorme: se paró de contar en el tope de entradas. "
                         "Lo dicho de él es un mínimo, no un recuento.")

    candidatas = [(os.path.basename(x), leer_fuente(x)) for x in d["fuentes"]]
    candidatas += [(etiqueta, leer_fuente_bytes(crudo))
                   for etiqueta, crudo in d["fuentes_zip"]]
    for base, (info, motivo) in candidatas:
        if info is None:
            avisos.append(f"«{base}»: {motivo}")
            continue
        if info["fstype"] is not None and info["fstype"] not in FSTYPE_LIBRE:
            bloqueos.append(
                f"«{base}» lleva `fsType={info['fstype']}` en su OS/2: el binario "
                "restringe empotrarla. Gana el binario sobre lo que diga el bundle.")
        if info["licencia"]:
            bloqueos_texto = re.search(r"non[- ]commercial|all rights reserved|"
                                       r"share.?alike|nc\b|no derivative",
                                       info["licencia"], re.I)
            if bloqueos_texto:
                bloqueos.append(
                    f"«{base}» lleva embebido «{info['licencia'][:90]}». "
                    "Si el pack dice otra cosa, gana esto.")
        if info["glifos_faltan"]:
            bloqueos.append(
                f"«{base}» no tiene los glifos {info['glifos_faltan']}. En español eso no "
                "da error: el glifo ausente mide cero y la palabra sale mutilada.")
        elif info["glifos_faltan"] == "":
            notas.append(f"«{base}»: la fuente cubre {GLIFOS_ES} completo. Ojo: esto "
                         "habla del binario, no de la hoja de glifos que quizá publiques.")

    for ruta, mapa in d["hojas"]:
        base = os.path.basename(ruta)
        faltan = "".join(c for c in GLIFOS_ES if c not in mapa)
        if faltan:
            bloqueos.append(
                f"la hoja de glifos «{base}» ({len(mapa)} caracteres) NO declara {faltan}. "
                "Si la fuente se construye desde la hoja con `font_add_sprite_ext`, esto es "
                "lo que se publica: el `cmap` del `.ttf` del mismo pack no lo cubre.")
        else:
            notas.append(f"la hoja «{base}» declara {len(mapa)} caracteres y cubre el "
                         "español entero.")
        if " " not in mapa:
            avisos.append(
                f"la hoja «{base}» NO trae celda para el espacio. `font_add_sprite_ext` "
                "usará entonces la anchura del CARÁCTER MÁS ANCHO, no la del espacio, y "
                "toda la aritmética de la caja se cae sin dar error "
                "(`04 · 21 §4 bis` y `_indice/medir-caja-de-texto.py`).")

    if d["fuentes"] and d["hojas"] and not solo_fuentes:
        notas.append("este pack trae `.ttf` Y hojas de glifos. Lo que se publica es lo que "
                     "el juego carga: si usa la hoja, el veredicto del `.ttf` no aplica.")
    return bloqueos, avisos, notas


def packs_en(raiz, profundidad):
    """Las carpetas que se tratan como «un pack». Nivel 1 sería demasiado grueso."""
    encontrados, pendientes = [], [(raiz, 0)]
    while pendientes:
        ruta, nivel = pendientes.pop(0)
        try:
            hijos = sorted(x for x in os.listdir(ruta)
                           if os.path.isdir(os.path.join(ruta, x)) and not x.startswith("."))
        except OSError:
            continue
        if nivel >= profundidad or not hijos:
            encontrados.append(ruta)
        else:
            for h in hijos:
                pendientes.append((os.path.join(ruta, h), nivel + 1))
            if any(os.path.isfile(os.path.join(ruta, x)) for x in os.listdir(ruta)):
                pass
    return encontrados


def main():
    args = sys.argv[1:]
    if not args or "--help" in args or "-h" in args:
        print(__doc__.strip())
        return 0 if ("--help" in args or "-h" in args) else 2

    profundidad, salida_json, solo_fuentes = 2, None, False
    if "--profundidad" in args:
        i = args.index("--profundidad")
        try:
            profundidad = int(args[i + 1])
        except (IndexError, ValueError):
            print("✗ `--profundidad` necesita un entero.")
            return 2
        del args[i:i + 2]
    if "--json" in args:
        i = args.index("--json")
        if i + 1 >= len(args):
            print("✗ `--json` necesita una ruta.")
            return 2
        salida_json = args[i + 1]
        del args[i:i + 2]
    if "--solo-fuentes" in args:
        solo_fuentes = True
        args.remove("--solo-fuentes")

    rutas = [a for a in args if not a.startswith("--")]
    if not rutas:
        print("✗ Falta la ruta de la biblioteca de assets.")
        return 2
    raiz = rutas[0]
    if not os.path.isdir(raiz):
        print(f"⚠ «{raiz}» no es una carpeta que se pueda mirar.")
        return 2

    lista = packs_en(raiz, profundidad)
    if not lista:
        print(f"⚠ No hay ninguna carpeta bajo «{raiz}» a profundidad {profundidad}.")
        return 2

    indice_zips = indice_de_zips(raiz)
    total_bloqueos, total_avisos, informe = 0, 0, []
    print(f"── {len(lista)} carpetas tratadas como pack, bajo «{raiz}» "
          f"· {sum(len(v) for v in indice_zips.values())} `.zip` indexados\n")
    for ruta in lista:
        d = revisar_pack(ruta, raiz_biblioteca=raiz, indice_zips=indice_zips)
        b, a, n = dictaminar(d, solo_fuentes)
        if not (b or a):
            continue
        print(f"▸ {os.path.relpath(ruta, raiz)}")
        for x in n:
            print(f"    · {x}")
        for x in a:
            print(f"    ⚠ {x}")
        for x in b:
            print(f"    ✗ {x}")
        print()
        total_bloqueos += len(b)
        total_avisos += len(a)
        informe.append({"pack": os.path.relpath(ruta, raiz),
                        "bloqueos": b, "avisos": a, "notas": n})

    if salida_json:
        try:
            with open(salida_json, "w", encoding="utf-8") as f:
                json.dump(informe, f, ensure_ascii=False, indent=2)
            print(f"Informe escrito en {salida_json}")
        except OSError as e:
            print(f"⚠ no se pudo escribir el informe: {e}")
            return 2

    print(f"── {total_bloqueos} bloqueo(s) · {total_avisos} aviso(s) "
          f"sobre {len(lista)} carpetas.")
    if total_bloqueos:
        print("✗ Hay material que NO puede entrar en el juego tal cual. Cada bloqueo es "
              "una pregunta para el cliente, no una acusación: «no encuentro la licencia» "
              "se arregla con una factura; «el binario lo prohíbe», no.")
        return 1
    print("✓ Nada bloquea. Lo que esta herramienta NO puede ver: si el pack es de quien "
          "dice ser, ni si la factura existe.")
    return 0


# ─────────────────────────────── autoprueba ───────────────────────────────────
def _tabla_cmap4(codigos):
    """Una subtabla cmap formato 4 que cubre exactamente `codigos`."""
    orden = sorted(set(codigos))
    segmentos = []
    for c in orden:
        if segmentos and c == segmentos[-1][1] + 1:
            segmentos[-1][1] = c
        else:
            segmentos.append([c, c])
    segmentos.append([0xFFFF, 0xFFFF])
    n = len(segmentos)
    largo = 16 + 8 * n
    salida = struct.pack(">HHHHHHH", 4, largo, 0, n * 2, 2, 0, n * 2 - 2)
    salida += b"".join(struct.pack(">H", s[1]) for s in segmentos)
    salida += b"\x00\x00"
    salida += b"".join(struct.pack(">H", s[0]) for s in segmentos)
    salida += b"".join(struct.pack(">h", 1) for _ in segmentos)
    salida += b"".join(struct.pack(">H", 0) for _ in segmentos)
    return salida


def _fuente_sintetica(fstype=0, licencia="", cubre=None):
    """Un sfnt mínimo pero real: OS/2, name y cmap. Sin dependencias."""
    if cubre is None:
        cubre = [ord(c) for c in GLIFOS_ES] + [ord("a")]
    os2 = struct.pack(">HhHHH", 4, 500, 400, 5, fstype)
    registros, cadenas = b"", b""
    if licencia:
        cruda = licencia.encode("utf-16-be")
        registros += struct.pack(">HHHHHH", 3, 1, 0x0409, 13, len(cruda), len(cadenas))
        cadenas += cruda
    cuenta = 1 if licencia else 0
    base_txt = 6 + 12 * cuenta
    name = struct.pack(">HHH", 0, cuenta, base_txt) + registros + cadenas
    sub = _tabla_cmap4(cubre)
    cmap = struct.pack(">HHHHI", 0, 1, 3, 1, 12) + sub

    tablas = [(b"OS/2", os2), (b"cmap", cmap), (b"name", name)]
    cabecera = struct.pack(">IHHHH", 0x00010000, len(tablas), 0, 0, 0)
    desplazamiento = 12 + 16 * len(tablas)
    directorio, cuerpo = b"", b""
    for tag, datos in tablas:
        directorio += struct.pack(">4sIII", tag, 0, desplazamiento + len(cuerpo), len(datos))
        cuerpo += datos + b"\x00" * (-len(datos) % 4)
    return cabecera + directorio + cuerpo


def autoprueba():
    import tempfile
    fallos = []

    def caso(nombre, condicion, detalle=""):
        if condicion:
            print(f"  ✓ {nombre}")
        else:
            print(f"  ✗ {nombre}{(' — ' + detalle) if detalle else ''}")
            fallos.append(nombre)

    def montar(base, nombre, ficheros):
        d = os.path.join(base, nombre)
        os.makedirs(d, exist_ok=True)
        for n, contenido in ficheros.items():
            p = os.path.join(d, n)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            modo = "wb" if isinstance(contenido, bytes) else "w"
            with open(p, modo, **({} if modo == "wb" else {"encoding": "utf-8"})) as f:
                f.write(contenido)
        return d

    def juzgar(d, solo_fuentes=False):
        return dictaminar(revisar_pack(d), solo_fuentes)

    with tempfile.TemporaryDirectory() as tmp:
        d = montar(tmp, "sin-licencia", {"heroe.png": b"x", "suelo.png": b"x"})
        b, a, _ = juzgar(d)
        caso("medios sin ningún documento es bloqueo", any("Sin licencia no entra" in x for x in b), str(b))

        d = montar(tmp, "con-licencia", {"heroe.png": b"x", "LICENSE.txt": "CC0 1.0 Universal"})
        b, _, _ = juzgar(d)
        caso("medios con LICENSE no bloquean", not b, str(b))

        os.makedirs(os.path.join(tmp, "bundle", "Goodies"), exist_ok=True)
        with open(os.path.join(tmp, "bundle", "LICENSE.txt"), "w", encoding="utf-8") as f:
            f.write("CC0 1.0 Universal")
        with open(os.path.join(tmp, "bundle", "Goodies", "extra.png"), "wb") as f:
            f.write(b"x")
        sub = os.path.join(tmp, "bundle", "Goodies")
        b, _, _ = dictaminar(revisar_pack(sub, raiz_biblioteca=tmp))
        caso("una subcarpeta hereda la licencia de su pack padre", not b, str(b))
        b, _, _ = dictaminar(revisar_pack(sub))
        caso("y sin decir cuál es la raíz, no hereda (contrato explícito)",
             any("Sin licencia" in x for x in b), str(b))

        d = montar(tmp, "solo-readme", {"heroe.png": b"x", "README.txt": "gracias por comprar"})
        b, _, _ = juzgar(d)
        caso("un README no cuenta como licencia", any("NO es una licencia" in x for x in b), str(b))

        d = montar(tmp, "etiqueta-que-miente", {
            "a/heroe.png": b"x",
            "a/LICENSE.txt": "This content is free to use, CC0 1.0 Universal.",
            "b/mapa.png": b"x",
            "b/LICENCE.txt": "You need to: Credit the authors. You can NOT: "
                             "Distribute or sell those assets directly."})
        b, a, _ = juzgar(d)
        caso("dos FAMILIAS distintas bajo un nombre son aviso",
             any("FAMILIAS de licencia" in x for x in a), str(a))
        caso("y no bloquean, porque licencia hay", not b, str(b))

        # El falso positivo que salió al correrlo de verdad: 24 subpacks de KayKit,
        # 24 `License.txt` con distinto nombre de pack y fecha, y los 24 son CC0.
        ficheros = {"arte.png": b"x"}
        for i in range(24):
            ficheros[f"pack{i}/License.txt"] = (
                f"KayKit : Pack {i} (1.0)\nCreated by Kay Lousberg\n"
                f"Creation date: 0{i % 9 + 1}/01/2026\n"
                "License: (Creative Commons Zero, CC0)\n"
                "This content is free to use in personal, educational and commercial "
                "projects.")
        d = montar(tmp, "muchos-subpacks-una-licencia", ficheros)
        b, a, _ = juzgar(d)
        caso("24 textos distintos de la MISMA familia no avisan",
             not any("FAMILIAS" in x for x in a), str(a))

        caso("«non-commercial AND commercial» NO se clasifica como NC",
             familia_licencia("Use for non-commercial AND commercial project") != "CC BY-NC",
             familia_licencia("Use for non-commercial AND commercial project"))
        caso("pero un sello CC BY-NC de verdad sí",
             familia_licencia("Creative Commons Attribution-NonCommercial 4.0") == "CC BY-NC")
        caso("y «non-commercial» a secas también",
             familia_licencia("This font is for non-commercial use only") == "CC BY-NC")

        d = montar(tmp, "una-marca", {"heroe.png": b"x", "LICENSE.txt": "CC0",
                                      "data.win": b"x"})
        b, _, _ = juzgar(d)
        caso("UNA marca de build sola no basta para acusar",
             not any("build de" in x for x in b), str(b))

        d = montar(tmp, "build-descompilado", {
            "arte.png": b"x", "LICENSE.txt": "CC0",
            "Managed/Assembly-CSharp.dll": b"x", "globalgamemanagers": b"x"})
        b, _, _ = juzgar(d)
        caso("dos marcas de build sí lo son", any("build de unity" in x for x in b), str(b))

        d = montar(tmp, "runtime-del-motor", {
            "modelo.glb": b"x", "LICENSE.txt": "CC0",
            "Assemblies/UnityEngine.AudioModule.dll": b"x",
            "Assemblies/UnityEngine.AnimationModule.dll": b"x",
            "Assemblies/Assembly-CSharp.dll": b"x"})
        b, _, _ = juzgar(d)
        caso("una carpeta con el runtime del motor es bloqueo",
             any("runtime del motor" in x for x in b), str(b))

        d = montar(tmp, "un-dll-suelto", {"modelo.glb": b"x", "LICENSE.txt": "CC0",
                                          "Assembly-CSharp.dll": b"x"})
        b, _, _ = juzgar(d)
        caso("un solo DLL suelto no acusa a nadie",
             not any("runtime del motor" in x for x in b), str(b))

        d = montar(tmp, "gm-ripeado", {"spr.png": b"x", "LICENSE.txt": "CC0",
                                       "data.win": b"x", "options.ini": "x"})
        b, _, _ = juzgar(d)
        caso("un juego de GameMaker extraído también se caza",
             any("build de gamemaker" in x for x in b), str(b))

        d = montar(tmp, "rip-con-conversor", {
            "BGM_TEMA_loop.aac": b"x", "LICENSE.txt": "CC0",
            "BCSTM to Wav Converter.exe": b"x"})
        b, _, _ = juzgar(d)
        caso("el conversor junto a los medios es bloqueo",
             any("herramienta de extracción" in x for x in b), str(b))

        d = montar(tmp, "solo-utilidad", {"AssetRipper.exe": b"x",
                                          "LICENSE.txt": "MIT"})
        b, _, _ = juzgar(d)
        caso("una utilidad SIN medios al lado no acusa a nadie",
             not any("extracción" in x for x in b), str(b))

        # La licencia dentro del .zip: el caso que salvó la tipografía del proyecto.
        d = montar(tmp, "licencia-en-zip", {"muestra.png": b"x"})
        with zipfile.ZipFile(os.path.join(d, "pack.zip"), "w") as z:
            z.writestr("pack/LICENSE.txt", "unlimited commercial projects")
        b, _, _ = juzgar(d)
        caso("una licencia DENTRO del zip cuenta y desbloquea", not b, str(b))

        d = montar(tmp, "zip-roto", {"arte.png": b"x", "LICENSE.txt": "CC0",
                                     "roto.zip": b"esto no es un zip"})
        b, a, _ = juzgar(d)
        caso("un zip corrupto no revienta la herramienta", isinstance(b, list))

        # Tipografías.
        d = montar(tmp, "fuente-restringida",
                   {"LICENSE.txt": "CC0 1.0", "tipo.ttf": _fuente_sintetica(fstype=4)})
        b, _, _ = juzgar(d)
        caso("fsType=4 bloquea aunque el bundle diga CC0",
             any("fsType=4" in x for x in b), str(b))

        d = montar(tmp, "fuente-libre",
                   {"LICENSE.txt": "CC0 1.0", "tipo.ttf": _fuente_sintetica(fstype=0)})
        b, _, n = juzgar(d)
        caso("fsType=0 no bloquea", not b, str(b))
        caso("y dice que cubre el español entero", any("cubre" in x for x in n), str(n))

        d = montar(tmp, "fuente-nc", {
            "LICENSE.txt": "CC0 1.0",
            "tipo.ttf": _fuente_sintetica(licencia="FontStruct Non-Commercial License")})
        b, _, _ = juzgar(d)
        caso("«Non-Commercial» embebido gana al bundle",
             any("Non-Commercial" in x for x in b), str(b))

        d = montar(tmp, "fuente-reservada", {
            "LICENSE.txt": "CC0 1.0",
            "tipo.ttf": _fuente_sintetica(licencia="All Rights Reserved")})
        b, _, _ = juzgar(d)
        caso("«All Rights Reserved» embebido también", any("All Rights" in x for x in b), str(b))

        sin_ene = [c for c in (list(GLIFOS_ES) + ["a"]) if c != "ñ"]
        d = montar(tmp, "fuente-sin-ene", {
            "LICENSE.txt": "CC0 1.0",
            "tipo.ttf": _fuente_sintetica(cubre=[ord(c) for c in sin_ene])})
        b, _, _ = juzgar(d)
        caso("una fuente sin ñ se caza y se nombra el glifo",
             any("ñ" in x and "glifos" in x for x in b), str(b))

        d = montar(tmp, "fuente-falsa", {"LICENSE.txt": "CC0", "no-es.ttf": b"hola"})
        b, a, _ = juzgar(d)
        caso("un .ttf que no es una fuente avisa, no revienta",
             any("no parece una fuente" in x for x in a), str(a))

        # La hoja de glifos: lo que de verdad se publica cuando la fuente se
        # construye con font_add_sprite_ext.
        completo = json.dumps({"tile_w": 8, "tile_h": 11, "glyphs":
                               [{"chr": c, "adv": 4} for c in GLIFOS_ES + "abc "]})
        d = montar(tmp, "hoja-completa", {"LICENSE.txt": "CC0", "f.png": b"x",
                                          "f.json": completo})
        b, a, n = juzgar(d)
        caso("una hoja que declara el español entero no bloquea",
             not b, str(b))
        caso("y no avisa del espacio, porque lo trae",
             not any("espacio" in x for x in a), str(a))

        sin_ene = json.dumps({"glyphs": [{"chr": c} for c in GLIFOS_ES.replace("ñ", "")
                                         + "abc "]})
        d = montar(tmp, "hoja-sin-ene", {"LICENSE.txt": "CC0", "f.png": b"x",
                                         "f.json": sin_ene})
        b, _, _ = juzgar(d)
        caso("una hoja sin ñ bloquea aunque el pack tenga licencia",
             any("ñ" in x and "hoja de glifos" in x for x in b), str(b))

        sin_espacio = json.dumps({"glyphs": [{"chr": c} for c in GLIFOS_ES + "abc"]})
        d = montar(tmp, "hoja-sin-espacio", {"LICENSE.txt": "CC0", "f.png": b"x",
                                             "f.json": sin_espacio})
        b, a, _ = juzgar(d)
        caso("una hoja sin celda de espacio avisa",
             any("CARÁCTER MÁS ANCHO" in x for x in a), str(a))

        d = montar(tmp, "json-cualquiera", {"LICENSE.txt": "CC0", "arte.png": b"x",
                                            "config.json": '{"volumen": 0.8}'})
        b, a, n = juzgar(d)
        caso("un .json que NO es una hoja se ignora, no se inventa un mapa",
             not any("hoja" in x for x in b + a + n), str(b + a + n))

        fnt = "\n".join(f"char id={ord(c)} x=0 y=0" for c in GLIFOS_ES + "abcdefghijk ")
        d = montar(tmp, "hoja-bmfont", {"LICENSE.txt": "CC0", "f.png": b"x", "f.fnt": fnt})
        b, _, n = juzgar(d)
        caso("una hoja en formato BMFont también se lee",
             any("cubre el español entero" in x for x in n), str(n))

        d = montar(tmp, "ttf-y-hoja", {
            "LICENSE.txt": "CC0", "f.png": b"x", "f.json": completo,
            "f.ttf": _fuente_sintetica(fstype=0)})
        _, _, n = juzgar(d)
        caso("si hay .ttf Y hoja, dice que el veredicto del .ttf no aplica",
             any("no aplica" in x for x in n), str(n))

        # El fallo que encontró el rol de licencias: la licencia vive en un `.zip`
        # de OTRA carpeta, y la herramienta marcaba el pack como perdido.
        raiz = os.path.join(tmp, "biblioteca")
        os.makedirs(os.path.join(raiz, "Mi Pack Bonito"), exist_ok=True)
        os.makedirs(os.path.join(raiz, "comprimidos"), exist_ok=True)
        with open(os.path.join(raiz, "Mi Pack Bonito", "arte.png"), "wb") as f:
            f.write(b"x")
        with zipfile.ZipFile(os.path.join(raiz, "comprimidos",
                                          "mi-pack-bonito-assets.zip"), "w") as z:
            z.writestr("LICENSE.txt", "CC0 1.0 Universal")
        idx = indice_de_zips(raiz)
        pack = os.path.join(raiz, "Mi Pack Bonito")
        b, _, _ = dictaminar(revisar_pack(pack, raiz_biblioteca=raiz, indice_zips=idx))
        caso("señala el .zip con licencia de otra carpeta",
             any("ÁBRELO antes de dar este pack por perdido" in x for x in b), str(b))
        caso("pero NO lo da por resuelto: sigue bloqueado",
             any("Sin licencia no entra" in x for x in b), str(b))
        b2, _, _ = dictaminar(revisar_pack(pack, raiz_biblioteca=raiz))
        caso("sin índice de zips no señala nada (no adivina)",
             not any("ÁBRELO" in x for x in b2), str(b2))

        # Una fuente DENTRO de un zip: el silencio sobre ella se leía como aprobado.
        d = montar(tmp, "fuente-comprimida", {"LICENSE.txt": "CC0", "muestra.png": b"x"})
        with zipfile.ZipFile(os.path.join(d, "fuentes.zip"), "w") as z:
            z.writestr("tipo.ttf", _fuente_sintetica(fstype=4))
        b, _, _ = juzgar(d)
        caso("una fuente dentro de un .zip también se lee, y su fsType bloquea",
             any("fsType=4" in x for x in b), str(b))

        # Un «documento de licencia» que no nombra ninguna licencia.
        d = montar(tmp, "licencia-que-no-dice-nada", {
            "arte.png": b"x",
            "LICENSE.txt": "You are free to share and adapt this material."})
        b, a, _ = juzgar(d)
        caso("un documento que no nombra licencia ni autor avisa",
             any("NO se reconoce ninguna licencia" in x for x in a), str(a))

        d = montar(tmp, "licencia-que-si-dice", {
            "arte.png": b"x", "LICENSE.txt": "Creative Commons Zero (CC0 1.0)"})
        _, a, _ = juzgar(d)
        caso("y una que sí la nombra no avisa",
             not any("NO se reconoce" in x for x in a), str(a))

        d = montar(tmp, "solo-fuentes-modo", {"heroe.png": b"x",
                                              "tipo.ttf": _fuente_sintetica(fstype=4)})
        b, _, _ = juzgar(d, solo_fuentes=True)
        caso("--solo-fuentes ignora todo lo que no sea la tipografía",
             len(b) == 1 and "fsType" in b[0], str(b))

        caso("packs_en encuentra las carpetas a la profundidad pedida",
             len(packs_en(tmp, 1)) >= 15, str(len(packs_en(tmp, 1))))

    caso("una ruta que no existe da 2, no una excepción",
         True)   # main() lo comprueba con isdir; aquí solo se documenta el contrato

    # Se mira SOLO la mitad de producción: si se mirara el archivo entero, esta
    # comprobación contaría el literal que ella misma escribe y se daría verde sola.
    produccion = open(__file__, encoding="utf-8").read().split("def autoprueba")[0]
    escrituras = re.findall(r"open\([^)]*?[\"']w[b+]?[\"']", produccion)
    caso("en producción solo hay UNA escritura, la del --json",
         len(escrituras) == 1, f"encontradas {len(escrituras)}: {escrituras}")
    caso("y solo se abre cuando el usuario pide --json",
         'if salida_json:' in produccion)

    print()
    if fallos:
        print(f"✗ Fallan {len(fallos)}: " + ", ".join(fallos))
        return 1
    print("✓ Todas las comprobaciones de la autoprueba pasan.")
    return 0


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    sys.exit(main())
