#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""buscar.py — buscador de la biblioteca de GameMaker.

Uso:
  python3 "_indice/buscar.py" <símbolo>            Ficha de una función/constante/variable
  python3 "_indice/buscar.py" --texto "<frase>"    Busca texto en los documentos en español
  python3 "_indice/buscar.py" --manual "<frase>"   Busca en el manual oficial espejado
  python3 "_indice/buscar.py" --codigo "<frase>"   Busca en el código GML descargado
  python3 "_indice/buscar.py" --listar <prefijo>   Lista símbolos que empiezan por un prefijo
  python3 "_indice/buscar.py" --todo "<frase>"     Busca en TODO a la vez (símbolos, biblioteca, manual, código)

Todo funciona sin conexión. Es la forma recomendada de comprobar si una función existe
antes de escribir código: si no aparece aquí, no está en este runtime.
"""
import os, re, sys, json, shutil, platform, subprocess

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
IDX = os.path.join(RAIZ, "_indice")


def _ruta_cache_gamemakercli():
    """Dónde guarda gm-cli sus runtimes descargados, replicando su propia lógica
    (dist/chunk-GBMHU7PM.js de @gamemaker/gm-cli 2.3.0 — sin dependencias tipo
    `env-paths`, la calcula a mano): macOS usa ~/Library/Caches, Windows
    %LOCALAPPDATA%\\GameMakerCLI\\cache, y el resto (Linux/BSD/…) el estándar
    XDG_CACHE_HOME. No verificado fuera de macOS: si una versión futura de gm-cli
    cambia esta lógica, hay que releerla del bundle instalado."""
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

_AVISO_GREP_DADO = False


def _grep_disponible():
    """`grep` viene de serie en macOS y Linux, pero no en Windows fuera de Git
    Bash/WSL. Sin él, la ficha de un símbolo conocido (buscar.py <nombre>) sigue
    funcionando entera: solo se pierden --texto/--manual/--codigo/--todo y el
    "¿es un prefijo del lenguaje?" de un símbolo no encontrado. Avisa una sola
    vez por ejecución en vez de fingir "sin resultados"."""
    global _AVISO_GREP_DADO
    if shutil.which("grep"):
        return True
    if not _AVISO_GREP_DADO:
        print("⚠ No encuentro el comando «grep» en el PATH: viene de serie en macOS y "
              "Linux; en Windows instala Git for Windows (trae grep) o usa WSL. Sin él, "
              "las búsquedas de texto (--texto/--manual/--codigo/--todo) no funcionan; "
              "la ficha de un símbolo conocido sí sigue funcionando.", file=sys.stderr)
        _AVISO_GREP_DADO = True
    return False


def runtime_instalado():
    """Versión del runtime que hay instalado ahora mismo, o None."""
    try:
        rts = sorted(d for d in os.listdir(RUNTIMES) if d.startswith("runtime-"))
    except OSError:
        return None
    return rts[-1].replace("runtime-", "") if rts else None


def avisar_si_caducado(meta):
    """Compara el índice con el runtime instalado y avisa si ya no coinciden.

    Es la salvaguarda contra el fallo más peligroso de esta biblioteca: que
    YoYo publique un runtime nuevo, nadie regenere los índices, y buscar.py
    siga respondiendo con la API vieja como si nada. Un índice caducado que
    calla es peor que no tener índice.
    """
    real = runtime_instalado()
    if not real or real == meta.get("runtime"):
        return
    print(f"⚠ ÍNDICE CADUCADO: se generó con el runtime {meta.get('runtime')} "
          f"pero el instalado es {real}.")
    print("  La API puede haber cambiado. Regenera antes de fiarte de esta ficha:")
    print("      python3 _indice/actualizar.py\n")


def cargar(avisar=True):
    ruta = os.path.join(IDX, "simbolos.json")
    if not os.path.exists(ruta):
        print("✗ No existe _indice/simbolos.json todavía.")
        print("  Se genera (desde el GmlSpec.xml de tu runtime instalado) con:")
        print("      python3 _indice/actualizar.py")
        sys.exit(1)
    with open(ruta, encoding="utf-8") as f:
        d = json.load(f)
    if avisar:
        avisar_si_caducado(d.get("meta", {}))
    return d


def _mencionado_en(nombre, limite=6):
    """Busca el literal en los documentos y en el manual. Devuelve rutas, sin duplicar."""
    args = ["grep", "-rlI", "--include=*.md", "-F", "-e", nombre]
    rutas_previas = len(args)
    for d in ("01 - Fundamentos", "02 - Novedades 2026", "04 - Recetas por género",
              "07 - Ecosistema", "08 - Referencia GML completa",
              "12 - Utilidades e integraciones",
              "09 - Manual oficial/manual-lts-2026-es"):
        ruta = os.path.join(RAIZ, d)
        if os.path.exists(ruta):
            args.append(ruta)
    if len(args) == rutas_previas:
        # Ninguna de las carpetas existe: un grep sin rutas recorrería el
        # directorio de trabajo entero en vez de devolver "sin resultados".
        return []
    if not _grep_disponible():
        return []
    try:
        r = subprocess.run(args, capture_output=True, text=True, check=False)
    except OSError:
        return []
    vistos = []
    for l in r.stdout.splitlines():
        rel = l.replace(RAIZ + os.sep, "")
        if rel not in vistos:
            vistos.append(rel)
        if len(vistos) >= limite:
            break
    return vistos


def _pagina_manual_exacta(nombre):
    """Páginas del manual espejado llamadas exactamente <nombre>.md (structs y enums)."""
    out = []
    base = os.path.join(IDX, "..", "09 - Manual oficial")
    for idioma in ("manual-lts-2026-es", "manual-lts-2026-en"):
        raiz = os.path.join(base, idioma)
        for r, _d, files in os.walk(raiz):
            if nombre + ".md" in files:
                out.append(os.path.relpath(os.path.join(r, nombre + ".md"), os.path.join(IDX, "..")))
    return out


def ficha(nombre):
    d = cargar()
    s = d["simbolos"].get(nombre)
    if not s:
        # Los structs y enumeraciones incorporados (AudioBus, AudioEffectType,
        # AnimCurveChannel…) no son símbolos de GmlSpec.xml, pero tienen página
        # propia en el manual con su nombre exacto. Decir de ellos «NO existe»
        # sería una alucinación al revés: se avisa antes de nada.
        pagina = _pagina_manual_exacta(nombre)
        if pagina:
            print(f"«{nombre}» es un STRUCT o ENUMERACIÓN incorporada, no una función:")
            print("  no figura en GmlSpec.xml, pero sí en el manual. Sus propiedades/valores:")
            for pg in pagina:
                print("  -", pg)
            return 0
        cand = [k for k in d["simbolos"] if nombre in k][:15]
        print(f"«{nombre}» NO existe en el runtime {d['meta']['runtime']}.")
        if cand:
            print("\n¿Quizá buscabas?")
            for c in sorted(cand):
                print("  -", c)
        else:
            # Antes de dar el veredicto: puede no ser un símbolo y aun así ser
            # algo real del lenguaje. `gmcallback_` es un prefijo, `#macro` una
            # directiva, `gml_pragma` un ajuste. Decir «no existe» de esas sería
            # justo el fallo que este buscador debe evitar.
            menciones = _mencionado_en(nombre)
            if menciones:
                print("\nNo es una función, constante ni variable del runtime,")
                print("pero SÍ aparece documentado. Puede ser un prefijo, una")
                print("directiva o una convención del lenguaje:")
                for m in menciones:
                    print("  -", m)
            else:
                print("Tampoco hay nada parecido. No la inventes: no existe.")
        return 1
    print(f"# {nombre}  ({s['tipo']})")
    if s.get("firma"):
        print(f"  firma:     {s['firma']}")
        if s.get("devuelve"):
            print(f"  devuelve:  {s['devuelve']}")
    if s.get("tipo_dato"):
        print(f"  tipo:      {s['tipo_dato']}")
    if s.get("ambito"):
        print(f"  ámbito:    {s['ambito']}")
    if s.get("obsoleta"):
        print("  ⚠️  OBSOLETA — no la uses en código nuevo")
    if s.get("fuente") == "fnames":
        print("  ⚠️  SOLO EN `fnames`, no en GmlSpec.xml")
        if s.get("nota"):
            print(f"      {s['nota']}")
    if s.get("solo_lectura"):
        print("  ⚠ SOLO LECTURA: se puede leer, pero asignarle un valor no hace nada.")
    if s.get("no_legible"):
        print("  ⚠ SOLO ESCRITURA: se le asigna, pero leerla no devuelve lo que esperas.")
    if s.get("modulo") and s["modulo"] != "Base":
        print(f"  módulo:    {s['modulo']}")
    for k, et in (("manual_es", "manual (es)"), ("manual_en", "manual (en)")):
        if s.get(k):
            print(f"  {et}: {s[k]}")
    if s.get("docs_es"):
        print("  explicada en la biblioteca:")
        for r in s["docs_es"]:
            print("    -", r)
    if s.get("ejemplos_en_codigo"):
        print("  uso real en código descargado:")
        for r in s["ejemplos_en_codigo"]:
            print("    -", r)
    return 0


def grep(subdirs, patron, exts, limite=40):
    # acepta tanto carpetas como archivos sueltos (README.md, RUTA.md…)
    existentes = [os.path.join(RAIZ, d) for d in subdirs
                  if os.path.exists(os.path.join(RAIZ, d))]
    if not existentes:
        # Sin rutas, un `grep -r` de este sistema no falla ni calla: recorre el
        # directorio de trabajo entero. Avisar de qué falta es lo correcto, no
        # devolver resultados de donde no tocaba buscar.
        print(f"No está instalado: {', '.join(subdirs)}")
        if any(d.startswith("09 - Manual oficial") for d in subdirs):
            print("  Instálalo con ./reconstruir.sh manual, o consulta "
                  "gm-cli manual read \"<tema>\" mientras tanto.")
        elif any(d.startswith("11 - Código descargado") for d in subdirs):
            print("  Instálalo con ./reconstruir.sh codigo.")
        return 0
    if not _grep_disponible():
        return 1
    args = ["grep", "-rniI", "--include=*" + exts[0]]
    for e in exts[1:]:
        args.append("--include=*" + e)
    args += ["-e", patron] + existentes
    try:
        r = subprocess.run(args, capture_output=True, text=True)
    except OSError as e:
        print(f"✗ No se pudo ejecutar «grep»: {e}")
        return 1
    lineas = r.stdout.splitlines()
    # Las coincidencias de PALABRA COMPLETA van primero. Sin esto, buscar «respec»
    # devuelve cincuenta «respecto» y entierra el documento que de verdad habla de
    # respec; lo mismo con «pi» dentro de «pixel» o «copia».
    exacta = re.compile(r"\b" + re.escape(patron) + r"\b", re.I)
    justas = [l for l in lineas if exacta.search(l)]
    resto = [l for l in lineas if not exacta.search(l)]
    n = 0
    for linea in justas + resto:
        print(linea.replace(RAIZ + os.sep, "")[:240])
        n += 1
        if n >= limite:
            print(f"… (recortado en {limite} resultados)")
            break
    if n == 0:
        print("Sin resultados.")
    return 0


def _buscar_en(subdirs, patron, exts, muestra=4):
    """Cuenta coincidencias en unas carpetas y devuelve (total, primeras rutas)."""
    existentes = [os.path.join(_RAIZ, d) for d in subdirs
                  if os.path.exists(os.path.join(_RAIZ, d))]
    if not existentes:
        # Sin rutas reales, un `grep -r` recorrería el directorio de trabajo
        # entero en vez de devolver "nada" — ver el mismo guardado en grep().
        return 0, []
    if not _grep_disponible():
        return 0, []
    args = ["grep", "-rilI", "--include=*" + exts[0]]
    for e in exts[1:]:
        args.append("--include=*" + e)
    args += ["-e", patron] + existentes
    try:
        r = subprocess.run(args, capture_output=True, text=True)
    except OSError:
        return 0, []
    rutas = [l.replace(_RAIZ + os.sep, "") for l in r.stdout.splitlines()]
    return len(rutas), rutas[:muestra]


def _buscar_en3(subdirs, patron, exts, muestra=4):
    """Como _buscar_en pero devuelve además la lista completa (para agrupar)."""
    existentes = [os.path.join(_RAIZ, d) for d in subdirs
                  if os.path.exists(os.path.join(_RAIZ, d))]
    if not existentes:
        return 0, [], []
    if not _grep_disponible():
        return 0, [], []
    args = ["grep", "-rilI", "--include=*" + exts[0]]
    for e in exts[1:]:
        args.append("--include=*" + e)
    args += ["-e", patron] + existentes
    try:
        r = subprocess.run(args, capture_output=True, text=True)
    except OSError:
        return 0, [], []
    rutas = [l.replace(_RAIZ + os.sep, "") for l in r.stdout.splitlines()]
    return len(rutas), rutas[:muestra], rutas


def buscar_todo(patron):
    """Una sola consulta que barre TODAS las fuentes a la vez, priorizadas.

    Es el punto de entrada para un LLM que no sabe de antemano si lo que busca
    es un símbolo, un concepto explicado, una página del manual o un ejemplo de
    código real. En vez de obligarle a elegir flag, mira en todo y ordena la
    respuesta por autoridad: símbolo exacto → biblioteca → manual → código real.
    """
    print(f"═══ «{patron}» en toda la biblioteca ═══\n")

    # 1 · ¿es un símbolo exacto del runtime?
    d = cargar(avisar=False)
    es_simbolo = patron in d["simbolos"]
    if es_simbolo:
        s = d["simbolos"][patron]
        obs = " ⚠️OBSOLETA" if s.get("obsoleta") else ""
        print(f"● SÍMBOLO del runtime: {s.get('firma') or patron}{obs}")
        if s.get("solo_lectura"):
            print("    ⚠ SOLO LECTURA: asignarle un valor no hace nada.")
        if s.get("manual_es"):
            print(f"    manual (es): {s['manual_es']}")
        # los documentos que lo explican vienen del cruce docs_es, no de un grep:
        # así «pi» encuentra la página que lo documenta aunque el texto «pi»
        # aparezca en miles de sitios.
        for r in (s.get("docs_es") or [])[:4]:
            print(f"    explicado en: {r}")
        print(f"    → ficha completa:  python3 _indice/buscar.py {patron}\n")

    # 2 · biblioteca en español (docs + cursos + recetas + referencia).
    #     Para un símbolo corto (<=3 letras) el grep de texto es puro ruido y el
    #     cruce docs_es de arriba ya dio la respuesta buena: se omite.
    n, m = (0, []) if (es_simbolo and len(patron) <= 3) else _buscar_en(DOCS, patron, [".md", ".gml"])
    if n:
        print(f"● BIBLIOTECA en español · {n} documento(s):")
        for r in m: print(f"    {r}")
        if n > len(m): print(f"    … y {n - len(m)} más (--texto para verlos todos)")
        print()

    # 3 · manual oficial espejado. Igual que arriba: para un símbolo corto ya
    #     resuelto, el grep de subcadena («pi» dentro de «pixel», «copia»…) es
    #     ruido; la página buena ya salió como `manual (es)` del símbolo.
    n, m = (0, []) if (es_simbolo and len(patron) <= 3) else \
        _buscar_en(["09 - Manual oficial/manual-lts-2026-es"], patron, [".md"])
    if n:
        print(f"● MANUAL oficial (es) · {n} página(s):")
        for r in m: print(f"    {r}")
        if n > len(m): print(f"    … y {n - len(m)} más (--manual para verlas todas)")
        print()

    # 4 · código real descargado (324 repos: 21 juegos, 28 librerías…)
    n, m, todas = _buscar_en3(["11 - Código descargado"], patron, [".gml"])
    if n:
        # categoría de alto nivel (juegos_y_motores, librerias…), para orientar
        cats = sorted({r.split(os.sep)[1] for r in todas if len(r.split(os.sep)) > 1})
        print(f"● CÓDIGO real · {n} archivo(s) en: {', '.join(cats)}")
        for r in m: print(f"    {r}")
        if n > len(m): print(f"    … y {n - len(m)} más (--codigo para verlos todos)")
        print()

    return 0


def listar(prefijo):
    d = cargar()
    hits = sorted(k for k in d["simbolos"] if k.startswith(prefijo))
    print(f"{len(hits)} símbolos empiezan por «{prefijo}»:")
    for h in hits:
        s = d["simbolos"][h]
        marca = " ⚠️obsoleta" if s.get("obsoleta") else ""
        print(f"  {s.get('firma') or h}{marca}")
    return 0


# Carpetas de documentación en español que recorre --texto.
# Se detectan del disco para que una carpeta nueva quede indexada sola.
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Lumbre (juego personal) y GameMaker_Fuentes (repos crudos) no son documentación.
_EXCLUIR = {"_indice", "09 - Manual oficial", "11 - Código descargado",
            "Lumbre", "GameMaker_Fuentes"}
DOCS = sorted(
    d for d in os.listdir(_RAIZ)
    if os.path.isdir(os.path.join(_RAIZ, d))
    and d not in _EXCLUIR and not d.startswith(".")
)
# …más los documentos sueltos de la raíz (README, AGENTS, RUTA, CLAUDE)
DOCS += [f for f in sorted(os.listdir(_RAIZ)) if f.endswith(".md")]
# …y los puntos de entrada que viven en carpetas excluidas
DOCS += ["_indice/COMO-BUSCAR.md", "_indice/traduccion/README.md",
         "09 - Manual oficial/README.md"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    a = sys.argv[1]
    # `--help` era lo primero que probaba cualquiera y lo peor que podía pasar: se
    # buscaba como si fuera un símbolo de GML y respondía «"--help" NO existe en el
    # runtime». La herramienta de entrada de toda la biblioteca no puede contestar eso.
    if a in ("--help", "-h", "help", "--ayuda"):
        print(__doc__)
        sys.exit(0)
    # Un modo mal escrito («--text», «--codigos») acabaría buscado como símbolo y daría
    # el mismo desconcierto: mejor decir qué modos hay.
    if a.startswith("--") and a not in ("--texto", "--manual", "--codigo", "--listar", "--todo"):
        print(f"No conozco el modo «{a}».")
        print("Modos: --texto · --manual · --codigo · --listar · --todo · --help")
        print("Sin modo, el argumento se busca como símbolo: buscar.py draw_sprite_ext")
        sys.exit(2)
    # Todos los modos piden un segundo argumento; sin él, `sys.argv[2]` reventaría
    # con un IndexError crudo en vez de decir qué falta.
    if a.startswith("--") and len(sys.argv) < 3:
        print(f"A «{a}» le falta qué buscar.  Ejemplo:  buscar.py {a} \"coyote time\"")
        sys.exit(2)
    if a == "--texto":
        sys.exit(grep(DOCS, sys.argv[2], [".md", ".gml"]))
    if a == "--manual":
        sys.exit(grep(["09 - Manual oficial"], sys.argv[2], [".md"]))
    if a == "--codigo":
        sys.exit(grep(["11 - Código descargado"], sys.argv[2], [".gml"]))
    if a == "--listar":
        sys.exit(listar(sys.argv[2]))
    if a == "--todo":
        sys.exit(buscar_todo(sys.argv[2]))
    sys.exit(ficha(a))
