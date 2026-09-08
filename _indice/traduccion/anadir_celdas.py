#!/usr/bin/env python3
"""Añade pares inglés→español a celdas_es.json leyendo un JSON por la entrada estándar."""
import json, os, sys

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

AQUI = os.path.dirname(os.path.abspath(__file__))
MEM = os.path.join(AQUI, "celdas_es.json")
memo = json.load(open(MEM, encoding="utf-8")) if os.path.exists(MEM) else {}
antes = len(memo)
memo.update(json.load(sys.stdin))
json.dump(memo, open(MEM, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print(f"celdas_es.json: {antes} → {len(memo)} (+{len(memo) - antes})")
