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

sys.exit(1 if (rotos or anclas_rotas) else 0)
