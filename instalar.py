#!/usr/bin/env python3
"""Instala la skill GameMaker con Python estándar, sin cambiar el agente ni sus modelos."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True

NOMBRE = "gamemaker-biblioteca"
SIDECAR = ".gamemaker-biblioteca-ruta"
RAIZ = Path(__file__).resolve().parent
ORIGEN = RAIZ / "_indice/skills" / NOMBRE
RESIDUOS = {".git", "__pycache__", ".DS_Store"}


class ErrorInstalacion(Exception):
    pass


def contenido(carpeta):
    archivos = {}
    for raiz, directorios, nombres in os.walk(carpeta, followlinks=False):
        directorios[:] = [n for n in directorios if n not in RESIDUOS]
        for nombre in directorios + nombres:
            ruta = Path(raiz) / nombre
            if ruta.is_symlink():
                raise ErrorInstalacion(f"El paquete contiene un enlace no portable: {ruta}")
        for nombre in nombres:
            if nombre in RESIDUOS or nombre.endswith((".pyc", ".pyo")):
                continue
            ruta = Path(raiz) / nombre
            if not ruta.is_file():
                raise ErrorInstalacion(f"Entrada no regular en el paquete: {ruta}")
            archivos[ruta.relative_to(carpeta).as_posix()] = hashlib.sha256(ruta.read_bytes()).hexdigest()
    return archivos


def validar_paquete(origen):
    try:
        manifiesto = json.loads((origen / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ErrorInstalacion("Falta un manifest.json válido. Regenera el paquete desde mantenimiento.") from error
    if (not isinstance(manifiesto, dict) or type(manifiesto.get("schema")) is not int or manifiesto["schema"] != 1 or
            manifiesto.get("name") != NOMBRE or not isinstance(manifiesto.get("version"), str) or
            not manifiesto["version"].strip() or not isinstance(manifiesto.get("files"), dict)):
        raise ErrorInstalacion("El manifiesto no corresponde al paquete GameMaker o a su esquema.")
    for nombre, huella in manifiesto["files"].items():
        ruta = PurePosixPath(nombre)
        if (not nombre or "\\" in nombre or ruta.is_absolute() or PureWindowsPath(nombre).drive or ".." in ruta.parts or
                ruta.as_posix() != nombre or nombre == "manifest.json" or
                not isinstance(huella, str) or not re.fullmatch(r"[0-9a-f]{64}", huella)):
            raise ErrorInstalacion(f"Entrada insegura o inválida en el manifiesto: {nombre}")
    archivos = contenido(origen)
    archivos.pop("manifest.json", None)
    if archivos != manifiesto["files"]:
        raise ErrorInstalacion("El paquete no coincide con su manifiesto SHA-256. No se ha instalado nada.")
    if "SKILL.md" not in archivos:
        raise ErrorInstalacion("Falta SKILL.md en el manifiesto.")
    texto = (origen / "SKILL.md").read_text(encoding="utf-8")
    version = re.search(r"<!--\s*SKILL-VERSION:\s*(.+?)\s*-->", texto)
    if not version or version.group(1) != manifiesto["version"]:
        raise ErrorInstalacion("La revisión de SKILL.md no coincide con el manifiesto.")
    return manifiesto


def cargar_harnesses():
    ruta = RAIZ / "_indice/harnesses.py"
    spec = importlib.util.spec_from_file_location("gm_harnesses_instalacion", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def resolver_opciones(argumentos, parser):
    modulo = cargar_harnesses()
    home = Path(argumentos.home).expanduser().absolute() if argumentos.home else Path.home()
    requiere_omp = (not argumentos.listar_harnesses or argumentos.comprobar_paquete) and (
        argumentos.harness == "omp" or (not argumentos.harness and not argumentos.destino))
    try:
        opciones = modulo.destinos(home, validar_omp=requiere_omp)
        omp_config = os.environ.get("PI_CONFIG_DIR", "")
        if requiere_omp and (Path(omp_config).is_absolute() or omp_config.startswith("~")):
            raise ValueError("PI_CONFIG_DIR debe ser relativo al home; usa PI_CODING_AGENT_DIR absoluto o --destino.")
    except ValueError as error:
        parser.error(str(error))
    if argumentos.harness and argumentos.harness not in opciones:
        parser.error("Harness desconocido: " + argumentos.harness)
    return home, opciones


def planificar(argumentos, home, opciones):
    if argumentos.destino:
        candidatas = [("destino", Path(argumentos.destino).expanduser().absolute())]
    else:
        candidatas = [(nombre, ruta) for nombre, (comandos, ruta) in opciones.items()
                      if (nombre == argumentos.harness if argumentos.harness else
                          not argumentos.detectar or not comandos or ruta.is_dir() or
                          any(shutil.which(c) for c in comandos))]
    grupos = {}
    fuente = ORIGEN.resolve()
    for nombre, base in candidatas:
        destino = base / NOMBRE
        real = destino.resolve()
        if real != fuente and fuente in real.parents:
            raise ErrorInstalacion("El destino está dentro del paquete canónico.")
        if real != fuente and real in fuente.parents:
            raise ErrorInstalacion("El destino contiene el paquete canónico.")
        if argumentos.home and not argumentos.destino and real != fuente and not real.is_relative_to(home.resolve()):
            raise ErrorInstalacion(f"El destino de {nombre} sale de --home; usa un override dentro de esa raíz o --destino.")
        grupo = grupos.setdefault(real, [])
        grupo.append((nombre, destino))
    plan = []
    rutas = list(grupos)
    for indice, ruta in enumerate(rutas):
        for otra in rutas[indice+1:]:
            if ruta in otra.parents or otra in ruta.parents:
                raise ErrorInstalacion(f"Los destinos se solapan: {ruta} y {otra}. No se ha instalado nada.")
    for real, miembros in grupos.items():
        if real == fuente:
            plan.append((real, miembros, True))
            continue
        # Un alias a otra copia se conserva; solo se escribe si su referente está elegido.
        if all(ruta.is_symlink() for _, ruta in miembros):
            if mismo_contenido(real):
                plan.append((real, miembros, True))
                continue
            raise ErrorInstalacion(f"El enlace {miembros[0][1]} apunta fuera del plan a {real}. "
                                   "Elige también ese destino o instálalo con --destino.")
        plan.append((real, miembros, False))
    return plan


def mismo_contenido(destino):
    if not destino.is_dir():
        return False
    try:
        return contenido(destino) == contenido(ORIGEN)
    except (OSError, ErrorInstalacion):
        return False


def instalar_en(destino, enlace=False, esperado=None):
    if esperado is not None and contenido(ORIGEN) != esperado:
        raise ErrorInstalacion("El paquete cambió durante la instalación; vuelve a comprobarlo.")
    if mismo_contenido(destino) and (not enlace or destino.is_symlink()):
        return None, False
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = Path(tempfile.mkdtemp(prefix=".gm-skill.", dir=destino.parent))
    copia = temporal / NOMBRE
    previa = None
    conservar_temporal = False
    try:
        if enlace:
            copia.symlink_to(ORIGEN.resolve(), target_is_directory=True)
        else:
            shutil.copytree(ORIGEN, copia, ignore=shutil.ignore_patterns(*RESIDUOS, "*.pyc", "*.pyo"))
            if contenido(copia) != (esperado if esperado is not None else contenido(ORIGEN)):
                raise ErrorInstalacion("Copia incompleta; se conserva el destino anterior.")
        if os.path.lexists(destino):
            carpeta_backup = destino.parent / ".gamemaker-biblioteca-backups" / ("copia." + uuid.uuid4().hex)
            carpeta_backup.mkdir(parents=True)
            previa = carpeta_backup / NOMBRE
            os.replace(destino, previa)
        try:
            os.replace(copia, destino)
        except OSError as error:
            if previa is not None:
                try:
                    os.replace(previa, destino)
                except OSError as restauracion:
                    conservar_temporal = True
                    raise ErrorInstalacion(f"Falló la instalación y la restauración: {restauracion}. "
                                           f"Copia anterior: {previa}; paquete preparado: {copia}") from error
            raise ErrorInstalacion("No se pudo instalar; el destino anterior se conserva o se ha restaurado.") from error
        return previa, True
    finally:
        if not conservar_temporal:
            shutil.rmtree(temporal)


def escribir_ruta(registro, conservar_anterior=False):
    valor = str(RAIZ.resolve())
    if registro.is_file() and registro.read_text(encoding="utf-8") == valor:
        return registro
    registro.parent.mkdir(parents=True, exist_ok=True)
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=registro.parent, delete=False) as archivo:
            temporal = Path(archivo.name)
            archivo.write(valor)
        if conservar_anterior and registro.is_file():
            backup = registro.with_name("ruta-anterior." + uuid.uuid4().hex)
            shutil.copy2(registro, backup)
            print("La ruta global de biblioteca cambia; copia anterior conservada: " + str(backup))
        os.replace(temporal, registro)
    finally:
        if temporal is not None and temporal.exists():
            temporal.unlink()
    return registro


def registrar(home):
    return escribir_ruta(home / ".config/gamemaker-biblioteca/ruta", conservar_anterior=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--harness", help="Instala solo en el destino nativo de ese agente.")
    grupo.add_argument("--destino", help="Carpeta de skills aislada, con registro propio de la biblioteca.")
    grupo.add_argument("--todos", action="store_true", help="Todos los destinos compatibles (predeterminado).")
    grupo.add_argument("--detectar", action="store_true", help="Solo comandos en PATH y directorios existentes.")
    parser.add_argument("--home", help="Raíz de usuario explícita, sin cambiar HOME.")
    parser.add_argument("--comprobar", action="store_true", help="Valida y muestra el plan sin escribir nada.")
    parser.add_argument("--comprobar-paquete", action="store_true", help="Valida solo el paquete y los selectores; no comprueba destinos ni escribe.")
    parser.add_argument("--enlace", action="store_true", help="Enlaza al checkout en vez de copiar.")
    parser.add_argument("--indices", action="store_true", help="Deriva índices antes de cambiar instalaciones.")
    parser.add_argument("--registrar", action="store_true", help="Registra también la biblioteca con --destino.")
    parser.add_argument("--listar-harnesses", action="store_true")
    argumentos = parser.parse_args(argv)
    try:
        home, opciones = resolver_opciones(argumentos, parser)
        if argumentos.listar_harnesses and not argumentos.comprobar_paquete:
            for nombre, (_, ruta) in opciones.items():
                print(f"{nombre}\t{ruta}")
            return 0
        manifiesto = validar_paquete(ORIGEN)
        if argumentos.comprobar_paquete:
            print(f"Paquete {manifiesto['version']}: {len(manifiesto['files'])} archivos verificados; sin comprobar destinos ni escribir.")
            return 0
        esperado = contenido(ORIGEN)
        plan = planificar(argumentos, home, opciones)
        if argumentos.home:
            for _, miembros, _ in plan:
                for _, destino_logico in miembros:
                    sidecar = destino_logico.parent / SIDECAR
                    if not sidecar.resolve().is_relative_to(home.resolve()) and not argumentos.destino:
                        raise ErrorInstalacion("El registro de un destino sale de --home a través de un enlace.")
        if argumentos.home and (not argumentos.destino or argumentos.registrar):
            registro = home / ".config/gamemaker-biblioteca/ruta"
            if not registro.resolve().is_relative_to(home.resolve()):
                raise ErrorInstalacion("El registro de biblioteca sale de --home a través de un enlace.")
        print(f"Skill {manifiesto['version']}: {len(manifiesto['files'])} archivos verificados.")
        for real, miembros, canonico in plan:
            nombres = ", ".join(nombre for nombre, _ in miembros)
            print(f"  {nombres}: {real}" + (" (enlace al día; se conserva)" if canonico else ""))
        if argumentos.comprobar:
            print("Paquete y plan comprobados; sin escrituras, instalación ni registro.")
            return 0
        if argumentos.indices:
            resultado = subprocess.run([sys.executable, str(RAIZ / "_indice/construir-indices.py")], check=False)
            if resultado.returncode:
                raise ErrorInstalacion("Índices no generados. Se conservan las instalaciones anteriores.")
        completados = 0
        for destino, miembros, canonico in plan:
            try:
                backup, cambiado = (None, False) if canonico else instalar_en(destino, argumentos.enlace, esperado)
                for _, destino_logico in miembros:
                    escribir_ruta(destino_logico.parent / SIDECAR)
            except (OSError, ErrorInstalacion) as error:
                raise ErrorInstalacion(f"{error} Destinos anteriores procesados: {completados}; "
                                       "sus cambios y copias previas se conservan.") from error
            completados += 1
            print(("Instalada: " if cambiado else "Ya al día: ") + str(destino))
            if backup:
                print("  Copia anterior conservada: " + str(backup))
            for _, alias in miembros:
                if alias.is_symlink():
                    print("  Enlace conservado: " + str(alias))
        if not argumentos.destino or argumentos.registrar:
            print("Ruta local registrada: " + str(registrar(home)))
        else:
            print("Biblioteca vinculada a este destino mediante su registro propio.")
        print("Lista para trabajar con GameMaker. Si el agente ya estaba abierto, recarga sus skills o reábrelo.")
        return 0
    except (ErrorInstalacion, OSError, ValueError, RuntimeError) as error:
        print("Error: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        raise SystemExit("Falta Python 3.10 o posterior.")
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    raise SystemExit(main())
