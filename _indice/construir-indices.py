#!/usr/bin/env python3
"""Regenera los índices de la biblioteca a partir del contenido real del disco.

Vive DENTRO del proyecto a propósito: los generadores anteriores estaban en un
directorio temporal y se perdían al limpiarse. Ejecútalo tras añadir o renombrar
documentos.

    python3 _indice/construir-indices.py

Regenera:
  · _indice/documentos.json  (documentos en español + páginas del manual)
  · _indice/simbolos.json    (metadatos: solo recuenta los .gml analizados)

Los dos están en .gitignore: se derivan del disco y del runtime instalado, no se
publican. En un clon limpio no existen todavía — este script los CREA desde cero,
no solo los actualiza — siempre que haya un runtime de GameMaker instalado (de ahí
sale `simbolos.json`, vía GmlSpec.xml). Sin runtime y sin un `simbolos.json` previo
que conservar, no hay forma de derivar la API por primera vez: falla con un
mensaje explicando qué instalar, no con un traceback.

No toca MAPA.json: ese lleva descripciones escritas a mano ("usar_cuando",
"no_usar_para") que no se pueden deducir del disco. Al añadir una carpeta nueva,
edítalo a mano.
"""
import glob, json, os, platform, re, sys

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
MANUAL = os.path.join(RAIZ, "09 - Manual oficial")
CODIGO = os.path.join(RAIZ, "11 - Código descargado")

# «Lumbre» es el juego personal del usuario y «GameMaker_Fuentes» el almacén crudo de repos
# clonados: ninguno es documentación de la biblioteca y no se indexan ni se revisan.
EXCLUIR = {"_indice", "09 - Manual oficial", "11 - Código descargado",
           "Lumbre", "GameMaker_Fuentes"}


def titulo_de(path):
    """Primer encabezado H1 del documento, o el nombre del archivo."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for _ in range(40):
                l = f.readline()
                if not l:
                    break
                if l.startswith("# "):
                    return re.sub(r"^#\s*", "", l).strip()
    except OSError:
        pass
    return os.path.splitext(os.path.basename(path))[0]


def documentos_es():
    out = []
    for carpeta in sorted(os.listdir(RAIZ)):
        d = os.path.join(RAIZ, carpeta)
        if not os.path.isdir(d) or carpeta in EXCLUIR or carpeta.startswith("."):
            continue
        for raiz, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if not x.startswith(".")]
            for f in sorted(files):
                if not f.endswith(".md"):
                    continue
                full = os.path.join(raiz, f)
                out.append({
                    "ruta": os.path.relpath(full, RAIZ),
                    "titulo": titulo_de(full),
                    "carpeta": carpeta,
                })
    # documentos sueltos de la raíz (README, AGENTS, RUTA…)
    for f in sorted(os.listdir(RAIZ)):
        if f.endswith(".md"):
            full = os.path.join(RAIZ, f)
            out.append({"ruta": f, "titulo": titulo_de(full), "carpeta": "(raíz)"})

    # documentos útiles que viven dentro de carpetas excluidas: se indexan a mano
    # (la carpeta se excluye por su volumen, pero estos son puntos de entrada reales).
    #
    # 🔴 **Solo los que VIAJAN en el repositorio.** `09 - Manual oficial/README.md`
    # estaba aquí y está en el `.gitignore` —el manual es de YoYo Games y no se
    # publica—, así que el MAPA.json publicado se generó en una máquina con el espejo
    # puesto y contaba 256 documentos. Quien clonaba y ejecutaba `actualizar.py`, que es
    # lo que manda el README, se encontraba MAPA.json modificado a 255 sin haber tocado
    # nada: un `git status` sucio que no había escrito él. Encontrado por un auditor
    # externo reconstruyendo desde un clon limpio.
    for rel in ("_indice/COMO-BUSCAR.md",
                "_indice/traduccion/README.md"):
        full = os.path.join(RAIZ, rel)
        if os.path.exists(full):
            out.append({"ruta": rel, "titulo": titulo_de(full),
                        "carpeta": os.path.dirname(rel)})
    return out


def paginas(sub):
    base = os.path.join(MANUAL, sub)
    out = []
    for raiz, _, files in os.walk(base):
        for f in sorted(files):
            if f.endswith(".md"):
                out.append(os.path.relpath(os.path.join(raiz, f), RAIZ))
    return sorted(out)


def contar_gml():
    n = 0
    for raiz, _, files in os.walk(CODIGO):
        n += sum(1 for f in files if f.endswith(".gml"))
    return n



IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _ruta_cache_gamemakercli():
    """Réplica de la lógica de gm-cli (ver buscar.py, misma función, para el porqué
    exacto): macOS → ~/Library/Caches, Windows → %LOCALAPPDATA%\\GameMakerCLI\\cache,
    resto → XDG_CACHE_HOME. No verificado fuera de macOS. Se repite aquí porque
    buscar.py no se importa: cada script deriva su propia RUNTIMES."""
    home = os.path.expanduser("~")
    sistema = platform.system()
    if sistema == "Darwin":
        return os.path.join(home, "Library", "Caches", "GameMakerCLI")
    if sistema == "Windows":
        base = os.environ.get("LOCALAPPDATA") or os.path.join(home, "AppData", "Local")
        return os.path.join(base, "GameMakerCLI", "cache")
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(home, ".cache")
    return os.path.join(base, "GameMakerCLI")


RUNTIMES = os.path.join(_ruta_cache_gamemakercli(), "runtimes-gms2")


def fusionar_fnames(simb):
    """Añade al índice los símbolos que están en `fnames` y no en GmlSpec.xml.

    El runtime trae DOS listas de símbolos y no coinciden: `GmlSpec.xml` (la que usa
    el IDE y Feather) y `fnames`. Hay 34 símbolos que solo están en `fnames` —entre
    ellos las 19 constantes `*_CHARSET` y dos funciones reales—, invisibles para
    cualquier herramienta basada en la documentación. Se marcan con `fuente: fnames`
    para avisar de que Feather no los reconoce.
    """
    if not os.path.isdir(RUNTIMES):
        return 0
    rts = sorted(d for d in os.listdir(RUNTIMES) if d.startswith("runtime-"))
    if not rts:
        return 0
    ruta = os.path.join(RUNTIMES, rts[-1], "fnames")   # el más reciente
    if not os.path.exists(ruta):
        return 0

    n = 0
    for l in open(ruta, encoding="utf-8", errors="replace"):
        l = l.rstrip("\n").strip()
        if l.startswith("//") or not l:
            continue
        if "(" in l:
            nom, tipo, firma = l.split("(")[0].strip(), "función", l
        elif l.endswith("#"):
            nom, tipo, firma = l[:-1].strip(), "constante", None
        elif l.endswith(("@", "&")):
            nom, tipo, firma = l[:-1].strip(), "variable", None
        else:
            nom, tipo, firma = l.strip(), "constante", None
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", nom) or nom in simb:
            continue          # GmlSpec.xml manda: nunca se pisa
        e = {"tipo": tipo, "obsoleta": False, "fuente": "fnames",
             "nota": "Está en el runtime (fnames) pero NO en GmlSpec.xml. "
                     "Feather no la reconoce: sin autocompletado. "
                     "Verifícala en tu proyecto."}
        if firma:
            e["firma"] = firma
        simb[nom] = e
        n += 1
    return n


# Solo se cruza lo que aparece como CÓDIGO (bloques ``` o entre acentos graves).
# Cruzar la prosa daría falsos positivos absurdos: «real», «string», «path» o
# «score» son a la vez símbolos de GML y palabras corrientes en español.
COD_BLOQUE = re.compile(r"```.*?```", re.S)
COD_INLINE = re.compile(r"`([^`\n]+)`")
# Sin mínimo de longitud: «pi», «id», «x» y «y» son símbolos reales de GML.
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def cruzar_docs(simb, docs):
    """Reconstruye docs_es: qué documento de la biblioteca explica cada símbolo."""
    for e in simb.values():
        e.pop("docs_es", None)

    idx = {}
    for d in docs:
        # Los volcados de _API del runtime listan LA API ENTERA: si se cruzan,
        # el 68 % de los símbolos apunta al mismo archivo y el cruce deja de
        # informar. Esa función ya la cumple buscar.py leyendo simbolos.json.
        if "_API del runtime" in d["ruta"]:
            continue
        full = os.path.join(RAIZ, d["ruta"])
        try:
            txt = open(full, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        codigo = " ".join(COD_BLOQUE.findall(txt)) + " " + " ".join(COD_INLINE.findall(txt))
        for tok in set(TOKEN.findall(codigo)):
            if tok in simb:
                idx.setdefault(tok, set()).add(d["ruta"])

    for nom, rutas in idx.items():
        simb[nom]["docs_es"] = sorted(rutas)
    return len(idx)


def titulo_gml(path):
    """Descripción de un script .gml: la primera línea de comentario con contenido."""
    base = os.path.splitext(os.path.basename(path))[0]
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for _ in range(12):
                l = f.readline()
                if not l:
                    break
                l = l.strip()
                if not l.startswith("//"):
                    continue
                l = l.lstrip("/").strip()
                # saltamos separadores «=====» y la línea que repite el nombre
                if not l or set(l) <= set("=-*") or l.startswith(base):
                    continue
                # la descripción suele continuar en la línea siguiente:
                # cortamos limpio en vez de dejarla colgando de una coma o una «y»
                l = l.rstrip(".: ")
                l = re.sub(r"[,;]?\s+(y|o|e|con|para|que|de|por|en|a|al|del|sin)$", "", l)
                return f"{base} — {l.rstrip(',;: ')}"
    except OSError:
        pass
    return base


def sincronizar_mapa(docs, n_simbolos):
    """Pone MAPA.json al día con el disco SIN perder la prosa escrita a mano.

    Lo que se deduce del disco (documentos, títulos, recuentos) se reescribe
    siempre. Lo que es criterio humano ("usar_cuando", "no_usar_para",
    "proposito") no se toca nunca. Si aparece una carpeta nueva se crea su
    entrada con la prosa vacía y se avisa, porque eso sí hay que escribirlo.

    Devuelve la lista de avisos: si no está vacía, algo requiere una persona.
    """
    ruta = os.path.join(IND, "MAPA.json")
    m = json.load(open(ruta, encoding="utf-8"))
    avisos = []

    # Carpetas de infraestructura: existen, están descritas en MAPA.json a mano,
    # pero no son carpetas de contenido y no se sincronizan documento a documento.
    # («11 - Código descargado» son 324 repos, no documentos en español.)
    INFRA = {"_indice", "09 - Manual oficial", "11 - Código descargado"}

    # documentos agrupados por carpeta de primer nivel
    por_carpeta = {}
    raiz_docs = []
    for d in docs:
        if os.sep in d["ruta"]:
            carpeta = d["ruta"].split(os.sep)[0]
            if carpeta in INFRA:
                continue
            por_carpeta.setdefault(carpeta, []).append(d)
        else:
            raiz_docs.append(d)

    entradas = {c.get("ruta"): c for c in m["carpetas"]}

    for carpeta in sorted(por_carpeta):
        lista = sorted(por_carpeta[carpeta], key=lambda x: x["ruta"])
        e = entradas.get(carpeta)
        if e is None:
            e = {"titulo": carpeta, "proposito": "", "usar_cuando": [],
                 "no_usar_para": [], "ruta": carpeta, "documentos": []}
            m["carpetas"].append(e)
            entradas[carpeta] = e
            avisos.append(f"carpeta nueva sin describir: «{carpeta}» "
                          f"— rellena proposito/usar_cuando en MAPA.json")
        elif not e.get("proposito"):
            avisos.append(f"carpeta sin proposito: «{carpeta}»")

        entradas_doc = [{"ruta": d["ruta"], "titulo": d["titulo"]} for d in lista]

        # Además de los .md, estas carpetas guardan scripts .gml listos para usar
        # (máquina de estados, tween, pathfinding…). Son contenido, no ruido:
        # si no se indexan aquí, ningún LLM los encuentra.
        #
        # **Excepción: el juego de referencia.** Sus ~30 `.gml` son eventos de objeto
        # —`Create_0`, `Step_0`, uno por objeto— y no son piezas reutilizables: un
        # `Create_0.gml` suelto no le sirve a nadie fuera de su juego. Indexarlos uno a
        # uno metía 31 «documentos» donde solo hay 2, dejaba el juego como la segunda
        # carpeta más grande de la biblioteca y llenaba las búsquedas de texto de
        # fragmentos sin contexto. Se indexan su README y su especificación, que es lo
        # que explica el conjunto — mismo criterio que `11 - Código descargado`, que
        # tiene catálogo en vez de entrada por archivo.
        _juego_ref = os.path.join(RAIZ, carpeta, "enjambre")
        for r, _dirs, fs in os.walk(os.path.join(RAIZ, carpeta)):
            if os.path.commonpath([os.path.abspath(r), os.path.abspath(_juego_ref)]) == \
                    os.path.abspath(_juego_ref):
                continue
            for f in sorted(fs):
                if not f.endswith(".gml"):
                    continue
                full = os.path.join(r, f)
                entradas_doc.append({"ruta": os.path.relpath(full, RAIZ),
                                     "titulo": titulo_gml(full)})

        e["documentos"] = sorted(entradas_doc, key=lambda x: x["ruta"])
        e["n_documentos"] = len(e["documentos"])

    for c in m["carpetas"]:
        r = c.get("ruta")
        if not r or r in INFRA or r in por_carpeta:
            continue
        if os.path.isdir(os.path.join(RAIZ, r)):
            avisos.append(f"carpeta sin ningún documento en español: «{r}»")
        else:
            avisos.append(f"MAPA.json lista una carpeta que ya no existe: «{r}»")

    # documentos sueltos de la raíz: deben estar todos en puntos_de_entrada
    pe = m.setdefault("puntos_de_entrada", {})
    for d in raiz_docs:
        if d["ruta"] not in pe:
            pe[d["ruta"]] = {"titulo": d["titulo"], "proposito": "",
                             "usar_cuando": [], "no_usar_para": []}
            avisos.append(f"documento nuevo en la raíz sin describir: «{d['ruta']}»")
        else:
            pe[d["ruta"]]["titulo"] = d["titulo"]
    for k in list(pe):
        if not os.path.exists(os.path.join(RAIZ, k)):
            avisos.append(f"punto de entrada que ya no existe: «{k}»")

    # recuentos que se quedan viejos solos
    fi = m.get("ficheros_indice", {})
    if "_indice/simbolos.json" in fi:
        fi["_indice/simbolos.json"] = (
            f"{n_simbolos} símbolos de GML cruzados con manual, documentación y código real")
    if "_indice/documentos.json" in fi:
        fi["_indice/documentos.json"] = f"los {len(docs)} documentos con su título"
    for k in fi:
        if not os.path.exists(os.path.join(RAIZ, k)):
            avisos.append(f"fichero de índice que ya no existe: «{k}»")

    m["total_documentos"] = len(docs)
    json.dump(m, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return avisos


def runtime_instalado():
    """Carpeta del runtime más reciente que hay instalado, y su versión."""
    if not os.path.isdir(RUNTIMES):
        return None, None
    rts = sorted(d for d in os.listdir(RUNTIMES) if d.startswith("runtime-"))
    if not rts:
        return None, None
    return os.path.join(RUNTIMES, rts[-1]), rts[-1].replace("runtime-", "")


def extraer_gmlspec(dir_runtime):
    """Lee los GmlSpec.xml del runtime y devuelve el diccionario de símbolos.

    Es LA fuente de verdad de la biblioteca: si YoYo publica un runtime nuevo,
    de aquí salen las firmas nuevas, las retiradas y los cambios de tipo. Antes
    esto se extrajo una vez y se quedó congelado en simbolos.json; ahora se
    re-deriva en cada ejecución, que es lo que hace que un runtime nuevo no pase
    desapercibido.
    """
    import xml.etree.ElementTree as ET

    simb = {}
    specs = sorted(glob.glob(os.path.join(dir_runtime, "**", "GmlSpec.xml"),
                             recursive=True))
    for ruta in specs:
        try:
            raiz = ET.parse(ruta).getroot()
        except ET.ParseError:
            continue
        modulo = raiz.attrib.get("Module", "Base")

        for f in raiz.iter("Function"):
            nom = f.attrib.get("Name")
            # el spec incluye marcadores internos del compilador
            # («$$implicit_argument$$»): no son API, no se indexan
            if not nom or not IDENT.match(nom):
                continue
            args = [p.attrib.get("Name", "?") for p in f.findall("Parameter")]
            opc = [p.attrib.get("Optional") == "true" for p in f.findall("Parameter")]
            partes = [f"[{a}]" if o else a for a, o in zip(args, opc)]
            simb[nom] = {
                "tipo": "función",
                "firma": f"{nom}({', '.join(partes)})",
                "devuelve": f.attrib.get("ReturnType") or "Undefined",
                "obsoleta": f.attrib.get("Deprecated") == "true",
                "modulo": modulo,
            }

        for v in raiz.iter("Variable"):
            nom = v.attrib.get("Name")
            if not nom or not IDENT.match(nom):
                continue
            # No hay atributo «Global»: el spec solo dice Instance true/false.
            e = {"tipo": "variable",
                 "tipo_dato": v.attrib.get("Type") or "Undefined",
                 "obsoleta": v.attrib.get("Deprecated") == "true",
                 "ambito": ("instancia" if v.attrib.get("Instance") == "true"
                            else "global")}
            # Get/Set dicen si se puede leer y escribir. Que «fps» sea de solo
            # lectura no está en ningún otro sitio del índice, y asignarle un
            # valor es un error que el LLM comete si nadie se lo dice.
            if v.attrib.get("Set") == "false":
                e["solo_lectura"] = True
            if v.attrib.get("Get") == "false":
                e["no_legible"] = True
            simb[nom] = e

        for c in raiz.iter("Constant"):
            nom = c.attrib.get("Name")
            if not nom or not IDENT.match(nom):
                continue
            simb[nom] = {"tipo": "constante",
                         "tipo_dato": c.attrib.get("Type") or "Real",
                         "obsoleta": c.attrib.get("Deprecated") == "true"}
    return simb


def cruzar_manual(simb, en, es):
    """Enlaza cada símbolo con su página del manual, por nombre de archivo."""
    def mapa(paginas):
        m = {}
        for r in paginas:
            m.setdefault(os.path.splitext(os.path.basename(r))[0], r)
        return m

    m_en, m_es = mapa(en), mapa(es)
    for nom, e in simb.items():
        e["manual_en"] = m_en.get(nom)
        e["manual_es"] = m_es.get(nom)


def main():
    docs = documentos_es()
    en, es = paginas("manual-lts-2026-en"), paginas("manual-lts-2026-es")
    json.dump({"documentos_es": docs, "manual_en": en, "manual_es": es},
              open(os.path.join(IND, "documentos.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    ruta_simbolos = os.path.join(IND, "simbolos.json")
    if os.path.exists(ruta_simbolos):
        previo = json.load(open(ruta_simbolos, encoding="utf-8"))
    else:
        # Primer arranque en un clon limpio: no hay índice previo que conservar
        # (ejemplos_en_codigo, meta...). Se parte de vacío; si hay runtime instalado,
        # el bloque de abajo lo rellena entero desde GmlSpec.xml.
        previo = {"meta": {}, "simbolos": {}}
    primera_vez = not previo["simbolos"]  # no confundir "se genera por primera vez" con "cambió"
    dir_rt, version_rt = runtime_instalado()

    if dir_rt:
        # Se re-deriva del runtime instalado: así un runtime nuevo aparece solo.
        nuevos = extraer_gmlspec(dir_rt)
        cruzar_manual(nuevos, en, es)

        # El análisis del corpus recorre 54 000 archivos .gml y no depende del
        # runtime: se conserva del índice anterior en vez de rehacerlo.
        for nom, e in nuevos.items():
            ej = previo["simbolos"].get(nom, {}).get("ejemplos_en_codigo")
            if ej:
                e["ejemplos_en_codigo"] = ej

        antes = {k for k, v in previo["simbolos"].items() if v.get("fuente") != "fnames"}
        cambios = {"añadidos": sorted(set(nuevos) - antes),
                   "retirados": sorted(antes - set(nuevos))}
        simb = {"meta": previo.get("meta") or {}, "simbolos": nuevos}
        simb["meta"]["runtime"] = version_rt
    elif previo["simbolos"]:
        print("⚠ no hay runtime instalado: se conservan los símbolos anteriores")
        simb, cambios = previo, {"añadidos": [], "retirados": []}
    else:
        # Ni runtime instalado ni un simbolos.json previo que conservar: no hay
        # ningún camino para derivar la API por primera vez. Fallar con claridad
        # en vez de escribir un índice vacío que luego mentiría en silencio.
        print("✗ No hay ningún runtime de GameMaker instalado en esta máquina, y")
        print(f"  {os.path.relpath(ruta_simbolos, RAIZ)} no existe todavía: no hay nada")
        print("  que conservar de una ejecución anterior.")
        print()
        print("  Los símbolos de esta biblioteca se derivan del GmlSpec.xml del runtime")
        print("  instalado (no hay una lista escrita a mano). Instala GameMaker Studio 2")
        print("  LTS 2026 (o solo el runtime, con `gm-cli`) y vuelve a ejecutar:")
        print("      python3 _indice/actualizar.py")
        return 1

    simb["meta"]["archivos_gml_analizados"] = contar_gml()
    extra = fusionar_fnames(simb["simbolos"])
    cruzados = cruzar_docs(simb["simbolos"], docs)
    simb["meta"]["simbolos"] = len(simb["simbolos"])
    simb["meta"]["fuentes"] = ["GmlSpec.xml", "fnames"]
    simb["meta"]["solo_en_fnames"] = extra
    json.dump(simb, open(os.path.join(IND, "simbolos.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    avisos = sincronizar_mapa(docs, simb["meta"]["simbolos"])

    print(f"documentos en español : {len(docs)}")
    print(f"manual (inglés)       : {len(en)}")
    print(f"manual (español)      : {len(es)}")
    print(f"archivos .gml          : {simb['meta']['archivos_gml_analizados']}")
    print(f"símbolos explicados    : {cruzados}  (cruce símbolo → documento)")
    print(f"símbolos de la API     : {simb['meta']['simbolos']}"
          f"  (de ellos {simb['meta']['solo_en_fnames']} solo en fnames)")
    print(f"runtime leído          : {simb['meta']['runtime']}")

    if primera_vez:
        # No es que "cambiara": es la primera vez que se generan en este clon. Decirlo
        # como un cambio de API confundiría a quien acaba de clonar el repositorio.
        print(f"\nPrimera generación en este clon: {len(cambios['añadidos'])} símbolos "
              "cargados desde el runtime instalado.")
    elif cambios["añadidos"] or cambios["retirados"]:
        print(f"\n\033[1mLA API HA CAMBIADO\033[0m respecto al índice anterior:")
        if cambios["añadidos"]:
            print(f"  + {len(cambios['añadidos'])} símbolos nuevos: "
                  + ", ".join(cambios["añadidos"][:12])
                  + (" …" if len(cambios["añadidos"]) > 12 else ""))
        if cambios["retirados"]:
            print(f"  - {len(cambios['retirados'])} símbolos retirados: "
                  + ", ".join(cambios["retirados"][:12])
                  + (" …" if len(cambios["retirados"]) > 12 else ""))
        print("  → revisa si algún documento de la biblioteca los usa.")

    if avisos:
        print("\nMAPA.json necesita una persona:")
        for a in avisos:
            print("  ⚠", a)
        return 1
    print("\nMAPA.json sincronizado con el disco.")
    return 0


import os as _os_arg, sys as _sys_arg
_sys_arg.path.insert(0, _os_arg.path.dirname(_os_arg.path.abspath(__file__)))
from argumentos import exigir_sin_rutas  # noqa: E402

if __name__ == "__main__":
    _sobra = exigir_sin_rutas('Para reconstruir los índices de OTRO árbol, cópialo y ejecútalo desde allí.', ())
    if _sobra:
        sys.exit(_sobra)
    sys.exit(main())
