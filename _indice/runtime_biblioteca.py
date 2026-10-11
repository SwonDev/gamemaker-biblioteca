"""Selecciona la fuente de API de la biblioteca, sin cambiar el runtime del proyecto."""
from dataclasses import dataclass
from pathlib import Path
import os
import platform
import re
import sys

for flujo in (sys.stdout, sys.stderr):
    try:
        flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


@dataclass(frozen=True)
class RuntimeBiblioteca:
    directorio: str
    version: str
    origen: str

    @property
    def descripcion(self):
        return f"{self.origen}: {self.version}"


def ruta_cache_gamemakercli():
    """Lógica de caché de gm-cli 2.3.0, verificada en macOS; no identifica un proyecto."""
    home = os.path.expanduser("~")
    sistema = platform.system()
    if sistema == "Darwin":
        return os.path.join(home, "Library", "Caches", "GameMakerCLI")
    if sistema == "Windows":
        base = os.environ.get("LOCALAPPDATA") or os.path.join(home, "AppData", "Local")
        return os.path.join(base, "GameMakerCLI", "cache")
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(home, ".cache")
    return os.path.join(base, "GameMakerCLI")


def error_runtime(mensaje):
    """Una fuente no verificable es error de lectura (2), nunca ausencia de símbolo."""
    print(f"✗ Runtime de la biblioteca: {mensaje}", file=sys.stderr)
    raise SystemExit(2)


def aviso_indice(meta, runtime):
    """Diferencia de fuentes: una caché nueva no demuestra un proyecto desactualizado."""
    version_indice = meta.get("runtime", "sin identificar")
    if runtime is None:
        return (f"⚠ No hay fuente de API disponible en la caché; el índice procede de {version_indice}.\n"
                "  No se ha verificado el runtime del proyecto. Selecciónalo con GM_BIBLIOTECA_RUNTIME.")
    if runtime.version == version_indice:
        return None
    estado = ("ÍNDICE CADUCADO PARA LA SELECCIÓN" if runtime.origen.startswith("seleccionado")
              else "ÍNDICE Y CACHÉ DISTINTOS")
    return (f"⚠ {estado}: el índice procede de {version_indice}; {runtime.descripcion}.\n"
            "  Esta fuente no acredita el runtime activo del proyecto.\n"
            "  Fija GM_BIBLIOTECA_RUNTIME a su versión o directorio y reconstruye el índice si corresponde:\n"
            "      python3 _indice/actualizar.py")


def seleccionar_runtime(runtimes=None):
    """Elección explícita o último directorio por versión; no cambia ningún proyecto."""
    if runtimes is None:
        runtimes = os.path.join(ruta_cache_gamemakercli(), "runtimes-gms2")
    if "GM_BIBLIOTECA_RUNTIME" in os.environ:
        eleccion = os.environ["GM_BIBLIOTECA_RUNTIME"].strip()
        version = re.fullmatch(r"(?:runtime-)?(\d+(?:\.\d+)*)", eleccion)
        try:
            ruta = Path(runtimes) / ("runtime-" + version[1]) if version else Path(eleccion).expanduser()
            if not eleccion or not ruta.is_dir():
                error_runtime(f"GM_BIBLIOTECA_RUNTIME={eleccion!r} no identifica un directorio existente; "
                              "corrige la elección o elimina la variable. No se usa otro runtime.")
            ruta = ruta.resolve()
            if not any(p.is_file() for p in ruta.rglob("GmlSpec.xml")):
                error_runtime(f"GM_BIBLIOTECA_RUNTIME={eleccion!r} no contiene GmlSpec.xml; "
                              "no se usa otro runtime.")
        except (OSError, RuntimeError, ValueError) as error:
            error_runtime(f"GM_BIBLIOTECA_RUNTIME={eleccion!r} no se puede resolver: {error}; "
                          "no se usa otro runtime.")
        version_nombre = re.fullmatch(r"(?:runtime-)?(\d+(?:\.\d+)*)", ruta.name)
        version_identificable = version or version_nombre
        identificador = version_identificable[1] if version_identificable else "directorio:" + str(ruta)
        return RuntimeBiblioteca(str(ruta), identificador, "seleccionado mediante GM_BIBLIOTECA_RUNTIME")
    candidatos = []
    try:
        entradas = Path(runtimes).iterdir()
        for ruta in entradas:
            version = re.fullmatch(r"runtime-(\d+(?:\.\d+)*)", ruta.name)
            if version and ruta.is_dir() and any(p.is_file() for p in ruta.rglob("GmlSpec.xml")):
                candidatos.append((tuple(map(int, version[1].split("."))), ruta, version[1]))
    except OSError:
        return None
    if not candidatos:
        return None
    _, ruta, version = max(candidatos, key=lambda e: e[0])
    return RuntimeBiblioteca(str(ruta.resolve()), version, "último disponible en caché")
