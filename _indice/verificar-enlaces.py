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

Uso:  python3 "_indice/verificar-enlaces.py" [carpeta]
"""
import os, re, sys, urllib.parse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = sys.argv[1] if len(sys.argv) > 1 else RAIZ

# Dos formas válidas de enlace en Markdown, y hay que comprobar las dos:
#   [texto](ruta-sin-espacios.md)
#   [texto](<ruta con espacios.md>)   ← la usa todo el índice de recetas
PAT_MD = re.compile(r"\[[^\]]*\]\(([^)\s<>]+)\)")
PAT_MD_ANG = re.compile(r"\[[^\]]*\]\(<([^>]+)>\)")
PAT_COD = re.compile(r"`(11 - Código descargado/[^`]+)`")

PAT_FENCE = re.compile(r"^(`{3,}|~{3,})")
PAT_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
PAT_MD_LINK_EN_TEXTO = re.compile(r"\[([^\]]*)\]\([^)]*\)")


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
            else:
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

print(f"{ok} rutas correctas · {len(rotos)} rotas")
for doc, d in rotos:
    print(f"  ✗ {doc}\n      → {d}")

print(f"{anclas_ok} anclas correctas · {len(anclas_rotas)} rotas")
for doc, destino, frag in anclas_rotas:
    print(f"  ✗ {doc}\n      → {destino}#{frag}")

sys.exit(1 if (rotos or anclas_rotas) else 0)
