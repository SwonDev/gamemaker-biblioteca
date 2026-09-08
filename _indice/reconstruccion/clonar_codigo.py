#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""clonar_codigo.py — reconstruye «11 - Código descargado» clonando los repositorios reales.

Uso normal (lo llama reconstruir.sh codigo):

    python3 clonar_codigo.py
    python3 clonar_codigo.py --limite 3 --destino /ruta/de/prueba   # prueba rápida
    python3 clonar_codigo.py --listar-excluidos                     # ver qué se excluiría

Fuente de la lista: `11 - Código descargado/_RUTAS.json` (nombre del repositorio → ruta
local, 608 entradas) — publicado porque son solo nombres y rutas, no código. La URL de
origen de cada uno se saca de `_CATALOGO.md`, que enlaza casi todos como
`` `Nombre` [↗](URL) `` o `[`Nombre`](URL)`` en sus tablas. Tres reglas cubren el resto:

  1. Los `DS-<nombre>` son los tutoriales de DragoniteSpam, que `_CATALOGO.md` no
     lista uno a uno (dice expresamente «en vez de re-listarlos aquí»): su URL es
     siempre `github.com/DragoniteSpam-GameMaker-Tutorials/<nombre sin DS->`.
  2. Un puñado de nombres (`AdvancedParticleSystem`, `ColMesh`, `gdash`, `Kawase`,
     `painfully-learned-lessons`, `TurboGML`, `YAL-steamworks.gml`) no aparecen en
     `_CATALOGO.md` con ese nombre exacto — verificados a mano contra GitHub el
     2026-09-07 (ver `URLS_EXCEPCION` más abajo).
  3. Lo que ni así se resuelve, se informa al final como «sin URL conocida» y se
     salta: mejor eso que inventar una URL.

Exclusión de juegos comerciales (siempre activa; no hay flag para desactivarla — solo
--listar-excluidos para *ver* qué se excluiría, sin clonar nada en absoluto): dentro de
la categoría
`juegos_y_motores/` de `_RUTAS.json` —la única con juegos y motores completos, no
librerías— se excluye todo lo que:
  a) mencione una de las franquicias comerciales conocidas (Pizza Tower, Deltarune,
     AM2R, Hotline Miami, Kirby) en su nombre, o
  b) no tenga en `_CATALOGO.md` una licencia libre reconocida (MIT, GPL, BSD, Apache,
     MPL, Unlicense, CC0, zlib, ISC…) — «sin licencia» o «propia» NO cuentan como libres.
Las demás 587 entradas (librerías, extensiones oficiales, plantillas, herramientas,
tutoriales…) se clonan tal cual: cada una conserva su propia licencia en su carpeta,
tal y como ya avisa `_CATALOGO.md`.

Reanudable: si la carpeta de destino de un repo ya existe (con contenido), se salta.
Si un `git clone` falla, se informa y se sigue con los demás — no aborta el resto.

Sin dependencias externas: biblioteca estándar de Python + el `git` del sistema.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

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


RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_CODIGO = os.path.join(RAIZ, "11 - Código descargado")
RUTAS_JSON = os.path.join(BASE_CODIGO, "_RUTAS.json")
CATALOGO_MD = os.path.join(BASE_CODIGO, "_CATALOGO.md")

ORG_DRAGONITESPAM = "https://github.com/DragoniteSpam-GameMaker-Tutorials/{}"

# Nombres que _CATALOGO.md no enlaza con el mismo nombre que usa _RUTAS.json (verificado
# a mano contra GitHub el 2026-09-07 — ver el hilo de reconstrucción para el rastro).
URLS_EXCEPCION = {
    "AdvancedParticleSystem": "https://github.com/Limekys/AdvancedParticleSystem",
    "ColMesh": "https://github.com/TheSnidr/ColMesh",
    "gdash": "https://github.com/gm-core/gdash",
    "Kawase": "https://github.com/JujuAdams/Kawase",
    "painfully-learned-lessons": "https://github.com/JujuAdams/painfully-learned-lessons",
    "TurboGML": "https://github.com/FoxyOfJungle/TurboGML",
    "YAL-steamworks.gml": "https://github.com/YAL-GameMaker/steamworks.gml",
}

LICENCIAS_LIBRES = {
    "mit", "gpl-2.0", "gpl-3.0", "lgpl-2.1", "lgpl-3.0", "lgpl-2.0", "agpl-3.0",
    "bsd-2-clause", "bsd-3-clause", "apache-2.0", "mpl-2.0", "mpl-1.1",
    "unlicense", "cc0-1.0", "cc0", "zlib", "isc", "wtfpl", "0bsd", "epl-2.0",
}

FRANQUICIAS_COMERCIALES = ["pizza tower", "deltarune", "am2r", "hotline miami", "kirby"]

PAT_NOMBRE_URL_A = re.compile(r"`([^`]+)`\s*\[↗\]\(([^)]+)\)")
PAT_NOMBRE_URL_B = re.compile(r"\[`([^`]+)`\]\(([^)]+)\)")


def cargar_rutas():
    with open(RUTAS_JSON, encoding="utf-8") as f:
        return json.load(f)


def extraer_urls_catalogo(texto):
    urls = {}
    for pat in (PAT_NOMBRE_URL_A, PAT_NOMBRE_URL_B):
        for m in pat.finditer(texto):
            nombre, url = m.group(1), m.group(2)
            if url.startswith("https://github.com/"):
                urls.setdefault(nombre, url)
    return urls


def extraer_licencias(texto):
    """{nombre: licencia} de CUALQUIER tabla del catálogo, no solo la de «juegos y
    motores»: algunos de sus repos (los de la auditoría de novedades 2025-2026,
    p.ej. `Butterscotch` u `OpenGM`) están catalogados en la sección
    «novedades-2026», con una tabla de 3 columnas en vez de las 6 habituales."""
    licencias = {}
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea.startswith("|") or set(linea) <= {"|", "-", " "}:
            continue
        celdas = [c.strip() for c in linea.strip("|").split("|")]
        m = PAT_NOMBRE_URL_A.search(celdas[0]) or PAT_NOMBRE_URL_B.search(celdas[0])
        if not m:
            continue
        if len(celdas) == 6:        # Repositorio | Qué es | ★ | Licencia | fecha | .gml
            licencia = celdas[3]
        elif len(celdas) == 3:      # Repo | Qué es | Licencia (tabla de novedades-2026)
            licencia = celdas[2]
        else:
            continue
        licencias.setdefault(m.group(1), licencia)
    return licencias


def resolver_url(nombre, urls_catalogo):
    if nombre in urls_catalogo:
        return urls_catalogo[nombre], "catálogo"
    if nombre in URLS_EXCEPCION:
        return URLS_EXCEPCION[nombre], "verificado a mano"
    if nombre.startswith("DS-") and len(nombre) > 3:
        return ORG_DRAGONITESPAM.format(nombre[3:]), "org. DragoniteSpam"
    return None, None


def _normalizar(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def motivo_exclusion(nombre, ruta, licencias):
    """None si se puede clonar; si no, el motivo por el que no."""
    ruta_norm = ruta.replace("\\", "/")
    if not ruta_norm.startswith("juegos_y_motores/"):
        return None
    bajo = _normalizar(nombre)
    for franquicia in FRANQUICIAS_COMERCIALES:
        if _normalizar(franquicia) in bajo:
            return f"juego comercial ({franquicia})"
    if nombre.startswith("DS-"):
        # Tutoriales de DragoniteSpam: `_CATALOGO.md` no los lista uno a uno a
        # propósito («en vez de re-listarlos aquí»), pero documenta que los
        # 193 son MIT — no hay que ir a buscar una fila que no existe.
        return None
    licencia = licencias.get(nombre, "")
    if licencia.strip().lower() not in LICENCIAS_LIBRES:
        return f"licencia no libre en «juegos y motores» ({licencia or 'sin licencia'})"
    return None


def _dir_con_contenido(ruta):
    return os.path.isdir(ruta) and bool(os.listdir(ruta))


def hay_red():
    """Comprobación barata contra github.com ANTES de lanzar hasta 608 `git clone`.

    Sin esto, sin conexión (o tras un cortafuegos que descarta paquetes en vez de
    rechazarlos), cada `git clone` podría agotar su timeout de 300 s uno detrás de
    otro — horas para avisar de algo que se sabe en segundos. Mismo criterio que
    `validar-enlaces-externos.py` y `descargar_manual.py`: comprobar la red ANTES,
    no descubrirlo a mitad de un barrido largo."""
    req = urllib.request.Request("https://github.com", headers={"User-Agent": "gamemaker-biblioteca-reconstruccion/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10):
            return True
    except urllib.error.HTTPError:
        return True  # el servidor respondió: hay red, aunque el código no sea 2xx
    except Exception:
        return False


def clonar_uno(nombre, url, destino):
    """git clone --depth 1. Devuelve (estado, detalle)."""
    if _dir_con_contenido(destino):
        return "saltado", "ya existe"
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    r = subprocess.run(
        ["git", "clone", "--depth", "1", "--quiet", url, destino],
        capture_output=True, text=True, timeout=300,
    )
    if r.returncode == 0:
        return "ok", None
    # una carpeta vacía a medio clonar no debe quedar como si existiera
    if os.path.isdir(destino) and not os.listdir(destino):
        os.rmdir(destino)
    return "error", (r.stderr or r.stdout or "git clone falló").strip().splitlines()[-1][:200]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limite", type=int, default=0,
                     help="clona como mucho N repositorios (pruebas)")
    ap.add_argument("--destino", default=BASE_CODIGO,
                     help="carpeta base de destino (por defecto «11 - Código descargado»)")
    ap.add_argument("--listar-excluidos", action="store_true",
                     help="no clona NADA: solo imprime qué se excluiría y por qué")
    args = ap.parse_args()

    if not os.path.isfile(RUTAS_JSON):
        print(f"✗ No encuentro {RUTAS_JSON}")
        return 2
    if not os.path.isfile(CATALOGO_MD):
        print(f"✗ No encuentro {CATALOGO_MD}")
        return 2

    # --listar-excluidos no clona nada: no necesita git ni red, así que se salta esto.
    if not args.listar_excluidos:
        if not shutil.which("git"):
            print("✗ No encuentro el comando «git» en el PATH. Instálalo y vuelve a intentarlo.")
            return 2
        print("comprobando conectividad con github.com…")
        if not hay_red():
            print("✗ No se pudo conectar con github.com.")
            print("  Puede ser que no haya red disponible ahora mismo, o que el servidor esté")
            print("  caído. No se ha clonado nada: reinténtalo cuando tengas conexión.")
            return 2

    rutas = cargar_rutas()
    catalogo = open(CATALOGO_MD, encoding="utf-8").read()
    urls_catalogo = extraer_urls_catalogo(catalogo)
    licencias = extraer_licencias(catalogo)

    print(f"→ {len(rutas)} repositorios en _RUTAS.json.")

    excluidos, sin_url, ok, saltados, errores = [], [], [], [], []
    nombres = sorted(rutas)
    if args.limite:
        nombres = nombres[: args.limite]

    for nombre in nombres:
        ruta_rel = rutas[nombre]
        motivo = motivo_exclusion(nombre, ruta_rel, licencias)
        if motivo:
            excluidos.append((nombre, motivo))
            continue
        if args.listar_excluidos:
            continue  # modo de solo listado: ni siquiera resuelve URL ni clona

        url, _origen = resolver_url(nombre, urls_catalogo)
        if not url:
            sin_url.append(nombre)
            continue

        destino = os.path.join(args.destino, ruta_rel)
        estado, detalle = clonar_uno(nombre, url, destino)
        if estado == "ok":
            ok.append(nombre)
            print(f"  ✓ {nombre}")
        elif estado == "saltado":
            saltados.append(nombre)
        else:
            errores.append((nombre, detalle))
            print(f"  ✗ {nombre}: {detalle}")

    print()
    print(f"✓ Clonados ahora: {len(ok)}")
    print(f"· Ya existían (reanudado): {len(saltados)}")
    print(f"⊘ Excluidos por no ser libres/juego comercial: {len(excluidos)}")
    if errores:
        print(f"✗ Con error de git: {len(errores)}")
        for nombre, detalle in errores:
            print(f"    {nombre}: {detalle}")
    if sin_url:
        print(f"? Sin URL conocida (no se pudieron resolver): {len(sin_url)}")
        for nombre in sin_url:
            print(f"    {nombre} → {rutas[nombre]}")
    if args.listar_excluidos and excluidos:
        print("\nExcluidos (motivo):")
        for nombre, motivo in excluidos:
            print(f"    {nombre}: {motivo}")

    return 0 if not errores else 1


if __name__ == "__main__":
    sys.exit(main())
