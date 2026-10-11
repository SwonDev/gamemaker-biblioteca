#!/usr/bin/env python3
"""Ámbito de la biblioteca: carpetas numeradas, herramientas y assets propios."""
from pathlib import Path
import re
import sys
import os
import json

for flujo in (sys.stdout, sys.stderr):
    try:
        flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

def carpeta_documental(nombre):
    return bool(re.match(r"^\d{2} - ", nombre))

def es_ajena(raiz, ruta, repos_permitidos=()):
    """Excluye árboles locales y repositorios anidados sin conocer sus nombres."""
    raiz, ruta = Path(raiz).absolute(), Path(ruta).absolute()
    try:
        partes = ruta.relative_to(raiz).parts
    except ValueError:
        return True
    if not partes:
        return False
    if not (carpeta_documental(partes[0]) or partes[0] in {"_indice", "assets", ".github"}):
        return True
    if any(p.startswith(".") and p != ".github" for p in partes):
        return True
    try:
        ruta.resolve().relative_to(raiz.resolve())
    except ValueError:
        return True
    if ruta.is_symlink():
        return es_ajena(raiz, ruta.resolve(), repos_permitidos)
    for n in range(1, len(partes)+1):
        ancestro = raiz.joinpath(*partes[:n])
        if (ancestro / ".git").exists() and ancestro not in repos_permitidos:
            return True
    return False

def rutas_no_publicables(raiz, rutas):
    """Control de nombres/ámbito; no sustituye una revisión del contenido."""
    salida = []
    for nombre in rutas:
        p = Path(nombre)
        secreto = any(re.match(r"^\.env(?:\..*)?$|^secrets?\.env$", x, re.I) for x in p.parts)
        manifiesto_privado = nombre.startswith("_indice/auditorias/r20-") and p.suffix == ".json"
        destino = Path(raiz)/p
        externo = (len(p.parts)>1 or destino.is_symlink()) and es_ajena(raiz, destino)
        if secreto or manifiesto_privado or externo or p.suffix.lower() in {".yy", ".yyp", ".pem", ".key", ".p12"}:
            salida.append(nombre)
    return salida

def repos_del_catalogo(raiz):
    """Solo autoriza los clones registrados del corpus opcional de consulta."""
    base = Path(raiz)/"11 - Código descargado"
    try:
        datos = json.loads((base/"_RUTAS.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    permitidos = set()
    for ruta in datos.values():
        p = base/ruta
        if not Path(ruta).is_absolute() and ".." not in Path(ruta).parts and not p.is_symlink():
            permitidos.add(p.absolute())
    return permitidos

def archivos_del_ambito(raiz, rutas, extensiones, corpus=False):
    """Enumera los árboles elegidos sin seguir enlaces ni repositorios ajenos."""
    raiz = Path(raiz)
    permitidos = repos_del_catalogo(raiz) if corpus else set()
    for nombre in rutas:
        base = raiz/nombre
        if base.is_file():
            if base.suffix in extensiones and not rutas_no_publicables(raiz, [str(base.relative_to(raiz))]):
                yield str(base)
            continue
        if es_ajena(raiz, base, permitidos):
            continue
        for carpeta, dirs, files in os.walk(base):
            dirs[:] = sorted(d for d in dirs if not es_ajena(raiz, Path(carpeta)/d, permitidos))
            for nombre_archivo in sorted(files):
                p = Path(carpeta)/nombre_archivo
                if p.suffix in extensiones and not es_ajena(raiz, p, permitidos):
                    yield str(p)

def autoprueba():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r = Path(td)
        (r/"13 - Diseño/sub").mkdir(parents=True)
        (r/"13 - Diseño/externo/.git").mkdir(parents=True)
        externo = Path(td).parent
        (r/"13 - Diseño/enlace").symlink_to(externo, target_is_directory=True)
        casos = [
            ("13 - Diseño", False), ("13 - Diseño/sub", False),
            ("_indice/skills", False), ("assets/readme", False), (".github/ISSUE_TEMPLATE", False),
            ("mi-juego", True), ("copia-del-juego", True), (".copia-privada", True),
            ("GameMaker_Fuentes", True), ("_pruebas", True),
            ("13 - Diseño/externo", True), ("13 - Diseño/enlace", True),
            ("13 - Diseño/.cache", True),
        ]
        for nombre, esperado in casos:
            assert es_ajena(r, r/nombre)==esperado, nombre
        (r/"13 - Diseño/fuera.md").symlink_to(r.parent/"privado.md")
        bloqueadas=[".env","_indice/secrets.env","13 - Diseño/externo/a.md", "13 - Diseño/fuera.md",
                    "assets/privado.key","_indice/auditorias/r20-fuentes.json","14 - Juego/a.yyp"]
        assert rutas_no_publicables(r,bloqueadas)==bloqueadas
        assert not rutas_no_publicables(r,["README.md","LICENSE","_indice/ambito.py","assets/readme/portada.webp"])
        print(f"✓ Ámbito y publicación: {len(casos)+2} controles pasan.")
    return 0

if __name__ == "__main__":
    if sys.argv[1:] == ["--autoprueba"]:
        raise SystemExit(autoprueba())
    raise SystemExit("Uso: ambito.py --autoprueba")
