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
        print("  Esto NO significa que el símbolo no exista: significa que no se ha buscado.")
        print("  Se genera (desde el GmlSpec.xml de tu runtime instalado) con:")
        print("      python3 _indice/actualizar.py")
        # Sale con 2, no con 1. El 1 es «he buscado y no está»; el 2 es «no he podido
        # buscar», que es lo mismo que dice la falta de `grep`. Salir con 1 aquí haría
        # que un agente encadenando comandos leyera «no existe» donde pone «no lo sé»,
        # y ese es exactamente el peor fallo que este proyecto persigue.
        sys.exit(2)
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
    hay_manual = False
    for k, et in (("manual_es", "manual (es)"), ("manual_en", "manual (en)")):
        if s.get(k):
            print(f"  {et}: {s[k]}")
            hay_manual = True
    if not hay_manual and not os.path.isdir(os.path.join(RAIZ, "09 - Manual oficial")):
        # Un clon recién hecho no trae el espejo del manual: es obra de YoYo Games y
        # no se publica (ver PUBLICAR.md). Callarse aquí haría creer que el símbolo no
        # tiene página, cuando lo que pasa es que no está instalada — el mismo error
        # que «0 enlaces rotos» cuando no se ha mirado ninguno.
        print("  manual:    este clon no tiene el espejo (`09 - Manual oficial/`), que no se")
        print("             publica por derechos. NO es que el símbolo no tenga página.")
        print(f"             Léela ya:   gm-cli manual read \"{nombre}\"")
        print("             O instálalo:  ./reconstruir.sh manual")
    if s.get("docs_es"):
        print("  explicada en la biblioteca:")
        for r in s["docs_es"]:
            print("    -", r)
    if s.get("ejemplos_en_codigo"):
        print("  uso real en código descargado:")
        for r in s["ejemplos_en_codigo"]:
            print("    -", r)
    return 0


def _sin_resultados(patron, ambito="la biblioteca"):
    """Qué decir cuando una búsqueda de TEXTO no encuentra nada.

    Existe porque el silencio era peligroso. Una frase sin coincidencias imprimía
    la cabecera y salía con 0, y un agente lo leía como «ya lo he buscado, no
    existe» — la conclusión más cara que puede sacar quien usa esta biblioteca,
    y justo la que su regla número uno intenta evitar en el otro sentido
    (_indice/auditorias/r13-prueba-rpg.md, hueco 10).

    No encontrar una FRASE no significa que el tema no esté: significa que no
    está redactado así. Para ayudar a la siguiente consulta se buscan las
    palabras por separado y se dice cuáles sí aparecen.
    """
    # En Windows sin `grep` (ni Git Bash ni WSL) las búsquedas de texto no se
    # ejecutan siquiera, y sin esta comprobación el mensaje de abajo diría «no lo
    # encuentro» dando a entender que se buscó y no había nada. La causa real es
    # otra y hay que decirla, o el usuario concluirá que el tema no está cubierto.
    if not shutil.which("grep"):
        print(f"✗ No se pudo BUSCAR «{patron}»: falta el comando «grep» en el PATH.")
        print("  Esto NO significa que no haya resultados: significa que no se ha buscado.")
        print("  En Windows, instala Git for Windows (trae grep) o usa WSL. En macOS y")
        print("  Linux viene de serie, así que si ves esto ahí es que el PATH está roto.")
        print("  Mientras tanto, la ficha de un símbolo concreto SÍ funciona:")
        print(f"      python3 _indice/buscar.py <nombre_de_la_funcion>")
        return 2

    print(f"Sin resultados para «{patron}» en {ambito}.")
    print()
    print("⚠️  «No lo encuentro» NO es «no existe». Una frase falla en cuanto una")
    print("    palabra está escrita de otra forma. Para un SÍMBOLO de GML el")
    print("    buscador sí es concluyente; para un concepto, no.")

    palabras = [p for p in re.split(r"[^0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ_]+", patron) if len(p) > 3]
    if len(palabras) > 1:
        sueltas = []
        for p in palabras:
            total, _ = _buscar_en(DOCS, p, [".md", ".gml"])
            if total:
                sueltas.append((total, p))
        if sueltas:
            sueltas.sort(reverse=True)
            print()
            print("    Por separado sí aparecen:")
            for total, p in sueltas[:6]:
                print(f"      «{p}» → {total} documento(s)")
            print("    Prueba con una sola de ellas, o con dos palabras en vez de la frase.")
        else:
            print()
            print("    Ninguna de sus palabras aparece suelta tampoco.")
    print()
    print("    Siguiente paso: `--todo` si usaste `--texto`, el índice de la carpeta")
    print("    que te suene (`_INDICE-*.md`), o `_indice/COMO-BUSCAR.md`.")
    return 1


def _tiene_contenido(ruta, exts, tope=40000):
    """¿Hay al menos UN archivo con esas extensiones ahí dentro?

    No basta con que la carpeta exista. En un clon recién sacado de GitHub,
    «11 - Código descargado» **existe** —viajan su `_CATALOGO.md` y su
    `_RUTAS.json`, que sí son nuestros— pero **no hay ni un `.gml`**: el corpus
    se reconstruye aparte. Mirar solo si la carpeta está hacía que `--codigo`
    contestara «sin resultados», que es el falso «no existe»: el peor fallo
    posible en una biblioteca cuyo trabajo es que un modelo no se invente cosas.
    Corta en el primer acierto, así que en el caso normal no recorre nada.
    """
    if os.path.isfile(ruta):
        return ruta.endswith(tuple(exts))
    vistos = 0
    for _base, _dirs, files in os.walk(ruta):
        _dirs[:] = [d for d in _dirs if d != ".git"]
        for f in files:
            if f.endswith(tuple(exts)):
                return True
            vistos += 1
            if vistos > tope:      # techo de seguridad: no barrer un disco entero
                return False
    return False


def grep(subdirs, patron, exts, limite=40):
    # acepta tanto carpetas como archivos sueltos (README.md, RUTA.md…)
    existentes = [os.path.join(RAIZ, d) for d in subdirs
                  if os.path.exists(os.path.join(RAIZ, d))
                  and _tiene_contenido(os.path.join(RAIZ, d), exts)]
    if not existentes:
        # Sin rutas, un `grep -r` de este sistema no falla ni calla: recorre el
        # directorio de trabajo entero. Avisar de qué falta es lo correcto, no
        # devolver resultados de donde no tocaba buscar.
        print(f"No está instalado (o no tiene {'/'.join(exts)}): {', '.join(subdirs)}")
        if any(d.startswith("09 - Manual oficial") for d in subdirs):
            print("  Instálalo con ./reconstruir.sh manual, o consulta "
                  "gm-cli manual read \"<tema>\" mientras tanto.")
        elif any(d.startswith("11 - Código descargado") for d in subdirs):
            print("  Instálalo con ./reconstruir.sh codigo. El `_CATALOGO.md` sí viaja en")
            print("  el repositorio: ahí está qué contiene cada repo, aunque no el código.")
        print("  ⚠️  Esto NO es «no se ha encontrado»: es «no se ha podido buscar».")
        print("      Sale con 2 justamente para que no se confunda con un 1.")
        return 2
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
        return _sin_resultados(patron)
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
    hubo = False

    # 1 · ¿es un símbolo exacto del runtime?
    d = cargar(avisar=False)
    es_simbolo = patron in d["simbolos"]
    if es_simbolo:
        s = d["simbolos"][patron]
        obs = " ⚠️OBSOLETA" if s.get("obsoleta") else ""
        hubo = True
        print(f"● SÍMBOLO del runtime: {s.get('firma') or patron}{obs}")
        if s.get("solo_lectura"):
            print("    ⚠ SOLO LECTURA: asignarle un valor no hace nada.")
        if s.get("manual_es"):
            print(f"    manual (es): {s['manual_es']}")
        elif not os.path.isdir(os.path.join(RAIZ, "09 - Manual oficial")):
            # Un clon recién hecho no trae el espejo del manual: es obra de YoYo
            # Games y no se publica. Callarse aquí haría creer que el símbolo no
            # tiene página, cuando lo que pasa es que no está instalada.
            print("    manual (es): este clon no tiene el espejo del manual "
                  "(`09 - Manual oficial/`).")
            print("                 No es que el símbolo no tenga página: es que no está aquí.")
            print("                 Genérala con  ./reconstruir.sh manual  — o pregunta al "
                  "manual instalado:")
            print(f"                 gm-cli manual read \"{patron}\"")
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
        hubo = True
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
        hubo = True
        print(f"● MANUAL oficial (es) · {n} página(s):")
        for r in m: print(f"    {r}")
        if n > len(m): print(f"    … y {n - len(m)} más (--manual para verlas todas)")
        print()

    # 4 · código real descargado (324 repos: 21 juegos, 28 librerías…)
    n, m, todas = _buscar_en3(["11 - Código descargado"], patron, [".gml"])
    if n:
        hubo = True
        # categoría de alto nivel (juegos_y_motores, librerias…), para orientar
        cats = sorted({r.split(os.sep)[1] for r in todas if len(r.split(os.sep)) > 1})
        print(f"● CÓDIGO real · {n} archivo(s) en: {', '.join(cats)}")
        for r in m: print(f"    {r}")
        if n > len(m): print(f"    … y {n - len(m)} más (--codigo para verlos todos)")
        print()

    if not hubo:
        return _sin_resultados(patron, "ninguna de las cuatro fuentes")
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

def autoprueba():
    """El **contrato de códigos de salida**, que es de lo que se fía todo lo demás.

        0 = encontrado / correcto
        1 = se ha buscado y NO está
        2 = no se ha podido buscar

    La diferencia entre 1 y 2 es la razón de ser de esta biblioteca. Un `1` dice
    «esa función no existe, no la escribas»; un `2` dice «no lo sé». Confundirlos
    en la dirección equivocada produce el peor fallo posible —dar por inexistente
    algo que sí existe— y en la otra, un falso verde. Se comprobó ejecutando la
    herramienta de verdad, en subprocesos, no llamando a funciones internas.
    """
    import subprocess
    yo = os.path.abspath(__file__)
    fallos = []

    def correr(*args):
        return subprocess.run([sys.executable, yo, *args],
                              capture_output=True, text=True)

    def revisar(nombre, ok, detalle=""):
        if ok:
            print("  \u2713 " + nombre)
        else:
            fallos.append(nombre)
            print("  \u2717 %s  ->  %s" % (nombre, detalle))

    hay_indice = os.path.exists(os.path.join(IDX, "simbolos.json"))

    r = correr("--help")
    revisar("--help sale con 0 y no lo busca como símbolo",
            r.returncode == 0 and "NO existe" not in r.stdout, "exit %d" % r.returncode)

    r = correr()
    revisar("sin argumentos sale con 2, no con 0", r.returncode == 2, "exit %d" % r.returncode)

    r = correr("--modoinventado", "x")
    revisar("un modo que no existe sale con 2 y los enumera",
            r.returncode == 2 and "Modos:" in r.stdout, "exit %d" % r.returncode)

    if hay_indice:
        r = correr("draw_sprite_ext")
        revisar("un símbolo que existe sale con 0", r.returncode == 0, "exit %d" % r.returncode)

        # El nombre real que un CLI con esta skill cargada se inventó el 09-09-2026.
        r = correr("sprite_set_interpolation")
        revisar("un símbolo inventado sale con 1 (no con 0)",
                r.returncode == 1, "exit %d" % r.returncode)
    else:
        print("  · sin simbolos.json: los dos casos de símbolo no se ejecutan "
              "(no es un fallo, ver actualizar.py paso 2)")

    # Lo que motivó esta autoprueba: en un clon de GitHub, «11 - Código descargado»
    # existe con su catálogo pero SIN un solo .gml. Antes eso daba «sin resultados»
    # y exit 1 —un falso «no existe»—, y el manual ausente daba exit 0 —un falso
    # verde—. Los dos son ahora 2.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        vacio = os.path.join(tmp, "11 - Código descargado")
        os.makedirs(vacio)
        with open(os.path.join(vacio, "_CATALOGO.md"), "w", encoding="utf-8") as f:
            f.write("# catálogo, pero ni un .gml\n")
        revisar("una carpeta con catálogo pero sin .gml NO cuenta como instalada",
                not _tiene_contenido(vacio, [".gml"]))
        with open(os.path.join(vacio, "x.gml"), "w", encoding="utf-8") as f:
            f.write("// ahora sí\n")
        revisar("y en cuanto hay un .gml, sí", _tiene_contenido(vacio, [".gml"]))

    if fallos:
        print("\n\u2717 %d comprobación(es) de la autoprueba fallan." % len(fallos))
        return 1
    print("\n\u2713 Las %d comprobaciones de la autoprueba pasan." % (7 if hay_indice else 5))
    return 0


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
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
