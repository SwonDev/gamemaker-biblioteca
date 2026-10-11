#!/usr/bin/env python3
"""Prueba GML documental HTTP con servidor local propio, sin proyectos existentes.

macOS VM, gm-cli 2.4.0, GMS2 2026.0.0.23. Reutiliza el ejecutor con tope de r47.
Extrae clasificador, lector y callbacks; el dominio liveops se sustituye por una
frontera de prueba declarada. No acredita CORS, TLS, backend remoto ni cola multis sesión.
--mutacion introduce un fallo solo en el fixture; debe devolver 1.
"""
from __future__ import annotations
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import threading

RAIZ = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("contratos_r47", Path(__file__).with_name("probar-contratos-r47.py"))
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)
DOC_HTTP = "12 - Utilidades e integraciones/12 - HTTP asíncrono - estados, propiedad y respuestas tardías.md"
DOC_LIVE = "04 - Recetas por género/52 - Live-ops técnico (config remota, versión mínima, mensajes del juego).md"
DOC_TELE = "13 - Diseño y producción de videojuegos/01 - Diseño de juego - core loop, mecánicas, balance y dificultad.md"
DOC_INPUT = "01 - Fundamentos/12 - Input - teclado, ratón y gamepad.md"
BLOQUE = re.compile(r"^```gml\s*\n(.*?)^```\s*$", re.M | re.S)

def extraer():
    recibos, bloques = [], []
    for ruta, marcador in [(DOC_HTTP, "function clasificar_respuesta_http("),
                           (DOC_LIVE, "/// obj_control · Async - HTTP"),
                           (DOC_TELE, "function telemetria_leer_pendiente("),
                           (DOC_TELE, "/// obj_arranque · Async - HTTP")]:
        contenido = (RAIZ / ruta).read_text(encoding="utf-8")
        candidatos = [b for b in BLOQUE.findall(contenido) if marcador in b]
        if len(candidatos) != 1: raise ValueError(f"Bloque ambiguo o ausente: {ruta}: {marcador}")
        b = candidatos[0]
        bloques.append(b)
        recibos.append({"ruta": ruta, "marcador": marcador,
                        "sha256_documento": hashlib.sha256(contenido.encode()).hexdigest(),
                        "sha256_bloque": hashlib.sha256(b.encode()).hexdigest()})
    contenido = (RAIZ / DOC_INPUT).read_text(encoding="utf-8")
    candidatos = [b for b in BLOQUE.findall(contenido) if "// ═══════════ obj_jugador (Step)" in b]
    if len(candidatos) != 1: raise ValueError("Step de input ambiguo o ausente")
    fragmento = candidatos[0].split("var _dx = input_mover_x();", 1)[1].split("move_and_collide(", 1)[0]
    fragmento = "var _dx = input_mover_x();" + fragmento
    bloques.append(fragmento)
    recibos.append({"ruta": DOC_INPUT, "marcador": "vector antes de move_and_collide",
                    "sha256_documento": hashlib.sha256(contenido.encode()).hexdigest(),
                    "sha256_bloque": hashlib.sha256(fragmento.encode()).hexdigest()})
    return bloques, recibos

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solo-extraer", action="store_true")
    parser.add_argument("--mutacion", choices=["progreso", "http", "cola", "input"])
    parser.add_argument("--tope", type=int, default=240)
    args = parser.parse_args()
    if args.tope <= 0: parser.error("--tope debe ser positivo")
    bloques, fuentes = extraer()
    if args.solo_extraer:
        print(json.dumps(fuentes, ensure_ascii=False, indent=2)); return 0
    gm = shutil.which("gm-cli")
    if not gm or sys.platform != "darwin":
        print("No ejecutado: requiere gm-cli y macOS."); return 2
    trabajo = Path(tempfile.mkdtemp(prefix="gm-r48-http-"))
    print(f"Artefactos privados: {trabajo}", flush=True)
    pedidos = []
    class Servidor(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def responder(self):
            cuerpo = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            codigo = 500 if self.path.endswith("500") else 204 if self.path.endswith("204") else 200
            datos = b"{roto" if self.path == "/configbad" else b'{"marca":"nueva"}'
            if codigo == 204: datos = b""
            pedidos.append({"ruta": self.path, "metodo": self.command, "codigo": codigo, "bytes_cuerpo": len(cuerpo)})
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)
        do_GET = responder
        do_POST = responder
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), Servidor)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    sha_script = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    recibo = {"runtime": BASE.RUNTIME, "target": "mac", "modo": "vm", "fuentes": fuentes, "sha256_orquestador": sha_script,
              "mutacion": args.mutacion, "estado": "no terminado", "limite_por_comando_segundos": args.tope,
              "limites": ["dominio liveops sustituido por validación JSON mínima", "sin TLS/CORS/backend remoto",
                          "sin cierre y recuperación de cola multisesión", "progreso y códigos ausentes sintéticos"]}
    env = os.environ.copy(); env["GM_BIBLIOTECA_RUNTIME"] = BASE.RUNTIME
    def correr(cmd, nombre, cwd=trabajo):
        return BASE.ejecutar(cmd, cwd, trabajo / (nombre + ".log"), env, args.tope)
    try:
        version = correr([gm, "--version"], "version")
        if not re.search(r"^2\.4\.0\s*$", version, re.M): raise RuntimeError("Requiere CLI 2.4.0 para esta matriz")
        recibo["gm_cli"] = "2.4.0"
        correr([gm, "init", "--no-interactive", "--name", "gm_http_r48", "--template", "blank",
                "--no-ai", "--no-actions", "--toolchain", "GMS2@" + BASE.RUNTIME], "init")
        proyecto = trabajo / "gm_http_r48"; yyp = proyecto / "gm_http_r48.yyp"
        comandos = ["resource create type=script name=scr_fuentes", "resource create type=script name=scr_banco"]
        for obj in ["obj_http", "obj_live", "obj_tele"]:
            comandos += [f"resource create type=object name={obj}",
                         f"object event findorcreate name={obj} type=other subtype=outside",
                         f"resource set expr={obj}.eventList[0].eventNum value=62",
                         f"room instance create room=room1 object={obj} name=inst_{obj} layer=Instances x=0 y=0"]
        comandos += ["object event findorcreate name=obj_http type=create", "object event findorcreate name=obj_http type=step subtype=step_normal"]
        lote = trabajo / "recursos.txt"; lote.write_text("\n".join(comandos) + "\n", encoding="utf-8")
        correr([gm, "resourcetool", "script", str(lote), str(yyp)], "recursos")
        helper, live, tele, callback, vector = bloques
        def mutar(texto, anterior, nuevo):
            if texto.count(anterior) != 1: raise ValueError("La mutación no tiene exactamente un punto de aplicación")
            return texto.replace(anterior, nuevo)
        if args.mutacion == "progreso":
            helper = mutar(helper, '_r.clase = "progreso"; return _r;', '_r.clase = "progreso"; _r.terminal = true; return _r;')
        if args.mutacion == "http": helper = mutar(helper, "_codigo >= 200 && _codigo < 300", "_codigo >= 200")
        if args.mutacion == "cola":
            callback = mutar(callback, "telemetria_leer_pendiente() == global.telemetria_envio_cuerpo", "true")
        if args.mutacion == "input": vector = mutar(vector, "if (_longitud > 1)", "if (_dx != 0 || _dy != 0)")
        fuentes_gml = (f'#macro HTTP_TEST_BASE "http://127.0.0.1:{servidor.server_port}"\n'
                       '#macro TELEMETRIA_ARCHIVO "http_r48_pendiente.json"\n'
                       '#macro TELEMETRIA_ACTIVA true\n#macro LIVEOPS_CONFIG_ARCHIVO "http_r48_config.json"\n'
                       + helper + "\n" + tele
                       + "\nfunction prueba_http_vector()\n{\n" + vector + "return [_dx, _dy];\n}\n")
        (proyecto / "scripts/scr_fuentes/scr_fuentes.gml").write_text(fuentes_gml, encoding="utf-8")
        banco = (RAIZ / "_indice/pruebas/banco_http_r48.gml").read_bytes()
        (proyecto / "scripts/scr_banco/scr_banco.gml").write_bytes(banco)
        for obj, fuente in [("obj_live", live), ("obj_tele", callback), ("obj_http",
                             'var _r = clasificar_respuesta_http(async_load, global.http_id);\n'
                             'if (_r.coincide && _r.terminal) { global.http_recibido = true;\n'
                             'show_debug_message("HTTP_EVENT_R48: " + json_stringify({ etapa: global.http_stage,\n'
                             'id_peticion: global.http_id, estado: async_load[? "status"],\n'
                             'codigo: ds_map_exists(async_load, "http_status") ? async_load[? "http_status"] : -1 })); }\n')]:
            carpeta = proyecto / "objects" / obj
            original = carpeta / "Other_0.gml"
            if not original.exists(): raise RuntimeError(f"No se creó evento base de {obj}")
            original.rename(carpeta / "Other_62.gml")
            (carpeta / "Other_62.gml").write_text(fuente, encoding="utf-8")
        (proyecto / "objects/obj_http/Create_0.gml").write_text("prueba_http_empezar();\n", encoding="utf-8")
        (proyecto / "objects/obj_http/Step_0.gml").write_text("prueba_http_avanzar();\n", encoding="utf-8")
        recibo["sha256_banco"] = hashlib.sha256(banco).hexdigest()
        recibo["sha256_fuente_fixture"] = hashlib.sha256(fuentes_gml.encode()).hexdigest()
        correr([sys.executable, str(RAIZ / "_indice/validar-proyecto.py"), str(proyecto), "--todo"], "validacion")
        args_gm = [str(yyp), "--target", "mac", "--runtime", "vm", "--toolchain", "GMS2@" + BASE.RUNTIME]
        correr([gm, "compile", *args_gm], "compilacion", proyecto)
        salida = correr([gm, "run", *args_gm], "ejecucion", proyecto)
        filas = re.findall(r"HTTP_R48: (\d+) correctas, (\d+) fallidas", salida)
        if len(filas) != 1: raise RuntimeError("Resultado del banco ausente o duplicado")
        correctas, fallidas = map(int, filas[0])
        if correctas + fallidas != 49: raise RuntimeError("El banco no ejecutó sus 49 comprobaciones")
        rutas = ["/config200", "/config500", "/config204", "/configbad", "/post500", "/post200", "/post204", "/postnuevo"]
        if [p["ruta"] for p in pedidos] != rutas: raise RuntimeError("No llegaron las ocho solicitudes esperadas al servidor")
        for i, p in enumerate(pedidos):
            if p["metodo"] != ("GET" if i < 4 else "POST") or p["bytes_cuerpo"] != (0 if i < 4 else len(b"lote inicial")):
                raise RuntimeError("Método o cuerpo inesperado en el servidor")
        trazas = [json.loads(t) for t in re.findall(r"HTTP_EVENT_R48: (\{[^\n]+\})", salida)]
        if len(trazas) != 8 or [t["etapa"] for t in trazas] != list(range(8)):
            raise RuntimeError("Faltan callbacks terminales reales")
        if extraer()[1] != fuentes: raise RuntimeError("Documentos cambiaron durante la ejecución")
        if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != sha_script or hashlib.sha256((RAIZ / "_indice/pruebas/banco_http_r48.gml").read_bytes()).hexdigest() != recibo["sha256_banco"]:
            raise RuntimeError("Orquestador o banco cambiaron durante la ejecución")
        recibo.update({"estado": "ejecutado", "correctas": correctas, "fallidas": fallidas, "callbacks_terminales": trazas})
        print(f"HTTP_R48: {correctas} correctas, {fallidas} fallidas")
        return 0 if fallidas == 0 else 1
    except (OSError, RuntimeError, ValueError) as error:
        recibo.update({"estado": "no completado", "error": str(error)}); print(str(error)); return 2
    finally:
        servidor.shutdown(); servidor.server_close(); hilo.join(timeout=3)
        recibo["peticiones_servidor"] = pedidos
        (trabajo / "recibo.json").write_text(json.dumps(recibo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__": sys.exit(main())
