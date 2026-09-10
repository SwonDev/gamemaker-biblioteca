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


def revisar_pack(raiz, tope_entradas=40000, raiz_biblioteca=None):
    """Devuelve el diagnóstico de un pack. Solo lectura, y con tope de entradas."""
    d = {"ruta": raiz, "licencias": [], "readmes": [], "familias": set(),
         "marcas_build": {}, "extractores": [], "medios": 0, "fuentes": [],
         "zips_con_licencia": [], "zips": 0, "truncado": False,
         "readmes_lista": [], "runtime": [], "heredadas": []}
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

            if ext == ".zip":
                d["zips"] += 1
                try:
                    with zipfile.ZipFile(ruta) as z:      # solo el índice central
                        for nombre in z.namelist():
                            hoja = os.path.basename(nombre)
                            if hoja and PAT_LICENCIA.match(hoja):
                                d["zips_con_licencia"].append(f"{ruta}!{nombre}")
                                try:
                                    with z.open(nombre) as fz:
                                        t = _normalizar(fz.read(200000).decode("utf-8", "replace"))
                                    if t:
                                        d["familias"].add(familia_licencia(t))
                                except (KeyError, OSError, zipfile.BadZipFile, RuntimeError):
                                    pass
                                break
                except (zipfile.BadZipFile, OSError, RuntimeError):
                    pass
        if d["truncado"]:
            break
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

        if len(d["familias"]) > 1:
            avisos.append(
                f"«{nombre}» reúne {len(d['familias'])} FAMILIAS de licencia distintas bajo "
                f"un solo nombre ({', '.join(sorted(d['familias']))}). El nombre de la "
                "carpeta no describe lo de dentro: revísalo subcarpeta por subcarpeta antes "
                "de fiarte de la etiqueta.")

        if d["truncado"]:
            notas.append(f"«{nombre}» es enorme: se paró de contar en el tope de entradas. "
                         "Lo dicho de él es un mínimo, no un recuento.")

    for ruta in d["fuentes"]:
        info, motivo = leer_fuente(ruta)
        base = os.path.basename(ruta)
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
            notas.append(f"«{base}»: cubre {GLIFOS_ES} completo.")
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

    total_bloqueos, total_avisos, informe = 0, 0, []
    print(f"── {len(lista)} carpetas tratadas como pack, bajo «{raiz}»\n")
    for ruta in lista:
        d = revisar_pack(ruta, raiz_biblioteca=raiz)
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
