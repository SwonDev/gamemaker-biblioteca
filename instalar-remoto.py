#!/usr/bin/env python3
"""Descarga una revisión pública y ejecuta su instalador; solo necesita Python 3.10+."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from urllib.request import Request, urlopen
from zipfile import ZipFile, BadZipFile

REPO = "SwonDev/gamemaker-biblioteca"
REVISION = "r50"
MAX_BYTES = 100 * 1024 * 1024

for flujo in (sys.stdout, sys.stderr):
    try:
        flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def contenido(raiz):
    return {p.relative_to(raiz).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in raiz.rglob("*") if p.is_file() and
            p.name != ".gamemaker-distribucion.json" and "__pycache__" not in p.parts}


def descargar(url):
    solicitud = Request(url, headers={"User-Agent": "gamemaker-biblioteca-instalar",
                                     "Accept": "application/vnd.github+json"})
    with urlopen(solicitud, timeout=60) as respuesta:
        datos = respuesta.read(MAX_BYTES + 1)
    if len(datos) > MAX_BYTES:
        raise ValueError("La descarga supera el límite de 100 MiB.")
    return datos


def extraer(datos, destino):
    """No extrae rutas absolutas, escapes, enlaces ni nombres especiales de Windows."""
    with ZipFile(io.BytesIO(datos)) as archivo:
        entradas = archivo.infolist()
        if len(entradas) > 20000 or sum(e.file_size for e in entradas) > MAX_BYTES:
            raise ValueError("El archivo supera los límites de extracción.")
        raices = set()
        vistos = set()
        for entrada in entradas:
            ruta = PurePosixPath(entrada.filename)
            partes = ruta.parts
            if (not partes or ruta.is_absolute() or ".." in partes or
                    "\\" in entrada.filename or
                    any(":" in p or p.endswith((".", " ")) or
                        re.fullmatch(r"(?:con|prn|aux|nul|com[0-9]|lpt[0-9])(?:\..*)?", p, re.I)
                        for p in partes) or
                    stat.S_ISLNK(entrada.external_attr >> 16)):
                raise ValueError("Ruta de archivo no permitida: " + entrada.filename)
            clave = "/".join(partes).casefold()
            if clave in vistos:
                raise ValueError("Ruta repetida: " + entrada.filename)
            vistos.add(clave)
            raices.add(partes[0])
        if len(raices) != 1:
            raise ValueError("Se esperaba una sola raíz en la distribución.")
        for entrada in entradas:
            salida = destino.joinpath(*PurePosixPath(entrada.filename).parts[1:])
            if entrada.is_dir():
                salida.mkdir(parents=True, exist_ok=True)
            else:
                salida.parent.mkdir(parents=True, exist_ok=True)
                salida.write_bytes(archivo.read(entrada))
                if os.name != "nt" and entrada.external_attr >> 16 & 0o111:
                    salida.chmod(0o755)
    if not (destino/"instalar.py").is_file():
        raise ValueError("La revisión no contiene instalar.py.")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--revision", default=REVISION, help="tag o SHA de la distribución oficial")
    p.add_argument("--biblioteca", type=Path, help="ubicación de la biblioteca completa")
    p.add_argument("--home", type=Path, help="raíz de usuario alternativa, también para pruebas")
    opciones, resto = p.parse_known_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,100}", opciones.revision):
        p.error("Revisión no válida; usa un tag o SHA.")
    home = (opciones.home or Path.home()).expanduser().absolute()
    biblioteca = (opciones.biblioteca or home/".local/share/gamemaker-biblioteca").expanduser().absolute()
    if biblioteca.is_symlink():
        p.error("La biblioteca de destino es un enlace; elige su ubicación real explícitamente.")
    comprobar = any(opcion in resto for opcion in ("--comprobar", "--comprobar-paquete"))
    try:
        es_sha = bool(re.fullmatch(r"[0-9a-f]{40}", opciones.revision))
        referencia = opciones.revision if es_sha else "refs/tags/" + opciones.revision
        paquete = descargar(f"https://codeload.github.com/{REPO}/zip/{referencia}")
        # git archive conserva el commit en el comentario ZIP. Se contrasta también
        # con el SHA solicitado; no necesita cuenta ni cuota de la API de GitHub.
        with ZipFile(io.BytesIO(paquete)) as zip_descargado:
            commit = zip_descargado.comment.decode("ascii")
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ValueError("La distribución no declara un commit identificable.")
        if es_sha and commit != opciones.revision:
            raise ValueError("La distribución no corresponde al SHA solicitado.")
        print(f"GameMaker · revisión {opciones.revision}: {commit}", flush=True)
        # Se prepara en el mismo volumen; la copia anterior se conserva completa.
        padre = biblioteca.parent if not comprobar else Path(tempfile.gettempdir())
        padre.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".gm-descarga-", dir=padre) as temporal:
            nueva = Path(temporal)/"biblioteca"
            nueva.mkdir()
            extraer(paquete, nueva)
            extra = ["--home", str(home)] if opciones.home else []
            comando = [sys.executable, str(nueva/"instalar.py"), "--comprobar-paquete"] + extra + resto
            subprocess.run(comando, check=True)
            if comprobar:
                print("Distribución comprobada; no se ha instalado ni registrado.")
                return 0
            recibo = {"revision": opciones.revision, "commit": commit,
                      "archivo_sha256": hashlib.sha256(paquete).hexdigest()}
            (nueva/".gamemaker-distribucion.json").write_text(
                json.dumps(recibo, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
            backup = None
            igual = biblioteca.is_dir() and contenido(biblioteca) == contenido(nueva)
            if biblioteca.exists() and not igual:
                backup = Path(tempfile.mkdtemp(prefix="gamemaker-biblioteca-anterior-", dir=padre))/"biblioteca"
                biblioteca.rename(backup)
            try:
                if not igual:
                    nueva.rename(biblioteca)
            except OSError:
                if backup is not None:
                    backup.rename(biblioteca)
                raise
            # Los enlaces existentes apuntan a la ubicación estable, no al staging.
            # Solo allí se puede comprobar el plan real de una actualización --enlace.
            try:
                subprocess.run([sys.executable, str(biblioteca/"instalar.py"),
                                "--comprobar"] + extra + resto, check=True)
            except subprocess.CalledProcessError:
                if not igual:
                    biblioteca.rename(nueva)
                    if backup is not None:
                        backup.rename(biblioteca)
                raise
            if backup:
                print(f"Biblioteca anterior conservada: {backup}", flush=True)
        argumentos = [sys.executable, str(biblioteca/"instalar.py")]
        if opciones.home:
            argumentos += ["--home", str(home)]
        return subprocess.run(argumentos + resto, check=False).returncode
    except (OSError, ValueError, BadZipFile, subprocess.CalledProcessError) as error:
        print(f"No se ha completado la instalación: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        raise SystemExit("Necesitas Python 3.10 o posterior.")
    raise SystemExit(main())
