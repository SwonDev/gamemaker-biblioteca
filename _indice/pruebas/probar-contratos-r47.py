#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ejecuta contratos CLDR entero, replay y snapshot del GML real documentado.

Requiere gm-cli 2.4.0 y GMS2 2026.0.0.23; abre brevemente el runner macOS.
Crea un proyecto temporal propio mediante ResourceTool, valida, compila y ejecuta.
Conserva logs y recibo en la carpeta temporal que imprime; no toca juegos existentes.
No acredita otros targets, un backend ni las reglas de gameplay de otro proyecto.

    python3 _indice/pruebas/probar-contratos-r47.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile

RAIZ = Path(__file__).resolve().parents[2]
RUNTIME = "2026.0.0.23"
DOC_IDIOMA = "04 - Recetas por género/21 - Localización e idiomas (con traducción por IA).md"
DOC_QA = "13 - Diseño y producción de videojuegos/10 - Testing y QA.md"
DOC_RED = "04 - Recetas por género/14 - Multijugador.md"
BLOQUE = re.compile(r"^```gml\s*\n(.*?)^```\s*$", re.M | re.S)
FUNCION = re.compile(r"^\s*function\s+(\w+)\s*\(", re.M)
GRUPOS = [
    (DOC_IDIOMA, ["txt", "categoria_plural_entero", "txt_n"]),
    (DOC_QA, ["AzarReproducible", "generar_botin"]),
    (DOC_QA, ["replay_iniciar", "replay_anotar", "replay_avanzar_frame", "replay_cerrar", "replay_verificar"]),
    (DOC_RED, ["recibir_snapshot"]),
    (DOC_RED, ["reconciliar"]),
    (DOC_RED, ["servidor_consumir_inputs"]),
]
EVENTOS = {"objNetManager": "// objNetManager — Create (persistente)",
           "objNetEntity": "// objNetEntity — Create"}


def extraer():
    """Cada familia debe estar íntegra en un único bloque; nunca una copia alternativa."""
    trozos, recibos = [], []
    for relativo, requeridas in GRUPOS:
        contenido = (RAIZ / relativo).read_text(encoding="utf-8")
        candidatas = [b for b in BLOQUE.findall(contenido)
                      if set(requeridas).issubset(FUNCION.findall(b))]
        if len(candidatas) != 1:
            raise ValueError(f"{relativo}: esperaba un bloque con {requeridas}; encontré {len(candidatas)}")
        bloque = candidatas[0]
        trozos.append(f"// EXTRAÍDO SIN CAMBIOS DE {relativo}\n{bloque.rstrip()}\n")
        recibos.append({"documento": relativo, "funciones": FUNCION.findall(bloque),
                        "sha256_documento": hashlib.sha256(contenido.encode()).hexdigest(),
                        "sha256_bloque": hashlib.sha256(bloque.encode()).hexdigest()})
    contenido_red = (RAIZ / DOC_RED).read_text(encoding="utf-8")
    bloques_red = BLOQUE.findall(contenido_red)
    seleccion = [b for b in bloques_red if re.search(r"^#macro NET_MAX_ENTIDADES\s", b, re.M)]
    if len(seleccion) != 1:
        raise ValueError("No encuentro un bloque único con el límite de entidades de red")
    eventos = {}
    for nombre, marcador in EVENTOS.items():
        candidatas = [b for b in bloques_red if marcador in b]
        if len(candidatas) != 1:
            raise ValueError(f"No encuentro un Create único de {nombre}")
        eventos[nombre] = candidatas[0]
    for nombre, bloque in [("constantes_red", seleccion[0]), *eventos.items()]:
        recibos.append({"documento": DOC_RED, "destino": nombre,
                        "sha256_documento": hashlib.sha256(contenido_red.encode()).hexdigest(),
                        "sha256_bloque": hashlib.sha256(bloque.encode()).hexdigest()})
    trozos.insert(0, seleccion[0])
    return "\n".join(trozos), recibos, eventos


def ejecutar(cmd, cwd, archivo, env, limite):
    """Tope por comando; un timeout termina solo el grupo creado para esta ejecución."""
    with archivo.open("wb") as salida:
        proceso = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=salida,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            codigo = proceso.wait(timeout=limite)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proceso.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                proceso.wait(timeout=3)
            except subprocess.TimeoutExpired:
                pass
            # El padre puede salir mientras un hijo ignora SIGTERM. El grupo
            # propio se termina también cuando wait() ya devolvió por el padre.
            try:
                os.killpg(proceso.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proceso.wait()
            raise RuntimeError(f"Tope de {limite}s agotado: {archivo.name}")
    if codigo != 0:
        raise RuntimeError(f"Código {codigo}: {archivo.name}")
    return archivo.read_text(encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tope", type=int, default=240, help="segundos máximos por comando")
    parser.add_argument("--solo-extraer", action="store_true", help="comprueba familias y muestra huellas, sin ejecutar GameMaker")
    args = parser.parse_args()
    if args.tope <= 0:
        parser.error("--tope debe ser positivo")
    fuente, fuentes, eventos = extraer()
    if args.solo_extraer:
        print(json.dumps(fuentes, ensure_ascii=False, indent=2))
        return 0
    gm = shutil.which("gm-cli")
    if not gm:
        print("✗ No se ha ejecutado: gm-cli no está disponible.")
        return 2
    if sys.platform != "darwin":
        print("✗ Este runner está verificado solo para macOS; no se ha ejecutado.")
        return 2
    trabajo = Path(tempfile.mkdtemp(prefix="gm-r47-contratos-"))
    print(f"Artefactos privados: {trabajo}", flush=True)
    env = os.environ.copy()
    env["GM_BIBLIOTECA_RUNTIME"] = RUNTIME
    recibo = {"runtime": RUNTIME, "target": "mac", "modo": "vm", "fuentes": fuentes,
              "estado": "no terminado", "limite_por_comando_segundos": args.tope}
    try:
        version = ejecutar([gm, "--version"], trabajo, trabajo / "version.log", env, args.tope)
        if not re.search(r"^2\.4\.0\s*$", version, re.M):
            raise RuntimeError("Este recibo requiere gm-cli 2.4.0; consulta version.log")
        recibo["gm_cli"] = "2.4.0"
        ejecutar([gm, "init", "--no-interactive", "--name", "gm_contratos_r47",
                  "--template", "blank", "--no-ai", "--no-actions", "--toolchain", "GMS2@" + RUNTIME],
                 trabajo, trabajo / "init.log", env, args.tope)
        proyecto = trabajo / "gm_contratos_r47"
        yyp = proyecto / "gm_contratos_r47.yyp"
        if not yyp.is_file():
            raise RuntimeError("Init no creó el proyecto esperado; consulta init.log")
        lote = trabajo / "recursos.txt"
        lote.write_text("\n".join([
            "resource create type=object name=obj_contratos",
            "resource create type=script name=scr_documentos",
            "resource create type=script name=scr_banco_contratos",
            "resource create type=object name=objNetManager",
            "resource create type=object name=objNetEntity",
            "object event findorcreate name=objNetManager type=create",
            "object event findorcreate name=objNetEntity type=create",
            "object event findorcreate name=obj_contratos type=create",
            "room instance create room=room1 object=obj_contratos name=inst_contratos layer=Instances x=0 y=0",
        ]) + "\n", encoding="utf-8")
        ejecutar([gm, "resourcetool", "script", str(lote), str(yyp)], trabajo,
                 trabajo / "recursos.log", env, args.tope)
        script = proyecto / "scripts/scr_documentos/scr_documentos.gml"
        banco = proyecto / "scripts/scr_banco_contratos/scr_banco_contratos.gml"
        evento = proyecto / "objects/obj_contratos/Create_0.gml"
        for archivo in (script, banco, evento):
            if not archivo.is_file():
                raise RuntimeError(f"El recurso no se creó: {archivo.relative_to(proyecto)}")
        if "inst_contratos" not in (proyecto / "rooms/room1/room1.yy").read_text():
            raise RuntimeError("La instancia de prueba no llegó a la sala")
        script.write_text(fuente, encoding="utf-8")
        for nombre, bloque in eventos.items():
            destino = proyecto / "objects" / nombre / "Create_0.gml"
            if not destino.is_file():
                raise RuntimeError(f"El Create de {nombre} no se creó")
            destino.write_text(bloque, encoding="utf-8")
        origen_banco = RAIZ / "_indice/pruebas/banco_contratos_r47.gml"
        banco.write_bytes(origen_banco.read_bytes())
        recibo["sha256_banco"] = hashlib.sha256(banco.read_bytes()).hexdigest()
        evento.write_text("banco_contratos_r47();\ngame_end();\n", encoding="utf-8")
        ejecutar([sys.executable, str(RAIZ / "_indice/validar-proyecto.py"), str(proyecto), "--todo"],
                 trabajo, trabajo / "validacion.log", env, args.tope)
        ejecutar([gm, "compile", str(yyp), "--target", "mac", "--runtime", "vm", "--toolchain", "GMS2@" + RUNTIME],
                 proyecto, trabajo / "compilacion.log", env, args.tope)
        salida = ejecutar([gm, "run", str(yyp), "--target", "mac", "--runtime", "vm", "--toolchain", "GMS2@" + RUNTIME],
                          proyecto, trabajo / "ejecucion.log", env, args.tope)
        resultados = re.findall(r"CONTRATOS_R47: (\d+) correctas, (\d+) fallidas", salida)
        if len(resultados) != 1:
            raise RuntimeError("El runner no emitió exactamente un resultado del banco")
        correctas, fallidas = map(int, resultados[0])
        if correctas == 0:
            raise RuntimeError("El banco no ejecutó ninguna comprobación")
        _, actuales, _ = extraer()
        if [x["sha256_bloque"] for x in actuales] != [x["sha256_bloque"] for x in fuentes]:
            raise RuntimeError("Los bloques documentales cambiaron durante la ejecución; el recibo no es vigente")
        recibo.update({"estado": "ejecutado", "correctas": correctas, "fallidas": fallidas})
        print(f"CONTRATOS_R47: {correctas} correctas, {fallidas} fallidas")
        return 0 if fallidas == 0 else 1
    except (OSError, RuntimeError, ValueError) as error:
        recibo.update({"estado": "no completado", "error": str(error)})
        print("✗ " + str(error))
        return 2
    finally:
        (trabajo / "recibo.json").write_text(json.dumps(recibo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
