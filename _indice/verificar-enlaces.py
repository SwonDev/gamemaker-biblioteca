#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que todas las rutas internas citadas en los documentos existen de verdad,
y que las anclas de sección (`documento.md#seccion`) resuelven contra un encabezado real
del documento de destino — incluidos los autoenlaces (`#seccion`) dentro del mismo documento.

El identificador de cada encabezado se genera con la misma regla de *slug* que usa GitHub:
minúsculas, los espacios se convierten en guiones, se eliminan los signos de puntuación
(incluidos los que generó el propio Markdown: backticks, asteriscos, paréntesis...), y se
conservan las tildes, las eñes y los guiones bajos. Los encabezados duplicados dentro de un
mismo documento reciben el sufijo `-1`, `-2`... en el orden en que aparecen, igual que GitHub.

Algoritmo calibrado contra enlaces reales que ya funcionan en la biblioteca (no es una
suposición): ver `_indice/auditorias/` para el detalle de la calibración.

«09 - Manual oficial» y «11 - Código descargado» son opcionales por diseño (se reconstruyen
con `./reconstruir.sh`): un enlace hacia una de las dos que no resuelve porque la carpeta
no está instalada NO cuenta como roto, solo se avisa. Si la carpeta SÍ está instalada y el
destino concreto no existe dentro, eso sigue contando como enlace roto de verdad.

`_indice/simbolos.json` y `_indice/documentos.json` tampoco cuentan como rotos si aún no
existen: los genera `construir-indices.py` (paso 2 de `actualizar.py`), no se publican.

Uso:  python3 "_indice/verificar-enlaces.py" [carpeta]
"""
import os, re, sys, urllib.parse

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

# El único argumento posicional es la carpeta a revisar. Comprobarlo NO es celo:
# sin esta guarda, `verificar-enlaces.py --loquesea` tomaba «--loquesea» como
# carpeta, no encontraba ni un archivo, e imprimía «0 rutas correctas · 0 rotas»
# con exit 0. Un verde perfecto habiendo verificado NADA — la peor salida posible
# para un script cuyo trabajo es dar garantías. Cualquier ruta mal escrita en un
# CI o un flag inventado por un agente lo disparaba.
if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help", "help"):
    print(__doc__ or "verificar-enlaces.py [carpeta]")
    print("\nSin argumentos revisa la raíz de la biblioteca. Con uno, esa carpeta.")
    sys.exit(0)

# Autoprueba: se lanza a sí mismo contra proyectos de mentira y comprueba los
# CÓDIGOS DE SALIDA, que es donde vivía el falso verde. Va antes de todo lo demás
# porque no necesita leer un solo archivo de la biblioteca.
if len(sys.argv) > 1 and sys.argv[1] == "--autoprueba":
    import subprocess, tempfile
    _yo = os.path.abspath(__file__)
    _fallos = []

    def _correr(carpeta, extra=None):
        _cmd = [sys.executable, _yo, carpeta] + (extra or [])
        _r = subprocess.run(_cmd, capture_output=True, text=True)
        return _r.returncode, _r.stdout

    def _revisar(nombre, condicion, detalle=""):
        if condicion:
            print("  ✓ " + nombre)
        else:
            _fallos.append(nombre)
            print("  ✗ %s  ->  %s" % (nombre, detalle))

    with tempfile.TemporaryDirectory() as _tmp:
        # a · Todo correcto: un enlace que existe y un ancla que existe.
        _a = os.path.join(_tmp, "bien"); os.makedirs(_a)
        open(os.path.join(_a, "uno.md"), "w", encoding="utf-8").write(
            "# Uno\n\n## Sección buena\n\nVer [dos](./dos.md) y [el ancla](#sección-buena).\n")
        open(os.path.join(_a, "dos.md"), "w", encoding="utf-8").write("# Dos\n")
        _c, _o = _correr(_a)
        _revisar("un árbol correcto sale con 0", _c == 0, "exit %d · %s" % (_c, _o.strip()[:80]))

        # b · Enlace roto: tiene que fallar.
        _b = os.path.join(_tmp, "roto"); os.makedirs(_b)
        open(os.path.join(_b, "uno.md"), "w", encoding="utf-8").write(
            "# Uno\n\nVer [tres](./tres.md).\n")
        _c, _o = _correr(_b)
        _revisar("un enlace roto NO sale con 0", _c != 0, "exit %d" % _c)

        # c · Ancla rota: también.
        _d = os.path.join(_tmp, "ancla"); os.makedirs(_d)
        open(os.path.join(_d, "uno.md"), "w", encoding="utf-8").write(
            "# Uno\n\n## Sección real\n\nVer [el ancla](#seccion-que-no-existe).\n")
        _c, _o = _correr(_d)
        _revisar("un ancla rota NO sale con 0", _c != 0, "exit %d" % _c)

        # d · Cero enlaces: NO es «todo bien», es «no he mirado nada».
        _e = os.path.join(_tmp, "vacio"); os.makedirs(_e)
        open(os.path.join(_e, "uno.md"), "w", encoding="utf-8").write("# Uno\n\nSin enlaces.\n")
        _c, _o = _correr(_e)
        _revisar("una carpeta sin un solo enlace NO sale con 0", _c != 0, "exit %d" % _c)

        # e · El falso verde original: un flag inventado se tomaba por carpeta.
        _cmd = [sys.executable, _yo, "--loquesea"]
        _r = subprocess.run(_cmd, capture_output=True, text=True)
        _revisar("un argumento inventado NO sale con 0", _r.returncode != 0,
                 "exit %d" % _r.returncode)
        _revisar("y no dice «0 rotas» habiendo mirado nada",
                 "0 rotas" not in _r.stdout, _r.stdout.strip()[:90])

        # f · Sobran argumentos.
        _c, _o = _correr(_a, ["extra"])
        _revisar("un argumento de más NO sale con 0", _c != 0, "exit %d" % _c)

        # g · Dos secciones con el mismo número: una cita «§N» ahí es ambigua.
        _g = os.path.join(_tmp, "dup"); os.makedirs(_g)
        open(os.path.join(_g, "uno.md"), "w", encoding="utf-8").write(
            "# Uno\n\n## 8.7 · Una cosa\n\nVer [dos](./dos.md).\n\n## 8.7 · Otra cosa\n")
        open(os.path.join(_g, "dos.md"), "w", encoding="utf-8").write("# Dos\n")
        _c, _o = _correr(_g)
        _revisar("dos secciones con el mismo número NO salen con 0", _c != 0, "exit %d" % _c)

        # h · Y la convención de la casa (`bis`, `ter`) NO se confunde con un duplicado.
        _h = os.path.join(_tmp, "bis"); os.makedirs(_h)
        open(os.path.join(_h, "uno.md"), "w", encoding="utf-8").write(
            "# Uno\n\n## 5 · Una\n\nVer [dos](./dos.md).\n\n## 5 bis · Otra\n\n"
            "### 5 bis.1 · Detalle\n\n### 2.5D · Ni esto\n")
        open(os.path.join(_h, "dos.md"), "w", encoding="utf-8").write("# Dos\n")
        _c, _o = _correr(_h)
        _revisar("`5 bis` y `2.5D` NO cuentan como duplicado de `5`", _c == 0,
                 "exit %d · %s" % (_c, _o.strip()[-100:]))

        # i · Citas por número entre documentos: «13 · 10 §8.7».
        def _arbol(nombre, cuerpo_citante, cuerpo_citado):
            raiz = os.path.join(_tmp, nombre)
            c1 = os.path.join(raiz, "13 - Diseño")
            c2 = os.path.join(raiz, "04 - Recetas")
            os.makedirs(c1); os.makedirs(c2)
            open(os.path.join(c1, "05 - Citante.md"), "w", encoding="utf-8").write(cuerpo_citante)
            open(os.path.join(c2, "06 - Citado.md"), "w", encoding="utf-8").write(cuerpo_citado)
            return raiz

        _citado = ("# Citado\n\n## 8. Cómo escalarlo\n\n"
                   "1. **Uno** — algo.\n2. **Atajos** — puertas de un solo sentido.\n\n"
                   "## 2 · El método\n\n| # | Qué |\n|---|---|\n| 2.2 | **Concepto** |\n")
        _ok = _arbol("citas_ok",
                     "# Citante\n\n## 1 · Uno\n\nVer [x](../04%20-%20Recetas/06%20-%20Citado.md) "
                     "y `04 · 06 §8.2` y `04 · 06 §2.2` y `04 · 06 §8`.\n", _citado)
        _c, _o = _correr(_ok)
        _revisar("citas a encabezado, punto de lista y fila de tabla resuelven", _c == 0,
                 "exit %d · %s" % (_c, _o.strip()[-140:]))

        _mal = _arbol("citas_mal",
                      "# Citante\n\n## 1 · Uno\n\nVer [x](../04%20-%20Recetas/06%20-%20Citado.md) "
                      "y `04 · 06 §99.9`.\n", _citado)
        _c, _o = _correr(_mal)
        _revisar("una cita a una sección que NO existe falla", _c != 0, "exit %d" % _c)

    if _fallos:
        print("\n✗ %d comprobación(es) de la autoprueba fallan." % len(_fallos))
        sys.exit(1)
    print("\n✓ Las 11 comprobaciones de la autoprueba pasan.")
    sys.exit(0)

DEST = sys.argv[1] if len(sys.argv) > 1 else RAIZ

if len(sys.argv) > 2:
    print(f"✗ Sobran argumentos: {' '.join(sys.argv[2:])}")
    print("  Uso: verificar-enlaces.py [carpeta]")
    sys.exit(2)

if not os.path.isdir(DEST):
    print(f"✗ «{DEST}» no es una carpeta.")
    print("  Uso: verificar-enlaces.py [carpeta]   (sin argumentos revisa la biblioteca entera)")
    sys.exit(2)

# Dos formas válidas de enlace en Markdown, y hay que comprobar las dos:
#   [texto](ruta-sin-espacios.md)
#   [texto](<ruta con espacios.md>)   ← la usa todo el índice de recetas
PAT_MD = re.compile(r"\[[^\]]*\]\(([^)\s<>]+)\)")
PAT_MD_ANG = re.compile(r"\[[^\]]*\]\(<([^>]+)>\)")
PAT_COD = re.compile(r"`(11 - Código descargado/[^`]+)`")

PAT_FENCE = re.compile(r"^(`{3,}|~{3,})")
PAT_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
PAT_MD_LINK_EN_TEXTO = re.compile(r"\[([^\]]*)\]\([^)]*\)")

# Estas dos carpetas son opcionales por diseño (ver .gitignore y PUBLICAR.md): un clon
# recién hecho no las trae, y eso es su estado normal, no un enlace roto. Se reconstruyen
# con ./reconstruir.sh. Un enlace hacia ellas solo cuenta como "roto" de verdad cuando la
# carpeta SÍ tiene contenido real y el destino concreto, aun así, no existe dentro.
CARPETAS_OPCIONALES = ("09 - Manual oficial", "11 - Código descargado")


def carpeta_opcional_de(ruta_abs):
    """Si `ruta_abs` cae dentro de una de las carpetas opcionales, devuelve su nombre."""
    rel = os.path.relpath(ruta_abs, RAIZ)
    for c in CARPETAS_OPCIONALES:
        if rel == c or rel.startswith(c + os.sep):
            return c
    return None


CACHE_INSTALADA = {}


def carpeta_instalada(nombre):
    """¿Hay contenido real en esta carpeta opcional, o solo está vacía / con el catálogo?

    «11 - Código descargado» siempre trae `_RUTAS.json` y `_CATALOGO.md` publicados (son
    solo metadatos, no código de nadie): su sola presencia no cuenta como "instalada", hace
    falta el contenido de verdad (los repos clonados). «09 - Manual oficial» directamente no
    existe en un clon limpio, así que con comprobar que el directorio existe basta.
    """
    if nombre in CACHE_INSTALADA:
        return CACHE_INSTALADA[nombre]
    ruta = os.path.join(RAIZ, nombre)
    if not os.path.isdir(ruta):
        CACHE_INSTALADA[nombre] = False
        return False
    contenido = [e for e in os.listdir(ruta) if e not in ("_RUTAS.json", "_CATALOGO.md")]
    CACHE_INSTALADA[nombre] = bool(contenido)
    return CACHE_INSTALADA[nombre]


# _indice/simbolos.json y _indice/documentos.json también están en .gitignore, pero por un
# motivo distinto al de las dos carpetas de arriba: no son opcionales, son GENERADOS. Los
# crea `construir-indices.py` (paso 2 de actualizar.py) a partir del disco y del runtime. En
# un clon recién hecho, antes de la primera ejecución, todavía no existen — un enlace hacia
# ellos no es un enlace roto, es orden de ejecución: se resuelve solo en cuanto se corre
# `python3 _indice/actualizar.py` una vez.
FICHEROS_GENERADOS = ("_indice/simbolos.json", "_indice/documentos.json")


def slugificar(texto):
    """Reproduce el algoritmo de *slug* de GitHub para anclas de encabezado."""
    # Un enlace Markdown dentro del propio encabezado se reduce a su texto visible.
    texto = PAT_MD_LINK_EN_TEXTO.sub(r"\1", texto)
    texto = texto.lower()
    conservados = []
    for ch in texto:
        # Unicode-aware: letras con tilde y eñes cuentan como alfanuméricas.
        if ch.isalnum() or ch in ("_", "-", " "):
            conservados.append(ch)
        # cualquier otro signo (backticks, paréntesis, comas, dos puntos, «·», «—»…)
        # se elimina sin más — no se sustituye por espacio, así que dos signos con
        # espacios a ambos lados dejan un guion doble.
    return "".join(conservados).replace(" ", "-")


CACHE_ENCABEZADOS = {}


def encabezados_de(ruta_md):
    """Devuelve la lista ordenada de anclas (con los sufijos -1, -2... de GitHub para
    encabezados duplicados) de un documento .md. Se cachea por ruta absoluta."""
    if ruta_md in CACHE_ENCABEZADOS:
        return CACHE_ENCABEZADOS[ruta_md]
    anclas = []
    try:
        txt = open(ruta_md, encoding="utf-8", errors="replace").read()
    except OSError:
        CACHE_ENCABEZADOS[ruta_md] = anclas
        return anclas
    en_bloque_codigo = False
    marca_cierre = None
    for linea in txt.splitlines():
        m_fence = PAT_FENCE.match(linea.strip())
        if m_fence:
            marca = m_fence.group(1)[0]
            if not en_bloque_codigo:
                en_bloque_codigo = True
                marca_cierre = marca
            elif marca == marca_cierre:
                en_bloque_codigo = False
                marca_cierre = None
            continue
        if en_bloque_codigo:
            continue
        m = PAT_HEADING.match(linea)
        if not m:
            continue
        texto = m.group(2)
        texto = re.sub(r"\s+#+\s*$", "", texto)  # cierre ATX opcional: "## Título ##"
        base = slugificar(texto)
        anclas.append(base)
    # Sufijos de duplicados, al estilo GitHub: -1, -2... en orden de aparición.
    vistos = {}
    resultado = []
    for base in anclas:
        if base in vistos:
            vistos[base] += 1
            resultado.append(f"{base}-{vistos[base]}")
        else:
            vistos[base] = 0
            resultado.append(base)
    CACHE_ENCABEZADOS[ruta_md] = resultado
    return resultado


rotos, ok = [], 0
anclas_rotas, anclas_ok = [], 0
pendientes_opcionales = {}  # {carpeta: [(doc, destino), ...]} — no instalada, no es un error
pendientes_generados = {}   # {fichero: [(doc, destino), ...]} — aún no generado, no es un error

for raiz, dirs, files in os.walk(DEST):
    # Lumbre (juego personal) y GameMaker_Fuentes (repos crudos) no son documentación.
    dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "11 - Código descargado",
                                            "09 - Manual oficial", ".ruff_cache",
                                            "Lumbre", "GameMaker_Fuentes",
                                            # informes de trabajo, no documentación: sus
                                            # rutas son relativas a la raíz, no a su carpeta
                                            "auditorias"}]
    for f in files:
        if not f.endswith(".md"):
            continue
        fp = os.path.join(raiz, f)
        try:
            txt = open(fp, encoding="utf-8", errors="replace").read()
        except OSError:
            continue

        # (ruta_sin_fragmento, fragmento_o_None) de cada enlace Markdown del documento,
        # incluidos los autoenlaces «#seccion» (antes se descartaban sin comprobar nada).
        enlaces = []
        for pat in (PAT_MD, PAT_MD_ANG):
            for m in pat.finditer(txt):
                u = m.group(1)
                if u.startswith(("http://", "https://", "mailto:")):
                    continue
                ruta_parte, _, frag_parte = u.partition("#")
                enlaces.append((urllib.parse.unquote(ruta_parte), frag_parte or None))
        for m in PAT_COD.finditer(txt):
            enlaces.append((m.group(1), None))

        destinos = set()
        for ruta_parte, _frag in enlaces:
            destinos.add(ruta_parte)

        for d in destinos:
            if not d:
                continue
            # Solo las rutas al catálogo de código se resuelven desde la raíz: un documento
            # cuyo nombre empiece por «11 - » (p. ej. «11 - Producción…») es relativo, como todos.
            base = raiz if not d.startswith("11 - Código descargado") else RAIZ
            ruta = os.path.normpath(os.path.join(base, d))
            if os.path.exists(ruta) or os.path.exists(ruta.rstrip("/")):
                ok += 1
                continue
            carpeta = carpeta_opcional_de(ruta)
            if carpeta and not carpeta_instalada(carpeta):
                # La carpeta entera no está instalada en este clon: pendiente esperado.
                pendientes_opcionales.setdefault(carpeta, []).append(
                    (os.path.relpath(fp, RAIZ), d))
                continue
            rel_ruta = os.path.relpath(ruta, RAIZ)
            if rel_ruta in FICHEROS_GENERADOS:
                # Aún no se ha ejecutado construir-indices.py en este clon: pendiente esperado.
                pendientes_generados.setdefault(rel_ruta, []).append(
                    (os.path.relpath(fp, RAIZ), d))
                continue
            rotos.append((os.path.relpath(fp, RAIZ), d))

        # Anclas: por cada enlace con fragmento, resolvemos el documento de destino
        # (el propio documento si la ruta viene vacía, es decir «#seccion») y comprobamos
        # que el fragmento coincide con alguna de sus anclas reales.
        for ruta_parte, frag in enlaces:
            if not frag:
                continue
            if ruta_parte:
                base = raiz if not ruta_parte.startswith("11 - Código descargado") else RAIZ
                ruta_destino = os.path.normpath(os.path.join(base, ruta_parte))
            else:
                ruta_destino = fp  # autoenlace dentro del propio documento
            if not ruta_destino.endswith(".md") or not os.path.isfile(ruta_destino):
                # No comprobamos anclas contra destinos que no son documentos .md de la
                # biblioteca (o cuya ruta ya está rota: eso ya se reportó arriba).
                continue
            frag_decodificado = urllib.parse.unquote(frag)
            anclas_validas = encabezados_de(ruta_destino)
            if frag_decodificado in anclas_validas:
                anclas_ok += 1
            else:
                anclas_rotas.append((os.path.relpath(fp, RAIZ),
                                      os.path.relpath(ruta_destino, RAIZ),
                                      frag_decodificado))

if ok == 0 and not rotos:
    print(f"✗ No he encontrado ni un enlace en «{DEST}».")
    print("  Cero comprobaciones no es lo mismo que cero problemas: revisa la ruta.")
    sys.exit(2)

print(f"{ok} rutas correctas · {len(rotos)} rotas")
for doc, d in rotos:
    print(f"  ✗ {doc}\n      → {d}")

if pendientes_opcionales:
    total_pend = sum(len(v) for v in pendientes_opcionales.values())
    print(f"\n⚠ {total_pend} enlaces sin comprobar: apuntan a carpetas opcionales que no "
          "están instaladas en este clon (es su estado normal, no un error):")
    for c in CARPETAS_OPCIONALES:
        if c in pendientes_opcionales:
            print(f"    · {len(pendientes_opcionales[c])} enlaces hacia «{c}/»")
    print("  Instálalas con ./reconstruir.sh (manual | codigo) si las necesitas.")

if pendientes_generados:
    total_gen = sum(len(v) for v in pendientes_generados.values())
    ficheros = ", ".join(pendientes_generados)
    print(f"\n⚠ {total_gen} enlaces sin comprobar: apuntan a ficheros que este clon todavía "
          f"no ha generado ({ficheros}). No es un error: se crean solos al ejecutar "
          "`python3 _indice/actualizar.py` (paso 2).")

print(f"\n{anclas_ok} anclas correctas · {len(anclas_rotas)} rotas")
for doc, destino, frag in anclas_rotas:
    print(f"  ✗ {doc}\n      → {destino}#{frag}")


# ─── Números de sección repetidos dentro de un mismo documento ───────────────
# «§8.7» en dos sitios del mismo documento hace ambigua cualquier cita por número,
# y de eso vive media biblioteca: la skill decía «las seis preguntas de 13/10 §8.7»
# cuando §8.7 era también el guion de humo. Se detectó a mano el 09-09-2026, se
# arreglaron los cuatro casos que había, y se deja vigilado para que no vuelva.
#
# La convención de la casa —`5 bis`, `3 ter`, `9 quater.2`— es legítima y se
# reconoce entera; lo que no vale es repetir la MISMA etiqueta.
PAT_SECCION = re.compile(
    r"^#{2,6}\s+(?>(\d+(?:\.\d+)*(?:\s+(?:bis|ter|quater|quinquies)(?:\.\d+)*)?))"
    r"(?=\s*(?:·|\.|—|:|-|\s)\s*\S)", re.I)


def secciones_repetidas(ruta_md):
    """Etiquetas de sección que aparecen más de una vez en el documento."""
    import collections
    vistos = collections.Counter()
    en_bloque = False
    try:
        txt = open(ruta_md, encoding="utf-8", errors="replace").read()
    except OSError:
        return {}
    for linea in txt.splitlines():
        if PAT_FENCE.match(linea.strip()):
            en_bloque = not en_bloque
            continue
        if en_bloque:
            continue
        m = PAT_SECCION.match(linea)
        if m:
            vistos[" ".join(m.group(1).lower().split())] += 1
    return {k: v for k, v in vistos.items() if v > 1}


# ─── Citas por número entre documentos: «13 · 10 §8.7» ──────────────────────
# 2 239 de estas hay en la biblioteca, y NO son enlaces: nadie las comprobaba. Se
# renumera una sección y se quedan apuntando al vacío en silencio. Se detectó al
# renumerar cuatro secciones el 09-09-2026, y una estaba rota de antes.
#
# Una etiqueta citable puede venir de tres sitios, y los tres son legítimos aquí:
#   · un encabezado           `### 8.7 · …`
#   · una fila de tabla        `| 2.2 | **Concepto y pitch** | …`
#   · un punto de lista numerada dentro de una sección numerada
#     (`## 8. Cómo escalarlo` + `2. **Atajos** …`  →  §8.2)
PAT_CITA = re.compile(
    r"\b(\d{2})\s*(?:·|/)\s*(\d{2})\s*§\s*"
    r"([0-9]+(?:\.[0-9]+)*(?:\s+(?:bis|ter|quater|quinquies)(?:\.[0-9]+)*)?)", re.I)
PAT_FILA_ETIQ = re.compile(
    r"^\|\s*([0-9]+(?:\.[0-9]+)*(?:\s+(?:bis|ter|quater|quinquies)(?:\.[0-9]+)*)?)\s*\|", re.I)
PAT_PUNTO = re.compile(r"^\s{0,3}(\d+)\.\s+\S")

CACHE_ETIQUETAS = {}


def etiquetas_citables(ruta_md):
    """Todas las etiquetas «§X» que ese documento define, de las tres formas."""
    if ruta_md in CACHE_ETIQUETAS:
        return CACHE_ETIQUETAS[ruta_md]
    etiquetas, dentro, seccion = set(), False, None
    try:
        txt = open(ruta_md, encoding="utf-8", errors="replace").read()
    except OSError:
        CACHE_ETIQUETAS[ruta_md] = etiquetas
        return etiquetas
    for linea in txt.splitlines():
        if PAT_FENCE.match(linea.strip()):
            dentro = not dentro
            continue
        if dentro:
            continue
        m = PAT_SECCION.match(linea)
        if m:
            et = " ".join(m.group(1).lower().split())
            etiquetas.add(et)
            seccion = et
            continue
        m = PAT_FILA_ETIQ.match(linea)
        if m:
            etiquetas.add(" ".join(m.group(1).lower().split()))
            continue
        m = PAT_PUNTO.match(linea)
        if m and seccion and "." not in seccion and " " not in seccion:
            etiquetas.add(f"{seccion}.{m.group(1)}")
    CACHE_ETIQUETAS[ruta_md] = etiquetas
    return etiquetas


def indice_de_documentos(destino):
    """(carpeta, documento) → ruta, para resolver «13 · 10»."""
    idx = {}
    for r, ds, fs in os.walk(destino):
        ds[:] = [d for d in ds if d not in {".git", "node_modules", "11 - Código descargado",
                                            "09 - Manual oficial", ".ruff_cache",
                                            "Lumbre", "GameMaker_Fuentes", "auditorias"}]
        for fi in fs:
            if not fi.endswith(".md"):
                continue
            mc = re.match(r"^(\d{2}) ", os.path.basename(r))
            mf = re.match(r"^(\d{2}) ", fi)
            if mc and mf:
                idx[(mc.group(1), mf.group(1))] = os.path.join(r, fi)
    return idx


duplicadas = []
revisados = 0
DOCS_POR_NUMERO = indice_de_documentos(DEST)
citas_rotas = []
citas_ok = 0
for _raiz, _dirs, _files in os.walk(DEST):
    _dirs[:] = [d for d in _dirs if d not in {".git", "node_modules", "11 - Código descargado",
                                              "09 - Manual oficial", ".ruff_cache",
                                              "Lumbre", "GameMaker_Fuentes", "auditorias"}]
    for _f in sorted(_files):
        if not _f.endswith(".md"):
            continue
        _ruta = os.path.join(_raiz, _f)
        revisados += 1
        rep = secciones_repetidas(_ruta)
        if rep:
            duplicadas.append((_ruta, rep))
        try:
            _txt = open(_ruta, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for _m in PAT_CITA.finditer(_txt):
            _dest = DOCS_POR_NUMERO.get((_m.group(1), _m.group(2)))
            if _dest is None:
                continue          # documento no numerado o fuera del árbol: no se juzga
            _et = " ".join(_m.group(3).lower().split())
            if _et in etiquetas_citables(_dest):
                citas_ok += 1
            else:
                citas_rotas.append((os.path.relpath(_ruta, RAIZ), _m.group(0),
                                    os.path.relpath(_dest, RAIZ)))

if duplicadas:
    print(f"\n✗ {len(duplicadas)} documento(s) repiten un número de sección "
          f"(una cita «§N» ahí es ambigua):")
    for ruta, rep in duplicadas:
        etiquetas = ", ".join(f"§{k} ×{v}" for k, v in sorted(rep.items()))
        print(f"  {os.path.relpath(ruta, RAIZ)}: {etiquetas}")
    print("  → renumera con la convención de la casa: `5 bis`, `3 ter`, `9 quater.2`.")
else:
    print(f"\n{revisados} documentos sin números de sección repetidos.")

if citas_rotas:
    print(f"\n✗ {len(citas_rotas)} cita(s) «NN · MM §X» apuntan a una sección que no existe:")
    for doc, cita, dest in citas_rotas[:20]:
        print(f"  {doc}\n      «{cita}» → {dest}")
    if len(citas_rotas) > 20:
        print(f"  … y {len(citas_rotas) - 20} más")
else:
    print(f"{citas_ok} citas por número («13 · 10 §8.7») resuelven a una sección real.")

sys.exit(1 if (rotos or anclas_rotas or duplicadas or citas_rotas) else 0)
