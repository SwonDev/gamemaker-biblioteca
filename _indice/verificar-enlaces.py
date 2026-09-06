#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que todas las rutas internas citadas en los documentos existen de verdad.

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

rotos, ok = [], 0
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
        destinos = set()
        for m in PAT_MD.finditer(txt):
            u = m.group(1)
            if u.startswith(("http://", "https://", "#", "mailto:")):
                continue
            destinos.add(urllib.parse.unquote(u.split("#")[0]))
        for m in PAT_MD_ANG.finditer(txt):
            u = m.group(1)
            if u.startswith(("http://", "https://", "#", "mailto:")):
                continue
            destinos.add(urllib.parse.unquote(u.split("#")[0]))
        for m in PAT_COD.finditer(txt):
            destinos.add(m.group(1))
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

print(f"{ok} rutas correctas · {len(rotos)} rotas")
for doc, d in rotos:
    print(f"  ✗ {doc}\n      → {d}")
sys.exit(1 if rotos else 0)
